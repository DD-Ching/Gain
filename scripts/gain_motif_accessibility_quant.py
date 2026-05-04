#!/usr/bin/env python3
"""gain motif-accessibility-quant - quantitative refinement on the
already-collected per-pair counts. No new HTTP.

Reads the three existing audit CSVs (NKX2-1 targets, SOX2 targets,
SOX2-motif controls), computes four normalised metrics per pair,
ranks the SOX2 + control panel, and applies a 3-tier selectivity
verdict per notes/motif_accessibility_quant_design.md.

Stdlib only.
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = REPO_ROOT / "metadata" / "motif_accessibility_quant_refinement.csv"

INPUT_NKX21 = REPO_ROOT / "metadata" / "nkx21_motif_accessibility_audit.csv"
INPUT_SOX2 = REPO_ROOT / "metadata" / "sox2_motif_accessibility_audit.csv"
INPUT_CONTROL = REPO_ROOT / "metadata" / "motif_accessibility_control_audit.csv"

# Category lookup per (regulator, target) — drives selectivity tagging.
CATEGORY: dict[tuple[str, str], str] = {
    # NKX2-1 canonical (4) — scanned with NKX2-1 motif (different motif from controls)
    ("NKX2-1", "SFTPC"):   "nkx21_canonical",
    ("NKX2-1", "SCGB1A1"): "nkx21_canonical",
    ("NKX2-1", "ABCA3"):   "nkx21_canonical",
    ("NKX2-1", "FOXA2"):   "nkx21_canonical",
    # SOX2 canonical (5) — scanned with SOX2 motif
    ("SOX2", "TP63"):      "sox2_canonical",
    ("SOX2", "KRT5"):      "sox2_canonical",
    ("SOX2", "MUC5B"):     "sox2_canonical",
    ("SOX2", "FOXJ1"):     "sox2_canonical",
    ("SOX2", "SCGB1A1"):   "sox2_canonical",
    # Controls (5) — scanned with SOX2 motif
    ("SOX2_control", "GAPDH"): "control_housekeeping",
    ("SOX2_control", "ACTB"):  "control_housekeeping",
    ("SOX2_control", "HBA1"):  "control_blood_specific",
    ("SOX2_control", "HBB"):   "control_blood_specific",
    ("SOX2_control", "SFTPC"): "control_lung_wrong_program",
}

OUT_FIELDS = (
    "regulator", "target", "category", "motif_id",
    "n_motif_hits_in_window", "n_fetal_peaks_in_window",
    "n_motif_hits_in_fetal_peaks", "n_supporting_fetal_experiments",
    "motif_capture_rate", "motif_density_per_fetal_peak",
    "cross_donor_consistency", "combined_quant_score",
    "rank_within_sox2_set", "separation_verdict",
)


def safe_div(num: float, den: float) -> float:
    if den == 0:
        return 0.0
    return num / den


def load_csv(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(f"missing input CSV: {path}")
    with path.open() as f:
        return list(csv.DictReader(f))


def compute_metrics(row: dict) -> dict:
    """Compute the four metrics from raw count fields."""
    n_motif = int(row.get("n_motif_hits_in_window", 0) or 0)
    n_fetal_peaks = int(row.get("n_fetal_peaks_in_window", 0) or 0)
    n_motif_in_fetal = int(row.get("n_motif_hits_in_fetal_peaks", 0) or 0)
    n_supp = int(row.get("n_supporting_fetal_experiments", 0) or 0)

    capture = safe_div(n_motif_in_fetal, n_motif)
    density = safe_div(n_motif_in_fetal, n_fetal_peaks)
    consistency = safe_div(n_supp, 13.0)
    combined = capture * consistency

    return {
        "n_motif_hits_in_window": n_motif,
        "n_fetal_peaks_in_window": n_fetal_peaks,
        "n_motif_hits_in_fetal_peaks": n_motif_in_fetal,
        "n_supporting_fetal_experiments": n_supp,
        "motif_capture_rate": round(capture, 4),
        "motif_density_per_fetal_peak": round(density, 4),
        "cross_donor_consistency": round(consistency, 4),
        "combined_quant_score": round(combined, 4),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="gain-motif-accessibility-quant",
        description="Quantitative refinement on existing motif+accessibility audit outputs.",
    )
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)

    print("Loading existing audit CSVs (no new HTTP)")
    nkx21_rows = load_csv(INPUT_NKX21)
    sox2_rows = load_csv(INPUT_SOX2)
    control_rows = load_csv(INPUT_CONTROL)
    print(f"  NKX2-1 targets: {len(nkx21_rows)}")
    print(f"  SOX2 targets:   {len(sox2_rows)}")
    print(f"  Controls:       {len(control_rows)}")

    all_rows: list[dict] = []
    for row in nkx21_rows + sox2_rows + control_rows:
        reg = row["regulator"]
        tgt = row["target"]
        category = CATEGORY.get((reg, tgt))
        if category is None:
            print(f"  warning: skipping unknown (regulator, target): "
                  f"({reg}, {tgt})", file=sys.stderr)
            continue
        metrics = compute_metrics(row)
        all_rows.append({
            "regulator": reg,
            "target": tgt,
            "category": category,
            "motif_id": row.get("motif_id", "?"),
            **metrics,
            "rank_within_sox2_set": "",
            "separation_verdict": "",
        })

    # Rank SOX2 + control panel by combined_quant_score (10 rows)
    sox2_set = [r for r in all_rows if r["category"] in (
        "sox2_canonical", "control_housekeeping",
        "control_blood_specific", "control_lung_wrong_program",
    )]
    sox2_set.sort(key=lambda r: r["combined_quant_score"], reverse=True)
    for i, r in enumerate(sox2_set, 1):
        r["rank_within_sox2_set"] = i

    # Selectivity verdict per the design's decision rule
    canonicals = [r for r in sox2_set if r["category"] == "sox2_canonical"]
    controls = [r for r in sox2_set if r["category"] != "sox2_canonical"]
    canonical_scores = sorted([r["combined_quant_score"] for r in canonicals])
    control_scores = sorted([r["combined_quant_score"] for r in controls])

    # all canonicals > all controls?
    if canonical_scores and control_scores and \
       min(canonical_scores) > max(control_scores):
        verdict = "salvageable"
    else:
        # check if blood controls are reliably below the canonical band
        blood = [r["combined_quant_score"] for r in controls
                 if r["category"] == "control_blood_specific"]
        if blood and max(blood) < min(canonical_scores):
            verdict = "partially_salvageable"
        else:
            verdict = "not_salvageable"

    for r in all_rows:
        r["separation_verdict"] = verdict

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=OUT_FIELDS)
        w.writeheader()
        for row in all_rows:
            w.writerow(row)

    try:
        out_display = str(args.out.relative_to(REPO_ROOT))
    except ValueError:
        out_display = str(args.out)
    print(f"\nwrote {out_display}")
    print(f"\n=== SOX2 + control panel ranked by combined_quant_score ===")
    print(f"  {'rank':>4}  {'gene':<10}  {'category':<28}  {'capture':>8}  {'density':>8}  {'consist':>8}  {'combined':>8}")
    for r in sox2_set:
        print(f"  {r['rank_within_sox2_set']:>4}  {r['target']:<10}  "
              f"{r['category']:<28}  "
              f"{r['motif_capture_rate']:>8.4f}  "
              f"{r['motif_density_per_fetal_peak']:>8.4f}  "
              f"{r['cross_donor_consistency']:>8.4f}  "
              f"{r['combined_quant_score']:>8.4f}")

    print(f"\n=== NKX2-1 targets (cross-motif; reported with caveat) ===")
    nkx21_set = sorted([r for r in all_rows if r["category"] == "nkx21_canonical"],
                      key=lambda r: r["combined_quant_score"], reverse=True)
    print(f"  {'gene':<10}  {'capture':>8}  {'density':>8}  {'consist':>8}  {'combined':>8}")
    for r in nkx21_set:
        print(f"  {r['target']:<10}  "
              f"{r['motif_capture_rate']:>8.4f}  "
              f"{r['motif_density_per_fetal_peak']:>8.4f}  "
              f"{r['cross_donor_consistency']:>8.4f}  "
              f"{r['combined_quant_score']:>8.4f}")

    print(f"\n=== Verdict ===")
    print(f"  Canonical SOX2 score range: {min(canonical_scores):.4f} - {max(canonical_scores):.4f}")
    print(f"  Control          score range: {min(control_scores):.4f} - {max(control_scores):.4f}")
    print(f"  Verdict: {verdict}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
