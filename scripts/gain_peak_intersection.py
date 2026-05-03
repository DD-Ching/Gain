#!/usr/bin/env python3
"""gain peak-intersection - validate the 4 indirect_human_evidence pairs at the target locus.

For each (regulator, target) pair classified as direct_human_non_lung_evidence
in metadata/evidence_audit.csv (SMAD1->ID1, SMAD1->ID2, GLI2->PTCH1,
GLI2->GLI1), query ENCODE for the regulator's TF ChIP-seq experiments,
download the peak BED files, and check whether any peaks fall within
+/- 50 kb of the target gene's TSS (hg38, Ensembl-derived coordinates).

Stdlib only: urllib.request, gzip, csv, json, argparse.

Output:
  metadata/peak_intersection_results.csv with per-(experiment, target) rows
  describing the peak count in window and the nearest-peak distance.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import io
import json
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = REPO_ROOT / "metadata" / "peak_intersection_results.csv"

ENCODE_BASE = "https://www.encodeproject.org"
USER_AGENT = "gain-peak-intersection/0.1 (+https://github.com/DD-Ching/Gain)"
WINDOW_BP = 50_000  # +/- 50 kb of the target's TSS

# (regulator, target, ENCODE experiment ID, biosample label)
# 4 pairs x 1-3 experiments each = 8 (experiment, target) tests grouped
# into 4 pairs.
PAIRS_TO_TEST: list[tuple[str, str, str, str]] = [
    ("SMAD1", "ID1", "ENCSR213QOZ", "HepG2"),
    ("SMAD1", "ID1", "ENCSR813DCK", "GM12878"),
    ("SMAD1", "ID1", "ENCSR038DJJ", "K562"),
    ("SMAD1", "ID2", "ENCSR213QOZ", "HepG2"),
    ("SMAD1", "ID2", "ENCSR813DCK", "GM12878"),
    ("SMAD1", "ID2", "ENCSR038DJJ", "K562"),
    ("GLI2", "PTCH1", "ENCSR978EQY", "HEK293"),
    ("GLI2", "GLI1", "ENCSR978EQY", "HEK293"),
]

# hg38 (GRCh38) target gene coordinates from Ensembl REST,
# verified 2026-05-03. TSS is `start` for + strand, `end` for - strand.
# Format: target -> (chrom, tss_position, strand_label, ensembl_summary)
TARGETS: dict[str, dict] = {
    "ID1":   {"chrom": "chr20", "tss": 31573014, "strand": "+",
              "source": "Ensembl ENSG00000125968 (chr20:31573014-31606515 +)"},
    "ID2":   {"chrom": "chr2",  "tss":  8678845, "strand": "+",
              "source": "Ensembl ENSG00000115738 (chr2:8678845-8684461 +)"},
    "PTCH1": {"chrom": "chr9",  "tss": 95517057, "strand": "-",
              "source": "Ensembl ENSG00000185920 (chr9:95442980-95517057 -)"},
    "GLI1":  {"chrom": "chr12", "tss": 57459785, "strand": "+",
              "source": "Ensembl ENSG00000111087 (chr12:57459785-57472268 +)"},
}

# Output column order
OUT_FIELDS = (
    "regulator", "target", "source_dataset", "experiment_id", "biosample",
    "genomic_interval_used", "target_locus_definition",
    "overlap_yes_no", "n_peaks_in_window", "n_peaks_total",
    "distance_to_target_locus_bp",
    "interpretation",
    "evidence_url",
)


# ----------- Network helpers -----------

def http_get_json(url: str, timeout: float = 20.0) -> dict | None:
    req = urllib.request.Request(
        url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.load(resp)
    except Exception as e:
        print(f"  HTTP error fetching {url}: {e}", file=sys.stderr)
        return None


def http_get_bytes(url: str, timeout: float = 60.0) -> bytes | None:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except Exception as e:
        print(f"  download error {url}: {e}", file=sys.stderr)
        return None


# ----------- ENCODE peak file selection -----------

def best_peak_file_url(experiment_id: str) -> tuple[str | None, str]:
    """Return (peak_bed_url_or_None, file_id_label) for the best representative
    peak BED file from this ENCODE experiment.

    Preference order on GRCh38 BED files:
      1. output_type == "conservative IDR thresholded peaks" (most stringent)
      2. output_type == "IDR thresholded peaks"
      3. output_type == "replicated peaks"
      4. any "bed narrowPeak" file_type
    """
    data = http_get_json(f"{ENCODE_BASE}/experiments/{experiment_id}/?format=json")
    if not data:
        return None, "no metadata"
    files = [
        f for f in data.get("files", [])
        if f.get("file_format") == "bed"
        and f.get("assembly") == "GRCh38"
        and f.get("status") in ("released", None)
    ]
    if not files:
        return None, "no GRCh38 BED files"

    def rank(f: dict) -> int:
        ot = (f.get("output_type") or "").lower()
        ft = (f.get("file_type") or "").lower()
        if "conservative idr thresholded peaks" in ot:
            return 0
        if "idr thresholded peaks" in ot:
            return 1
        if "replicated peaks" in ot:
            return 2
        if ft == "bed narrowpeak":
            return 3
        return 4

    files.sort(key=rank)
    chosen = files[0]
    href = chosen.get("href", "")
    full_url = ENCODE_BASE + href if href.startswith("/") else href
    label = f"{chosen.get('@id', '?')} ({chosen.get('output_type', '?')})"
    return full_url, label


# ----------- BED parsing & intersection -----------

def parse_bed_gz(blob: bytes) -> list[tuple[str, int, int]]:
    """Return list of (chrom, start, end). Handles plain or gzipped input."""
    data = blob
    if blob[:2] == b"\x1f\x8b":  # gzip magic
        data = gzip.decompress(blob)
    out: list[tuple[str, int, int]] = []
    for line in data.decode("utf-8", errors="replace").splitlines():
        if not line or line.startswith("#") or line.startswith("track"):
            continue
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        try:
            out.append((parts[0], int(parts[1]), int(parts[2])))
        except ValueError:
            continue
    return out


def intersection_summary(peaks: list[tuple[str, int, int]],
                         target: dict) -> tuple[int, int, int]:
    """Return (n_peaks_in_window, n_peaks_total_on_chrom, nearest_distance_bp).

    nearest_distance_bp is 0 if any peak overlaps the TSS exactly,
    otherwise the smallest absolute distance from any peak edge to TSS.
    Returns nearest_distance_bp = -1 if no peaks on the target chromosome.
    """
    chrom = target["chrom"]
    tss = target["tss"]
    lo, hi = tss - WINDOW_BP, tss + WINDOW_BP

    on_chrom = [(s, e) for c, s, e in peaks if c == chrom]
    if not on_chrom:
        return 0, 0, -1

    in_window = sum(1 for s, e in on_chrom if e >= lo and s <= hi)

    # nearest distance: 0 if peak spans tss; else min |edge - tss|
    nearest = None
    for s, e in on_chrom:
        if s <= tss <= e:
            nearest = 0
            break
        d = min(abs(s - tss), abs(e - tss))
        if nearest is None or d < nearest:
            nearest = d
    return in_window, len(on_chrom), int(nearest if nearest is not None else -1)


def interpret(in_window: int, distance: int) -> str:
    if distance == -1:
        return "no_locus_support"
    if distance == 0:
        return "supports"
    if in_window >= 1 and distance <= 5_000:
        return "supports"
    if in_window >= 1 and distance <= WINDOW_BP:
        return "weak_support"
    return "no_locus_support"


# ----------- Main pipeline -----------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="gain-peak-intersection",
        description="Peak-level validation of the 4 direct_human_non_lung_evidence pairs.",
    )
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--sleep", type=float, default=0.3,
                        help="seconds between ENCODE requests (default 0.3)")
    args = parser.parse_args(argv)

    # Cache peak files by experiment (each experiment is fetched at most once).
    experiment_peaks: dict[str, list[tuple[str, int, int]]] = {}
    experiment_url: dict[str, str] = {}
    experiment_label: dict[str, str] = {}

    unique_exps = sorted({pair[2] for pair in PAIRS_TO_TEST})
    print(f"fetching peak files for {len(unique_exps)} experiments")
    for i, exp_id in enumerate(unique_exps, 1):
        print(f"  [{i}/{len(unique_exps)}] {exp_id}: locating peak BED...")
        url, label = best_peak_file_url(exp_id)
        if not url:
            print(f"      ! no peak file found ({label})")
            experiment_peaks[exp_id] = []
            experiment_url[exp_id] = ""
            experiment_label[exp_id] = label
            time.sleep(args.sleep)
            continue
        experiment_url[exp_id] = url
        experiment_label[exp_id] = label
        print(f"      file: {label}")
        print(f"      url:  {url}")
        time.sleep(args.sleep)
        blob = http_get_bytes(url)
        if blob is None:
            print(f"      ! download failed")
            experiment_peaks[exp_id] = []
            continue
        peaks = parse_bed_gz(blob)
        experiment_peaks[exp_id] = peaks
        print(f"      parsed {len(peaks)} peaks ({len(blob):,} bytes)")
        time.sleep(args.sleep)

    rows: list[dict] = []
    for regulator, target_name, exp_id, biosample in PAIRS_TO_TEST:
        target = TARGETS[target_name]
        peaks = experiment_peaks.get(exp_id, [])
        in_window, on_chrom, nearest = intersection_summary(peaks, target)

        chrom = target["chrom"]
        lo, hi = target["tss"] - WINDOW_BP, target["tss"] + WINDOW_BP
        interval = f"{chrom}:{lo}-{hi}"
        locus = f"{target_name} TSS at {chrom}:{target['tss']} ({target['strand']} strand) — {target['source']}"

        overlap = "yes" if (nearest != -1 and in_window > 0) else "no"
        if nearest == -1:
            distance_str = "n/a (no peaks on chromosome)"
            interpretation = "inconclusive"
        else:
            distance_str = str(nearest)
            interpretation = interpret(in_window, nearest)

        source_dataset = f"ENCODE {exp_id} ({regulator} ChIP, {biosample})"
        evidence_url = f"https://www.encodeproject.org/experiments/{exp_id}/"

        rows.append({
            "regulator": regulator,
            "target": target_name,
            "source_dataset": source_dataset,
            "experiment_id": exp_id,
            "biosample": biosample,
            "genomic_interval_used": interval,
            "target_locus_definition": locus,
            "overlap_yes_no": overlap,
            "n_peaks_in_window": in_window,
            "n_peaks_total": on_chrom,
            "distance_to_target_locus_bp": distance_str,
            "interpretation": interpretation,
            "evidence_url": evidence_url,
        })

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=OUT_FIELDS)
        w.writeheader()
        for row in rows:
            w.writerow(row)

    # Summary printout
    print()
    print(f"wrote {args.out.relative_to(REPO_ROOT)}")
    print(f"  generated_at: {datetime.now(timezone.utc).isoformat(timespec='seconds')}")
    print(f"  total tests:  {len(rows)}")
    interp_counts: dict[str, int] = {}
    for r in rows:
        interp_counts[r["interpretation"]] = interp_counts.get(r["interpretation"], 0) + 1
    print(f"\n  interpretation counts:")
    for cls in ("supports", "weak_support", "no_locus_support", "inconclusive"):
        print(f"    {cls}: {interp_counts.get(cls, 0)}")

    # Per-pair aggregation
    print(f"\n  per-pair (across multiple experiments where applicable):")
    by_pair: dict[tuple[str, str], list[dict]] = {}
    for r in rows:
        by_pair.setdefault((r["regulator"], r["target"]), []).append(r)
    for (reg, tgt), prs in by_pair.items():
        n_supp = sum(1 for p in prs if p["interpretation"] == "supports")
        n_weak = sum(1 for p in prs if p["interpretation"] == "weak_support")
        n_no = sum(1 for p in prs if p["interpretation"] == "no_locus_support")
        n_inc = sum(1 for p in prs if p["interpretation"] == "inconclusive")
        print(f"    {reg:>6} -> {tgt:<6}: supports={n_supp} weak={n_weak} "
              f"no_support={n_no} inconclusive={n_inc} (n_experiments={len(prs)})")

    return 0


if __name__ == "__main__":
    sys.exit(main())
