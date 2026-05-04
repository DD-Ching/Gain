# Motif + Accessibility Audit — Design

**Status:** design contract for the first-pass indirect-evidence audit.
Implementation must match this document; deviations require updating
it first.

**Why this audit.** The chain audit's standing finding is that
NKX2-1 / SOX2 / SOX9 lung-context ChIP is missing or non-physiological,
and that NKX2-1's four canonical alveolar/airway targets (SFTPC,
SCGB1A1, ABCA3, FOXA2) lack proximal-promoter ChIP support even at
bed05 in cancer-line substrate. This audit asks the orthogonal
question: **in primary human lung tissue accessible chromatin, does
the NKX2-1 binding motif occur near these target TSSs?** If yes, that
is *indirect* evidence that NKX2-1 could plausibly bind in lung —
the substrate the chain audit could never reach with ChIP.

This is **not** a generic motif framework. It is a narrow audit on
exactly four NKX2-1 → target pairs.

## Substrate (verified 2026-05-04)

**Motif source: JASPAR (jaspar.elixir.no).** The jaspar.genereg.net
URL redirects to the new Elixir host. NKX2-1 has two PFM versions:

- `MA1994.1` (2020): 13-bp PFM with extended flanks
- **`MA1994.2` (2024): 7-bp core PFM** — used in this audit

The 7-bp core captures the canonical NKX2-1 homeodomain motif
(consensus CACTTGA / RC TCAAGTG); JASPAR PFM is `>MA1994.2 Nkx2-1`.

**Accessibility source: ENCODE human lung ATAC-seq + DNase-seq.**
Programmatic search for `assay_title in {ATAC-seq, DNase-seq}` +
`biosample_ontology.term_name=lung` + organism `Homo sapiens` returns
**15 experiments**, of which **13 are fetal**:

| Stage | n | Examples |
|---|---:|---|
| Fetal (54–120 days) | 13 | ENCSR141IUS (76d), ENCSR318WOD (103d), ENCSR986XLW (101d), ENCSR482HQE (108d), ENCSR141VGA (85d), ENCSR076YBB (108d), etc. |
| Adult | 2 | ENCSR945JJB (47y, DNase), ENCSR647AOY (47y, ATAC) |

**This is the developmental substrate the chain audit has been
missing.** 13 fetal lung accessibility experiments at 54–120 days
of gestation (pseudoglandular / canalicular stages, where alveolar
and airway specification is in progress) is the right substrate to
ask the developmental binding question — even if only at the level
of motif + accessibility, not direct ChIP.

**Sequence source: UCSC API.** `https://api.genome.ucsc.edu/getData/sequence?genome=hg38;chrom=...;start=...;end=...` returns JSON with the requested DNA. Verified for our targets.

## Targets (4)

| Target | hg38 TSS | Strand | Status entering audit |
|---|---|---|---|
| SFTPC | chr8:22,156,913 | + | NKX2-1 v0+sensitivity: 0 prox / 5 nearby / 22 no_local at bed05 (cancer substrate) — robustly weak |
| SCGB1A1 | chr11:62,405,103 | + | 0 prox / 5 nearby / 7 no_local at bed05 — robustly weak |
| ABCA3 | chr16:2,340,749 | − | promotes to validated at bed05 (3 prox); weakest in proximal terms at bed10 |
| FOXA2 | chr20:22,585,455 | − | promotes to validated at bed05 (1 prox); marginal — strongest distal-candidate signal in NKX2-1 |

These four are the chain audit's standing "robustly failing" or
"threshold-marginal" pairs — exactly where the indirect-evidence
question is most decision-relevant.

## Method (v0)

Per (NKX2-1, target) pair:

1. **Fetch the target's hg38 sequence ±50 kb of TSS** via the UCSC
   API. 100 kb per target × 4 = ~400 kb total. One request per target.
2. **Scan the sequence with the JASPAR MA1994.2 NKX2-1 PWM** (both
   strands). Convert PFM → log-odds PWM with pseudocount 0.5,
   uniform 0.25 background. Record motif occurrences whose
   `relative_score >= 0.85` (the JASPAR-recommended default
   high-confidence threshold).
3. **For each of the 15 lung accessibility experiments** (1 ATAC + 14
   DNase): fetch the experiment's peak BED file from ENCODE (prefer
   `narrowPeak | peaks` output_type on GRCh38), parse, retain peaks
   that overlap the target's ±50 kb window.
4. **Intersect motif occurrences with accessible peaks.** A motif
   "supports indirect accessibility binding" if its position falls
   within at least one accessible peak in at least one lung
   experiment.
5. **Tag each supporting peak by developmental stage** (fetal vs
   adult) using the ENCODE biosample metadata.

## Five output classes

Ordered by evidence strength:

1. **`indirect_accessibility_support_in_fetal_lung_tissue`** — at
   least one motif occurrence (relative_score ≥ 0.85) falls within
   an ATAC/DNase peak from at least one **fetal** lung experiment.
   The strongest indirect tier; uses primary lung tissue substrate
   in the developmental window.
2. **`indirect_accessibility_support_in_adult_lung_tissue_only`** —
   support exists in adult lung accessibility data only, with zero
   fetal-lung motif-in-peak overlaps. Weaker indirect: cancer-vs-
   primary distinction is gone, but developmental relevance is
   uncertain.
3. **`motif_in_accessible_chromatin_negative`** — lung accessibility
   peaks exist within the ±50 kb window AND motif occurrences exist
   within the window, but **none of the motif positions fall within
   any accessible peak**. Substantive negative finding: the
   regulatory landscape exists in lung tissue but NKX2-1 motifs are
   not where the accessibility is. Includes the case where motifs
   are absent entirely from the window (peaks exist but no motif at
   threshold).
4. **`unresolved_no_lung_accessibility`** — zero lung ATAC/DNase
   peaks within ±50 kb of TSS across all 15 experiments. Cannot
   conclude either way; lung accessibility data simply doesn't
   exist for this window in the available substrate.
5. **`error`** — sequence fetch or peak download failure.

## Output schema (`metadata/nkx21_motif_accessibility_audit.csv`)

| column | meaning |
|---|---|
| regulator | always `NKX2-1` |
| target | one of the 4 |
| target_locus | `chr:tss (strand)` |
| motif_id | always `MA1994.2` |
| n_motif_hits_in_window | total motif occurrences (relative_score ≥ 0.85) within ±50 kb |
| n_lung_peaks_in_window | total lung ATAC/DNase peaks within ±50 kb (across all 15 experiments) |
| n_fetal_peaks_in_window | subset of above from fetal experiments |
| n_adult_peaks_in_window | subset from adult experiments |
| n_motif_hits_in_lung_peaks | motif occurrences that fall within at least one lung peak |
| n_motif_hits_in_fetal_peaks | subset, fetal only |
| n_motif_hits_in_adult_peaks | subset, adult only |
| n_supporting_fetal_experiments | distinct fetal experiments with at least one motif-in-peak overlap |
| n_supporting_adult_experiments | same, adult |
| best_supporting_locus | genomic position of highest-scoring motif hit within an accessible peak; `n/a` if none |
| best_supporting_motif_score | corresponding `relative_score`; `n/a` if none |
| final_class | one of the 5 |
| justification | short text |
| evidence_url | ENCODE search for the lung accessibility data |

## Anti-overclaim rules baked into the audit

- **"Indirect" means indirect.** Motif + accessibility plausibility
  is *necessary but not sufficient* for binding. The audit's positive
  classes explicitly say "indirect_accessibility_support" — no
  enhancer claim, no regulatory claim, no direct-binding claim.
- **JASPAR motifs are degenerate.** A 7-bp motif at relative_score
  0.85 will hit ~ 1 position per 1–2 kb of random sequence. False
  positives are inherent. The audit's strongest claim is "the
  binding site could plausibly exist here", not "binding occurs."
- **Bulk lung accessibility averages over cell types.** Fetal lung
  DNase profiles all cells in the tissue; cell-type-specific binding
  in (say) AT2 progenitors may be diluted out. False negatives are
  possible.
- **Even fetal lung is not a regulator-target validation.** Knowing
  the chromatin is accessible and the motif occurs nearby does not
  establish that NKX2-1 binds, regulates, or is required for the
  target gene's expression. It is *one tier* of indirect evidence.

## Decision checkpoint (built into the audit)

After running on the 4 targets and writing the report, the audit
**stops** and reports four numbers (per the user's instruction):

- How many of the 4 gain `indirect_accessibility_support_in_fetal_lung_tissue` or `indirect_accessibility_support_in_adult_lung_tissue_only`.
- Which target has the strongest indirect support.
- Which target remains weakest.
- Whether ≥ 2 of the 4 cross the positive threshold (positive class 1 or 2).

If < 2 of 4 cross the threshold: **stop.** Do not expand to SOX2.
Recommend project-summary mode (Option D from the post-chain memo).

If ≥ 2 of 4 cross the threshold: **stop and report**, with a
recommendation for whether the next expansion should be SOX2 failing
pairs or a stronger NKX2-1 follow-up (e.g., motif scanning in fetal
ATAC peaks + Hi-C contact data, or expanding to NKX2-1's distal
candidates that had chromatin support from the histone filter).

## Implementation outline

**Single new script:** `scripts/gain_motif_accessibility_audit.py`.

Sibling-imports:
- From `gain_nkx21_audit`: `http_get_bytes` (small helper).
- From `gain_peak_intersection`: `parse_bed_gz` (gzipped BED parser).
  Note: `best_peak_file_url` is ChIP-seq-tuned; this audit uses a
  small adapted variant inline that selects `narrowPeak | peaks` for
  ATAC/DNase output_type.

New code (~ 200–300 LoC, stdlib only):
- `fetch_jaspar_pfm(motif_id)` — GET from `jaspar.elixir.no`, parse
  PFM, cache to `metadata/cache/jaspar_<motif_id>.json` (gitignored).
- `pfm_to_log_odds(pfm)` — convert counts → log-odds PWM.
- `fetch_sequence(chrom, start, end)` — UCSC API.
- `scan_pwm(pwm, sequence, threshold)` — slide PWM both strands;
  return motif hits with relative scores.
- `find_lung_accessibility_experiments()` — ENCODE search; return
  list of (experiment_id, assay, biosample_summary, fetal_or_adult).
- `best_lung_peak_file_url(experiment_id, assay)` — adapt selection
  for ATAC/DNase output types.
- Main pipeline: 4 targets × 15 experiments = 4 sequence fetches +
  ~ 15 peak file downloads + per-target intersection.

Estimated runtime: ~ 1–2 minutes (15 BED downloads is the main cost).

Total dependency add: **zero new Python packages**. The JASPAR PFM
file (~ 1–2 KB cached) is the only new artifact; gitignored under
`metadata/cache/`.

## Out of scope

- Other regulators (SOX2, SOX9, etc.).
- Other targets beyond the 4 listed.
- Multiple motif models (only MA1994.2; not MA1994.1, not de-novo).
- Sensitivity sweep across motif thresholds (only 0.85 in v0).
- Hi-C / chromatin contact data.
- Mouse lung accessibility (only human hg38).
- Cell-type-deconvolved accessibility (bulk only).
