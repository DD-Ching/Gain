#!/usr/bin/env python3
"""gain nkx21-distal-candidates - rank distal-band candidate loci for the 4
NKX2-1 targets that lack proximal-promoter support.

For SFTPC, SCGB1A1, ABCA3, FOXA2: pool NKX2-1 ChIP-Atlas peaks within +/- 200
kb of each target's hg38 TSS across 21 cancer-line experiments x 2 thresholds
(bed05, bed10). Greedy-merge peaks within 1 kb to form candidate loci.
Classify each locus into one of four candidate tiers per
notes/nkx21_distal_candidate_design.md.

Stdlib only. Sibling import from gain_nkx21_audit.py.
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

# Sibling import
sys.path.insert(0, str(Path(__file__).parent))
from gain_nkx21_audit import EXPERIMENTS, TARGETS  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = REPO_ROOT / "metadata" / "nkx21_distal_candidates.csv"

USER_AGENT = "gain-nkx21-distal/0.1 (+https://github.com/DD-Ching/Gain)"

# Subset of targets: the 4 originally-failing pairs from the sensitivity audit
DISTAL_TARGET_NAMES = ("SFTPC", "SCGB1A1", "ABCA3", "FOXA2")
DISTAL_TARGETS = {k: TARGETS[k] for k in DISTAL_TARGET_NAMES}

DISTAL_LOWER_BP = 50_000
DISTAL_UPPER_BP = 200_000
MERGE_GAP_BP = 1_000
THRESHOLDS = (5, 10)  # bed05, bed10

CONCENTRATED_BP = 1_000
SCATTERED_BP = 5_000

CANDIDATE_TIERS = (
    "strong_distal_candidate",
    "moderate_distal_candidate",
    "weak_distal_candidate",
    "low_priority_or_likely_noise",
)

OUT_FIELDS = (
    "target", "target_tss",
    "locus_chrom", "locus_start", "locus_end", "locus_midpoint",
    "locus_width_bp",
    "distance_to_tss_bp", "distance_band",
    "n_experiments_supporting",
    "n_experiments_at_bed10", "n_experiments_at_bed05",
    "support_pattern", "support_concentration_metric_bp",
    "supporting_experiment_ids",
    "biosample_summary",
    "candidate_tier",
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


def nearest_edge_distance(peak_start: int, peak_end: int, tss: int) -> int:
    """Absolute distance from the peak's nearest edge to TSS. 0 if peak spans TSS."""
    if peak_start <= tss <= peak_end:
        return 0
    return min(abs(peak_start - tss), abs(peak_end - tss))


def signed_distance_to_tss(peak_start: int, peak_end: int, tss: int, strand: str) -> int:
    """Signed distance: + downstream, - upstream of TSS (strand-aware)."""
    midpoint = (peak_start + peak_end) // 2
    delta = midpoint - tss
    if strand == "-":
        delta = -delta
    return delta


def distance_band(signed_dist: int) -> str:
    abs_dist = abs(signed_dist)
    direction = "downstream" if signed_dist >= 0 else "upstream"
    if abs_dist <= 100_000:
        return f"50-100kb_{direction}"
    return f"100-200kb_{direction}"


def filter_distal_peaks(peaks: list[tuple[str, int, int]], target: dict) -> list[tuple[str, int, int]]:
    """Keep peaks whose nearest edge to TSS is in [50 kb, 200 kb] and on target's chrom."""
    chrom, tss = target["chrom"], target["tss"]
    out = []
    for c, s, e in peaks:
        if c != chrom:
            continue
        d = nearest_edge_distance(s, e, tss)
        if DISTAL_LOWER_BP <= d <= DISTAL_UPPER_BP:
            out.append((c, s, e))
    return out


def greedy_merge(tagged_peaks: list[dict]) -> list[dict]:
    """Merge peaks (each with srx + threshold tags) within MERGE_GAP_BP into loci.

    Input: list of {chrom, start, end, srx, threshold}.
    Output: list of {chrom, start, end, supports = list of (srx, threshold)}.
    """
    if not tagged_peaks:
        return []
    sorted_peaks = sorted(tagged_peaks, key=lambda p: (p["chrom"], p["start"]))
    loci = []
    cur = {
        "chrom": sorted_peaks[0]["chrom"],
        "start": sorted_peaks[0]["start"],
        "end": sorted_peaks[0]["end"],
        "supports": [(sorted_peaks[0]["srx"], sorted_peaks[0]["threshold"])],
    }
    for p in sorted_peaks[1:]:
        if p["chrom"] == cur["chrom"] and p["start"] <= cur["end"] + MERGE_GAP_BP:
            cur["end"] = max(cur["end"], p["end"])
            cur["supports"].append((p["srx"], p["threshold"]))
        else:
            loci.append(cur)
            cur = {
                "chrom": p["chrom"],
                "start": p["start"],
                "end": p["end"],
                "supports": [(p["srx"], p["threshold"])],
            }
    loci.append(cur)
    return loci


def assign_tier(n_at_bed10: int, n_at_any: int) -> str:
    if n_at_bed10 >= 5 or n_at_any >= 7:
        return "strong_distal_candidate"
    if n_at_bed10 >= 3 or n_at_any >= 5:
        return "moderate_distal_candidate"
    if n_at_any >= 2:
        return "weak_distal_candidate"
    return "low_priority_or_likely_noise"


def support_pattern(width: int) -> str:
    if width < CONCENTRATED_BP:
        return "concentrated"
    if width < SCATTERED_BP:
        return "moderately_concentrated"
    return "scattered"


def biosample_summary(srx_list: list[str]) -> str:
    by_class: dict[str, int] = {}
    by_srx = {e["srx"]: e for e in EXPERIMENTS}
    for srx in set(srx_list):
        bs = by_srx.get(srx, {}).get("biosample_class", "unknown")
        by_class[bs] = by_class.get(bs, 0) + 1
    parts = [f"{k}={v}" for k, v in sorted(by_class.items())]
    return "; ".join(parts)


def justify(tier: str, target: str, locus: dict, n_bed10: int, n_bed05: int,
            n_distinct: int, dist_band: str, pattern: str) -> str:
    base = (f"Tier driven by bed10 support count = {n_bed10} "
            f"(any-threshold = {n_distinct}). Locus is {pattern} "
            f"(width = {locus['end'] - locus['start']} bp), "
            f"in band {dist_band} relative to {target} TSS.")
    suffix = (" Candidate-level only: cancer-line ChIP does not establish "
              "developmental binding; locus-distance proximity does not "
              "establish regulatory contact.")
    if tier == "strong_distal_candidate":
        return ("Strong distal candidate: warrants Hi-C / promoter-capture / "
                f"perturbation follow-up. {base}{suffix}")
    if tier == "moderate_distal_candidate":
        return f"Moderate distal candidate. {base}{suffix}"
    if tier == "weak_distal_candidate":
        return f"Weak distal candidate. {base}{suffix}"
    return ("Low-priority candidate (single experiment); likely noise or "
            f"cell-line-specific. {base}{suffix}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="gain-nkx21-distal-candidates",
        description="Distal-band candidate loci for the 4 NKX2-1 targets "
                    "lacking proximal-promoter support.",
    )
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--sleep", type=float, default=0.3)
    args = parser.parse_args(argv)

    print(f"NKX2-1 distal-candidate audit: {len(EXPERIMENTS)} experiments x "
          f"{len(DISTAL_TARGETS)} targets x {len(THRESHOLDS)} thresholds")
    print(f"  targets: {', '.join(DISTAL_TARGET_NAMES)}")
    print(f"  distal band: {DISTAL_LOWER_BP}-{DISTAL_UPPER_BP} bp from TSS")
    print(f"  merge gap: {MERGE_GAP_BP} bp")

    # peaks_per_target[target] = list of {chrom, start, end, srx, threshold}
    peaks_per_target: dict[str, list[dict]] = {t: [] for t in DISTAL_TARGET_NAMES}

    for thr in THRESHOLDS:
        print(f"\n=== Threshold bed{thr:02d} (q < 1e-{thr}) ===")
        for i, e in enumerate(EXPERIMENTS, 1):
            srx = e["srx"]
            url = chipatlas_bed_url(srx, thr)
            print(f"  [{i:>2}/{len(EXPERIMENTS)}] {srx} ({e['label']})", end=" ")
            blob = http_get_bytes(url)
            if blob is None:
                print("FAILED")
                if i < len(EXPERIMENTS):
                    time.sleep(args.sleep)
                continue
            peaks = parse_bed(blob)
            # For each target, filter peaks to its distal band
            new_peaks = 0
            for t_name, t in DISTAL_TARGETS.items():
                distal = filter_distal_peaks(peaks, t)
                for c, s, ed in distal:
                    peaks_per_target[t_name].append({
                        "chrom": c, "start": s, "end": ed,
                        "srx": srx, "threshold": thr,
                    })
                    new_peaks += 1
            print(f"-> {len(peaks):>5} peaks total, {new_peaks} added to distal pools "
                  f"({len(blob):,} bytes)")
            if i < len(EXPERIMENTS):
                time.sleep(args.sleep)

    # Merge per target and classify
    out_rows: list[dict] = []
    print(f"\n=== Merging and classifying candidate loci ===")
    for t_name in DISTAL_TARGET_NAMES:
        target = DISTAL_TARGETS[t_name]
        loci = greedy_merge(peaks_per_target[t_name])
        print(f"  {t_name}: {len(peaks_per_target[t_name])} distal peaks -> "
              f"{len(loci)} merged candidate loci")
        for locus in loci:
            distinct_srx = sorted({s for s, _ in locus["supports"]})
            srx_at_bed10 = {s for s, t in locus["supports"] if t == 10}
            srx_at_bed05 = {s for s, t in locus["supports"] if t == 5}
            n_bed10 = len(srx_at_bed10)
            n_bed05 = len(srx_at_bed05)
            n_distinct = len(distinct_srx)
            tier = assign_tier(n_bed10, n_distinct)

            mid = (locus["start"] + locus["end"]) // 2
            width = locus["end"] - locus["start"]
            sd = signed_distance_to_tss(locus["start"], locus["end"],
                                        target["tss"], target["strand"])
            band = distance_band(sd)
            pattern = support_pattern(width)

            out_rows.append({
                "target": t_name,
                "target_tss": f"{target['chrom']}:{target['tss']} ({target['strand']})",
                "locus_chrom": locus["chrom"],
                "locus_start": locus["start"],
                "locus_end": locus["end"],
                "locus_midpoint": mid,
                "locus_width_bp": width,
                "distance_to_tss_bp": sd,
                "distance_band": band,
                "n_experiments_supporting": n_distinct,
                "n_experiments_at_bed10": n_bed10,
                "n_experiments_at_bed05": n_bed05,
                "support_pattern": pattern,
                "support_concentration_metric_bp": width,
                "supporting_experiment_ids": ";".join(distinct_srx),
                "biosample_summary": biosample_summary(distinct_srx),
                "candidate_tier": tier,
                "justification": justify(tier, t_name, locus, n_bed10, n_bed05,
                                          n_distinct, band, pattern),
            })

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=OUT_FIELDS)
        w.writeheader()
        for row in out_rows:
            w.writerow(row)

    print(f"\nwrote {args.out.relative_to(REPO_ROOT)}")
    print(f"  generated_at: {datetime.now(timezone.utc).isoformat(timespec='seconds')}")
    print(f"  total candidate loci: {len(out_rows)}")

    print(f"\n  Per-target tier breakdown:")
    by_target: dict[str, dict[str, int]] = {}
    for row in out_rows:
        d = by_target.setdefault(row["target"], {t: 0 for t in CANDIDATE_TIERS})
        d[row["candidate_tier"]] += 1
    print(f"  {'Target':<8}  {'strong':>7} {'moderate':>9} {'weak':>5} {'low_priority':>13}")
    for t_name in DISTAL_TARGET_NAMES:
        d = by_target.get(t_name, {t: 0 for t in CANDIDATE_TIERS})
        print(f"  {t_name:<8}  "
              f"{d['strong_distal_candidate']:>7} "
              f"{d['moderate_distal_candidate']:>9} "
              f"{d['weak_distal_candidate']:>5} "
              f"{d['low_priority_or_likely_noise']:>13}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
