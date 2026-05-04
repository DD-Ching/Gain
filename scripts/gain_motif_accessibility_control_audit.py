#!/usr/bin/env python3
"""gain motif-accessibility-control-audit - paired control calibration.

Runs the SOX2 motif against a 5-gene control panel (3 housekeeping + 2
blood-specific + 1 lung-but-wrong-program) to estimate the false-
positive rate of the indirect-evidence layer. Compared against the
SOX2 canonical-target audit to determine whether the method is
selective enough to use across the regulator chain.

Sibling-imports the shared run_motif_accessibility_audit pipeline.
Stdlib only. Per notes/sox2_motif_accessibility_design.md.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from gain_motif_accessibility_audit import (  # noqa: E402
    MOTIF_RELATIVE_SCORE_THRESHOLD,
    run_motif_accessibility_audit,
)
from gain_sox2_motif_accessibility_audit import SOX2_MOTIF_ID  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = REPO_ROOT / "metadata" / "motif_accessibility_control_audit.csv"

# 5 control genes — none are canonical SOX2 lung-developmental targets.
# Mix of housekeeping (broadly accessible), blood-specific (wrong tissue),
# and lung-but-wrong-program (lung accessible, alveolar not airway).
# hg38 TSS verified via Ensembl REST 2026-05-04.
CONTROL_TARGETS: dict[str, dict] = {
    "GAPDH":  {"chrom": "chr12", "tss":   6534012, "strand": "+",
               "source": "Ensembl ENSG00000111640 (housekeeping; ubiquitously expressed)"},
    "ACTB":   {"chrom": "chr7",  "tss":   5563902, "strand": "-",
               "source": "Ensembl ENSG00000075624 (housekeeping; ubiquitously expressed)"},
    "HBA1":   {"chrom": "chr16", "tss":    176680, "strand": "+",
               "source": "Ensembl ENSG00000206172 (blood-specific; erythrocyte hemoglobin alpha)"},
    "HBB":    {"chrom": "chr11", "tss":   5229395, "strand": "-",
               "source": "Ensembl ENSG00000244734 (blood-specific; erythrocyte hemoglobin beta)"},
    "SFTPC":  {"chrom": "chr8",  "tss":  22156913, "strand": "+",
               "source": "Ensembl ENSG00000168484 (lung but distal/alveolar; NOT a SOX2 airway target)"},
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="gain-motif-accessibility-control-audit",
        description="Control calibration: SOX2 motif vs 5 non-SOX2-target genes.",
    )
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--sleep", type=float, default=0.3)
    parser.add_argument("--threshold", type=float,
                        default=MOTIF_RELATIVE_SCORE_THRESHOLD)
    args = parser.parse_args(argv)
    return run_motif_accessibility_audit(
        regulator="SOX2_control",
        motif_id=SOX2_MOTIF_ID,
        targets=CONTROL_TARGETS,
        out_path=args.out,
        sleep=args.sleep,
        threshold=args.threshold,
    )


if __name__ == "__main__":
    sys.exit(main())
