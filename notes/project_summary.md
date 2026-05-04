# Project Summary

**Repo:** [github.com/DD-Ching/Gain](https://github.com/DD-Ching/Gain)
**Status:** v0 cycle complete. Stop point reached after the
quantitative refinement of the indirect-evidence layer.
**Audience:** a researcher new to the project who wants to know what
this repo establishes, what it doesn't, and what would meaningfully
extend it.

## Project goal

Build a small, useful, reality-grounded research-engineering
contribution at the boundary of human lung developmental control
logic and computational genomics. Specifically: audit the
**middle-layer regulatory chain** — NKX2-1 → SOX2 / SOX9 →
FGF10 / WNT / BMP / SHH → airway / alveolar output programs — against
public human data. Make the question "what does the public-data
record actually support?" answerable and reproducible.

The project is **not** a discovery effort. It is an **evidence
audit** with a candidate-finding side product.

## What was built

Eighteen scripts and ~30 metadata / notes files. All stdlib-only;
no Python packages added beyond what ships with `python3`. Every
script is sibling-importable and reuses helpers from earlier audits.

**Foundation (v0 deliverables):**
- [`gain_manifest.py`](../scripts/gain_manifest.py) — curated
  lung-development resource manifest CLI.
- [`gain_verify.py`](../scripts/gain_verify.py) — live URL probe
  for source-list drift.
- [`gain_switch_explorer.py`](../scripts/gain_switch_explorer.py) —
  per-node evidence report joining the regulatory chain to the
  manifest.

**Q3 evidence audit (the project's first real-question artifact):**
- [`gain_evidence_audit.py`](../scripts/gain_evidence_audit.py) —
  ENCODE-only per-pair evidence classification.
- [`gain_evidence_audit_extended.py`](../scripts/gain_evidence_audit_extended.py) —
  cross-resource extension (Cistrome / ReMap surfaced as lookup
  pointers).
- [`gain_evidence_audit_v2.py`](../scripts/gain_evidence_audit_v2.py) —
  ChIP-Atlas integrated as first-class source; six-class evidence
  hierarchy.

**Per-pair locus audits:**
- [`gain_peak_intersection.py`](../scripts/gain_peak_intersection.py) —
  four `direct_human_non_lung_evidence` SMAD1 / GLI2 pairs validated
  at locus level.

**NKX2-1 audit cycle (deepest):**
- [`gain_nkx21_audit.py`](../scripts/gain_nkx21_audit.py) — first-pass
  cancer-context locus audit on 7 canonical targets.
- [`gain_nkx21_audit_sensitivity.py`](../scripts/gain_nkx21_audit_sensitivity.py) —
  bed10 vs bed05 + 4 proximity tiers.
- [`gain_nkx21_distal_candidates.py`](../scripts/gain_nkx21_distal_candidates.py) —
  candidate-locus tiering (strong / moderate / weak / low-priority)
  on the four robustly-failing pairs.
- (NKX2-1 histone-support filter; was a separate script in the
  history.)

**SOX2 / SOX9 audit cycles:**
- [`gain_sox2_audit.py`](../scripts/gain_sox2_audit.py) +
  [`gain_sox2_audit_sensitivity.py`](../scripts/gain_sox2_audit_sensitivity.py)
- [`gain_sox9_audit.py`](../scripts/gain_sox9_audit.py) +
  [`gain_sox9_audit_sensitivity.py`](../scripts/gain_sox9_audit_sensitivity.py)

**Indirect-evidence (motif + accessibility) cycle:**
- [`gain_motif_accessibility_audit.py`](../scripts/gain_motif_accessibility_audit.py)
  — NKX2-1 motif scan against ENCODE lung accessibility (1 ATAC + 14
  DNase, 13 of which are fetal).
- [`gain_sox2_motif_accessibility_audit.py`](../scripts/gain_sox2_motif_accessibility_audit.py)
  — SOX2 motif on the same substrate.
- [`gain_motif_accessibility_control_audit.py`](../scripts/gain_motif_accessibility_control_audit.py)
  — paired control calibration (5 control genes).
- [`gain_motif_accessibility_quant.py`](../scripts/gain_motif_accessibility_quant.py)
  — quantitative refinement on already-collected counts.

## What was learned from NKX2-1

- **No human ENCODE TF ChIP-seq for NKX2-1 exists** in any biosample,
  any species. ChIP-Atlas adds 21 hg38 experiments — **all in lung
  cancer cell lines** (small-cell lung cancer + lung adenocarcinoma:
  NCI-H441, A549, NCI-H3122, etc.). Zero non-cancer / primary / fetal
  NKX2-1 ChIP-seq is publicly deposited as of the audit's external
  search (verified via NCBI E-utilities GEO + SRA).
- **Cancer-line locus support exists but is uneven** across the 7
  canonical targets:
  - SFTPB validates strongly (7 / 21 cancer experiments at bed10).
  - SOX2 and SOX9 validate moderately (3 / 21 each).
  - **SFTPC, SCGB1A1, ABCA3, FOXA2 do NOT have strong proximal-
    promoter NKX2-1 peaks at bed10 in cancer-line ChIP.**
- **Sensitivity sweep** (bed10 + bed05) confirmed:
  - **SFTPC and SCGB1A1 robustly lack proximal binding even at
    bed05** — the most surprising finding, given these are textbook
    NKX2-1 targets.
  - ABCA3 and FOXA2 promote at bed05 (gain 3 and 1 proximal hits
    respectively) — threshold-marginal.
- **Distal-candidate analysis** identified 11 strong + 18 moderate
  candidate loci (50–200 kb of TSS). The histone-support filter
  retained 5 candidates with corroborating H3K27ac + H3K4me1 in
  ENCODE lung tissue:
  - **FOXA2 chr20:22,716,796** — the strongest single candidate
  - FOXA2 chr20:22,390,152
  - SCGB1A1 chr11:62,497,136 and chr11:62,534,332
  - ABCA3 chr16:2,155,403
- **Indirect-evidence layer** (NKX2-1 motif + fetal lung
  accessibility): 4 / 4 of the originally-failing pairs produced
  motif-in-accessible-peak overlaps in fetal lung. **Initially read
  as "rescue of the substrate ceiling."** Subsequent control
  calibration (see "indirect layer" section below) softened this to
  "consistent with both real signal and method permissiveness."

## What was learned from SOX2

- ChIP-Atlas hg38 has 95 SOX2 experiments; **27 are lung-context** —
  but they split into 19 cancer cell lines (lung squamous + small-
  cell lung cancer) + 8 MRC-5 fetal-lung-fibroblast experiments. The
  MRC-5 experiments are **OSKM Yamanaka-factor reprogramming
  contexts** (SOX2 overexpressed for iPSC induction), not endogenous
  epithelial SOX2. **No primary lung-epithelial SOX2 ChIP exists in
  ChIP-Atlas hg38**, parallel to NKX2-1.
- **First-pass locus audit at bed10:** 0 / 7 SOX2 → target pairs
  validate proximally; 3 pairs show only nearby support (FOXJ1,
  NKX2-1, SOX9); 4 pairs have no peaks within 50 kb (TP63, KRT5,
  MUC5B, SCGB1A1).
- **Sensitivity sweep at bed05:** still 0 / 7 proximal validations.
  Only 2 pairs change class (KRT5, SCGB1A1, both gaining nearby
  peaks). Failure is **context-driven, not threshold-driven** — the
  cancer-line + reprogramming substrate does not engage canonical
  airway-program promoters.
- **MUC5B is robustly empty** across all thresholds and all 27
  experiments — strongest negative finding within the SOX2 audit.

## What was learned from SOX9

- ChIP-Atlas hg38 has 27 SOX9 experiments — **zero lung-context.**
  Substrate divides into 20 non-lung cancer cell lines (prostate
  LNCAP / VCaP, breast MCF-7, colon HT-29 / LoVo, pancreas PANC-1,
  lymphoma) + 7 ESC-derived (retinal × 6 + pancreatic × 1).
  Notably, **no skeletal / chondrocyte hg38 SOX9 ChIP** appears in
  the slice despite SOX9's canonical chondrocyte master-regulator
  role.
- **First-pass locus audit at bed10:** 1 / 7 pairs proximal-validate
  (SOX9 → ID2 in non-lung cancer); 2 pairs nearby (AGER, SFTPC); 4
  pairs robustly empty (SFTPB, HOPX, NKX2-1, SOX2).
- **Sensitivity sweep at bed05:** 3 pairs change class. ID2 and
  NKX2-1 both reach `peak_validated_in_non_lung_context_only` at
  bed05 — the **bidirectional cross-context binding** at the
  SOX9 ↔ NKX2-1 proximal-distal axis loci is a genuine finding.
- **All evidence remains non-lung.** ESC-derived context contributes
  zero peaks at any tier in any pair, paralleling MRC-5's
  irrelevance for SOX2.

## Why the regulator-audit chain stopped

After NKX2-1, SOX2, and SOX9 the audit cycle hit a **public-data
substrate ceiling** that the next regulators cannot escape:

| Regulator | hg38 ChIP-Atlas | Lung-context |
|---|---:|---|
| NKX2-1 | 21 | 21 (all cancer LUAD/SCLC) |
| SOX2 | 95 | 27 (cancer + MRC-5 reprogramming) |
| SOX9 | 27 | 0 |
| FGF10 (ligand) | n/a | n/a (not auditable by ChIP) |
| CTNNB1 (β-catenin / WNT) | 78 | 0 |
| SMAD1 (BMP) | 42 | 0 |
| GLI2 (SHH) | 4 | 0 |

The chain's downstream effectors all share SOX9's substrate
constraint or worse. Continuing past SOX9 in the same audit shape
would replicate the pipeline on shrinking and similarly-non-lung
substrates with diminishing returns. The constraint is now the
**public-data ecosystem**, not the audit machinery.

## Why the indirect layer was tested

Direct ChIP evidence in primary lung tissue was the missing piece
across the chain audit. The natural orthogonal question:
**in primary lung accessible chromatin, do TF binding motifs occur
near the canonical target TSSs?** If yes, that is *indirect*
evidence — necessary but not sufficient — that the regulator could
plausibly bind in lung. The substrate (ENCODE 13 fetal lung DNase +
1 fetal-relevant ATAC + 1 adult ATAC + 1 adult DNase) is exactly
the developmental window the chain audit could never reach with
ChIP.

## Why the indirect layer failed at bulk-lung scale

Three structural reasons (documented in
[`notes/motif_accessibility_quant_refinement.md`](motif_accessibility_quant_refinement.md)):

1. **Bulk fetal lung accessibility is too broad.** Each fetal
   experiment generates 60,000–420,000 peaks genome-wide. Almost any
   gene's ± 50 kb window contains hundreds of accessible peaks.
2. **JASPAR motifs at relative_score ≥ 0.85 are degenerate.** A
   7-bp homeodomain (NKX2-1) hits ~ 1 / 400–500 bp of random
   sequence; an 11-bp SOX HMG box (SOX2) is similarly permissive at
   that threshold.
3. **The categorical "any motif in any peak" rule cannot recover
   selectivity.** In a 5-target × 5-control calibration, all 5 SOX2
   canonical targets and all 5 controls cross the positive class.
   Quantitative refinement on the existing per-pair counts (motif
   capture rate, density per accessible peak, cross-donor
   consistency) does not separate them either — three controls
   outrank all canonical SOX2 targets, and one canonical (TP63)
   sits between two blood-specific controls.

The indirect layer **does** discriminate one thing: extremely
tissue-restricted (RBC) genes from "any lung-expressed gene". But
that bar is too low for regulator-target validation. **At v0 settings
the method effectively measures "is this locus accessible in fetal
lung at all?" — which is not regulator-specific.**

The earlier "4 of 4 NKX2-1 indirect rescue" interpretation was an
**overclaim.** Corrected: NKX2-1's 4 failing pairs all return
positive at the categorical tier — but so do housekeeping, blood-
specific, and lung-wrong-program controls. The substrate ceiling
has not been pierced in a discriminating way.

## Standing outputs worth preserving

These are the artefacts a future researcher can pick up directly:

1. **The dataset manifest** —
   [`metadata/sources.json`](../metadata/sources.json) +
   [`metadata/manifest.csv`](../metadata/manifest.csv). 12 curated
   lung-development-relevant resources (CELLxGENE, LungMAP, ENCODE,
   ChIP-Atlas-adjacent links). Live URL drift checked by
   `gain_verify.py`.

2. **The 5 NKX2-1 chromatin-supported standing distal candidates**
   from the histone filter pass:
   - **FOXA2 chr20:22,716,796** (strongest single candidate; 7 NKX2-1
     ChIP support + H3K27ac + H3K4me1 in adult lung tissue)
   - FOXA2 chr20:22,390,152
   - SCGB1A1 chr11:62,497,136 (cancer-line + canonical airway
     histone marks)
   - SCGB1A1 chr11:62,534,332
   - ABCA3 chr16:2,155,403

   These are *candidate* loci — not validated regulatory elements.
   They are the first-pass list to test if/when primary lung
   developmental NKX2-1 ChIP becomes available, or if Hi-C / 4C /
   promoter-capture data is brought into scope.

3. **The audit machinery itself** — five-class evidence model, peak-
   intersection logic, sensitivity sweep, distal-candidate tiering,
   histone-support filter, motif + accessibility scan, quantitative
   refinement. Each component is < 300 LoC of stdlib Python; each is
   reusable per regulator without further design work. **The
   pipelines are mature; they wait on substrate.**

4. **The substrate-gap diagnosis** as a standalone finding. Verified
   programmatically (via `gain_verify.py` + the chain audits + the
   external-source GEO/SRA search): no primary human lung tissue
   ChIP-seq exists for NKX2-1 / SOX2 / SOX9 / CTNNB1 / SMAD1 / GLI2
   in ChIP-Atlas hg38, and an external search confirms the gap is
   real, not a snapshot artefact.

5. **The calibration finding** — bulk-lung motif + accessibility,
   at v0 settings, cannot serve as a discriminating indirect-
   evidence layer for regulator-target validation. This is itself a
   useful negative finding for any future audit attempting the same
   approach.

## Most realistic future directions

Each future direction requires a new substrate or a new method,
not a continuation of the v0 audit cycle. Sized in
[`notes/limitations_and_next_methods.md`](limitations_and_next_methods.md).

The two most realistic near-term pivots:

1. **Cell-type-resolved accessibility.** AT2-cell, basal-cell,
   secretory-cell-specific ATAC / scATAC from human lung tissue
   would replace the bulk-lung confound and likely restore
   selectivity to the motif + accessibility method.
2. **Expression-correlation route via CELLxGENE Census.** Q1 and Q2
   from `notes/unresolved_questions.md` (commitment timing in the
   bipotent SOX2/SOX9 progenitor; continuous gradient vs discrete
   switch) are still real research questions and the substrate
   exists. This is the natural pivot if motif + accessibility is
   off the table.

Less near-term but most decisive: **primary lung tissue / fetal lung
NKX2-1 / SOX2 / SOX9 ChIP-seq deposition.** This is wet-lab
territory — outside the project's current scope — but if it ever
appears in GEO, the standing audit machinery applies immediately.
