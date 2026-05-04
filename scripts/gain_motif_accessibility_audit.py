#!/usr/bin/env python3
"""gain motif-accessibility-audit - first-pass indirect-evidence audit.

For NKX2-1's 4 robustly-failing canonical pairs (SFTPC, SCGB1A1, ABCA3,
FOXA2): scan the JASPAR NKX2-1 motif (MA1994.2) across hg38 sequence
+/- 50 kb of each TSS, intersect motif occurrences with ENCODE human
lung ATAC + DNase accessible peaks, and classify per-pair indirect
evidence under the 5-class scheme defined in
notes/motif_accessibility_audit_design.md.

Stdlib only. Sibling-imports http_get_bytes from gain_nkx21_audit and
parse_bed_gz from gain_peak_intersection. JASPAR PFM cached to
metadata/cache/ (gitignored).
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# Sibling imports
sys.path.insert(0, str(Path(__file__).parent))
from gain_nkx21_audit import http_get_bytes  # noqa: E402
from gain_peak_intersection import parse_bed_gz  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = REPO_ROOT / "metadata" / "nkx21_motif_accessibility_audit.csv"
JASPAR_CACHE_DIR = REPO_ROOT / "metadata" / "cache"

USER_AGENT = "gain-motif-accessibility/0.1 (+https://github.com/DD-Ching/Gain)"
WINDOW_BP = 50_000

# JASPAR (Elixir Norway, 2024) -- the genereg.net URL redirects here.
JASPAR_BASE = "https://jaspar.elixir.no/api/v1/matrix"
NKX21_MOTIF_ID = "MA1994.2"
MOTIF_RELATIVE_SCORE_THRESHOLD = 0.85

ENCODE_BASE = "https://www.encodeproject.org"
UCSC_API = "https://api.genome.ucsc.edu/getData/sequence"

# 4 NKX2-1 failing pairs (hg38 TSS, Ensembl)
TARGETS: dict[str, dict] = {
    "SFTPC":   {"chrom": "chr8",  "tss": 22156913, "strand": "+",
                "source": "Ensembl ENSG00000168484"},
    "SCGB1A1": {"chrom": "chr11", "tss": 62405103, "strand": "+",
                "source": "Ensembl ENSG00000169035"},
    "ABCA3":   {"chrom": "chr16", "tss":  2340749, "strand": "-",
                "source": "Ensembl ENSG00000167972"},
    "FOXA2":   {"chrom": "chr20", "tss": 22585455, "strand": "-",
                "source": "Ensembl ENSG00000125798"},
}

# 15 ENCODE human lung accessibility experiments (verified 2026-05-04).
EXPERIMENTS: list[dict] = [
    # Fetal DNase-seq (13)
    {"id": "ENCSR141IUS", "assay": "DNase-seq", "stage": "fetal", "label": "fetal lung 76d female"},
    {"id": "ENCSR214XJO", "assay": "DNase-seq", "stage": "fetal", "label": "fetal lung 120d female"},
    {"id": "ENCSR986XLW", "assay": "DNase-seq", "stage": "fetal", "label": "fetal lung 101d"},
    {"id": "ENCSR482HQE", "assay": "DNase-seq", "stage": "fetal", "label": "fetal lung 108d female"},
    {"id": "ENCSR318WOD", "assay": "DNase-seq", "stage": "fetal", "label": "fetal lung 103d male"},
    {"id": "ENCSR504KZE", "assay": "DNase-seq", "stage": "fetal", "label": "fetal lung 67d"},
    {"id": "ENCSR141VGA", "assay": "DNase-seq", "stage": "fetal", "label": "fetal lung 85d female"},
    {"id": "ENCSR847RSJ", "assay": "DNase-seq", "stage": "fetal", "label": "fetal lung 96d female"},
    {"id": "ENCSR076YBB", "assay": "DNase-seq", "stage": "fetal", "label": "fetal lung 108d male"},
    {"id": "ENCSR006IJP", "assay": "DNase-seq", "stage": "fetal", "label": "fetal lung 112d"},
    {"id": "ENCSR587HPR", "assay": "DNase-seq", "stage": "fetal", "label": "fetal lung 82d male"},
    {"id": "ENCSR582IPV", "assay": "DNase-seq", "stage": "fetal", "label": "fetal lung 76-80d male (mixed)"},
    {"id": "ENCSR627NIF", "assay": "DNase-seq", "stage": "fetal", "label": "fetal lung 54-58d male (mixed)"},
    # Adult (2)
    {"id": "ENCSR945JJB", "assay": "DNase-seq", "stage": "adult", "label": "adult lung 47y female"},
    {"id": "ENCSR647AOY", "assay": "ATAC-seq",  "stage": "adult", "label": "adult lung 47y female"},
]

CLASSES = (
    "indirect_accessibility_support_in_fetal_lung_tissue",
    "indirect_accessibility_support_in_adult_lung_tissue_only",
    "motif_in_accessible_chromatin_negative",
    "unresolved_no_lung_accessibility",
    "error",
)

OUT_FIELDS = (
    "regulator", "target", "target_locus", "motif_id",
    "n_motif_hits_in_window",
    "n_lung_peaks_in_window",
    "n_fetal_peaks_in_window", "n_adult_peaks_in_window",
    "n_motif_hits_in_lung_peaks",
    "n_motif_hits_in_fetal_peaks", "n_motif_hits_in_adult_peaks",
    "n_supporting_fetal_experiments", "n_supporting_adult_experiments",
    "best_supporting_locus", "best_supporting_motif_score",
    "final_class", "justification", "evidence_url",
)

COMP = str.maketrans("ACGTacgtN", "TGCAtgcaN")


# ---------- HTTP helpers ----------

def http_get_json(url: str, timeout: float = 20.0) -> dict | None:
    blob = http_get_bytes(url, timeout=timeout)
    if blob is None:
        return None
    try:
        return json.loads(blob.decode("utf-8"))
    except Exception as e:
        print(f"  json parse error from {url}: {e}", file=sys.stderr)
        return None


# ---------- JASPAR PFM ----------

def fetch_jaspar_pfm(motif_id: str) -> dict[str, list[int]]:
    """Fetch and cache the PFM for `motif_id` from JASPAR Elixir.

    Cache path derived from motif_id so this function is reusable across
    motif IDs (NKX2-1, SOX2, etc.).
    """
    cache_path = JASPAR_CACHE_DIR / f"jaspar_{motif_id}.json"
    if cache_path.exists():
        with cache_path.open() as f:
            return json.load(f)
    url = f"{JASPAR_BASE}/{motif_id}/?format=jaspar"
    print(f"  fetching JASPAR PFM {motif_id} from {url}")
    blob = http_get_bytes(url)
    if blob is None:
        raise RuntimeError(f"could not fetch JASPAR motif {motif_id}")
    text = blob.decode("utf-8")
    pfm: dict[str, list[int]] = {b: [] for b in "ACGT"}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith(">"):
            continue
        if line[0] in "ACGT" and (len(line) > 1 and line[1] in (" ", "\t")):
            base = line[0]
            # Tolerate "A  [   1   2 ... ]" or "A  1 2 3 ..."
            payload = line[1:].strip()
            if payload.startswith("["):
                payload = payload[1:]
            if payload.endswith("]"):
                payload = payload[:-1]
            try:
                pfm[base] = [int(x) for x in payload.split()]
            except ValueError:
                pass
    if not all(pfm[b] for b in "ACGT") or len(set(len(pfm[b]) for b in "ACGT")) != 1:
        raise RuntimeError(f"PFM parse failed for {motif_id}: {pfm}")
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with cache_path.open("w") as f:
        json.dump(pfm, f)
    print(f"  cached PFM at {cache_path.relative_to(REPO_ROOT)} (motif length {len(pfm['A'])})")
    return pfm


def run_motif_accessibility_audit(
    regulator: str,
    motif_id: str,
    targets: dict,
    out_path: Path,
    sleep: float = 0.3,
    threshold: float = MOTIF_RELATIVE_SCORE_THRESHOLD,
) -> int:
    """Reusable pipeline. Used by main() with NKX2-1 defaults and by sibling
    audit scripts (SOX2, controls) with their own (motif_id, targets, out_path).
    Returns 0 on success, non-zero on error."""
    print(f"{regulator} motif + accessibility audit ({len(targets)} targets x {len(EXPERIMENTS)} lung experiments)")
    print(f"  motif: JASPAR {motif_id}")
    print(f"  threshold: relative_score >= {threshold}")
    print(f"  window: +/- {WINDOW_BP} bp around TSS")
    print()

    pfm = fetch_jaspar_pfm(motif_id)
    pwm = pfm_to_log_odds(pfm)
    motif_len = len(pwm["A"])

    print(f"\nFetching sequence + scanning motif per target...")
    target_data: dict[str, dict] = {}
    for target_name, target in targets.items():
        start = target["tss"] - WINDOW_BP
        end = target["tss"] + WINDOW_BP
        seq = fetch_hg38_window(target["chrom"], start, end)
        if seq is None:
            print(f"  {target_name}: sequence fetch FAILED")
            target_data[target_name] = {"start": start, "end": end, "seq": None, "hits": None}
            time.sleep(sleep)
            continue
        hits = scan_pwm(pwm, seq, threshold_relative=threshold)
        target_data[target_name] = {"start": start, "end": end, "seq": seq, "hits": hits}
        print(f"  {target_name}: seq {len(seq)} bp, {len(hits)} motif hits at relative_score >= {threshold}")
        time.sleep(sleep)

    target_peaks: dict[str, list[dict]] = {tn: [] for tn in targets}
    print(f"\nFetching ENCODE lung accessibility peak files...")
    for i, e in enumerate(EXPERIMENTS, 1):
        print(f"  [{i:>2}/{len(EXPERIMENTS)}] {e['id']} ({e['assay']:<9} {e['stage']:<5} | {e['label']})", end=" ")
        url, label = best_lung_peak_file_url(e["id"])
        if url is None:
            print(f"NO PEAK FILE ({label})")
            time.sleep(sleep)
            continue
        time.sleep(sleep)
        blob = http_get_bytes(url)
        if blob is None:
            print(f"DOWNLOAD FAILED")
            time.sleep(sleep)
            continue
        peaks = parse_bed_gz(blob)
        for target_name, target in targets.items():
            for c, s, ed in peaks:
                if c != target["chrom"]:
                    continue
                w_start = target["tss"] - WINDOW_BP
                w_end = target["tss"] + WINDOW_BP
                if ed >= w_start and s <= w_end:
                    target_peaks[target_name].append({
                        "exp_id": e["id"], "assay": e["assay"], "stage": e["stage"],
                        "peak_start": s, "peak_end": ed,
                    })
        print(f"-> {len(peaks):>5} peaks parsed")
        time.sleep(sleep)

    out_rows: list[dict] = []
    print(f"\nIntersecting motif hits with lung accessibility peaks...")
    for target_name, target in targets.items():
        td = target_data[target_name]
        if td["hits"] is None:
            cls = "error"
            row = {f: 0 for f in OUT_FIELDS}
            row["regulator"] = regulator
            row["target"] = target_name
            row["target_locus"] = f"{target['chrom']}:{target['tss']} ({target['strand']}) — {target.get('source', '')}"
            row["motif_id"] = motif_id
            row["best_supporting_locus"] = "n/a"
            row["best_supporting_motif_score"] = "n/a"
            row["final_class"] = cls
            row["justification"] = "Sequence fetch failed; cannot classify."
            row["evidence_url"] = "n/a"
            out_rows.append(row)
            continue

        peaks = target_peaks[target_name]
        n_lung_peaks = len(peaks)
        n_fetal_peaks = sum(1 for p in peaks if p["stage"] == "fetal")
        n_adult_peaks = sum(1 for p in peaks if p["stage"] == "adult")

        hits = td["hits"]
        n_motif_hits = len(hits)

        n_motif_in_lung = 0
        n_motif_in_fetal = 0
        n_motif_in_adult = 0
        fetal_supporting_exps: set[str] = set()
        adult_supporting_exps: set[str] = set()
        best_score = -1.0
        best_locus_pos = None

        for hit in hits:
            hit_genomic_start = td["start"] + hit["position_in_window"]
            hit_genomic_end = hit_genomic_start + motif_len - 1
            in_any_lung = False
            for p in peaks:
                if hit_genomic_end >= p["peak_start"] and hit_genomic_start <= p["peak_end"]:
                    in_any_lung = True
                    if p["stage"] == "fetal":
                        n_motif_in_fetal += 1
                        fetal_supporting_exps.add(p["exp_id"])
                    else:
                        n_motif_in_adult += 1
                        adult_supporting_exps.add(p["exp_id"])
                    if hit["relative_score"] > best_score:
                        best_score = hit["relative_score"]
                        best_locus_pos = hit_genomic_start
            if in_any_lung:
                n_motif_in_lung += 1

        cls = classify(n_motif_in_fetal, n_motif_in_adult, n_lung_peaks, n_motif_hits)
        out_rows.append({
            "regulator": regulator,
            "target": target_name,
            "target_locus": f"{target['chrom']}:{target['tss']} ({target['strand']}) — {target.get('source', '')}",
            "motif_id": motif_id,
            "n_motif_hits_in_window": n_motif_hits,
            "n_lung_peaks_in_window": n_lung_peaks,
            "n_fetal_peaks_in_window": n_fetal_peaks,
            "n_adult_peaks_in_window": n_adult_peaks,
            "n_motif_hits_in_lung_peaks": n_motif_in_lung,
            "n_motif_hits_in_fetal_peaks": n_motif_in_fetal,
            "n_motif_hits_in_adult_peaks": n_motif_in_adult,
            "n_supporting_fetal_experiments": len(fetal_supporting_exps),
            "n_supporting_adult_experiments": len(adult_supporting_exps),
            "best_supporting_locus": f"{target['chrom']}:{best_locus_pos}" if best_locus_pos else "n/a",
            "best_supporting_motif_score": f"{best_score:.3f}" if best_score >= 0 else "n/a",
            "final_class": cls,
            "justification": justify(cls, target_name, n_motif_hits, n_lung_peaks,
                                      n_fetal_peaks, n_adult_peaks,
                                      n_motif_in_fetal, n_motif_in_adult,
                                      len(fetal_supporting_exps), len(adult_supporting_exps)),
            "evidence_url": "https://www.encodeproject.org/search/?type=Experiment&assay_title=DNase-seq&biosample_ontology.term_name=lung&replicates.library.biosample.donor.organism.scientific_name=Homo+sapiens",
        })

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=OUT_FIELDS)
        w.writeheader()
        for row in out_rows:
            w.writerow(row)

    try:
        out_display = str(out_path.relative_to(REPO_ROOT))
    except ValueError:
        out_display = str(out_path)
    print(f"\nwrote {out_display}")
    print(f"  generated_at: {datetime.now(timezone.utc).isoformat(timespec='seconds')}")
    print(f"\n  Per-pair results:")
    for row in out_rows:
        print(f"    {regulator} -> {row['target']:<8} "
              f"motif={row['n_motif_hits_in_window']:>4} | "
              f"lung_peaks={row['n_lung_peaks_in_window']:>4} (fetal={row['n_fetal_peaks_in_window']}, adult={row['n_adult_peaks_in_window']}) | "
              f"motif_in_fetal={row['n_motif_hits_in_fetal_peaks']:>3} ({row['n_supporting_fetal_experiments']} expts) "
              f"-> {row['final_class']}")

    counts_by_class = {c: 0 for c in CLASSES}
    for r in out_rows:
        counts_by_class[r["final_class"]] = counts_by_class.get(r["final_class"], 0) + 1
    print(f"\n  Class counts:")
    for c in CLASSES:
        if counts_by_class[c] > 0:
            print(f"    {c}: {counts_by_class[c]}")

    n_positive = (counts_by_class.get("indirect_accessibility_support_in_fetal_lung_tissue", 0)
                  + counts_by_class.get("indirect_accessibility_support_in_adult_lung_tissue_only", 0))
    print(f"\n  Positive: {n_positive} of {len(targets)} pairs cross indirect-evidence threshold")
    return 0


def pfm_to_log_odds(pfm: dict[str, list[int]],
                    pseudocount: float = 0.5,
                    background: float = 0.25) -> dict[str, list[float]]:
    n_pos = len(pfm["A"])
    pwm: dict[str, list[float]] = {b: [] for b in "ACGT"}
    for pos in range(n_pos):
        col_total = sum(pfm[b][pos] for b in "ACGT") + 4 * pseudocount
        for base in "ACGT":
            freq = (pfm[base][pos] + pseudocount) / col_total
            pwm[base].append(math.log2(freq / background))
    return pwm


# ---------- Sequence fetch ----------

def fetch_hg38_window(chrom: str, start: int, end: int) -> str | None:
    url = f"{UCSC_API}?genome=hg38;chrom={chrom};start={start};end={end}"
    data = http_get_json(url, timeout=30.0)
    if not data:
        return None
    seq = data.get("dna")
    if not seq or len(seq) != end - start:
        print(f"  sequence fetch returned unexpected length: "
              f"got {len(seq) if seq else 0}, wanted {end - start}", file=sys.stderr)
        return None
    return seq.upper()


# ---------- PWM scanning ----------

def reverse_complement(seq: str) -> str:
    return seq.translate(COMP)[::-1]


def scan_pwm(pwm: dict[str, list[float]], sequence: str,
             threshold_relative: float = MOTIF_RELATIVE_SCORE_THRESHOLD
             ) -> list[dict]:
    motif_len = len(pwm["A"])
    max_score = sum(max(pwm[b][p] for b in "ACGT") for p in range(motif_len))
    min_score = sum(min(pwm[b][p] for b in "ACGT") for p in range(motif_len))
    span = max_score - min_score
    threshold_score = min_score + threshold_relative * span

    hits: list[dict] = []
    seq_len = len(sequence)
    for i in range(seq_len - motif_len + 1):
        window_fwd = sequence[i:i + motif_len]
        if "N" in window_fwd:
            continue
        # Forward strand
        s_fwd = 0.0
        for p, b in enumerate(window_fwd):
            s_fwd += pwm[b][p]
        if s_fwd >= threshold_score:
            hits.append({"position_in_window": i, "strand": "+",
                         "score": s_fwd,
                         "relative_score": (s_fwd - min_score) / span})
        # Reverse strand: scan the reverse complement of the same window
        window_rev = reverse_complement(window_fwd)
        s_rev = 0.0
        for p, b in enumerate(window_rev):
            s_rev += pwm[b][p]
        if s_rev >= threshold_score:
            hits.append({"position_in_window": i, "strand": "-",
                         "score": s_rev,
                         "relative_score": (s_rev - min_score) / span})
    return hits


# ---------- ENCODE peak fetching ----------

def best_lung_peak_file_url(experiment_id: str) -> tuple[str | None, str]:
    """Adapted from gain_peak_intersection for ATAC/DNase output types."""
    data = http_get_json(f"{ENCODE_BASE}/experiments/{experiment_id}/?format=json")
    if not data:
        return None, "no metadata"
    files = [f for f in data.get("files", [])
             if f.get("file_format") == "bed"
             and f.get("assembly") == "GRCh38"
             and f.get("status") in ("released", None)]
    if not files:
        return None, "no GRCh38 BED files"

    def rank(f: dict) -> int:
        ot = (f.get("output_type") or "").lower()
        ft = (f.get("file_type") or "").lower()
        if ft == "bed narrowpeak" and ot == "peaks":
            return 0
        if "idr thresholded peaks" in ot and "narrowpeak" in ft:
            return 1
        if ot == "peaks" and "narrowpeak" in ft:
            return 2
        if ot == "peaks":
            return 3
        return 4

    files.sort(key=rank)
    chosen = files[0]
    href = chosen.get("href", "")
    full = ENCODE_BASE + href if href.startswith("/") else href
    label = f"{chosen.get('@id', '?')} ({chosen.get('output_type', '?')})"
    return full, label


# ---------- Per-pair classification ----------

def classify(n_motif_in_fetal: int, n_motif_in_adult: int,
             n_lung_peaks: int, n_motif_hits: int) -> str:
    if n_motif_in_fetal > 0:
        return "indirect_accessibility_support_in_fetal_lung_tissue"
    if n_motif_in_adult > 0:
        return "indirect_accessibility_support_in_adult_lung_tissue_only"
    if n_lung_peaks > 0:
        # peaks exist but no motif within them
        return "motif_in_accessible_chromatin_negative"
    return "unresolved_no_lung_accessibility"


def justify(cls: str, target: str, n_motif_hits: int,
            n_lung_peaks: int, n_fetal_peaks: int, n_adult_peaks: int,
            n_motif_in_fetal: int, n_motif_in_adult: int,
            n_fetal_supp: int, n_adult_supp: int) -> str:
    suffix = (" Indirect evidence: motif + accessibility plausibility "
              "is necessary but not sufficient for binding; "
              "JASPAR motifs are degenerate (false positives inherent); "
              "bulk lung accessibility averages over cell types.")
    if cls == "indirect_accessibility_support_in_fetal_lung_tissue":
        return (f"NKX2-1 motif (MA1994.2) at relative_score >= "
                f"{MOTIF_RELATIVE_SCORE_THRESHOLD} occurs within an "
                f"accessible peak in {n_fetal_supp} fetal lung experiment(s) "
                f"({n_motif_in_fetal} motif-in-peak overlaps). "
                f"Adult lung overlaps: {n_motif_in_adult}. "
                f"Strongest indirect tier: primary lung tissue substrate in "
                f"the developmental window." + suffix)
    if cls == "indirect_accessibility_support_in_adult_lung_tissue_only":
        return (f"NKX2-1 motif occurs within accessible peaks in "
                f"{n_adult_supp} adult lung experiment(s) "
                f"({n_motif_in_adult} overlaps); zero fetal-lung overlaps. "
                f"Indirect support but in adult substrate; developmental "
                f"relevance uncertain." + suffix)
    if cls == "motif_in_accessible_chromatin_negative":
        return (f"Lung accessibility data exists in window "
                f"({n_lung_peaks} peaks across 15 experiments) and "
                f"{n_motif_hits} motif occurrences exist in window, but "
                f"none of the motif positions fall within an accessible "
                f"peak. Substantive negative finding: the regulatory "
                f"landscape is in lung tissue, but NKX2-1 motifs are not "
                f"where the accessibility is.")
    if cls == "unresolved_no_lung_accessibility":
        return (f"Zero lung ATAC/DNase peaks within +/- 50 kb of {target} "
                f"TSS across all 15 checked experiments. Cannot conclude; "
                f"primary lung accessibility data does not cover this "
                f"window.")
    return f"Error during audit of {target}."


# ---------- Main ----------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="gain-motif-accessibility-audit",
        description="NKX2-1 motif + lung accessibility indirect-evidence audit.",
    )
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--sleep", type=float, default=0.3,
                        help="seconds between HTTP requests (default 0.3)")
    parser.add_argument("--threshold", type=float,
                        default=MOTIF_RELATIVE_SCORE_THRESHOLD,
                        help="motif relative_score threshold (default 0.85)")
    args = parser.parse_args(argv)
    return run_motif_accessibility_audit(
        regulator="NKX2-1",
        motif_id=NKX21_MOTIF_ID,
        targets=TARGETS,
        out_path=args.out,
        sleep=args.sleep,
        threshold=args.threshold,
    )


if __name__ == "__main__":
    sys.exit(main())
