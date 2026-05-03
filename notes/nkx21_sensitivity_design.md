# NKX2-1 Sensitivity Audit — Design

**Status:** design contract for the robustness check on the previous
NKX2-1 locus audit. Implementation must match this document; deviations
require updating it first.

**Why this audit.** The previous audit
([`notes/nkx21_peak_audit.md`](nkx21_peak_audit.md)) found that 4 of 7
canonical NKX2-1 → target pairs (SFTPC, SCGB1A1, ABCA3, FOXA2) had
zero peaks within ± 5 kb of the target TSS at bed10 (q < 10⁻¹⁰)
across 21 cancer-line ChIP experiments. **That is a sharp finding,
but the v0 setup makes two assumptions that have not been tested:**

1. **bed10 (q < 10⁻¹⁰) is the right threshold.** ChIP-Atlas also
   publishes bed05 (q < 10⁻⁵). At bed05 some moderate-strength peaks
   that the bed10 threshold filters out would surface.
2. **Proximal promoter (≤ 5 kb of TSS) is the right window.** Many
   developmental TF regulatory elements sit at 50–200 kb from the TSS
   (distal enhancers); a strict promoter-proximal cutoff misses them.

Before making any biological claim — especially anything that looks
like "the textbook is wrong" — the result needs to survive both a
threshold relaxation and a distal-window expansion. **This audit is a
robustness check, not a refutation pass.**

## What we are explicitly *not* doing

- Not switching regulators (per the user's "do not broaden the project").
- Not adding non-cancer experiments (none exist for NKX2-1 in
  ChIP-Atlas hg38).
- Not making strong anti-textbook claims regardless of the result.
- Not promoting any pair to `peak_validated_in_lung_context` — that
  class still requires non-cancer experiments which still do not
  exist; the cancer-context restriction holds.
- Not changing the underlying scope (NKX2-1 + 7 targets).

## Comparisons to run

### A. Threshold sweep

Same 21 NKX2-1 hg38 cancer-line ChIP experiments. Re-run at:

- **bed10** — q < 10⁻¹⁰ (the v0 threshold; output already produced)
- **bed05** — q < 10⁻⁵ (more permissive)

Skip bed20 (more stringent than bed10; not informative for the
"failing pairs gain support" question).

### B. Per-experiment proximity tiers

For each `(threshold, experiment, target)`, classify the peak/TSS
relationship into one of:

| Tier | Distance (bp from TSS to nearest peak edge or 0 if peak overlaps) |
|---|---|
| `proximal_promoter_support` | ≤ 5,000 |
| `nearby_support` | 5,001–50,000 |
| `distal_candidate_support` | 50,001–200,000 |
| `no_local_support` | > 200,000 (or no peaks on chromosome at all) |

The cap at 200 kb is a defensible upper bound for cis-regulatory
contact. Beyond that, peaks are unlikely to be acting on the target.

### C. Cancer / non-cancer separation preserved

The biosample classification from v0 carries forward unchanged. All
21 experiments remain `cancer_lung_line`; `noncancer_lung` and
`unclear` remain at zero. Aggregate classes that require non-cancer
support (`peak_validated_in_lung_context`) stay structurally
unreachable.

## Class precedence (extended for the sensitivity audit)

Order: highest-strength applicable class wins. Six classes (one new
relative to v0):

1. **`peak_validated_in_lung_context`** — at least one **non-cancer**
   experiment shows `proximal_promoter_support`. Unreachable in v0
   and v0-sensitivity (no non-cancer experiments).
2. **`peak_validated_in_cancer_lung_context_only`** — at least one
   **cancer** experiment shows `proximal_promoter_support`; zero
   non-cancer.
3. **`lung_context_source_only`** — no `proximal_promoter_support`,
   at least one experiment shows `nearby_support` (5–50 kb).
4. **`distal_candidate_support_only`** *(new for sensitivity)* — no
   `proximal_promoter_support` and no `nearby_support`, at least one
   experiment shows `distal_candidate_support` (50–200 kb).
5. **`no_locus_support`** — every checked experiment shows
   `no_local_support`.
6. **`unresolved_due_to_context`** — biosample classification ambiguous
   or all peak downloads failed.

Each pair is classified independently per threshold (bed10 and bed05),
and the audit records the change between the two. A pair that moves
from `no_locus_support` at bed10 to `distal_candidate_support_only`
at bed05 has gained distal support; one that stays in
`lung_context_source_only` is robust to threshold change.

## Output

`metadata/nkx21_peak_audit_sensitivity.csv` — one row per
`(threshold, target)` pair. Schema:

| column | meaning |
|---|---|
| threshold | `bed05` or `bed10` |
| target | one of the 7 |
| target_locus | for cross-reference |
| n_experiments_total | 21 |
| n_proximal_promoter_cancer | proximal hits in cancer-line ChIP |
| n_proximal_promoter_noncancer | (always 0 in v0; column for symmetry / future use) |
| n_nearby_cancer | nearby hits |
| n_distal_candidate_cancer | distal hits |
| n_no_local_cancer | no-support count |
| n_download_failed | per threshold |
| final_class | one of the 6 |
| class_at_other_threshold | the class assigned at the other threshold (for change detection) |
| class_changed | `yes` / `no` |
| justification | short text |

`notes/nkx21_peak_audit_sensitivity.md` — the report. Required
sections:

- The four user-stated questions, answered:
  1. Which of the 4 "failing" pairs remain weak even at bed05?
  2. Which of them gain only distal candidate support?
  3. Does the main conclusion stay the same after threshold sensitivity?
  4. Which pair is most robustly unsupported across all tested settings?
- Per-pair before/after table (bed10 → bed05).
- The robustness statement (which conclusions survive, which do not).

## Anti-overclaim rules carried forward

- **bed05 ≠ "more truth," it is "more permissive."** Some bed05 peaks
  represent weaker / lower-quality binding events; the false-positive
  rate is higher. Pair-level promotion at bed05 is not equivalent to
  binding confirmation.
- **A distal candidate peak is not a confirmed regulatory link.**
  Distance ≤ 200 kb makes a peak a *candidate* regulatory element;
  contact + functional readout (Hi-C, perturbation) would be needed
  to confirm action on the target.
- **Cancer-line ChIP remains cancer-line ChIP.** Threshold relaxation
  and window expansion do not address the cancer-vs-developmental
  distinction. The strongest classes reachable in this audit are
  `peak_validated_in_cancer_lung_context_only` and
  `distal_candidate_support_only`. **The textbook claim about
  developmental NKX2-1 → target binding is not being tested by this
  audit.**
- **Re-running the audit on the same 21 experiments at a different
  threshold is not a new ChIP experiment.** The audit's information
  ceiling is bounded by what those 21 cancer-line experiments
  capture.

## Implementation outline

Extends `scripts/gain_nkx21_audit.py` cleanly via a new file
`scripts/gain_nkx21_audit_sensitivity.py` that:

- Reuses the same `EXPERIMENTS` list and `TARGETS` dict (duplicated
  rather than imported, since the `scripts/` directory has no
  package boilerplate; small intentional duplication is preferable
  to introducing `__init__.py`).
- Loops over thresholds in `[5, 10]`, downloads the corresponding
  bed05 / bed10 BEDs from ChIP-Atlas (~ 50–60 MB total), and computes
  the four-tier proximity classification per `(threshold,
  experiment, target)`.
- Aggregates per `(threshold, target)` using the six-class precedence.
- Records `class_at_other_threshold` and `class_changed`.

Stdlib only. Two thresholds × 21 experiments = 42 BED downloads;
~ 0.3 s sleep ≈ 13 s total HTTP overhead plus actual transfer
(probably ~ 1–2 minutes total).
