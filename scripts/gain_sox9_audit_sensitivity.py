#!/usr/bin/env python3
"""gain sox9-audit-sensitivity - threshold sensitivity sweep on SOX9,
mirroring the NKX2-1 and SOX2 sensitivity logic.

Same 27 SOX9 hg38 ChIP-Atlas experiments (all non-lung: 20 cancer cell
lines + 7 ESC-derived) and 7 lung-developmental targets as
gain_sox9_audit.py, run at TWO thresholds (bed05 and bed10) with FOUR
proximity tiers (proximal <= 5 kb, nearby 5-50 kb, distal_candidate
50-200 kb, no_local > 200 kb).

Per-pair class at each threshold, plus class_changed. Five reachable
output classes (lung-tier classes are structurally unreachable
because the substrate has zero lung experiments).

Stdlib only. No new framework -- sibling imports both NKX2-1 helpers
and SOX9 constants.
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
from gain_sox9_audit import SOX9_EXPERIMENTS, SOX9_TARGETS  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = REPO_ROOT / "metadata" / "sox9_sensitivity_audit.csv"

PROXIMAL_BP = 5_000
NEARBY_BP = 50_000
DISTAL_BP = 200_000

THRESHOLDS = (5, 10)

# Reachable classes only (lung-tier classes structurally unreachable for SOX9)
CLASSES = (
    "peak_validated_in_non_lung_context_only",
    "non_lung_context_source_only",
    "distal_candidate_support_only",
    "no_locus_support",
    "unresolved_due_to_context_mismatch",
)

OUT_FIELDS = (
    "threshold", "target", "target_locus",
    "n_experiments_total",
    "n_proximal_cancer", "n_proximal_esc",
    "n_nearby_cancer", "n_nearby_esc",
    "n_distal_cancer", "n_distal_esc",
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
              for ctx in ("cancer", "esc")}
    counts["no_local"] = 0
    counts["download_failed"] = 0
    for r in per_exp_results:
        if r["tier"] == "download_failed":
            counts["download_failed"] += 1
            continue
        bs = r["biosample_class"]
        ctx = "cancer" if bs == "non_lung_cancer" else "esc"
        if r["tier"] == "no_local":
            counts["no_local"] += 1
        else:
            counts[f"{r['tier']}_{ctx}"] += 1
    return counts


def classify(counts: dict, n_attempted: int) -> str:
    if n_attempted == 0:
        return "unresolved_due_to_context_mismatch"
    if counts["proximal_cancer"] + counts["proximal_esc"] > 0:
        return "peak_validated_in_non_lung_context_only"
    if counts["nearby_cancer"] + counts["nearby_esc"] > 0:
        return "non_lung_context_source_only"
    if counts["distal_cancer"] + counts["distal_esc"] > 0:
        return "distal_candidate_support_only"
    return "no_locus_support"


def justify(cls: str, target: str, counts: dict, threshold: int) -> str:
    pc = counts["proximal_cancer"]
    pe = counts["proximal_esc"]
    nc = counts["nearby_cancer"]
    ne = counts["nearby_esc"]
    dc = counts["distal_cancer"]
    de = counts["distal_esc"]
    band = f"q < 1e-{threshold}"
    suffix = (" SOX9 ChIP-Atlas hg38 has zero lung-context experiments; the "
              "audit's information ceiling is bounded by non-lung substrate. "
              "Cross-context binding does not validate the lung-developmental "
              "claim.")
    if cls == "peak_validated_in_non_lung_context_only":
        return (f"At {band}: {pc + pe} non-lung experiment(s) show SOX9 peak "
                f"<= 5 kb of {target} TSS (cancer={pc}, ESC={pe})." + suffix)
    if cls == "non_lung_context_source_only":
        return (f"At {band}: zero proximal-promoter peaks; {nc + ne} "
                f"experiment(s) show peaks within 5-50 kb of {target} TSS "
                f"(cancer={nc}, ESC={ne}).")
    if cls == "distal_candidate_support_only":
        return (f"At {band}: zero proximal/nearby peaks; {dc + de} "
                f"experiment(s) show peaks within 50-200 kb of {target} TSS "
                f"(cancer={dc}, ESC={de}). Candidate distal regulatory "
                f"binding only; requires functional validation.")
    if cls == "no_locus_support":
        return (f"At {band}: no SOX9 peaks within +/- 200 kb of {target} TSS "
                f"in any of the {len(SOX9_EXPERIMENTS) - counts['download_failed']} "
                f"checked experiments.")
    return f"Unable to classify {target} at {band}."


def run_threshold(threshold: int, sleep: float, peak_cache: dict) -> dict:
    print(f"\n=== Threshold bed{threshold:02d} (q < 1e-{threshold}) ===")
    for i, e in enumerate(SOX9_EXPERIMENTS, 1):
        srx = e["srx"]
        key = (srx, threshold)
        if key in peak_cache:
            continue
        url = chipatlas_bed_url(srx, threshold)
        print(f"  [{i:>2}/{len(SOX9_EXPERIMENTS)}] {srx} ({e['biosample_class']:<16})", end=" ")
        blob = http_get_bytes(url)
        if blob is None:
            peak_cache[key] = None
            print("FAILED")
        else:
            peaks = parse_bed(blob)
            peak_cache[key] = peaks
            print(f"-> {len(peaks):>6} peaks ({len(blob):,} bytes)")
        if i < len(SOX9_EXPERIMENTS):
            time.sleep(sleep)

    rows: dict[str, dict] = {}
    for target_name, target in SOX9_TARGETS.items():
        per_exp: list[dict] = []
        for e in SOX9_EXPERIMENTS:
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
        cls = classify(counts, n_attempted)
        rows[target_name] = {
            "threshold": f"bed{threshold:02d}",
            "target": target_name,
            "target_locus": f"{target['chrom']}:{target['tss']} ({target['strand']}) — {target['source']}",
            "n_experiments_total": len(SOX9_EXPERIMENTS),
            "n_proximal_cancer": counts["proximal_cancer"],
            "n_proximal_esc": counts["proximal_esc"],
            "n_nearby_cancer": counts["nearby_cancer"],
            "n_nearby_esc": counts["nearby_esc"],
            "n_distal_cancer": counts["distal_cancer"],
            "n_distal_esc": counts["distal_esc"],
            "n_no_local_total": counts["no_local"],
            "n_download_failed": counts["download_failed"],
            "final_class": cls,
            "_counts": counts,
        }
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="gain-sox9-audit-sensitivity",
        description="Threshold sensitivity sweep on SOX9 (bed10 + bed05).",
    )
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--sleep", type=float, default=0.3)
    args = parser.parse_args(argv)

    print(f"SOX9 sensitivity audit: {len(SOX9_EXPERIMENTS)} experiments x "
          f"{len(SOX9_TARGETS)} targets x {len(THRESHOLDS)} thresholds")
    print(f"  substrate: 20 non_lung_cancer + 7 esc_derived (zero lung)")

    peak_cache: dict = {}
    per_threshold: dict[int, dict] = {}
    for thr in THRESHOLDS:
        per_threshold[thr] = run_threshold(thr, args.sleep, peak_cache)

    out_rows: list[dict] = []
    for thr in THRESHOLDS:
        other = [t for t in THRESHOLDS if t != thr][0]
        for target_name in SOX9_TARGETS:
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
    for target_name in SOX9_TARGETS:
        c10 = per_threshold[10][target_name]["final_class"]
        c05 = per_threshold[5][target_name]["final_class"]
        flag = "[CHANGED]" if c10 != c05 else ""
        def short(c):
            return (c.replace("peak_validated_in_", "")
                     .replace("non_lung_context_only", "non_lung_only")
                     .replace("non_lung_context_", "")
                     .replace("source_only", "src_only")
                     .replace("distal_candidate_", "distal_")
                     .replace("_due_to_context_mismatch", ""))
        print(f"    {target_name:<8} bed10: {short(c10):<22} -> bed05: {short(c05):<22} {flag}")

    changes = sum(1 for r in out_rows if r["class_changed"] == "yes") // 2
    print(f"\n  Pairs whose class changed between bed10 and bed05: {changes} of {len(SOX9_TARGETS)}")

    print(f"\n  Per-pair tier counts at bed05:")
    for target_name in SOX9_TARGETS:
        r = per_threshold[5][target_name]
        print(f"    {target_name:<8} prox(c+e)={r['n_proximal_cancer']:>2}+{r['n_proximal_esc']:>1} "
              f"near(c+e)={r['n_nearby_cancer']:>2}+{r['n_nearby_esc']:>1} "
              f"dist(c+e)={r['n_distal_cancer']:>2}+{r['n_distal_esc']:>1} "
              f"no_local={r['n_no_local_total']:>2}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
