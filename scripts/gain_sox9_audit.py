#!/usr/bin/env python3
"""gain sox9-audit - first-pass locus audit for SOX9 against 7 lung-focused
distal/alveolar targets, per notes/sox9_audit_design.md.

SOX9's substrate is all non-lung (27 hg38 ChIP-Atlas experiments: 20 cancer
cell lines from prostate / breast / colon / pancreas / lymphoma + 7
ESC-derived retinal / pancreatic). All lung-tier classes are unreachable.
This audit asks whether non-lung SOX9 ChIP places peaks at the canonical
lung-developmental target TSSs.

Reuses helpers from gain_nkx21_audit.py via sibling import.

Stdlib only.
"""
from __future__ import annotations

import argparse
import csv
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Sibling imports
sys.path.insert(0, str(Path(__file__).parent))
from gain_nkx21_audit import (  # noqa: E402
    chipatlas_bed_url,
    http_get_bytes,
    parse_bed,
    peak_distance_to_tss,
    classify_per_experiment,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = REPO_ROOT / "metadata" / "sox9_initial_audit.csv"

PROXIMAL_BP = 5_000  # via classify_per_experiment from NKX2-1 module
WINDOW_BP = 50_000

CLASSES = (
    "peak_validated_in_lung_context",                       # unreachable
    "peak_validated_in_cancer_lung_context_only",           # unreachable
    "peak_validated_in_lung_reprogramming_context_only",    # unreachable
    "peak_validated_in_non_lung_context_only",              # NEW for SOX9
    "lung_context_source_only",                             # unreachable
    "non_lung_context_source_only",                         # NEW for SOX9
    "distal_candidate_support_only",                        # not populated by v0 (no distal-band probe)
    "no_locus_support",
    "unresolved_due_to_context_mismatch",
)

# 27 SOX9 hg38 ChIP-Atlas experiments classified by tissue context.
# Extracted from metadata/cache/chipatlas_experimentList.tab on 2026-05-04.
# All 27 are non-lung; biosample_class splits into cancer (20) vs ESC-derived (7).
SOX9_EXPERIMENTS: list[dict] = [
    # PANC-1 pancreas cancer (2)
    {"srx": "SRX10175282", "biosample_class": "non_lung_cancer", "label": "PANC-1 pancreas cancer rep1"},
    {"srx": "SRX10175283", "biosample_class": "non_lung_cancer", "label": "PANC-1 pancreas cancer rep2"},
    # HT-29 colon cancer (3)
    {"srx": "SRX11220467", "biosample_class": "non_lung_cancer", "label": "HT-29 colon cancer rep1"},
    {"srx": "SRX11220468", "biosample_class": "non_lung_cancer", "label": "HT-29 colon cancer rep2"},
    {"srx": "SRX768290",   "biosample_class": "non_lung_cancer", "label": "HT-29 colon cancer (older)"},
    # KARPAS-422 lymphoma (1)
    {"srx": "SRX11416753", "biosample_class": "non_lung_cancer", "label": "KARPAS-422 B-cell lymphoma"},
    # LNCAP prostate cancer (8)
    {"srx": "SRX11856133", "biosample_class": "non_lung_cancer", "label": "LNCAP prostate"},
    {"srx": "SRX11856134", "biosample_class": "non_lung_cancer", "label": "LNCAP prostate"},
    {"srx": "SRX11856137", "biosample_class": "non_lung_cancer", "label": "LNCAP prostate"},
    {"srx": "SRX11856138", "biosample_class": "non_lung_cancer", "label": "LNCAP prostate"},
    {"srx": "SRX11856139", "biosample_class": "non_lung_cancer", "label": "LNCAP prostate"},
    {"srx": "SRX11856140", "biosample_class": "non_lung_cancer", "label": "LNCAP prostate"},
    {"srx": "SRX11856141", "biosample_class": "non_lung_cancer", "label": "LNCAP prostate"},
    {"srx": "SRX11856142", "biosample_class": "non_lung_cancer", "label": "LNCAP prostate"},
    # MCF-7 breast cancer (4)
    {"srx": "SRX13867212", "biosample_class": "non_lung_cancer", "label": "MCF-7 breast cancer"},
    {"srx": "SRX13867213", "biosample_class": "non_lung_cancer", "label": "MCF-7 breast cancer"},
    {"srx": "SRX13867216", "biosample_class": "non_lung_cancer", "label": "MCF-7 breast cancer"},
    {"srx": "SRX13867217", "biosample_class": "non_lung_cancer", "label": "MCF-7 breast cancer"},
    # VCaP prostate cancer (1)
    {"srx": "SRX1510444",  "biosample_class": "non_lung_cancer", "label": "VCaP prostate cancer"},
    # LoVo colon cancer (1)
    {"srx": "SRX359919",   "biosample_class": "non_lung_cancer", "label": "LoVo colon cancer"},
    # hESC-derived retinal cells (6)
    {"srx": "SRX4065343",  "biosample_class": "esc_derived", "label": "hESC-derived retinal cells"},
    {"srx": "SRX4065344",  "biosample_class": "esc_derived", "label": "hESC-derived retinal cells"},
    {"srx": "SRX4065345",  "biosample_class": "esc_derived", "label": "hESC-derived retinal cells"},
    {"srx": "SRX4065346",  "biosample_class": "esc_derived", "label": "hESC-derived retinal cells"},
    {"srx": "SRX4065347",  "biosample_class": "esc_derived", "label": "hESC-derived retinal cells"},
    {"srx": "SRX4065348",  "biosample_class": "esc_derived", "label": "hESC-derived retinal cells"},
    # hESC-derived pancreatic cells (1)
    {"srx": "SRX718108",   "biosample_class": "esc_derived", "label": "hESC-derived pancreatic cells"},
]

# 7 hg38 TSS coordinates from Ensembl REST (verified 2026-05-04).
SOX9_TARGETS: dict[str, dict] = {
    "SFTPC":  {"chrom": "chr8",  "tss": 22156913, "strand": "+",
               "source": "Ensembl ENSG00000168484"},
    "SFTPB":  {"chrom": "chr2",  "tss": 85668741, "strand": "-",
               "source": "Ensembl ENSG00000168878"},
    "ID2":    {"chrom": "chr2",  "tss":  8678845, "strand": "+",
               "source": "Ensembl ENSG00000115738"},
    "HOPX":   {"chrom": "chr4",  "tss": 56681877, "strand": "-",
               "source": "Ensembl ENSG00000171476"},
    "AGER":   {"chrom": "chr6",  "tss": 32184344, "strand": "-",
               "source": "Ensembl ENSG00000204305"},
    "NKX2-1": {"chrom": "chr14", "tss": 36521149, "strand": "-",
               "source": "Ensembl ENSG00000136352"},
    "SOX2":   {"chrom": "chr3",  "tss": 181711925, "strand": "+",
               "source": "Ensembl ENSG00000181449"},
}

OUT_FIELDS = (
    "regulator", "target", "target_locus",
    "n_experiments_total",
    "n_non_lung_cancer", "n_esc_derived",
    "n_proximal_cancer", "n_proximal_esc",
    "n_nearby_cancer", "n_nearby_esc",
    "n_no_local_total",
    "n_download_failed",
    "final_class",
    "justification",
    "evidence_url",
)


def aggregate(per_exp_results: list[dict]) -> dict:
    counts = {
        "proximal_cancer": 0, "proximal_esc": 0,
        "nearby_cancer": 0, "nearby_esc": 0,
        "no_local": 0, "download_failed": 0,
    }
    for r in per_exp_results:
        cls = r["classification"]
        bs = r["biosample_class"]
        if cls == "download_failed":
            counts["download_failed"] += 1
            continue
        ctx = "cancer" if bs == "non_lung_cancer" else "esc"
        if cls == "strong":
            counts[f"proximal_{ctx}"] += 1
        elif cls == "nearby":
            counts[f"nearby_{ctx}"] += 1
        else:
            counts["no_local"] += 1
    return counts


def classify(counts: dict, n_attempted: int) -> str:
    if n_attempted == 0:
        return "unresolved_due_to_context_mismatch"
    if counts["proximal_cancer"] + counts["proximal_esc"] > 0:
        return "peak_validated_in_non_lung_context_only"
    if counts["nearby_cancer"] + counts["nearby_esc"] > 0:
        return "non_lung_context_source_only"
    if counts["no_local"] > 0:
        return "no_locus_support"
    return "unresolved_due_to_context_mismatch"


def justify(cls: str, target: str, counts: dict, n_total: int) -> str:
    pc = counts["proximal_cancer"]
    pe = counts["proximal_esc"]
    nc = counts["nearby_cancer"]
    ne = counts["nearby_esc"]
    nl = counts["no_local"]
    df = counts["download_failed"]
    suffix = (" SOX9 ChIP-Atlas hg38 has zero lung-context experiments; the "
              "audit's information ceiling is bounded by non-lung substrate. "
              "Cross-context binding evidence does not validate the "
              "lung-developmental claim.")
    if cls == "peak_validated_in_non_lung_context_only":
        return (f"{pc + pe} of {n_total - df} non-lung experiment(s) show "
                f"SOX9 peak <= 5 kb of {target} TSS (cancer={pc}, ESC={pe}). "
                f"Cross-context binding evidence: SOX9 binding at this locus "
                f"in non-lung tissues does not establish binding in lung." + suffix)
    if cls == "non_lung_context_source_only":
        return (f"No proximal-promoter SOX9 peaks at {target} TSS in any "
                f"checked experiment. Nearby support: {nc + ne} (cancer={nc}, "
                f"ESC={ne}) within 5-50 kb. All in non-lung context." + suffix)
    if cls == "no_locus_support":
        return (f"All {n_total - df} checked non-lung experiments have no "
                f"SOX9 peaks within +/- 50 kb of {target} TSS. Substantive "
                f"negative finding within non-lung substrate." + suffix)
    return f"Cannot classify SOX9 -> {target}: {df} of {n_total} downloads failed."


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="gain-sox9-audit",
        description="First-pass SOX9 locus audit (non-lung substrate only).",
    )
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--sleep", type=float, default=0.3)
    args = parser.parse_args(argv)

    cancer_n = sum(1 for e in SOX9_EXPERIMENTS if e["biosample_class"] == "non_lung_cancer")
    esc_n = sum(1 for e in SOX9_EXPERIMENTS if e["biosample_class"] == "esc_derived")
    print(f"SOX9 audit: {len(SOX9_EXPERIMENTS)} experiments x {len(SOX9_TARGETS)} targets")
    print(f"  non_lung_cancer:   {cancer_n}")
    print(f"  esc_derived:       {esc_n}")
    print(f"  lung-context:      0 (structurally absent in ChIP-Atlas hg38 SOX9)")
    print()
    print(f"Downloading bed10 peak files for {len(SOX9_EXPERIMENTS)} experiments...")

    exp_peaks: dict[str, list | None] = {}
    for i, e in enumerate(SOX9_EXPERIMENTS, 1):
        srx = e["srx"]
        url = chipatlas_bed_url(srx, threshold=10)
        print(f"  [{i:>2}/{len(SOX9_EXPERIMENTS)}] {srx} ({e['biosample_class']:<16} | {e['label']})", end=" ")
        blob = http_get_bytes(url)
        if blob is None:
            exp_peaks[srx] = None
            print("FAILED")
        else:
            peaks = parse_bed(blob)
            exp_peaks[srx] = peaks
            print(f"-> {len(peaks):>6} peaks ({len(blob):,} bytes)")
        if i < len(SOX9_EXPERIMENTS):
            time.sleep(args.sleep)

    out_rows: list[dict] = []
    print(f"\nIntersecting peaks with target loci...")
    for target_name, target in SOX9_TARGETS.items():
        per_exp: list[dict] = []
        for e in SOX9_EXPERIMENTS:
            peaks = exp_peaks.get(e["srx"])
            if peaks is None:
                per_exp.append({"biosample_class": e["biosample_class"],
                                "classification": "download_failed"})
                continue
            d = peak_distance_to_tss(peaks, target)
            per_exp.append({"biosample_class": e["biosample_class"],
                            "classification": classify_per_experiment(d)})

        counts = aggregate(per_exp)
        n_attempted = len(per_exp) - counts["download_failed"]
        cls = classify(counts, n_attempted)

        out_rows.append({
            "regulator": "SOX9",
            "target": target_name,
            "target_locus": f"{target['chrom']}:{target['tss']} ({target['strand']}) — {target['source']}",
            "n_experiments_total": len(SOX9_EXPERIMENTS),
            "n_non_lung_cancer": cancer_n,
            "n_esc_derived": esc_n,
            "n_proximal_cancer": counts["proximal_cancer"],
            "n_proximal_esc": counts["proximal_esc"],
            "n_nearby_cancer": counts["nearby_cancer"],
            "n_nearby_esc": counts["nearby_esc"],
            "n_no_local_total": counts["no_local"],
            "n_download_failed": counts["download_failed"],
            "final_class": cls,
            "justification": justify(cls, target_name, counts, len(SOX9_EXPERIMENTS)),
            "evidence_url": "https://chip-atlas.dbcls.jp/?factor=SOX9&genome=hg38",
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
        print(f"    SOX9 -> {row['target']:<8} "
              f"prox(c+e)={row['n_proximal_cancer']:>2}+{row['n_proximal_esc']:>1} "
              f"near(c+e)={row['n_nearby_cancer']:>2}+{row['n_nearby_esc']:>1} "
              f"no_local={row['n_no_local_total']:>2} "
              f"-> {row['final_class']}")

    counts_by_class = {c: 0 for c in CLASSES}
    for r in out_rows:
        counts_by_class[r["final_class"]] = counts_by_class.get(r["final_class"], 0) + 1
    print(f"\n  Class counts:")
    for c in CLASSES:
        if counts_by_class[c] > 0:
            print(f"    {c}: {counts_by_class[c]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
