#!/usr/bin/env python3
"""gain nkx21-audit - locus-level audit of NKX2-1 against 7 canonical targets,
with strict cancer-vs-developmental separation per notes/nkx21_audit_design.md.

For each of the 21 NKX2-1 ChIP-Atlas hg38 experiments, downloads the bed10
peak file (q < 10^-10) and checks for peaks within +/- 50 kb of each
target gene's hg38 Ensembl TSS, classifying biosamples as cancer_lung_line
vs noncancer_lung vs unclear.

Output: metadata/nkx21_peak_audit.csv with per-(NKX2-1, target) classification
under the strict 5-class hierarchy.

Stdlib only (urllib.request, csv, argparse, pathlib).
"""
from __future__ import annotations

import argparse
import csv
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = REPO_ROOT / "metadata" / "nkx21_peak_audit.csv"

USER_AGENT = "gain-nkx21-audit/0.1 (+https://github.com/DD-Ching/Gain)"

# Window definitions
WINDOW_BP = 50_000
STRONG_BP = 5_000

# ChIP-Atlas peak BED URL pattern (verified 2026-05-03 with HEAD probes)
# threshold 10 = q < 10^-10 (high-confidence)
def chipatlas_bed_url(srx: str, threshold: int = 10) -> str:
    return f"https://chip-atlas.dbcls.jp/data/hg38/eachData/bed{threshold:02d}/{srx}.{threshold:02d}.bed"

# 21 NKX2-1 hg38 experiments classified by biosample.
# Extracted from metadata/cache/chipatlas_experimentList.tab on 2026-05-03.
# All 21 are cancer_lung_line per the design's pre-implementation probe.
EXPERIMENTS: list[dict] = [
    # SRX12008* series (small cell lung cancer + lung adenocarcinoma cell lines)
    {"srx": "SRX12008006", "biosample_class": "cancer_lung_line", "label": "small cell lung cancer line"},
    {"srx": "SRX12008007", "biosample_class": "cancer_lung_line", "label": "small cell lung cancer line"},
    {"srx": "SRX12008008", "biosample_class": "cancer_lung_line", "label": "small cell lung cancer line"},
    {"srx": "SRX12008009", "biosample_class": "cancer_lung_line", "label": "small cell lung cancer line"},
    {"srx": "SRX12008010", "biosample_class": "cancer_lung_line", "label": "small cell lung cancer line"},
    {"srx": "SRX12008011", "biosample_class": "cancer_lung_line", "label": "small cell lung cancer line"},
    {"srx": "SRX12008014", "biosample_class": "cancer_lung_line", "label": "lung adenocarcinoma line"},
    {"srx": "SRX12008015", "biosample_class": "cancer_lung_line", "label": "lung adenocarcinoma line"},
    {"srx": "SRX12008016", "biosample_class": "cancer_lung_line", "label": "small cell lung cancer line"},
    {"srx": "SRX12008017", "biosample_class": "cancer_lung_line", "label": "small cell lung cancer line"},
    {"srx": "SRX12008018", "biosample_class": "cancer_lung_line", "label": "small cell lung cancer line"},
    {"srx": "SRX12008019", "biosample_class": "cancer_lung_line", "label": "small cell lung cancer line"},
    {"srx": "SRX12008020", "biosample_class": "cancer_lung_line", "label": "small cell lung cancer line"},
    # SRX174* series (named NSCLC adenocarcinoma cell lines)
    {"srx": "SRX174813",   "biosample_class": "cancer_lung_line", "label": "NCI-H3122 (NSCLC adenocarcinoma)"},
    {"srx": "SRX174815",   "biosample_class": "cancer_lung_line", "label": "NCI-H1819 (NSCLC adenocarcinoma)"},
    {"srx": "SRX174817",   "biosample_class": "cancer_lung_line", "label": "NCI-H2087 (NSCLC adenocarcinoma)"},
    {"srx": "SRX174819",   "biosample_class": "cancer_lung_line", "label": "NCI-H3122 (NSCLC adenocarcinoma) replicate"},
    # SRX2164* (A549 with lentivirus-overexpressed NKX2-1)
    {"srx": "SRX2164786",  "biosample_class": "cancer_lung_line", "label": "A549 + lentiviral NKX2-1 overexpression"},
    {"srx": "SRX2164788",  "biosample_class": "cancer_lung_line", "label": "A549 + lentiviral NKX2-1 overexpression"},
    # SRX366* (NCI-H441, antibody = TTF-1)
    {"srx": "SRX366169",   "biosample_class": "cancer_lung_line", "label": "NCI-H441 (lung adenocarcinoma)"},
    {"srx": "SRX366170",   "biosample_class": "cancer_lung_line", "label": "NCI-H441 (lung adenocarcinoma) +1.5h"},
]

# 7 target hg38 TSS coordinates (Ensembl REST, verified 2026-05-03).
# TSS = `start` for + strand, `end` for - strand.
TARGETS: dict[str, dict] = {
    "SFTPC":   {"chrom": "chr8",  "tss": 22156913, "strand": "+",
                "source": "Ensembl ENSG00000168484"},
    "SFTPB":   {"chrom": "chr2",  "tss": 85668741, "strand": "-",
                "source": "Ensembl ENSG00000168878"},
    "SCGB1A1": {"chrom": "chr11", "tss": 62405103, "strand": "+",
                "source": "Ensembl ENSG00000169035"},
    "ABCA3":   {"chrom": "chr16", "tss":  2340749, "strand": "-",
                "source": "Ensembl ENSG00000167972"},
    "SOX2":    {"chrom": "chr3",  "tss": 181711925, "strand": "+",
                "source": "Ensembl ENSG00000181449"},
    "SOX9":    {"chrom": "chr17", "tss": 72121020, "strand": "+",
                "source": "Ensembl ENSG00000125398"},
    "FOXA2":   {"chrom": "chr20", "tss": 22585455, "strand": "-",
                "source": "Ensembl ENSG00000125798"},
}

OUT_FIELDS = (
    "regulator", "target", "target_locus",
    "n_experiments_total", "n_cancer_lung", "n_noncancer_lung", "n_unclear",
    "n_strong_support", "n_strong_support_noncancer", "n_strong_support_cancer_only",
    "n_nearby_support", "n_no_local_support",
    "n_download_failed",
    "biosample_context_summary", "final_class", "justification",
    "evidence_url",
)

CLASSES = (
    "peak_validated_in_lung_context",
    "peak_validated_in_cancer_lung_context_only",
    "lung_context_source_only",
    "no_locus_support",
    "unresolved_due_to_context",
)


def http_get_bytes(url: str, timeout: float = 60.0) -> bytes | None:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except Exception as e:
        print(f"  download error {url}: {e}", file=sys.stderr)
        return None


def parse_bed(blob: bytes) -> list[tuple[str, int, int]]:
    out: list[tuple[str, int, int]] = []
    for line in blob.decode("utf-8", errors="replace").splitlines():
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


def peak_distance_to_tss(peaks: list[tuple[str, int, int]], target: dict) -> int:
    """Return min absolute distance from any peak to TSS, or -1 if no peaks on chrom."""
    chrom, tss = target["chrom"], target["tss"]
    on_chrom = [(s, e) for c, s, e in peaks if c == chrom]
    if not on_chrom:
        return -1
    nearest = None
    for s, e in on_chrom:
        if s <= tss <= e:
            return 0
        d = min(abs(s - tss), abs(e - tss))
        if nearest is None or d < nearest:
            nearest = d
    return nearest if nearest is not None else -1


def classify_per_experiment(distance: int) -> str:
    """Return 'strong' | 'nearby' | 'no_local' based on distance to TSS."""
    if distance < 0:
        return "no_local"
    if distance <= STRONG_BP:
        return "strong"
    if distance <= WINDOW_BP:
        return "nearby"
    return "no_local"


def aggregate_class(per_exp_results: list[dict]) -> tuple[str, dict]:
    """Aggregate per-(experiment, target) results to a final class for the pair.

    per_exp_results: list of {biosample_class, classification (strong/nearby/no_local/download_failed)}.
    """
    counts = {
        "strong_noncancer": 0, "strong_cancer": 0, "strong_unclear": 0,
        "nearby": 0, "no_local": 0, "download_failed": 0,
    }
    for r in per_exp_results:
        cls = r["classification"]
        bs = r["biosample_class"]
        if cls == "download_failed":
            counts["download_failed"] += 1
            continue
        if cls == "strong":
            if bs == "noncancer_lung":
                counts["strong_noncancer"] += 1
            elif bs == "cancer_lung_line":
                counts["strong_cancer"] += 1
            else:
                counts["strong_unclear"] += 1
        elif cls == "nearby":
            counts["nearby"] += 1
        else:  # no_local
            counts["no_local"] += 1

    n_strong = counts["strong_noncancer"] + counts["strong_cancer"] + counts["strong_unclear"]
    n_attempted = len(per_exp_results) - counts["download_failed"]

    if n_attempted == 0:
        return "unresolved_due_to_context", counts

    if counts["strong_noncancer"] > 0:
        return "peak_validated_in_lung_context", counts
    if counts["strong_cancer"] > 0:
        return "peak_validated_in_cancer_lung_context_only", counts
    if counts["nearby"] > 0:
        return "lung_context_source_only", counts
    if counts["no_local"] > 0:
        return "no_locus_support", counts
    return "unresolved_due_to_context", counts


def biosample_context_summary(experiments: list[dict]) -> str:
    by_class: dict[str, int] = {}
    for e in experiments:
        by_class[e["biosample_class"]] = by_class.get(e["biosample_class"], 0) + 1
    parts = [f"{k}={v}" for k, v in sorted(by_class.items())]
    return "; ".join(parts)


def justification(cls: str, regulator: str, target: str, counts: dict, n_total: int) -> str:
    if cls == "peak_validated_in_lung_context":
        return (f"{counts['strong_noncancer']} non-cancer lung experiment(s) "
                f"show {regulator} peak within 5 kb of {target} TSS. "
                f"Locus-level support in primary/developmental lung context.")
    if cls == "peak_validated_in_cancer_lung_context_only":
        return (f"{counts['strong_cancer']} of {n_total} experiments (all "
                f"cancer cell lines) show {regulator} peak within 5 kb of "
                f"{target} TSS; zero non-cancer experiments exist for "
                f"{regulator} in ChIP-Atlas hg38. Cancer-line locus support "
                f"is real but DOES NOT establish developmental binding.")
    if cls == "lung_context_source_only":
        return (f"No strong locus support; {counts['nearby']} experiment(s) "
                f"show peaks within 50 kb but >5 kb from TSS. Distal regulatory "
                f"binding plausible; promoter-proximal binding not detected.")
    if cls == "no_locus_support":
        return (f"All {n_total - counts['download_failed']} checked experiments "
                f"have no {regulator} peaks within +/- 50 kb of {target} TSS. "
                f"This is a substantive negative finding at the locus level, "
                f"with the caveats that the available substrate is entirely "
                f"cancer cell lines and the antibody / threshold could shift "
                f"the result.")
    return (f"Cannot classify {regulator}->{target}: insufficient peak data "
            f"({counts['download_failed']} of {n_total} downloads failed).")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="gain-nkx21-audit",
        description="NKX2-1 locus-level audit (ChIP-Atlas hg38 bed10 peaks).",
    )
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--sleep", type=float, default=0.3,
                        help="seconds between BED downloads (default 0.3)")
    args = parser.parse_args(argv)

    print(f"NKX2-1 locus audit: {len(EXPERIMENTS)} experiments x {len(TARGETS)} targets")
    print(f"  {sum(1 for e in EXPERIMENTS if e['biosample_class']=='cancer_lung_line')} cancer_lung_line")
    print(f"  {sum(1 for e in EXPERIMENTS if e['biosample_class']=='noncancer_lung')} noncancer_lung")
    print(f"  {sum(1 for e in EXPERIMENTS if e['biosample_class']=='unclear')} unclear")

    # Download peaks per experiment
    exp_peaks: dict[str, list[tuple[str, int, int]] | None] = {}
    print(f"\nDownloading bed10 peak files...")
    for i, e in enumerate(EXPERIMENTS, 1):
        srx = e["srx"]
        url = chipatlas_bed_url(srx, threshold=10)
        print(f"  [{i:>2}/{len(EXPERIMENTS)}] {srx} ({e['label']})", end=" ")
        blob = http_get_bytes(url)
        if blob is None:
            exp_peaks[srx] = None
            print("FAILED")
        else:
            peaks = parse_bed(blob)
            exp_peaks[srx] = peaks
            print(f"-> {len(peaks):>6} peaks ({len(blob):,} bytes)")
        if i < len(EXPERIMENTS):
            time.sleep(args.sleep)

    # Per-target audit
    out_rows: list[dict] = []
    for target_name, target in TARGETS.items():
        per_exp: list[dict] = []
        for e in EXPERIMENTS:
            srx = e["srx"]
            peaks = exp_peaks.get(srx)
            if peaks is None:
                per_exp.append({"biosample_class": e["biosample_class"],
                                "classification": "download_failed"})
                continue
            d = peak_distance_to_tss(peaks, target)
            per_exp.append({"biosample_class": e["biosample_class"],
                            "classification": classify_per_experiment(d)})

        cls, counts = aggregate_class(per_exp)

        n_cancer = sum(1 for e in EXPERIMENTS if e["biosample_class"] == "cancer_lung_line")
        n_noncancer = sum(1 for e in EXPERIMENTS if e["biosample_class"] == "noncancer_lung")
        n_unclear = sum(1 for e in EXPERIMENTS if e["biosample_class"] == "unclear")

        n_strong = counts["strong_noncancer"] + counts["strong_cancer"] + counts["strong_unclear"]

        out_rows.append({
            "regulator": "NKX2-1",
            "target": target_name,
            "target_locus": f"{target['chrom']}:{target['tss']} ({target['strand']} strand) — {target['source']}",
            "n_experiments_total": len(EXPERIMENTS),
            "n_cancer_lung": n_cancer,
            "n_noncancer_lung": n_noncancer,
            "n_unclear": n_unclear,
            "n_strong_support": n_strong,
            "n_strong_support_noncancer": counts["strong_noncancer"],
            "n_strong_support_cancer_only": counts["strong_cancer"],
            "n_nearby_support": counts["nearby"],
            "n_no_local_support": counts["no_local"],
            "n_download_failed": counts["download_failed"],
            "biosample_context_summary": biosample_context_summary(EXPERIMENTS),
            "final_class": cls,
            "justification": justification(cls, "NKX2-1", target_name, counts, len(EXPERIMENTS)),
            "evidence_url": f"https://chip-atlas.dbcls.jp/?factor=NKX2-1&genome=hg38",
        })

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=OUT_FIELDS)
        w.writeheader()
        for row in out_rows:
            w.writerow(row)

    print(f"\nwrote {args.out.relative_to(REPO_ROOT)}")
    print(f"  generated_at: {datetime.now(timezone.utc).isoformat(timespec='seconds')}")
    print(f"\n  Per-pair results:")
    for row in out_rows:
        print(f"    NKX2-1 -> {row['target']:<8} "
              f"strong={row['n_strong_support']:>2} "
              f"nearby={row['n_nearby_support']:>2} "
              f"no_local={row['n_no_local_support']:>2} "
              f"-> {row['final_class']}")

    counts_by_class: dict[str, int] = {c: 0 for c in CLASSES}
    for r in out_rows:
        counts_by_class[r["final_class"]] = counts_by_class.get(r["final_class"], 0) + 1
    print(f"\n  Class counts:")
    for c in CLASSES:
        print(f"    {c}: {counts_by_class[c]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
