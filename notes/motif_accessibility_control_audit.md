# Motif + Accessibility Control Audit — Calibration Result

**Run:** 2026-05-04 (UTC)
**Inputs:** JASPAR MA0143.5 (SOX2 11-bp PFM) + 15 ENCODE human lung
accessibility experiments × 5 control genes (3 housekeeping + 2
blood-specific + 1 lung-wrong-program).
**Output:** [`metadata/motif_accessibility_control_audit.csv`](../metadata/motif_accessibility_control_audit.csv)
**Script:** [`scripts/gain_motif_accessibility_control_audit.py`](../scripts/gain_motif_accessibility_control_audit.py)
**Companion audits:**
- [`notes/sox2_motif_accessibility_audit.md`](sox2_motif_accessibility_audit.md) (SOX2 5 canonical targets)
- [`notes/nkx21_motif_accessibility_audit.md`](nkx21_motif_accessibility_audit.md) (NKX2-1 4 canonical targets)

## Per-control results

| Control | Class | motif hits | lung peaks (fetal/adult) | motif_in_fetal | supporting fetal expts |
|---|---|---:|---:|---:|---:|
| **GAPDH** (housekeeping) | `indirect_accessibility_support_in_fetal_lung_tissue` | 313 | 198 (172/26) | **66** | 12/13 |
| **ACTB** (housekeeping) | `indirect_accessibility_support_in_fetal_lung_tissue` | 207 | 364 (311/53) | **157** | 12/13 |
| **HBA1** (blood, RBC) | `indirect_accessibility_support_in_fetal_lung_tissue` | 280 | 83 (75/8) | **5** | 3/13 |
| **HBB** (blood, RBC) | `indirect_accessibility_support_in_fetal_lung_tissue` | 475 | 42 (42/0) | 15 | 6/13 |
| **SFTPC** (lung but distal/alveolar; not SOX2 program) | `indirect_accessibility_support_in_fetal_lung_tissue` | 228 | 166 (133/33) | 48 | 13/13 |

Class distribution:

| Class | Count |
|---|---:|
| `indirect_accessibility_support_in_fetal_lung_tissue` | **5 / 5** |
| All other classes | 0 |

## Headline verdict

**The control panel returns 5 of 5 positives at the same tier as the
SOX2 canonical targets.** Per the decision matrix in
[`notes/sox2_motif_accessibility_design.md`](sox2_motif_accessibility_design.md):

> **targets ≥ 4 / 5 + controls 5 / 5 → method is too permissive. Re-interpret
> the NKX2-1 4-of-4 and SOX2 5-of-5 results as not selective; the
> method finds positives everywhere. Stop and pivot.**

The categorical tier
`indirect_accessibility_support_in_fetal_lung_tissue` does not
distinguish canonical SOX2 targets from housekeeping genes,
blood-specific genes, or lung-wrong-program genes.

## Side-by-side: SOX2 targets vs controls (motif-in-fetal-peak counts)

| Gene | Class | motif_in_fetal | category |
|---|---|---:|---|
| **ACTB** (control) | housekeeping | **157** | highest |
| GAPDH (control) | housekeeping | 66 | high |
| SOX2 → SCGB1A1 | canonical SOX2 | 53 | medium-high |
| **SFTPC** (control) | lung wrong-program | 48 | medium-high |
| SOX2 → FOXJ1 | canonical SOX2 | 40 | medium |
| SOX2 → MUC5B | canonical SOX2 | 38 | medium |
| SOX2 → KRT5 | canonical SOX2 | 24 | low-medium |
| HBB (control) | blood-specific | 15 | low |
| SOX2 → TP63 | canonical SOX2 | 14 | low |
| **HBA1** (control) | blood-specific | **5** | lowest |

**The canonical SOX2 targets cluster with controls, not above them.**
TP63 (canonical) is right next to HBB (blood control); SCGB1A1
(canonical) is right next to SFTPC (lung wrong-program); housekeeping
controls dominate the high end. Only HBA1 (one of two blood-specific
controls) clearly stands apart at the very bottom.

## What the method *does* discriminate

The two RBC-restricted blood genes — HBA1 and HBB — sit at or near
the bottom of the count distribution (5 and 15 motif-in-fetal-peak
overlaps respectively). HBA1 in particular has only 3 of 13 fetal
experiments supporting it.

This is **the only meaningful discrimination** the method achieves
in this calibration: extremely tissue-restricted (RBC) genes can
plausibly be told apart from "any expressed gene in fetal lung". But
that bar is so low it does not discriminate between the canonical
SOX2 program and any other gene that is plausibly expressed in fetal
lung (housekeeping, alveolar SFTPC, or canonical airway markers).

## Why this happened (likely root causes)

1. **Motif degeneracy at the chosen threshold.** SOX2's MA0143.5 is
   an 11-bp PFM at relative_score ≥ 0.85 — a permissive cutoff that
   yields hundreds of hits per 100-kb window even in random sequence.
   NKX2-1's MA1994.2 (7-bp) at the same threshold has the same problem.
2. **Bulk-tissue accessibility is broad.** Each fetal lung DNase
   experiment generates 60,000–420,000 peaks genome-wide. Any gene's
   ± 50 kb window will contain dozens to hundreds of accessible
   peaks; the union across 13 fetal experiments is wider still.
3. **The categorical "any motif in any peak" rule is too coarse.**
   With dozens of motif occurrences and dozens of accessible peaks
   per window, the chance of *no* overlap is small for any expressed
   gene.

## Implication for the NKX2-1 audit's headline

The previous turn's NKX2-1 audit reported "4 of 4 NKX2-1 canonical
pairs gain `indirect_accessibility_support_in_fetal_lung_tissue`" as
a "rescue of the substrate ceiling". **That interpretation must be
softened.** The 4-of-4 result is consistent with both:

- **(a) a true rescue** — NKX2-1 motifs really do mark plausible
  binding sites in fetal lung accessible chromatin at the four
  target loci.
- **(b) a method-permissiveness artefact** — *any* lung-expressed
  gene's ± 50 kb window will return positive at this threshold.

The control calibration shows that **(b) is at least partly
operating**, and we cannot currently distinguish (a) from (b) without
further refinement.

The corrected reading of the NKX2-1 result:

> *"All 4 NKX2-1 canonical targets contain NKX2-1 motif occurrences
> within fetal lung accessible chromatin — but so do all 5 SOX2
> canonical targets, all 3 housekeeping controls, all 2 blood-
> specific controls, and a lung-wrong-program control. At the
> categorical level, the indirect-evidence method does not select
> targets above the background of any expressed gene. The substrate
> ceiling has *not* been pierced in a discriminating way."*

The chain audit's underlying finding (no primary-tissue NKX2-1 / SOX2
ChIP exists; the textbook claims rest on substrate the audit cannot
match) stands unchanged. The indirect-evidence layer is real but
non-discriminating at v0 settings.

## What this audit does *not* claim

- That NKX2-1 / SOX2 do not bind their canonical targets.
- That the textbook claims are wrong.
- That motif + accessibility cannot be made informative — only that
  *the v0 categorical version is not*.

## The five user-stated questions, answered

### 1. How many SOX2 targets gain `indirect_accessibility_support_in_fetal_lung_tissue`?

**5 of 5** (TP63, KRT5, MUC5B, FOXJ1, SCGB1A1).

### 2. Do TP63 and KRT5 become positive at the indirect layer?

**Yes** — TP63 with 14 motif-in-fetal-peak overlaps in 5 supporting
experiments; KRT5 with 24 in 11 supporting. Both cross the
categorical positive threshold. **But they sit alongside HBB
(blood control, 15 overlaps) and below SFTPC (lung wrong-program
control, 48 overlaps) in the count distribution** — so "positive"
is not equivalent to "supported above background".

### 3. How does the positive rate in SOX2 targets compare to the control set?

**Identical: 5 / 5 = 5 / 5.** The selectivity ratio is 1.0 at the
categorical level. Quantitatively, SOX2 targets span 14–53 motif-in-
fetal-peak overlaps; controls span 5 (HBA1) to 157 (ACTB). The
canonical-target range is *fully contained within* the control range.

### 4. Does the method still look selective enough to justify continuing the chain?

**No, not in its current form.** With targets and controls both at
5/5 positive and the count distributions overlapping, the v0
categorical method cannot serve as an indirect-evidence layer that
distinguishes SOX2 program-specific binding from baseline. The chain
audit cannot continue using this method as-is.

### 5. After this pass, should the next step be:
- SOX2 distal-locus refinement
- NKX2-1 distal-locus refinement
- stop and summarize
- or pivot methods again

**Pivot methods.** Two concrete refinement directions, in order of
expected payoff:

1. **Quantitative refinement of the same method** — replace the
   categorical "any motif in any peak" classifier with a
   *normalised density* metric (motif occurrences per accessible
   bp, relative to a gene-window-accessibility expectation, or
   compared to a per-gene shuffled-motif null distribution). This
   would convert the existing pipeline from binary to continuous,
   and might rescue selectivity if blood-specific HBA1 (the lowest)
   is consistently below canonical targets in normalised terms.
   ~ 100 LoC of additions to the existing script. **First test on
   the same 5 + 5 pairs already run.**
2. **Stricter motif threshold or different motif model** — try
   relative_score ≥ 0.95, or use multiple JASPAR PFMs per regulator
   (e.g., MA1994.2 + MA1994.1 for NKX2-1 with consensus-only hits).
   This addresses the degeneracy issue but might still be too
   permissive given the broad accessibility substrate.

A third less-promising option:

3. **Stop and summarize.** The chain audit's findings are
   publishable as-is, and the indirect-evidence layer's failure to
   discriminate is itself a finding worth documenting. But the
   quantitative-refinement option (1) is cheap enough that one
   more focused pass before handoff is warranted.

**Recommended next move: option (1).** Run the same 10 pairs (5 SOX2
canonical + 5 controls) with a normalised density metric on the
existing per-pair counts (already in the CSVs — no new HTTP
required). Decision rule: if HBA1 / HBB drop substantially below
the canonical-SOX2 range under normalisation, the quantitative
method has selective signal worth pursuing. Otherwise, stop and
summarize.

## Reproducing this audit

```sh
python3 scripts/gain_motif_accessibility_control_audit.py
```

Stdlib only. ~ 35 HTTP requests, ~ 1.5 minutes runtime.
