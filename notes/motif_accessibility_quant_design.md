# Motif + Accessibility — Quantitative Refinement Design

**Status:** design contract for one quantitative refinement pass on
the already-collected data. **No new HTTP.** No new genes, regulators,
or infrastructure beyond a small reading + scoring script.

**Why this audit.** The categorical motif+accessibility audit
([`notes/motif_accessibility_control_audit.md`](motif_accessibility_control_audit.md))
found that 5 of 5 SOX2 canonical targets *and* 5 of 5 controls cross
the same positive class. The categorical method does not distinguish
canonical targets from controls. Before recommending project-summary
mode, the user requested one **quantitative refinement** pass on the
existing per-pair counts to test whether continuous scoring can
separate targets from controls where the binary classifier could not.

## Scope (strict)

- **Inputs (already on disk; no new HTTP):**
  - `metadata/nkx21_motif_accessibility_audit.csv` (4 NKX2-1 targets)
  - `metadata/sox2_motif_accessibility_audit.csv` (5 SOX2 targets)
  - `metadata/motif_accessibility_control_audit.csv` (5 controls — scanned with the SOX2 motif)
- **Output:** `metadata/motif_accessibility_quant_refinement.csv` —
  per-pair quantitative metrics + rank labels
- **Script:** `scripts/gain_motif_accessibility_quant.py` — stdlib
  only, ~ 100–150 LoC
- **Report:** `notes/motif_accessibility_quant_refinement.md`

## What can be computed from the existing CSVs

Each row already records:

- `n_motif_hits_in_window` — total motif occurrences in ± 50 kb
- `n_lung_peaks_in_window` (and `n_fetal_peaks_in_window`,
  `n_adult_peaks_in_window`) — accessibility peaks
- `n_motif_hits_in_fetal_peaks` (and `_adult_peaks`) — overlap counts
- `n_supporting_fetal_experiments` — distinct fetal donors

Aggregate counts only — **per-base accessibility coverage and per-peak
widths are not in the CSV**. So "motif occurrences per accessible bp"
cannot be computed without re-fetching peak BEDs (which is forbidden).
Computable metrics are necessarily *per-peak* and *per-experiment*,
not *per-bp*.

## Metrics computed in this refinement

Per pair, compute four metrics. All are stdlib-trivial divisions of
existing counts.

1. **`motif_capture_rate`** — fraction of all motif occurrences in
   the window that fall within at least one fetal lung accessible
   peak. Formula:
   `n_motif_hits_in_fetal_peaks / n_motif_hits_in_window`.
   Range 0–1. Higher = motifs are concentrated in accessible regions
   (the regulator's binding sites coincide with accessible chromatin
   in fetal lung).

2. **`motif_density_per_fetal_peak`** — average number of motif
   occurrences per fetal lung peak in the window. Formula:
   `n_motif_hits_in_fetal_peaks / n_fetal_peaks_in_window`.
   Higher = each accessible peak harbours more motif sites.

3. **`cross_donor_consistency`** — fraction of the 13 fetal lung
   donors that support the pair. Formula:
   `n_supporting_fetal_experiments / 13`.
   Range 0–1. Higher = the signal is consistent across donors,
   not a single-donor artefact.

4. **`combined_quant_score`** — joint score capturing both motif-
   accessibility coincidence and donor reproducibility. Formula:
   `motif_capture_rate × cross_donor_consistency`.
   Range 0–1.

## Separation criteria

For the SOX2 + control comparison (apples-to-apples — same SOX2
motif scanned against both):

- Compute each of the four metrics for the 5 SOX2 canonical targets
  (TP63, KRT5, MUC5B, FOXJ1, SCGB1A1) and the 5 controls (GAPDH,
  ACTB, HBA1, HBB, SFTPC).
- Rank the 10 genes by `combined_quant_score`.
- **Selectivity question:** under any metric, do the 5 SOX2
  canonical targets cluster *above* the 5 controls?

For the NKX2-1 set, an apples-to-apples comparison is **not
available** in this refinement because the controls were scanned with
the SOX2 motif (not NKX2-1's). Cross-motif comparison is methodologically
weaker. The refinement nonetheless reports NKX2-1 targets' metrics
and notes whether they fall in the same range as the
SOX2-motif-scored controls — with the explicit caveat that motif
occurrence rates differ between MA1994.2 (NKX2-1, 7-bp) and MA0143.5
(SOX2, 11-bp).

## Decision rule

After computing metrics:

- **Salvageable** — at least one of the four metrics produces a clean
  ordering where ALL canonical SOX2 targets score above ALL controls.
  In this case, recommend continuing with the quantitative method
  (e.g., extend to NKX2-1 targets with controls scanned under the
  NKX2-1 motif).
- **Partially salvageable** — canonical SOX2 targets are mixed with
  controls but two of the controls (HBA1, HBB blood-specific) are
  reliably at the bottom under one or more metrics. The method
  detects extreme tissue-restriction but not within-lung
  selectivity. **Do not continue** — this is essentially "is the
  locus accessible in lung?" which is not regulator-specific.
- **Not salvageable** — canonical SOX2 targets are interleaved with
  controls under every metric. The method fundamentally lacks
  selectivity at bulk-lung scale. Stop and recommend project-summary
  mode.

## What this refinement does *not* do

- **Does not normalise by per-base accessibility coverage.** That
  requires the actual peak coordinates (peak widths), which would
  need re-fetching peak BEDs. Forbidden by scope.
- **Does not compute shuffled-motif null distributions.** That
  requires per-locus sequence or peak-coord shuffling. Forbidden.
- **Does not change the motif threshold or substrate.** Same
  relative_score ≥ 0.85, same 15 lung experiments.
- **Does not add new genes, regulators, or downstream methods.**
  Same 14 genes (4 NKX2-1 + 5 SOX2 + 5 controls) as the existing
  CSVs.
- **Does not use HTTP.** Reads only the three local CSVs.

## Output schema

`metadata/motif_accessibility_quant_refinement.csv` — one row per of
the 14 pairs already in the existing CSVs. Schema:

| column | meaning |
|---|---|
| regulator | `NKX2-1`, `SOX2`, or `SOX2_control` |
| target | gene symbol |
| category | `nkx21_canonical`, `sox2_canonical`, or `control_<subtype>` |
| motif_id | `MA1994.2` for NKX2-1; `MA0143.5` for SOX2 + controls |
| n_motif_hits_in_window | from input CSV |
| n_fetal_peaks_in_window | from input CSV |
| n_motif_hits_in_fetal_peaks | from input CSV |
| n_supporting_fetal_experiments | from input CSV |
| motif_capture_rate | computed |
| motif_density_per_fetal_peak | computed |
| cross_donor_consistency | computed |
| combined_quant_score | computed |
| rank_within_sox2_set | 1–10 ranking under combined_quant_score (only sox2 + sox2_control rows) |
| separation_verdict | `above_controls`, `interleaved_with_controls`, or `below_controls` per the SOX2 vs control comparison |

`notes/motif_accessibility_quant_refinement.md` — report covering
the four user-stated questions.

## Caveats baked in

- **Cross-motif comparison limitation.** Direct numeric comparison
  between NKX2-1 motif scores and SOX2 motif scores is not safe.
  The NKX2-1 targets' metrics are reported but the principal
  selectivity test uses only the SOX2 motif (apples-to-apples).
- **Aggregate-only refinement.** Without per-base coverage data, the
  refinement is bounded above by what counts can express. Per-bp
  density would be a stricter test but requires forbidden HTTP.
- **The decision rule trades off cheaply.** "Partially salvageable"
  is the most likely outcome based on the categorical numbers —
  HBA1 / HBB are clearly low; everything else is mixed — and the
  rule explicitly classifies that as "do not continue".
- **No statistical inference.** With 5 canonicals and 5 controls,
  formal hypothesis testing is not warranted. The verdict is based
  on rank-ordering and the user's stated question.

## Implementation

`scripts/gain_motif_accessibility_quant.py` — stdlib only:

- Read the three CSVs into a unified list of dicts.
- Tag each row with `category` from a small lookup table.
- Compute the four metrics per row.
- Compute SOX2 vs control ranking under `combined_quant_score`.
- Apply the `separation_verdict` rule.
- Emit the unified CSV + a console summary.

No HTTP. ~ 150 LoC. Runtime < 1 second.
