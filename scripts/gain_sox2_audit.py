#!/usr/bin/env python3
"""gain sox2-audit - first-pass locus audit for SOX2 against 7 lung-focused
targets, per notes/sox2_audit_design.md.

Reuses helpers from gain_nkx21_audit.py via sibling import (no new
infrastructure). Hardcoded SOX2 lung-context experiment list (27, split into
19 cancer cell lines + 8 MRC-5 reprogramming biosamples) and 7 target hg38
TSS coordinates.

Output classes (6, with one new tier vs the NKX2-1 audit):
  peak_validated_in_lung_context                          (unreachable in v0)
  peak_validated_in_cancer_lung_context_only
  peak_validated_in_lung_reprogramming_context_only       (NEW - MRC-5 OSKM)
  lung_context_source_only
  no_locus_support
  unresolved_due_to_context_mismatch

Stdlib only.
"""
from __future__ import annotations

import argparse
import csv
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Sibling import of the helpers
sys.path.insert(0, str(Path(__file__).parent))
from gain_nkx21_audit import (  # noqa: E402
    chipatlas_bed_url,
    http_get_bytes,
    parse_bed,
    peak_distance_to_tss,
    classify_per_experiment,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = REPO_ROOT / "metadata" / "sox2_initial_audit.csv"

PROXIMAL_BP = 5_000  # same as NKX2-1 v0
WINDOW_BP = 50_000

CLASSES = (
    "peak_validated_in_lung_context",
    "peak_validated_in_cancer_lung_context_only",
    "peak_validated_in_lung_reprogramming_context_only",
    "lung_context_source_only",
    "no_locus_support",
    "unresolved_due_to_context_mismatch",
)

# 27 SOX2 hg38 lung-context ChIP-Atlas experiments classified by biosample.
# Extracted from metadata/cache/chipatlas_experimentList.tab on 2026-05-04.
SOX2_EXPERIMENTS: list[dict] = [
    # ArrayExpress lung cancer (4)
    {"srx": "ERX2260038",  "biosample_class": "cancer_lung_line", "label": "ArrayExpress lung cancer"},
    {"srx": "ERX2260040",  "biosample_class": "cancer_lung_line", "label": "ArrayExpress lung cancer"},
    {"srx": "ERX2260044",  "biosample_class": "cancer_lung_line", "label": "ArrayExpress lung cancer"},
    {"srx": "ERX2260046",  "biosample_class": "cancer_lung_line", "label": "ArrayExpress lung cancer"},
    # H29 SCLC (2)
    {"srx": "SRX11904439", "biosample_class": "cancer_lung_line", "label": "H29 (SCLC) RD antibody"},
    {"srx": "SRX11904440", "biosample_class": "cancer_lung_line", "label": "H29 (SCLC) EMD antibody"},
    # NCI-H82 SCLC (2)
    {"srx": "SRX11904441", "biosample_class": "cancer_lung_line", "label": "NCI-H82 (SCLC) RD"},
    {"srx": "SRX11904442", "biosample_class": "cancer_lung_line", "label": "NCI-H82 (SCLC) EMD"},
    # NCI-H1836 SCLC (2)
    {"srx": "SRX11904443", "biosample_class": "cancer_lung_line", "label": "NCI-H1836 (SCLC) RD"},
    {"srx": "SRX11904444", "biosample_class": "cancer_lung_line", "label": "NCI-H1836 (SCLC) EMD"},
    # MRC-5 reprogramming (8) — fetal lung fibroblast in OSKM/OSvKM/OSK Yamanaka context
    {"srx": "SRX1813580",  "biosample_class": "mrc5_reprogramming", "label": "MRC-5 endogenous SOX2 rep1"},
    {"srx": "SRX1813581",  "biosample_class": "mrc5_reprogramming", "label": "MRC-5 endogenous SOX2 rep2"},
    {"srx": "SRX1813582",  "biosample_class": "mrc5_reprogramming", "label": "MRC-5 OSKM-induced SOX2 rep1"},
    {"srx": "SRX1813583",  "biosample_class": "mrc5_reprogramming", "label": "MRC-5 OSKM-induced SOX2 rep2"},
    {"srx": "SRX1813584",  "biosample_class": "mrc5_reprogramming", "label": "MRC-5 OSvKM-induced SOX2 rep1"},
    {"srx": "SRX1813585",  "biosample_class": "mrc5_reprogramming", "label": "MRC-5 OSvKM-induced SOX2 rep2"},
    {"srx": "SRX2732210",  "biosample_class": "mrc5_reprogramming", "label": "MRC-5 OSK-induced SOX2 day 5 rep1"},
    {"srx": "SRX2732211",  "biosample_class": "mrc5_reprogramming", "label": "MRC-5 OSvK-induced SOX2 day 5 rep1"},
    # Patient-derived NSCLC (1)
    {"srx": "SRX2731713",  "biosample_class": "cancer_lung_line", "label": "PDCL#24 NSCLC patient-derived"},
    # HCC95 squamous (1, AF2018 antibody — older replicate)
    {"srx": "SRX277137",   "biosample_class": "cancer_lung_line", "label": "HCC95 (lung squamous, AF2018)"},
    # Lung squamous panel (LK-2, NCI-H520, HCC95 v2, KNS-62, HCC2814, LK-2 GFP, LK-2 DNp63)
    {"srx": "SRX6852808",  "biosample_class": "cancer_lung_line", "label": "LK-2 (lung squamous)"},
    {"srx": "SRX6852809",  "biosample_class": "cancer_lung_line", "label": "NCI-H520 (lung squamous)"},
    {"srx": "SRX6852810",  "biosample_class": "cancer_lung_line", "label": "HCC95 (lung squamous, replicate)"},
    {"srx": "SRX6852811",  "biosample_class": "cancer_lung_line", "label": "KNS-62 (NSCLC squamous)"},
    {"srx": "SRX6852812",  "biosample_class": "cancer_lung_line", "label": "HCC2814 (lung squamous)"},
    {"srx": "SRX6852813",  "biosample_class": "cancer_lung_line", "label": "LK-2 GFP-modified"},
    {"srx": "SRX6852814",  "biosample_class": "cancer_lung_line", "label": "LK-2 DNp63-modified"},
]

# 7 hg38 TSS coordinates from Ensembl REST (verified 2026-05-04).
SOX2_TARGETS: dict[str, dict] = {
    "TP63":    {"chrom": "chr3",  "tss": 189631389, "strand": "+",
                "source": "Ensembl ENSG00000073282 (chr3:189631389-189897276 +)"},
    "KRT5":    {"chrom": "chr12", "tss": 52520530,  "strand": "-",
                "source": "Ensembl ENSG00000186081 (chr12:52514575-52520530 -)"},
    "MUC5B":   {"chrom": "chr11", "tss":  1223066,  "strand": "+",
                "source": "Ensembl ENSG00000117983 (chr11:1223066-1262172 +)"},
    "FOXJ1":   {"chrom": "chr17", "tss": 76141245,  "strand": "-",
                "source": "Ensembl ENSG00000129654 (chr17:76136333-76141245 -)"},
    "SCGB1A1": {"chrom": "chr11", "tss": 62405103,  "strand": "+",
                "source": "Ensembl ENSG00000169035 (chr11:62405103-62423195 +)"},
    "NKX2-1":  {"chrom": "chr14", "tss": 36521149,  "strand": "-",
                "source": "Ensembl ENSG00000136352 (chr14:36516392-36521149 -)"},
    "SOX9":    {"chrom": "chr17", "tss": 72121020,  "strand": "+",
                "source": "Ensembl ENSG00000125398 (chr17:72121020-72126416 +)"},
}

OUT_FIELDS = (
    "regulator", "target", "target_locus",
    "n_experiments_total",
    "n_cancer_line", "n_mrc5_reprogramming",
    "n_proximal_cancer", "n_proximal_mrc5",
    "n_nearby_cancer", "n_nearby_mrc5",
    "n_no_local_total",
    "n_download_failed",
    "final_class",
    "justification",
    "evidence_url",
)


def aggregate(per_exp_results: list[dict]) -> dict:
    counts = {
        "proximal_cancer": 0, "proximal_mrc5": 0,
        "nearby_cancer": 0, "nearby_mrc5": 0,
        "no_local": 0, "download_failed": 0,
    }
    for r in per_exp_results:
        cls = r["classification"]
        bs = r["biosample_class"]
        if cls == "download_failed":
            counts["download_failed"] += 1
            continue
        ctx = "cancer" if bs == "cancer_lung_line" else "mrc5"
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
    # peak_validated_in_lung_context unreachable: no primary epithelial
    if counts["proximal_cancer"] > 0:
        # Cancer takes precedence even if MRC-5 also has proximal
        return "peak_validated_in_cancer_lung_context_only"
    if counts["proximal_mrc5"] > 0:
        return "peak_validated_in_lung_reprogramming_context_only"
    if counts["nearby_cancer"] + counts["nearby_mrc5"] > 0:
        return "lung_context_source_only"
    if counts["no_local"] > 0:
        return "no_locus_support"
    return "unresolved_due_to_context_mismatch"


def justify(cls: str, target: str, counts: dict, n_total: int) -> str:
    pc = counts["proximal_cancer"]
    pm = counts["proximal_mrc5"]
    nc = counts["nearby_cancer"]
    nm = counts["nearby_mrc5"]
    nl = counts["no_local"]
    df = counts["download_failed"]
    suffix = (" Cancer-line and MRC-5 reprogramming contexts both reflect "
              "non-physiological SOX2 activity (cancer lineage program / "
              "Yamanaka factor overexpression respectively); neither tests "
              "the developmental claim that SOX2 binds these targets in "
              "primary lung-epithelial progenitors.")
    if cls == "peak_validated_in_cancer_lung_context_only":
        return (f"{pc} of {n_total - df} cancer-line experiment(s) show SOX2 "
                f"peak <= 5 kb of {target} TSS (MRC-5 reprogramming proximal "
                f"hits = {pm}). Cancer-line locus support is real but "
                f"reflects SOX2's role as a lung-squamous lineage oncogene "
                f"(or SCLC subtype driver), not its developmental role." + suffix)
    if cls == "peak_validated_in_lung_reprogramming_context_only":
        return (f"{pm} of 8 MRC-5 reprogramming experiment(s) show SOX2 peak "
                f"<= 5 kb of {target} TSS; zero proximal hits in any cancer "
                f"line. MRC-5 SOX2 binding reflects Yamanaka-factor "
                f"overexpression in fetal lung fibroblasts (mesenchymal, "
                f"not epithelial)." + suffix)
    if cls == "lung_context_source_only":
        return (f"No proximal-promoter SOX2 peaks at {target} TSS in any "
                f"checked experiment. Nearby support: {nc} cancer-line + {nm} "
                f"MRC-5 within 5-50 kb. Distal regulatory binding plausible; "
                f"proximal binding is absent at bed10 in this v0 sweep.")
    if cls == "no_locus_support":
        return (f"All {n_total - df} checked experiments have no SOX2 peaks "
                f"within +/- 50 kb of {target} TSS. Substantive negative "
                f"finding at this threshold within the cancer-line + MRC-5 "
                f"reprogramming substrate available." + suffix)
    return (f"Cannot classify SOX2 -> {target}: {df} of {n_total} downloads "
            f"failed.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="gain-sox2-audit",
        description="First-pass SOX2 locus audit (lung-context experiments only).",
    )
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--sleep", type=float, default=0.3)
    args = parser.parse_args(argv)

    cancer_n = sum(1 for e in SOX2_EXPERIMENTS if e["biosample_class"] == "cancer_lung_line")
    mrc5_n = sum(1 for e in SOX2_EXPERIMENTS if e["biosample_class"] == "mrc5_reprogramming")
    print(f"SOX2 audit: {len(SOX2_EXPERIMENTS)} lung-context experiments x "
          f"{len(SOX2_TARGETS)} targets")
    print(f"  cancer_lung_line:    {cancer_n}")
    print(f"  mrc5_reprogramming:  {mrc5_n}")
    print()
    print(f"Downloading bed10 peak files for {len(SOX2_EXPERIMENTS)} experiments...")

    exp_peaks: dict[str, list | None] = {}
    for i, e in enumerate(SOX2_EXPERIMENTS, 1):
        srx = e["srx"]
        url = chipatlas_bed_url(srx, threshold=10)
        print(f"  [{i:>2}/{len(SOX2_EXPERIMENTS)}] {srx} ({e['biosample_class']:<18} | {e['label']})", end=" ")
        blob = http_get_bytes(url)
        if blob is None:
            exp_peaks[srx] = None
            print("FAILED")
        else:
            peaks = parse_bed(blob)
            exp_peaks[srx] = peaks
            print(f"-> {len(peaks):>6} peaks ({len(blob):,} bytes)")
        if i < len(SOX2_EXPERIMENTS):
            time.sleep(args.sleep)

    out_rows: list[dict] = []
    print(f"\nIntersecting peaks with target loci...")
    for target_name, target in SOX2_TARGETS.items():
        per_exp: list[dict] = []
        for e in SOX2_EXPERIMENTS:
            peaks = exp_peaks.get(e["srx"])
            if peaks is None:
                per_exp.append({"biosample_class": e["biosample_class"],
                                "classification": "download_failed"})
                continue
            d = peak_distance_to_tss(peaks, target)
            # classify_per_experiment from gain_nkx21_audit returns:
            #   'strong' if distance <= 5_000
            #   'nearby' if 5_000 < distance <= 50_000
            #   'no_local' otherwise
            per_exp.append({"biosample_class": e["biosample_class"],
                            "classification": classify_per_experiment(d)})

        counts = aggregate(per_exp)
        n_attempted = len(per_exp) - counts["download_failed"]
        cls = classify(counts, n_attempted)

        out_rows.append({
            "regulator": "SOX2",
            "target": target_name,
            "target_locus": f"{target['chrom']}:{target['tss']} ({target['strand']}) — {target['source']}",
            "n_experiments_total": len(SOX2_EXPERIMENTS),
            "n_cancer_line": cancer_n,
            "n_mrc5_reprogramming": mrc5_n,
            "n_proximal_cancer": counts["proximal_cancer"],
            "n_proximal_mrc5": counts["proximal_mrc5"],
            "n_nearby_cancer": counts["nearby_cancer"],
            "n_nearby_mrc5": counts["nearby_mrc5"],
            "n_no_local_total": counts["no_local"],
            "n_download_failed": counts["download_failed"],
            "final_class": cls,
            "justification": justify(cls, target_name, counts, len(SOX2_EXPERIMENTS)),
            "evidence_url": "https://chip-atlas.dbcls.jp/?factor=SOX2&genome=hg38",
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
        print(f"    SOX2 -> {row['target']:<8} "
              f"prox(c+m)={row['n_proximal_cancer']:>2}+{row['n_proximal_mrc5']:>1} "
              f"near(c+m)={row['n_nearby_cancer']:>2}+{row['n_nearby_mrc5']:>1} "
              f"no_local={row['n_no_local_total']:>2} "
              f"-> {row['final_class']}")

    counts_by_class = {c: 0 for c in CLASSES}
    for r in out_rows:
        counts_by_class[r["final_class"]] = counts_by_class.get(r["final_class"], 0) + 1
    print(f"\n  Class counts:")
    for c in CLASSES:
        print(f"    {c}: {counts_by_class[c]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
