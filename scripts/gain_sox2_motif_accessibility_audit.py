#!/usr/bin/env python3
"""gain sox2-motif-accessibility-audit - SOX2 indirect-evidence audit
on the 5 canonical proximal/airway program targets.

Mirrors the NKX2-1 motif+accessibility audit; sibling-imports the
shared run_motif_accessibility_audit pipeline and only specifies the
SOX2 motif ID + target list.

Stdlib only. Per notes/sox2_motif_accessibility_design.md.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Sibling import of the reusable pipeline + helpers
sys.path.insert(0, str(Path(__file__).parent))
from gain_motif_accessibility_audit import (  # noqa: E402
    MOTIF_RELATIVE_SCORE_THRESHOLD,
    run_motif_accessibility_audit,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = REPO_ROOT / "metadata" / "sox2_motif_accessibility_audit.csv"

# JASPAR MA0143.5 = current SOX2 motif (11-bp SOX HMG box, consensus around CATTGT)
SOX2_MOTIF_ID = "MA0143.5"

# 5 SOX2 canonical proximal/airway program targets per the design.
# Within-chain pairs (NKX2-1, SOX9) are deliberately excluded -- this audit
# is about the airway program, not reciprocal regulation.
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
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="gain-sox2-motif-accessibility-audit",
        description="SOX2 motif + lung accessibility indirect-evidence audit.",
    )
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--sleep", type=float, default=0.3)
    parser.add_argument("--threshold", type=float,
                        default=MOTIF_RELATIVE_SCORE_THRESHOLD)
    args = parser.parse_args(argv)
    return run_motif_accessibility_audit(
        regulator="SOX2",
        motif_id=SOX2_MOTIF_ID,
        targets=SOX2_TARGETS,
        out_path=args.out,
        sleep=args.sleep,
        threshold=args.threshold,
    )


if __name__ == "__main__":
    sys.exit(main())
