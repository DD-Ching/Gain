# SOX2 Motif + Accessibility Audit — Results

**Run:** 2026-05-04 (UTC)
**Inputs:** JASPAR MA0143.5 (SOX2 11-bp PFM) + 15 ENCODE human lung
accessibility experiments (13 fetal DNase + 1 adult DNase + 1 adult
ATAC) × 5 SOX2 canonical proximal/airway program targets.
**Output:** [`metadata/sox2_motif_accessibility_audit.csv`](../metadata/sox2_motif_accessibility_audit.csv)
**Script:** [`scripts/gain_sox2_motif_accessibility_audit.py`](../scripts/gain_sox2_motif_accessibility_audit.py)
**Companion audit (read this together):** [`notes/motif_accessibility_control_audit.md`](motif_accessibility_control_audit.md)

## Per-pair results

| Pair | motif hits | lung peaks (fetal/adult) | motif_in_fetal | supporting fetal expts | Class |
|---|---:|---:|---:|---:|---|
| SOX2 → SCGB1A1 | 337 | 180 (168/12) | **53** | **13/13** | `indirect_accessibility_support_in_fetal_lung_tissue` |
| SOX2 → FOXJ1 | 291 | 141 (131/10) | 40 | 13/13 | `indirect_accessibility_support_in_fetal_lung_tissue` |
| SOX2 → MUC5B | 221 | 149 (145/4)  | 38 | 10/13 | `indirect_accessibility_support_in_fetal_lung_tissue` |
| SOX2 → KRT5 | 390 | 73 (51/22)   | 24 | 11/13 | `indirect_accessibility_support_in_fetal_lung_tissue` |
| SOX2 → TP63 | 473 | 32 (31/1)    | 14 | 5/13  | `indirect_accessibility_support_in_fetal_lung_tissue` |

Class distribution:

| Class | Count |
|---|---:|
| `indirect_accessibility_support_in_fetal_lung_tissue` | **5 / 5** |
| All other classes | 0 |

## Headline

**5 of 5 SOX2 canonical airway-program targets gain
`indirect_accessibility_support_in_fetal_lung_tissue`.** TP63, KRT5,
MUC5B, FOXJ1, and SCGB1A1 all show SOX2 motif occurrences within
accessible chromatin in fetal lung tissue, in 5–13 of 13 independent
fetal donor experiments.

If this were the *only* result, it would be a strong rescue parallel
to NKX2-1's 4-of-4. **But the paired control audit on 5 non-SOX2-
target genes also returns 5 of 5 positive at the same tier** — see
[`notes/motif_accessibility_control_audit.md`](motif_accessibility_control_audit.md).
**The method is too permissive at the categorical level to distinguish
SOX2's canonical targets from non-targets.** This SOX2 result must be
read in light of that calibration finding.

## Per-target detail (within the SOX2 audit alone)

- **TP63** has the lowest fetal-experiment support (5 / 13) and
  the fewest motif-in-fetal-peak overlaps (14). Its lung-peak
  coverage in the ± 50 kb window is also the lowest (32) — TP63's
  TSS region simply has less accessible chromatin in fetal lung,
  consistent with TP63 being expressed in a subset of basal cells
  rather than ubiquitously.
- **KRT5** has 24 overlaps in 11 of 13 fetal experiments. Stronger
  than TP63 but moderate.
- **MUC5B** has 38 overlaps in 10 of 13 — comparable density to
  KRT5 but in a more accessible window.
- **FOXJ1** and **SCGB1A1** are tied at 13 / 13 supporting fetal
  experiments. SCGB1A1 has the most overlaps (53), FOXJ1 has 40.
  Both show consensus across all fetal donors.

Within the SOX2 audit, there is some quantitative variation — TP63
is the weakest, SCGB1A1 the strongest. But the categorical answer
is uniform: all 5 cross.

## What this audit does *not* establish

- That SOX2 binds TP63 / KRT5 / MUC5B / FOXJ1 / SCGB1A1 in primary
  lung tissue.
- That the indirect-evidence layer is *selective* — see the
  control audit; at this threshold and substrate it is not.
- That SOX2's developmental binding is supported by public data —
  the same caveat as NKX2-1 (no primary-tissue SOX2 ChIP exists in
  ChIP-Atlas hg38).
- That a 5-of-5 result is meaningfully different from a control
  5-of-5. **It is not, at the categorical level.**

## Quantitative-signal observations (foreshadowing the calibration)

The absolute counts of motif-in-fetal-peak overlaps span an order
of magnitude across the 5 SOX2 targets (14 to 53). This range:

| Pair | overlaps |
|---|---:|
| TP63 | 14 |
| KRT5 | 24 |
| MUC5B | 38 |
| FOXJ1 | 40 |
| SCGB1A1 | 53 |

is **not** systematically separable from the control panel's range —
where housekeeping controls (GAPDH 66, ACTB 157) score *higher* than
any SOX2 target, and the lung-wrong-program control (SFTPC 48) sits
in the middle of the SOX2 range. See the calibration note for the
full comparison.

A v1 quantitative refinement (motif density per accessible peak,
normalized to gene-window accessibility coverage) might recover some
selectivity, but is out of scope for this first-pass audit.

## Reproducing this audit

```sh
python3 scripts/gain_sox2_motif_accessibility_audit.py
```

Stdlib only. ~ 35 HTTP requests, ~ 1.5 minutes runtime. Sibling-imports
the `run_motif_accessibility_audit` pipeline from
`gain_motif_accessibility_audit.py`; the only differences vs the
NKX2-1 audit are the motif ID (MA0143.5 vs MA1994.2) and the target
list (5 vs 4). JASPAR PFM cached after first run.
