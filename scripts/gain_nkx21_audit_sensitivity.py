#!/usr/bin/env python3
"""gain nkx21-audit-sensitivity - threshold + distal-window robustness check.

Re-tests the same 21 NKX2-1 ChIP-Atlas experiments and 7 targets used by
gain_nkx21_audit.py at TWO thresholds (bed10 and bed05) with FOUR
proximity tiers (proximal <=5 kb, nearby 5-50 kb, distal_candidate
50-200 kb, no_local >200 kb). Reports per-pair class at each threshold
plus a class_changed flag.

Per notes/nkx21_sensitivity_design.md. Stdlib only. Imports the EXPERIMENTS
and TARGETS constants from the original audit script to avoid duplication.
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

# Allow importing the sibling script
sys.path.insert(0, str(Path(__file__).parent))
from gain_nkx21_audit import EXPERIMENTS, TARGETS  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = REPO_ROOT / "metadata" / "nkx21_peak_audit_sensitivity.csv"

USER_AGENT = "gain-nkx21-audit-sensitivity/0.1 (+https://github.com/DD-Ching/Gain)"

# Proximity tier cutoffs (bp)
PROXIMAL_BP = 5_000
NEARBY_BP = 50_000
DISTAL_BP = 200_000

THRESHOLDS = (5, 10)  # bed05 (q < 10^-5), bed10 (q < 10^-10)

CLASSES = (
    "peak_validated_in_lung_context",
    "peak_validated_in_cancer_lung_context_only",
    "lung_context_source_only",
    "distal_candidate_support_only",
    "no_locus_support",
    "unresolved_due_to_context",
)

OUT_FIELDS = (
    "threshold", "target", "target_locus",
    "n_experiments_total",
    "n_proximal_cancer", "n_proximal_noncancer",
    "n_nearby_cancer", "n_nearby_noncancer",
    "n_distal_cancer", "n_distal_noncancer",
    "n_no_local_cancer", "n_no_local_noncancer",
    "n_download_failed",
    "final_class", "class_at_other_threshold", "class_changed",
    "justification",
)


def chipatlas_bed_url(srx: str, threshold: int) -> str:
    return f"https://chip-atlas.dbcls.jp/data/hg38/eachData/bed{threshold:02d}/{srx}.{threshold:02d}.bed"


def http_get_bytes(url: str, timeout: float = 90.0) -> bytes | None:
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


def peak_distance(peaks: list[tuple[str, int, int]], target: dict) -> int:
    """Return min distance from any peak edge to TSS, or -1 if no peaks on chrom."""
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


def classify_distance(distance: int) -> str:
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
              for tier in ("proximal", "nearby", "distal", "no_local")
              for ctx in ("cancer", "noncancer")}
    counts["download_failed"] = 0
    for r in per_exp_results:
        if r["tier"] == "download_failed":
            counts["download_failed"] += 1
            continue
        bs = r["biosample_class"]
        if bs == "noncancer_lung":
            ctx = "noncancer"
        elif bs == "cancer_lung_line":
            ctx = "cancer"
        else:
            # 'unclear' counted as cancer for v0 (none in this dataset)
            ctx = "cancer"
        counts[f"{r['tier']}_{ctx}"] += 1
    return counts


def classify_v6(counts: dict) -> str:
    if counts.get("proximal_noncancer", 0) > 0:
        return "peak_validated_in_lung_context"
    if counts.get("proximal_cancer", 0) > 0:
        return "peak_validated_in_cancer_lung_context_only"
    if counts.get("nearby_cancer", 0) + counts.get("nearby_noncancer", 0) > 0:
        return "lung_context_source_only"
    if counts.get("distal_cancer", 0) + counts.get("distal_noncancer", 0) > 0:
        return "distal_candidate_support_only"
    if counts.get("no_local_cancer", 0) + counts.get("no_local_noncancer", 0) > 0:
        return "no_locus_support"
    return "unresolved_due_to_context"


def justify(cls: str, target: str, counts: dict, threshold: int) -> str:
    p = counts.get("proximal_cancer", 0) + counts.get("proximal_noncancer", 0)
    n = counts.get("nearby_cancer", 0) + counts.get("nearby_noncancer", 0)
    d = counts.get("distal_cancer", 0) + counts.get("distal_noncancer", 0)
    nl = counts.get("no_local_cancer", 0) + counts.get("no_local_noncancer", 0)
    band = f"q < 1e-{threshold}"

    if cls == "peak_validated_in_cancer_lung_context_only":
        return (f"At {band}: {p} cancer experiment(s) show NKX2-1 peak "
                f"<= 5 kb of {target} TSS; zero non-cancer support exists "
                f"in ChIP-Atlas hg38. Cancer-line locus support is real but "
                f"does not establish developmental binding.")
    if cls == "lung_context_source_only":
        return (f"At {band}: zero proximal-promoter peaks; {n} experiment(s) "
                f"show peaks within 5-50 kb of {target} TSS (nearby band). "
                f"Distal regulatory binding plausible but proximal "
                f"binding is absent at this threshold.")
    if cls == "distal_candidate_support_only":
        return (f"At {band}: zero proximal/nearby peaks; {d} experiment(s) "
                f"show peaks within 50-200 kb of {target} TSS (distal "
                f"candidate band). Candidate distal regulatory element only; "
                f"requires Hi-C / functional validation to confirm action "
                f"on the target.")
    if cls == "no_locus_support":
        return (f"At {band}: no peaks within +/- 200 kb of {target} TSS in "
                f"any of the {nl} checked cancer-line experiments. "
                f"Substantive negative finding at this threshold; remains "
                f"context-limited (cancer cell lines only).")
    return f"Unable to classify {target} at {band} (download failures or no usable data)."


def run_threshold(threshold: int, sleep: float, peak_cache: dict) -> dict:
    """Returns {target_name: row dict} for the given threshold."""
    print(f"\n=== Threshold bed{threshold:02d} (q < 1e-{threshold}) ===")
    # Download peaks per experiment for this threshold
    for i, e in enumerate(EXPERIMENTS, 1):
        srx = e["srx"]
        key = (srx, threshold)
        if key in peak_cache:
            continue
        url = chipatlas_bed_url(srx, threshold)
        print(f"  [{i:>2}/{len(EXPERIMENTS)}] {srx} ({e['label']})", end=" ")
        blob = http_get_bytes(url)
        if blob is None:
            peak_cache[key] = None
            print("FAILED")
        else:
            peaks = parse_bed(blob)
            peak_cache[key] = peaks
            print(f"-> {len(peaks):>6} peaks ({len(blob):,} bytes)")
        if i < len(EXPERIMENTS):
            time.sleep(sleep)

    # Per-target
    rows: dict[str, dict] = {}
    for target_name, target in TARGETS.items():
        per_exp: list[dict] = []
        for e in EXPERIMENTS:
            peaks = peak_cache.get((e["srx"], threshold))
            if peaks is None:
                per_exp.append({"biosample_class": e["biosample_class"],
                                "tier": "download_failed"})
                continue
            d = peak_distance(peaks, target)
            per_exp.append({"biosample_class": e["biosample_class"],
                            "tier": classify_distance(d)})
        counts = aggregate(per_exp)
        cls = classify_v6(counts)
        rows[target_name] = {
            "threshold": f"bed{threshold:02d}",
            "target": target_name,
            "target_locus": f"{target['chrom']}:{target['tss']} ({target['strand']}) — {target['source']}",
            "n_experiments_total": len(EXPERIMENTS),
            "n_proximal_cancer": counts["proximal_cancer"],
            "n_proximal_noncancer": counts["proximal_noncancer"],
            "n_nearby_cancer": counts["nearby_cancer"],
            "n_nearby_noncancer": counts["nearby_noncancer"],
            "n_distal_cancer": counts["distal_cancer"],
            "n_distal_noncancer": counts["distal_noncancer"],
            "n_no_local_cancer": counts["no_local_cancer"],
            "n_no_local_noncancer": counts["no_local_noncancer"],
            "n_download_failed": counts["download_failed"],
            "final_class": cls,
            "_counts_dict": counts,  # private; popped before write
        }
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="gain-nkx21-audit-sensitivity",
        description="Threshold + distal-window robustness check on the NKX2-1 audit.",
    )
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--sleep", type=float, default=0.3)
    args = parser.parse_args(argv)

    print(f"NKX2-1 sensitivity audit: {len(EXPERIMENTS)} experiments x "
          f"{len(TARGETS)} targets x {len(THRESHOLDS)} thresholds")

    peak_cache: dict = {}
    per_threshold: dict[int, dict] = {}
    for thr in THRESHOLDS:
        per_threshold[thr] = run_threshold(thr, args.sleep, peak_cache)

    # Build output rows: one per (threshold, target). Compute class_at_other_threshold + class_changed.
    out_rows: list[dict] = []
    for thr in THRESHOLDS:
        other_thr = [t for t in THRESHOLDS if t != thr][0]
        for target_name in TARGETS:
            row = per_threshold[thr][target_name]
            other_row = per_threshold[other_thr][target_name]
            row["class_at_other_threshold"] = other_row["final_class"]
            row["class_changed"] = "yes" if row["final_class"] != other_row["final_class"] else "no"
            row["justification"] = justify(
                row["final_class"], target_name, row["_counts_dict"], thr,
            )
            row.pop("_counts_dict", None)
            out_rows.append(row)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=OUT_FIELDS)
        w.writeheader()
        for row in out_rows:
            w.writerow(row)

    # Console summary
    print(f"\nwrote {args.out.relative_to(REPO_ROOT)}")
    print(f"  generated_at: {datetime.now(timezone.utc).isoformat(timespec='seconds')}")
    print(f"\n  Per-pair side-by-side (bed10 -> bed05):")
    for target_name in TARGETS:
        c10 = per_threshold[10][target_name]["final_class"]
        c05 = per_threshold[5][target_name]["final_class"]
        flag = "[CHANGED]" if c10 != c05 else ""
        # Strip the 'peak_validated_in_' / 'lung_context_' prefixes for compact display
        def short(c):
            return (c.replace("peak_validated_in_", "")
                     .replace("lung_context_", "")
                     .replace("cancer_lung_context_only", "cancer_only")
                     .replace("source_only", "src_only")
                     .replace("distal_candidate_", "distal_")
                     .replace("_due_to_context", ""))
        print(f"    {target_name:<8} bed10: {short(c10):<20} -> bed05: {short(c05):<20} {flag}")

    changes = sum(1 for r in out_rows if r["class_changed"] == "yes")
    # Halve because each pair is counted twice (once per threshold)
    print(f"\n  Pairs whose class changed between bed10 and bed05: {changes // 2} of {len(TARGETS)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
