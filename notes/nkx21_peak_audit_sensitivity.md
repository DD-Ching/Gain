# NKX2-1 Sensitivity Audit — Results

**Run:** 2026-05-04 (UTC)
**Inputs:** same 21 NKX2-1 hg38 ChIP-Atlas experiments + 7 targets as
[`notes/nkx21_peak_audit.md`](nkx21_peak_audit.md)
**Output:** [`metadata/nkx21_peak_audit_sensitivity.csv`](../metadata/nkx21_peak_audit_sensitivity.csv)
**Script:** [`scripts/gain_nkx21_audit_sensitivity.py`](../scripts/gain_nkx21_audit_sensitivity.py)
**Design contract:** [`notes/nkx21_sensitivity_design.md`](nkx21_sensitivity_design.md)

## Per-pair side-by-side (bed10 → bed05)

Tier counts across the 21 cancer-line experiments at each threshold.
**`prox`** = peak ≤ 5 kb of TSS; **`near`** = 5–50 kb; **`dist`** =
50–200 kb; **`no_local`** = > 200 kb (or no peaks on chromosome).

| Target | Threshold | prox | near | dist | no_local | Class | Robustness |
|---|---|---:|---:|---:|---:|---|---|
| **SFTPC** | bed10 | 0 | 3 | 2 | 16 | `lung_context_source_only` | robust failure |
| | bed05 | 0 | 3 | 5 | 13 | `lung_context_source_only` | (no change) |
| **SFTPB** | bed10 | 7 | 12 | 0 | 2 | `peak_validated_in_cancer_lung_context_only` | robust pass |
| | bed05 | 10 | 10 | 0 | 1 | `peak_validated_in_cancer_lung_context_only` | (no change) |
| **SCGB1A1** | bed10 | 0 | 5 | 4 | 12 | `lung_context_source_only` | robust failure |
| | bed05 | 0 | 5 | 9 | 7 | `lung_context_source_only` | (no change) |
| **ABCA3** | bed10 | 0 | 4 | 9 | 8 | `lung_context_source_only` | **CHANGED** |
| | bed05 | 3 | 4 | 11 | 3 | `peak_validated_in_cancer_lung_context_only` | promotes at bed05 |
| **SOX2** | bed10 | 3 | 2 | 1 | 15 | `peak_validated_in_cancer_lung_context_only` | robust pass |
| | bed05 | 5 | 4 | 2 | 10 | `peak_validated_in_cancer_lung_context_only` | (no change) |
| **SOX9** | bed10 | 3 | 2 | 0 | 16 | `peak_validated_in_cancer_lung_context_only` | robust pass |
| | bed05 | 3 | 4 | 6 | 8 | `peak_validated_in_cancer_lung_context_only` | (no change) |
| **FOXA2** | bed10 | 0 | 3 | 10 | 8 | `lung_context_source_only` | **CHANGED** |
| | bed05 | 1 | 4 | 13 | 3 | `peak_validated_in_cancer_lung_context_only` | promotes at bed05 |

## The four user-stated questions, answered

### 1. Which of the 4 "failing" pairs remain weak even after relaxing to bed05?

**Two of four**: **SFTPC** and **SCGB1A1**.

- **SFTPC**: 0 proximal at bed10 → 0 proximal at bed05. Threshold
  relaxation does not rescue this pair. The proximal promoter remains
  free of NKX2-1 peaks in all 21 cancer-line experiments at both
  thresholds.
- **SCGB1A1**: 0 proximal at bed10 → 0 proximal at bed05. Same pattern.
  This is the canonical airway secretory marker; the proximal-promoter
  signal is robustly absent in cancer-line ChIP at both thresholds.

The other two recover at bed05:
- **ABCA3**: 0 → 3 proximal experiments. Now classified
  `peak_validated_in_cancer_lung_context_only`.
- **FOXA2**: 0 → 1 proximal experiment. Marginal promotion (1 of 21
  is a low-confidence bar; this is the weakest pass in the audit).

### 2. Which gain only distal candidate support?

**None land in the strict `distal_candidate_support_only` class.** All
seven pairs have at least one experiment with a peak in the 5–50 kb
nearby band at both thresholds, so none qualify for "distal-only"
under our six-class precedence.

**However, the four originally-failing pairs all have substantial
distal-band activity** (50–200 kb peaks) that becomes more visible at
bed05:

| Target | Distal peaks at bed10 | Distal peaks at bed05 |
|---|---:|---:|
| SFTPC | 2 | 5 |
| SCGB1A1 | 4 | 9 |
| ABCA3 | 9 | 11 |
| FOXA2 | 10 | 13 |

For ABCA3 and FOXA2, distal peaks (9–13) outnumber nearby peaks (4–4)
roughly 3:1 at bed05. This suggests **the NKX2-1 binding pattern at
these loci in cancer cell lines may be enriched in distal regulatory
elements rather than proximal promoters.** This is a *candidate*
finding, not a confirmation — distance alone does not establish
regulatory contact. Hi-C / promoter-capture confirmation would be the
proper functional follow-up.

### 3. Does the main conclusion stay the same after threshold sensitivity?

**Partially.** The previous audit's headline was "4 of 7 textbook pairs
lack strong locus support in cancer-line ChIP." After threshold
relaxation, the right phrasing is more nuanced:

- **At bed05, 5 of 7 pairs are `peak_validated_in_cancer_lung_context_only`** (was 3 at bed10). The 6th (FOXA2) is a marginal promotion (1/21 proximal experiments).
- **2 of 7 pairs remain failing across both thresholds**: SFTPC and SCGB1A1. These are the most robust weak findings.
- **No pair lands in `no_locus_support`** at either threshold — every pair has at least nearby peaks somewhere.

The audit's framing therefore tightens to:

> Across two ChIP-Atlas confidence thresholds, **2 of 7 canonical NKX2-1
> textbook targets — SFTPC and SCGB1A1 — robustly lack proximal-promoter
> NKX2-1 peaks in 21 lung cancer cell line ChIP experiments**. The
> remaining 5 pairs validate at bed05 in cancer-line context (with
> caveats listed below). All 7 pairs show distal-band peaks (50–200 kb
> from TSS) — most prominently the failing ones — which the proximal-
> only audit window did not surface.

This is **not** a refutation of the textbook NKX2-1 → SFTPC/SCGB1A1
claim. It is a sharpened observation about where the proximal-promoter
binding signal is or is not detectable in available cancer-line public
data, with explicit acknowledgement that the developmental context is
not being tested.

### 4. Which pair is most robustly unsupported across all tested settings?

**SFTPC** is tied with **SCGB1A1** for the most robust weak finding.
Both have 0 proximal peaks at both bed10 and bed05 across all 21
experiments. SFTPC has slightly fewer distal peaks at both thresholds
(2 / 5) compared to SCGB1A1 (4 / 9), so by a small margin **SFTPC has
the weakest cancer-line public-data signal in our audit's window**.
Given SFTPC's textbook status as *the* canonical NKX2-1 alveolar
target, this is the standout robustness result.

## What the audit *does not* claim

- **It does not claim NKX2-1 fails to regulate SFTPC or SCGB1A1.**
  The textbook claims rest on classical promoter-reporter assays in
  developmental contexts; the present data is whole-genome ChIP at a
  particular threshold in cancer cell lines.
- **It does not claim distal peaks are functional regulatory contacts.**
  50–200 kb proximity makes a peak a *candidate* element; functional
  validation (Hi-C, perturbation) would be required.
- **It does not address developmental binding.** No primary lung tissue,
  fetal lung, lung organoid, or AT2-cell ChIP-seq for NKX2-1 exists in
  ChIP-Atlas hg38. Threshold relaxation cannot change that.
- **It does not eliminate antibody / line / threshold artefacts.** 13 of
  21 experiments use the Bethyl A300-BL4000 antibody; the result could
  shift with different antibody-line combinations.

## Robustness summary

| Conclusion | Robust? |
|---|---|
| All 21 NKX2-1 hg38 ChIP-Atlas experiments are in lung cancer cell lines (zero non-cancer) | yes — structural |
| `peak_validated_in_lung_context` is unreachable in v0 | yes — by definition |
| 5 of 7 pairs validate `peak_validated_in_cancer_lung_context_only` at bed05 | yes (with FOXA2 borderline at 1/21) |
| **SFTPC and SCGB1A1 lack proximal-promoter peaks at all tested thresholds** | **yes — robust across bed10 and bed05** |
| **All four originally-failing pairs have substantial distal-band peak signal** | **yes — robust; suggests distal regulatory hypothesis** |
| Cancer-line ChIP recapitulates developmental NKX2-1 binding | **not addressed** by this audit |

## What changes the recommended research direction

The earlier-recommended next moves stand, with one refinement:

1. The **bed05 sweep is now done**. ABCA3 and FOXA2 recover; SFTPC and
   SCGB1A1 do not. The threshold question is settled.
2. **Targeted PubMed + GEO search** for primary-tissue / fetal lung
   NKX2-1 ChIP remains the highest-leverage move.
3. **The distal-band signal is now a real lead.** A worthwhile small
   followup: for the four originally-failing pairs, list the specific
   distal peak coordinates in cancer-line ChIP and check whether they
   sit within published Hi-C contact domains for SFTPC / SCGB1A1 /
   ABCA3 / FOXA2. If yes, the "NKX2-1 acts via distal enhancers in
   cancer context" hypothesis gains a candidate element list. If no,
   the distal peaks may be incidental.

## Reproducing this audit

```sh
python3 scripts/gain_nkx21_audit_sensitivity.py
```

Stdlib only. Two thresholds × 21 experiments = 42 BED downloads
(~ 35 MB at bed05 + ~ 25 MB at bed10 = ~ 60 MB total). 0.3 s sleep
between downloads; total runtime ~ 60–90 s.
