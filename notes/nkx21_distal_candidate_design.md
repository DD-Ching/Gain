# NKX2-1 Distal-Candidate Refinement — Design

**Status:** design contract for the candidate-list pass over the 4
NKX2-1 targets that lack proximal-promoter support but show distal-band
peak signal. Implementation must match this document; deviations
require updating it first.

**Why this audit.** The sensitivity audit
([`notes/nkx21_peak_audit_sensitivity.md`](nkx21_peak_audit_sensitivity.md))
showed that **SFTPC, SCGB1A1, ABCA3, FOXA2** — all four pairs that
fail the proximal-promoter test in cancer-line ChIP — have substantial
distal-band (50–200 kb of TSS) peak signal. At bed05 the distal counts
are SFTPC=5, SCGB1A1=9, ABCA3=11, FOXA2=13. **The natural followup is
to convert those raw distal-peak counts into a ranked list of
**candidate** distal regulatory loci**, with explicit caveats about
what "candidate" does and does not mean.

## What this audit *does not* claim

Read this section before reading the rest:

- **Distal peaks are not enhancers.** A peak in a 50–200 kb window
  around a target's TSS is a *candidate* regulatory element; without
  Hi-C / promoter-capture / functional perturbation, we cannot claim
  it acts on the target.
- **No direct regulation is claimed.** The fact that NKX2-1 ChIP-Atlas
  peaks land in the vicinity of these target genes does not establish
  that NKX2-1 regulates them through these elements.
- **Cancer-line ChIP, again.** Every peak comes from one of the 21
  lung cancer cell line ChIP experiments. Even a "strong" distal
  candidate is supported only by cancer-context data; the
  developmental claim remains untested.
- **No new framework.** This audit produces one CSV and one report
  for the four targets. It does not generalise to other regulators or
  build a per-pair candidate-element pipeline.

Anything that reads like an enhancer claim or a regulatory-mechanism
claim should be flagged in review and softened to candidate-level
language.

## What counts as a distal candidate?

A **candidate locus** is a genomic interval within **50–200 kb of the
target's hg38 TSS** that is the result of greedy-merging overlapping
or near-adjacent NKX2-1 ChIP-Atlas peaks across experiments and
thresholds.

Specifically:

1. For each (experiment, threshold), pull all peaks within ± 200 kb of
   the target's TSS. Filter to those whose nearest edge is **between
   50,000 and 200,000 bp** away from the TSS (i.e., outside the
   nearby band, inside the distal cap).
2. Pool peaks from all 21 experiments × 2 thresholds (bed10 and
   bed05) per target. Tag each peak with its `(srx, threshold)`.
3. Sort by genomic start. **Greedy merge** any two consecutive peaks
   on the same chromosome whose end + `MERGE_GAP_BP` (1,000 bp) ≥ the
   next peak's start. The merged locus spans from the leftmost start
   to the rightmost end.
4. Each merged locus is one **candidate**. Its **support set** is the
   set of distinct experiments that contributed at least one peak to
   the locus (across both thresholds).

Loci must overlap the 50–200 kb band on at least one edge to qualify;
candidates that drift into the 5–50 kb nearby band are excluded
(those are nearby support, already counted in the sensitivity audit).

## How are candidate tiers assigned?

Four tiers, in precedence order:

1. **`strong_distal_candidate`** — supported by **≥ 5 distinct
   experiments at bed10** (q < 10⁻¹⁰), **or** ≥ 7 distinct experiments
   at any threshold. The high-confidence threshold count is the
   primary criterion; the broader count covers cases where the high-
   confidence threshold splits a peak across replicates.
2. **`moderate_distal_candidate`** — ≥ 3 distinct experiments at bed10,
   **or** ≥ 5 distinct experiments at any threshold.
3. **`weak_distal_candidate`** — ≥ 2 distinct experiments at any
   threshold.
4. **`low_priority_or_likely_noise`** — supported by exactly 1
   experiment. Almost certainly cell-line- or replicate-specific; not
   worth following up without other evidence.

## How is repeated support across experiments weighted?

- **Distinct experiments**, not distinct peaks. If one experiment has
  multiple peaks in the same merged locus, it counts once.
- **bed10 evidence weighted more heavily.** A locus supported by 5
  experiments at bed10 outranks one supported by 5 experiments at
  bed05-only. The tier rules above encode this asymmetry.
- **Same experiment at both thresholds counts once.** If an experiment
  has a peak at the locus in both bed10 and bed05, it is one supporting
  experiment with high confidence; the tier check uses the bed10
  count first.

## How is "concentrated vs scattered" defined?

For each candidate locus:
- **`concentrated`** — merged locus width < 1 kb. Peaks across
  experiments converge on the same genomic position; high confidence
  this is one regulatory site.
- **`moderately_concentrated`** — width 1–5 kb. Peaks broadly agree
  but with some shift.
- **`scattered`** — width > 5 kb. Peaks span a broad region; may
  represent multiple adjacent sites or noise.

This is a heuristic; v0 does not implement statistical tests for
concentration.

## What would make a candidate strong enough to justify Hi-C /
## perturbation follow-up?

A candidate worth lab follow-up should be **at least
`moderate_distal_candidate`** *and* satisfy at least one of:

- Sits within 50–100 kb of the target TSS (closer = more likely to
  physically contact the promoter).
- `concentrated` support pattern (peaks converge).
- Supported by experiments from > 1 cell line family (i.e., not all
  from the same SRX12008* batch).

These are heuristics, not guarantees. Functional confirmation always
requires Hi-C / 4C / promoter-capture or perturbation. **The audit
flags candidates; it does not prioritise lab work.**

## Inputs

- The 4 target genes (subset of the 7 from `gain_nkx21_audit.py`):
  SFTPC, SCGB1A1, ABCA3, FOXA2.
- The 21 cancer-line NKX2-1 ChIP-Atlas experiments (same as previous
  audits).
- Two thresholds: bed10 and bed05.

## Output

`metadata/nkx21_distal_candidates.csv` — one row per candidate locus.
Schema:

| column | meaning |
|---|---|
| target | one of SFTPC / SCGB1A1 / ABCA3 / FOXA2 |
| target_tss | for cross-reference |
| locus_chrom | chr |
| locus_start | merged-locus start |
| locus_end | merged-locus end |
| locus_midpoint | (start + end) // 2 |
| locus_width_bp | end − start |
| distance_to_tss_bp | signed: + downstream, − upstream of TSS (strand-aware) |
| distance_band | e.g., "50-100kb_upstream" |
| n_experiments_supporting | distinct experiments with at least one peak in the locus |
| n_experiments_at_bed10 | subset supported at bed10 |
| n_experiments_at_bed05 | subset supported at bed05 |
| support_pattern | `concentrated` / `moderately_concentrated` / `scattered` |
| support_concentration_metric | locus_width_bp (the same number, repeated for clarity) |
| supporting_experiment_ids | semicolon-separated SRX list |
| biosample_summary | e.g., "21 cancer_lung_line; 0 noncancer" |
| candidate_tier | one of the 4 tiers |
| justification | short explanation citing tier + counts + caveats |

`notes/nkx21_distal_candidates.md` — the report. Required sections:
- Per-target candidate list with tier counts.
- Cross-target comparison: which target has the strongest distal-
  candidate case?
- The reminder that candidate ≠ confirmed.
- Followup recommendations.

## Implementation outline

Sibling script: `scripts/gain_nkx21_distal_candidates.py`. Reuses the
EXPERIMENTS list and TARGETS dict from `gain_nkx21_audit.py` via
sibling import. For each `(threshold ∈ {5, 10}, experiment)`:

1. Download the bed BED file from ChIP-Atlas (~ 0.4–7.7 MB each).
2. Parse peaks; for each of the 4 distal targets, retain only peaks
   whose nearest edge is 50–200 kb from the TSS.
3. Tag each retained peak with `(srx, threshold)` and target.
4. Per target, pool all retained peaks; sort and greedy-merge.
5. Per merged locus, compute support metrics, assign tier.

Stdlib only. ~ 42 BED downloads, ~ 60 MB total transfer, ~ 60–90 s
runtime expected.

## Anti-overclaim rules carried forward

- "Candidate" means candidate. No language like "regulates",
  "controls", "is an enhancer for", "drives expression of" appears
  in the report.
- The cancer-line caveat is repeated in every justification line that
  cites support counts.
- The `strong_distal_candidate` tier is the strongest claim available
  in this audit, and even it is described as "warrants Hi-C /
  perturbation followup", not "is a regulatory element."

## Out of scope

- Hi-C / promoter-capture / chromatin-contact data integration. Future
  work; the audit explicitly notes which candidates would benefit
  most.
- Histone-mark co-localisation. ENCODE has 59 lung histone ChIP
  experiments; cross-referencing them against our candidate loci is a
  natural followup but lives outside this audit's scope.
- Motif scanning for NKX2-1 binding motif under each peak. Would
  require JASPAR PWM + scanning code.
- Other regulators or other targets. Strict NKX2-1 + 4 targets.
