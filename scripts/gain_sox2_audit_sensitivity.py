#!/usr/bin/env python3
"""gain sox2-audit-sensitivity - threshold sensitivity sweep on SOX2,
mirroring the NKX2-1 sensitivity logic.

Same 27 SOX2 lung-context ChIP-Atlas experiments + 7 lung-developmental
targets as gain_sox2_audit.py, run at TWO thresholds (bed05 and bed10)
with FOUR proximity tiers (proximal <=5 kb, nearby 5-50 kb,
distal_candidate 50-200 kb, no_local >200 kb).

Per pair per threshold: classify into one of seven classes (the six
SOX2 v0 classes plus distal_candidate_support_only, parallel to the
NKX2-1 sensitivity framework). Records class_changed between thresholds.

Stdlib only. No new framework -- sibling imports both NKX2-1 helpers
and SOX2 constants.
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
)
from gain_sox2_audit import SOX2_EXPERIMENTS, SOX2_TARGETS  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = REPO_ROOT / "metadata" / "sox2_sensitivity_audit.csv"

# Proximity tier cutoffs (bp)
PROXIMAL_BP = 5_000
NEARBY_BP = 50_000
DISTAL_BP = 200_000

THRESHOLDS = (5, 10)

CLASSES = (
    "peak_validated_in_lung_context",  # unreachable in v0
    "peak_validated_in_cancer_lung_context_only",
    "peak_validated_in_lung_reprogramming_context_only",
    "lung_context_source_only",
    "distal_candidate_support_only",
    "no_locus_support",
    "unresolved_due_to_context_mismatch",
)

OUT_FIELDS = (
    "threshold", "target", "target_locus",
    "n_experiments_total",
    "n_proximal_cancer", "n_proximal_mrc5",
    "n_nearby_cancer", "n_nearby_mrc5",
    "n_distal_cancer", "n_distal_mrc5",
    "n_no_local_total",
    "n_download_failed",
    "final_class",
    "class_at_other_threshold",
    "class_changed",
    "justification",
)


def classify_distance_4tier(distance: int) -> str:
    if distance < 0:
        return "no_local"
    if distance <= PROXIMAL_BP:
        return "proximal"
    if distance <= NEARBY_BP:
        return "nearby"
    if distance <= DISTAL_BP:
        return "distal"
    return "no_local"


def aggregate(per_exp_results: list[dict]) -> dict:
    counts = {f"{tier}_{ctx}": 0
              for tier in ("proximal", "nearby", "distal")
              for ctx in ("cancer", "mrc5")}
    counts["no_local"] = 0
    counts["download_failed"] = 0
    for r in per_exp_results:
        if r["tier"] == "download_failed":
            counts["download_failed"] += 1
            continue
        bs = r["biosample_class"]
        ctx = "cancer" if bs == "cancer_lung_line" else "mrc5"
        if r["tier"] == "no_local":
            counts["no_local"] += 1
        else:
            counts[f"{r['tier']}_{ctx}"] += 1
    return counts


def classify_v7(counts: dict, n_attempted: int) -> str:
    if n_attempted == 0:
        return "unresolved_due_to_context_mismatch"
    # peak_validated_in_lung_context unreachable: no primary epithelial
    if counts["proximal_cancer"] > 0:
        return "peak_validated_in_cancer_lung_context_only"
    if counts["proximal_mrc5"] > 0:
        return "peak_validated_in_lung_reprogramming_context_only"
    if counts["nearby_cancer"] + counts["nearby_mrc5"] > 0:
        return "lung_context_source_only"
    if counts["distal_cancer"] + counts["distal_mrc5"] > 0:
        return "distal_candidate_support_only"
    return "no_locus_support"


def justify(cls: str, target: str, counts: dict, threshold: int) -> str:
    pc = counts["proximal_cancer"]
    pm = counts["proximal_mrc5"]
    nc = counts["nearby_cancer"]
    nm = counts["nearby_mrc5"]
    dc = counts["distal_cancer"]
    dm = counts["distal_mrc5"]
    nl = counts["no_local"]
    band = f"q < 1e-{threshold}"
    suffix = (" Cancer-line and MRC-5 reprogramming contexts both reflect "
              "non-physiological SOX2 activity; neither tests the "
              "developmental claim.")
    if cls == "peak_validated_in_cancer_lung_context_only":
        return (f"At {band}: {pc} cancer-line experiment(s) show SOX2 peak "
                f"<= 5 kb of {target} TSS (MRC-5 proximal = {pm}). "
                f"Cancer-line locus support is real but reflects SOX2 as a "
                f"lung-squamous lineage oncogene (or SCLC subtype driver)." + suffix)
    if cls == "peak_validated_in_lung_reprogramming_context_only":
        return (f"At {band}: {pm} MRC-5 reprogramming experiment(s) show "
                f"SOX2 peak <= 5 kb of {target} TSS; zero cancer-line "
                f"proximal hits. MRC-5 SOX2 binding reflects Yamanaka "
                f"overexpression in fetal lung fibroblasts." + suffix)
    if cls == "lung_context_source_only":
        return (f"At {band}: zero proximal-promoter peaks; nearby support "
                f"= {nc + nm} (cancer={nc}, MRC-5={nm}). Distal binding "
                f"plausible; proximal absent.")
    if cls == "distal_candidate_support_only":
        return (f"At {band}: zero proximal/nearby peaks; distal candidate "
                f"support = {dc + dm} (cancer={dc}, MRC-5={dm}) within "
                f"50-200 kb. Candidate distal regulatory binding only; "
                f"requires Hi-C / functional validation.")
    if cls == "no_locus_support":
        return (f"At {band}: no SOX2 peaks within +/- 200 kb of {target} "
                f"TSS in any of {nl} checked experiments. Substantive "
                f"negative finding at this threshold within the cancer-line "
                f"+ MRC-5 reprogramming substrate.")
    return f"Unable to classify {target} at {band} (download or other failure)."


def run_threshold(threshold: int, sleep: float, peak_cache: dict) -> dict:
    print(f"\n=== Threshold bed{threshold:02d} (q < 1e-{threshold}) ===")
    for i, e in enumerate(SOX2_EXPERIMENTS, 1):
        srx = e["srx"]
        key = (srx, threshold)
        if key in peak_cache:
            continue
        url = chipatlas_bed_url(srx, threshold)
        print(f"  [{i:>2}/{len(SOX2_EXPERIMENTS)}] {srx} ({e['biosample_class']:<18})", end=" ")
        blob = http_get_bytes(url)
        if blob is None:
            peak_cache[key] = None
            print("FAILED")
        else:
            peaks = parse_bed(blob)
            peak_cache[key] = peaks
            print(f"-> {len(peaks):>6} peaks ({len(blob):,} bytes)")
        if i < len(SOX2_EXPERIMENTS):
            time.sleep(sleep)

    rows: dict[str, dict] = {}
    for target_name, target in SOX2_TARGETS.items():
        per_exp: list[dict] = []
        for e in SOX2_EXPERIMENTS:
            peaks = peak_cache.get((e["srx"], threshold))
            if peaks is None:
                per_exp.append({"biosample_class": e["biosample_class"],
                                "tier": "download_failed"})
                continue
            d = peak_distance_to_tss(peaks, target)
            per_exp.append({"biosample_class": e["biosample_class"],
                            "tier": classify_distance_4tier(d)})
        counts = aggregate(per_exp)
        n_attempted = len(per_exp) - counts["download_failed"]
        cls = classify_v7(counts, n_attempted)
        rows[target_name] = {
            "threshold": f"bed{threshold:02d}",
            "target": target_name,
            "target_locus": f"{target['chrom']}:{target['tss']} ({target['strand']}) — {target['source']}",
            "n_experiments_total": len(SOX2_EXPERIMENTS),
            "n_proximal_cancer": counts["proximal_cancer"],
            "n_proximal_mrc5": counts["proximal_mrc5"],
            "n_nearby_cancer": counts["nearby_cancer"],
            "n_nearby_mrc5": counts["nearby_mrc5"],
            "n_distal_cancer": counts["distal_cancer"],
            "n_distal_mrc5": counts["distal_mrc5"],
            "n_no_local_total": counts["no_local"],
            "n_download_failed": counts["download_failed"],
            "final_class": cls,
            "_counts": counts,  # private
        }
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="gain-sox2-audit-sensitivity",
        description="Threshold sensitivity sweep on SOX2 (bed10 + bed05).",
    )
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--sleep", type=float, default=0.3)
    args = parser.parse_args(argv)

    print(f"SOX2 sensitivity audit: {len(SOX2_EXPERIMENTS)} experiments x "
          f"{len(SOX2_TARGETS)} targets x {len(THRESHOLDS)} thresholds")

    peak_cache: dict = {}
    per_threshold: dict[int, dict] = {}
    for thr in THRESHOLDS:
        per_threshold[thr] = run_threshold(thr, args.sleep, peak_cache)

    out_rows: list[dict] = []
    for thr in THRESHOLDS:
        other = [t for t in THRESHOLDS if t != thr][0]
        for target_name in SOX2_TARGETS:
            row = per_threshold[thr][target_name]
            other_row = per_threshold[other][target_name]
            row["class_at_other_threshold"] = other_row["final_class"]
            row["class_changed"] = "yes" if row["final_class"] != other_row["final_class"] else "no"
            row["justification"] = justify(row["final_class"], target_name, row["_counts"], thr)
            row.pop("_counts", None)
            out_rows.append(row)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=OUT_FIELDS)
        w.writeheader()
        for row in out_rows:
            w.writerow(row)

    print(f"\nwrote {args.out.relative_to(REPO_ROOT)}")
    print(f"  generated_at: {datetime.now(timezone.utc).isoformat(timespec='seconds')}")

    print(f"\n  Per-pair side-by-side (bed10 -> bed05):")
    for target_name in SOX2_TARGETS:
        c10 = per_threshold[10][target_name]["final_class"]
        c05 = per_threshold[5][target_name]["final_class"]
        flag = "[CHANGED]" if c10 != c05 else ""
        def short(c):
            return (c.replace("peak_validated_in_", "")
                     .replace("lung_context_", "")
                     .replace("cancer_lung_context_only", "cancer_only")
                     .replace("lung_reprogramming_context_only", "mrc5_only")
                     .replace("source_only", "src_only")
                     .replace("distal_candidate_", "distal_")
                     .replace("_due_to_context_mismatch", "")
                     .replace("_due_to_context", ""))
        print(f"    {target_name:<8} bed10: {short(c10):<22} -> bed05: {short(c05):<22} {flag}")

    changes = sum(1 for r in out_rows if r["class_changed"] == "yes") // 2
    print(f"\n  Pairs whose class changed between bed10 and bed05: {changes} of {len(SOX2_TARGETS)}")

    print(f"\n  Per-pair tier counts at bed05:")
    for target_name in SOX2_TARGETS:
        r = per_threshold[5][target_name]
        print(f"    {target_name:<8} prox(c+m)={r['n_proximal_cancer']:>2}+{r['n_proximal_mrc5']:>1} "
              f"near(c+m)={r['n_nearby_cancer']:>2}+{r['n_nearby_mrc5']:>1} "
              f"dist(c+m)={r['n_distal_cancer']:>2}+{r['n_distal_mrc5']:>1} "
              f"no_local={r['n_no_local_total']:>2}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
