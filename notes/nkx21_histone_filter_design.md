# NKX2-1 Histone-Support Filter — Design

**Status:** design contract for the histone-support filtering pass over
the 11 strong NKX2-1 distal candidates. Implementation must match this
document; deviations require updating it first.

**Why this audit.** The previous distal-candidate pass
([`notes/nkx21_distal_candidates.md`](nkx21_distal_candidates.md))
identified 11 strong NKX2-1 distal candidate loci (50–200 kb of TSS,
≥ 5 cancer-line bed10 supports). All 11 are supported entirely by
**cancer-line** ChIP. **The natural next filter is to ask which of those
loci sit in *active regulatory chromatin* in primary lung tissue**, using
ENCODE's lung tissue Histone ChIP-seq experiments — most of which are
primary fetal or adult tissue, **not** cancer cell lines.

Pre-implementation probe of ENCODE: 59 lung Histone ChIP experiments
total. Biosample distribution (crude keyword classifier):

| Category | n |
|---|---:|
| mouse_lung | 34 |
| human_fetal_lung | 13 |
| human_adult_lung_tissue | 12 |
| cancer_lung_line | 0 |

Histone-mark distribution:

| Mark | n | Class |
|---|---:|---|
| H3K4me1 | 10 | active enhancer |
| H3K4me3 | 9 | active promoter |
| H3K9me3 | 8 | repressive (heterochromatin) |
| H3K36me3 | 8 | gene body / transcribed |
| H3K27me3 | 8 | repressive (Polycomb) |
| H3K27ac | 6 | active enhancer/promoter |
| H3K9ac | 6 | active |
| H3K4me2 | 4 | active |

This is a strong substrate: **25 human lung tissue (fetal + adult)
histone ChIP experiments**, including both active and repressive
marks, with zero cancer-line contamination. **The histone evidence is
in a distinct biological context from the NKX2-1 ChIP** — exactly
what the user asked for ("keep cancer-context and tissue-context
separate").

## Scope

- **Input:** the 11 `strong_distal_candidate` loci from
  `metadata/nkx21_distal_candidates.csv`, no others.
- **Histone source:** ENCODE lung tissue Histone ChIP-seq, hg38 only.
  Mouse experiments (34 of 59) are recorded for context but **not used
  for overlap testing** — their peaks are mm10 and we deliberately do
  not implement lift-over in v0.
- **Active-mark filter:** experiments whose `target.label` is in
  `{H3K27ac, H3K4me1, H3K4me3, H3K9ac, H3K4me2}`. Repressive marks
  (`H3K27me3`, `H3K9me3`) are tracked separately because their
  presence at a locus *weakens* the regulatory hypothesis.
  H3K36me3 (gene body) is informational only.
- **Window:** the candidate locus itself (`locus_start` → `locus_end`).
  A histone peak is considered to "overlap" if any portion of its
  interval intersects the locus interval — i.e. `peak_end >=
  locus_start AND peak_start <= locus_end`.

## Updated tier system (per user's specification)

Each of the 11 strong candidates is reclassified into one of:

1. **`strong_distal_candidate_with_chromatin_support`** — at least one
   **active-mark** histone peak in **human lung tissue** (fetal or
   adult) overlaps the candidate locus. The strongest tier reachable
   in v0 of the histone filter.
2. **`strong_distal_candidate_without_chromatin_support`** — human
   lung tissue active-mark histone ChIP exists for the candidate's
   chromosome and could have produced an overlapping peak, but **no
   active-mark peak overlaps** the candidate locus. The locus appears
   inactive in primary lung tissue.
3. **`downgraded_candidate`** — chromatin support exists *only* in
   cancer-context histone ChIP (in v0, this tier is structurally
   unreachable because ENCODE has no cancer-line lung histone
   experiments) **or** the overlapping evidence is exclusively
   *repressive* marks (H3K27me3 / H3K9me3) in primary tissue,
   suggesting the locus is silent rather than active.
4. **`unresolved_due_to_context_mismatch`** — overlap exists only in
   mouse lung histone ChIP, or the active/repressive signal is
   ambiguous (e.g., one active mark in fetal but a repressive mark in
   adult), or histone download failed for the relevant chromosome.

Precedence: assigned in the order above. The **first applicable**
tier wins.

## Cancer vs tissue separation rules

- ENCODE lung histone ChIP biosamples are classified at audit time
  using the experiment metadata:
  - `replicates.library.biosample.donor.organism.scientific_name`
    → `Homo sapiens` / `Mus musculus`
  - `biosample_ontology.classification` → `tissue` / `cell line` / ...
  - presence of "fetal" / "embryo" in `biosample_summary` →
    `human_fetal_lung`
  - human + tissue + no fetal keyword → `human_adult_lung_tissue`
  - human + cell line → `cancer_lung_line` (predicted zero in v0)
  - mouse → `mouse_lung`
- **Only `human_fetal_lung` and `human_adult_lung_tissue` count as
  "lung tissue" support** in tier 1. Cancer-line histone (if any
  exists in a future ENCODE refresh) would feed tier 3
  (`downgraded_candidate`) — never tier 1.
- The CSV records the per-mark, per-biosample-category overlap
  separately so the cancer / tissue / mouse distinction is preserved
  at row level.

## What this audit does *not* claim

- **Active histone marks ≠ enhancer function.** H3K27ac / H3K4me1
  overlap makes a locus a *more credible* candidate; it does not
  confirm regulatory action on the target gene.
- **No developmental-validity claim.** Even with fetal-lung histone
  support, the audit cannot claim NKX2-1 *binds* the locus during
  development — the binding evidence is still cancer-line ChIP.
  What it can claim is that the locus *appears active* in fetal lung
  tissue, raising the prior that the cancer-line NKX2-1 binding is
  also a real regulatory event in development. **Raising the prior is
  not confirmation.**
- **No conclusion that "without chromatin support" means the
  candidate is wrong.** A locus might be inactive in adult / fetal
  lung but active in the specific subset of cells (e.g., AT2 cells)
  that NKX2-1 functions in; bulk lung histone ChIP averages across
  cell types and may dilute cell-type-specific signals.
- **Repressive-mark overlap is a *flag*, not a refutation.** Polycomb
  silencing is dynamic during development; a locus that is H3K27me3
  in adult lung might be active during fetal lung development.

## What would make a candidate worth lab follow-up after this filter

A candidate that gains tier 1 (`with_chromatin_support`) is
strictly more interesting than the same candidate before this audit.
But the audit does **not** prioritise lab work; that decision rests
with whoever is investing the time. A reasonable rule of thumb:

- Tier 1 + within 50–100 kb of TSS + concentrated support pattern +
  H3K27ac AND H3K4me1 overlap → strongest case for Hi-C / promoter-
  capture follow-up.
- Tier 1 + only H3K4me3 (promoter mark) → may indicate the candidate
  is itself a promoter for a different gene; check before lab work.

These are heuristics, not guarantees.

## Inputs

1. `metadata/nkx21_distal_candidates.csv` — filter to
   `candidate_tier == "strong_distal_candidate"`.
2. ENCODE Histone ChIP-seq REST API:
   `type=Experiment&assay_title=Histone+ChIP-seq&biosample_ontology.term_name=lung`.
3. For each kept experiment: per-experiment `?format=json` to get
   the BED peak file URLs (matches `gain_peak_intersection.py` shape).

## Output

`metadata/nkx21_histone_filtered_candidates.csv` — one row per
(candidate locus, audited histone mark/biosample combination it was
tested against, OR a rolled-up summary). For v0, schema is **one row
per candidate locus** with overlap counts split by mark + biosample
category. Columns:

| column | meaning |
|---|---|
| target | gene symbol |
| candidate_locus | `chr:start-end` |
| distance_to_tss_bp | from previous audit |
| supporting_nkx21_experiments | distinct SRX list from previous audit |
| n_overlap_h3k27ac_fetal | active-mark fetal lung overlaps |
| n_overlap_h3k27ac_adult | active-mark adult lung overlaps |
| n_overlap_h3k4me1_fetal | |
| n_overlap_h3k4me1_adult | |
| n_overlap_h3k4me3_fetal | |
| n_overlap_h3k4me3_adult | |
| n_overlap_repressive_fetal | H3K27me3 + H3K9me3 in fetal |
| n_overlap_repressive_adult | H3K27me3 + H3K9me3 in adult |
| n_overlap_mouse_active | mouse active-mark overlaps (recorded but not used for tiering) |
| histone_evidence_summary | short text |
| histone_source_context | `human_fetal_lung` / `human_adult_lung_tissue` / `mouse_lung` / `none` |
| updated_tier | one of the four classes above |
| justification | short text |

`notes/nkx21_histone_filtered_candidates.md` — the report. Required
sections:
- Per-target updated tier counts.
- Per-candidate detail: which marks overlap, in which biosample.
- The four user-stated questions, answered:
  - How many of the 11 gain lung-relevant chromatin support?
  - Does ABCA3 still remain the strongest follow-up target?
  - Does any FOXA2 or SCGB1A1 candidate become equally strong?
  - Does NKX2-1 deserve one final focused pass after histone filtering?

## Implementation outline

Sibling script: `scripts/gain_nkx21_histone_filter.py`. Reuses the
EXPERIMENTS / TARGETS dict from `gain_nkx21_audit.py` only for
biosample classification (we don't actually need the NKX2-1 ChIP data
in this script — we need the precomputed strong candidates from the
CSV).

1. Read `metadata/nkx21_distal_candidates.csv`, filter to strong tier
   (11 rows expected).
2. Query ENCODE lung Histone ChIP experiments (a single search call;
   59 experiments). For each:
   - Classify biosample (human_fetal / human_adult / mouse / cancer / unclear).
   - Classify mark (active / repressive / gene-body / other).
   - Drop mouse and gene-body experiments from the overlap test
     pool; keep them for context recording.
3. For each kept experiment, fetch the experiment's full metadata
   and pick the best representative BED file (preference order
   matches `gain_peak_intersection.py`).
4. Download BEDs (~ 25 files, ~ 30 MB total).
5. For each `(candidate, experiment)` pair on the same chromosome,
   compute overlap; record per (mark, biosample_category) totals.
6. Apply tier rules; write CSV + Markdown report.

Stdlib only.

## Anti-overclaim rules carried forward

- **Cancer-context binding + tissue-context chromatin** is *consistent
  with* a real regulatory element but does not prove one. The audit's
  output describes the consistency, not the proof.
- Every justification line for tier 1 must explicitly state that the
  result raises the prior on a regulatory candidate without
  establishing function or confirming developmental binding.
- Tier 2 / tier 3 must explicitly state what is *not* claimed:
  inactivity in bulk lung tissue is not equivalent to non-regulatory
  status in cell-type-specific contexts.
