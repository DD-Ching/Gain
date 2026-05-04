# NKX2-1 Histone-Filtered Candidates — Results

**Run:** 2026-05-04 (UTC)
**Input:** the 11 `strong_distal_candidate` rows from
[`metadata/nkx21_distal_candidates.csv`](../metadata/nkx21_distal_candidates.csv)
**Output:** [`metadata/nkx21_histone_filtered_candidates.csv`](../metadata/nkx21_histone_filtered_candidates.csv)
**Script:** [`scripts/gain_nkx21_histone_filter.py`](../scripts/gain_nkx21_histone_filter.py)
**Design contract:** [`notes/nkx21_histone_filter_design.md`](nkx21_histone_filter_design.md)

## Updated tier distribution

| Tier | Count |
|---|---:|
| `strong_distal_candidate_with_chromatin_support` | **5** |
| `strong_distal_candidate_without_chromatin_support` | **5** |
| `downgraded_candidate` | 1 |
| `unresolved_due_to_context_mismatch` | 0 |

ENCODE substrate: 13 active-mark + 8 repressive-mark **human lung
tissue** Histone ChIP-seq experiments (12 adult + 13 fetal lung tissue;
zero cancer-line). 34 mouse experiments recorded in metadata but
deliberately excluded from overlap testing (no hg38 lift-over in v0).

## Per-candidate result, ranked by histone strength

Each row inherits the previous audit's NKX2-1 ChIP support counts
(supporting cancer-line experiments at bed10 / bed05). The **histone
evidence** column shows active-mark peak overlaps in the candidate
locus, separated by fetal vs adult lung tissue context.

| Target | Locus | NKX2-1 bed10 / bed05 | Histone evidence | Tier |
|---|---|---|---|---|
| **FOXA2** | chr20:22,716,796 | 7 / 8 | **H3K27ac(adult)×3 + H3K4me1(adult)×2** — canonical active-enhancer combo | **with chromatin support** (strongest) |
| **FOXA2** | chr20:22,390,152 | 5 / 5 | **H3K27ac(adult)×2 + H3K4me1(fetal)** — multi-mark, fetal context | **with chromatin support** |
| **ABCA3** | chr16:2,155,403 | 3 / 7 | H3K27ac(adult) + H3K4me3(fetal+adult) — promoter-proximal-style mark | **with chromatin support** |
| **SCGB1A1** | chr11:62,497,136 | 6 / 6 | H3K27ac(adult) + H3K4me1(adult) — canonical active-enhancer combo | **with chromatin support** |
| **SCGB1A1** | chr11:62,534,332 | 3 / 10 | H3K4me1(fetal) only | **with chromatin support** |
| FOXA2 | chr20:22,463,535 | **8** / 12 | none | without |
| ABCA3 | chr16:2,490,817 | 7 / 9 | none | without |
| ABCA3 | chr16:2,399,387 | 5 / 5 | none | without |
| SCGB1A1 | chr11:62,326,687 | 5 / 6 | none | without |
| SFTPC | chr8:22,092,696 | 5 / 7 | none | without |
| ABCA3 | chr16:2,231,273 | 5 / 8 | repressive (H3K27me3 adult) only | **downgraded** |

## How many of the 11 gain lung-relevant chromatin support?

**5 of 11** gain `strong_distal_candidate_with_chromatin_support`. The
five are:

- FOXA2 chr20:22,716,796 (strongest)
- FOXA2 chr20:22,390,152
- ABCA3 chr16:2,155,403
- SCGB1A1 chr11:62,497,136
- SCGB1A1 chr11:62,534,332

Five remain `without_chromatin_support` — supplementary human lung
tissue active-mark histone ChIP exists for the relevant chromosomes,
but no peak overlaps the candidate locus.

One is `downgraded`: ABCA3 chr16:2,231,273 has only a repressive H3K27me3
peak overlapping it in adult lung tissue. The locus is Polycomb-
silenced in bulk adult lung; the candidate weakens accordingly, with
the caveat that Polycomb states are developmental-stage-dependent and
fetal coverage at this locus did not show the same.

## Does ABCA3 still remain the strongest follow-up target?

**No — the priority shifts to FOXA2.**

ABCA3 went from "the strongest distal-candidate case" (4 strong,
3 moderate, leading on raw count) to a more mixed picture: 1 with
chromatin support / 1 downgraded (repressive) / 2 without support.
Notably the highest-supported ABCA3 NKX2-1 locus (chr16:2,490,817 with
NKX2-1 bed10=7) **does not** have histone support, which weakens the
case for that specific locus.

**FOXA2 now leads** on the histone-filter axis:
- 2 of 3 strong candidates gain chromatin support
- The single best candidate in the entire 11-pair audit is now
  **FOXA2 chr20:22,716,796**, with 7 NKX2-1 bed10 supports plus
  3 H3K27ac and 2 H3K4me1 peaks in human adult lung tissue —
  the canonical active-enhancer mark combination.

Per-target after the histone filter:

| Target | with_support | without | downgraded | strong_total |
|---|---:|---:|---:|---:|
| **FOXA2** | **2** | 1 | 0 | 3 |
| **SCGB1A1** | **2** | 1 | 0 | 3 |
| ABCA3 | 1 | 2 | 1 | 4 |
| SFTPC | 0 | 1 | 0 | 1 |

FOXA2 and SCGB1A1 each have 2 of 3 strong candidates retaining their
status with chromatin support. ABCA3 has 1 of 4. SFTPC's only
candidate fails the histone filter.

## Do any FOXA2 or SCGB1A1 candidates become equally strong?

**Yes — both FOXA2 candidates and both SCGB1A1 candidates that gained
chromatin support are now stronger than any ABCA3 candidate.**

The standout pair, ordered:

1. **FOXA2 chr20:22,716,796** — 7 NKX2-1 bed10 / 8 bed05 + H3K27ac(adult)×3 + H3K4me1(adult)×2. Canonical adult lung active-enhancer signature plus high cancer-line NKX2-1 support. **Highest single follow-up priority.**
2. **FOXA2 chr20:22,390,152** — 5/5 NKX2-1 + H3K27ac(adult)×2 + H3K4me1(fetal). Has both adult and fetal evidence.
3. **SCGB1A1 chr11:62,497,136** — 6/6 NKX2-1 + H3K27ac(adult) + H3K4me1(adult). Adult lung canonical-combo support.
4. **ABCA3 chr16:2,155,403** — 3/7 NKX2-1 + H3K27ac(adult) + H3K4me3(fetal+adult). Mixed promoter-style and enhancer-style marks.
5. **SCGB1A1 chr11:62,534,332** — 3/10 NKX2-1 + H3K4me1(fetal). Single mark, but fetal context is developmentally important.

## Important caveats

- **Active-mark overlap raises the prior. It does not confirm the
  regulatory link.** Even FOXA2 chr20:22,716,796, the strongest case,
  is a **candidate** for an enhancer / NKX2-1 binding site in lung
  development — not a confirmed one. Hi-C / promoter-capture / 4C
  for the FOXA2 locus, plus an NKX2-1 ChIP in primary AT2 or fetal
  lung, would be the proper functional follow-up.
- **The 5 "without chromatin support" candidates are not refuted.**
  They may bind in cell types that bulk lung tissue averages over;
  H3K27ac in bulk tissue is dominated by the most abundant active cell
  types (e.g., endothelial in adult lung), so AT2- or airway-specific
  enhancers may be diluted below detection.
- **The 1 "downgraded" candidate (ABCA3 chr16:2,231,273) is not refuted
  either.** H3K27me3 (Polycomb) in adult bulk tissue is consistent
  with active regulation in fetal or adult AT2 cells — Polycomb
  states change across developmental stages and cell types.
- **No mouse evidence used.** Mouse lung histone ChIP overlap with
  hg38 candidates would require lift-over; deliberately deferred.
- **Cancer-line NKX2-1 binding is still cancer-line context.** Even
  with chromatin support in primary lung, the audit cannot establish
  that NKX2-1 *binds* these candidates in primary lung — only that
  the candidate loci appear active in primary lung.

## Does NKX2-1 deserve one final focused pass after this filter?

**Yes — one final pass, kept narrow.** The natural completion of the
NKX2-1 audit cycle is to **search GEO / NCBI / SRA for primary lung
tissue / AT2-cell / fetal lung NKX2-1 ChIP-seq deposited after the
ChIP-Atlas snapshot used here**. The systemic absence of non-cancer
NKX2-1 ChIP in ChIP-Atlas hg38 may reflect a stale snapshot rather
than a true gap — recent papers from Treutlein / Whitsett / Morrisey
groups (post-2022) are highest-yield candidates.

If even one primary-tissue NKX2-1 ChIP-seq exists, then the **5
chromatin-supported candidates** become directly testable: do those
NKX2-1 peaks fall on the same loci that show active-mark histone
support in lung tissue? That single test would be the cleanest
possible bridge between cancer-line binding evidence and developmental
relevance, without expanding scope or adding new infrastructure.

After that, the audit machinery should hand off to **SOX2** and
**SOX9** — the next-most-cited regulators in the chain. The 5-class
v2 evidence model, peak-intersection script, sensitivity sweep,
distal-candidate tiering, and now the histone-support filter are all
reusable per regulator without further design work.

## What v0 of this filter does *not* do

- No per-cell-type histone deconvolution (e.g., AT2-specific H3K27ac
  via subset-specific data).
- No ATAC-seq / DNase overlap (the 35 ENCODE lung ATAC + DNase
  experiments were inventoried earlier; cross-referencing them is a
  natural sibling to histone overlap but is not required for the
  binary "with / without chromatin support" tier).
- No motif scanning to confirm an NKX2-1 binding motif is present
  under each peak.
- No mouse-to-human lift-over.
- No statistical test for the per-pair tier transitions; tiers are
  rule-based.

## Reproducing the audit

```sh
python3 scripts/gain_nkx21_histone_filter.py
```

Stdlib only. Single ENCODE search call (59 experiments), 21
per-experiment metadata calls, ~ 21 BED downloads (active + repressive
human only). Total runtime ~ 60–90 s; ~ 30 MB downloads.
