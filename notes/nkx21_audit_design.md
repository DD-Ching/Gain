# NKX2-1 Locus-Level Audit — Design

**Status:** design contract for the focused NKX2-1 audit. Implementation
must match this document; deviations require updating it first.

**Why this audit matters.** v2 classified all 7 NKX2-1 → target pairs as
`direct_human_lung_evidence` because ChIP-Atlas reports 21 NKX2-1 hg38
ChIP-seq experiments in lung biosamples. **A pre-implementation probe of
the experimentList.tab cache reveals that all 21 experiments are in lung
cancer cell lines** (small cell lung cancer × 11, lung adenocarcinoma
lines: NCI-H441, A549, NCI-H3122, HCC1819, NCI-H2087 × 10). **Zero non-
cancer / primary / fetal / developmental lung NKX2-1 ChIP-seq exists in
ChIP-Atlas hg38.**

This means the v2 `direct_human_lung_evidence` label is technically
correct but operationally misleading — for all 7 NKX2-1 target pairs,
the only available human "lung-context" public data is cancer-cell-line
ChIP. The textbook NKX2-1 → SFTPC / SFTPB / SCGB1A1 / ABCA3 / SOX2 /
SOX9 / FOXA2 claims are about **lung development**, not lung cancer.
This audit asks: at the **locus level**, do the cancer-line ChIP peaks
even support the canonical claims, and is there any non-cancer lung ChIP
that would directly test the developmental claim?

## Audit scope

In scope:
- **Regulator:** NKX2-1 only.
- **Targets:** SFTPC, SFTPB, SCGB1A1, ABCA3, SOX2, SOX9, FOXA2 — 7 pairs.
- **Source:** ChIP-Atlas peak BED files for all 21 hg38 NKX2-1 experiments
  (URL pattern verified 2026-05-03:
  `https://chip-atlas.dbcls.jp/data/hg38/eachData/bed{threshold}/{srx_id}.{threshold}.bed`).
- **Threshold:** `bed10` (q < 10⁻¹⁰) — ChIP-Atlas's standard high-confidence
  threshold. `bed05` is too permissive for binding inference; `bed20` may
  miss real but moderate-strength peaks.

Out of scope:
- All other regulators (per user's "do not expand beyond NKX2-1").
- Non-ChIP-Atlas peak sources (ENCODE has no NKX2-1 ChIP, so this is the
  only source; ReMap/Cistrome remain JS-rendered).
- Mouse NKX2-1 ChIP (none exists in ChIP-Atlas mm10 anyway).
- Motif scanning, accessibility-only inference, or cross-species lift-over.

## What counts as target-locus support?

For each (NKX2-1, target) pair, define a **±50 kb window** around the
target's hg38 Ensembl TSS:

| Target | hg38 TSS | Strand | Window |
|---|---:|---|---|
| SFTPC | chr8:22,156,913 | + | chr8:22,106,913–22,206,913 |
| SFTPB | chr2:85,668,741 | − (TSS at end) | chr2:85,618,741–85,718,741 |
| SCGB1A1 | chr11:62,405,103 | + | chr11:62,355,103–62,455,103 |
| ABCA3 | chr16:2,340,749 | − | chr16:2,290,749–2,390,749 |
| SOX2 | chr3:181,711,925 | + | chr3:181,661,925–181,761,925 |
| SOX9 | chr17:72,121,020 | + | chr17:72,071,020–72,171,020 |
| FOXA2 | chr20:22,585,455 | − | chr20:22,535,455–22,635,455 |

Within that window, **peak proximity tiers**:

- **`strong_support`** — peak overlaps the TSS (distance = 0) **or** any
  edge of the peak is within **5 kb** of the TSS. Captures core promoter
  / proximal enhancer binding.
- **`nearby_support`** — peak within ± 50 kb of the TSS but > 5 kb from
  it. Suggests distal regulatory binding; weaker claim.
- **`no_local_support`** — no peaks anywhere within ± 50 kb of the TSS.

## What counts as "nearby"?

± 50 kb is the same window used by `gain_peak_intersection.py` for the
SMAD1/GLI2 audit. Defensible default for cis-regulatory binding (covers
proximal promoter and most enhancers). Genuine long-range loops (> 50
kb) would be missed; out of scope for v0.

## How will cancer-line evidence be downgraded?

Each of the 21 NKX2-1 experiments is classified into one of three
biosample types from the cached `experimentList.tab` cell-type and
description columns:

| Biosample class | Match rules |
|---|---|
| **`cancer_lung_line`** | Cell-type or description contains any of: `lung adenocarcinoma`, `lung carcinoma`, `small cell lung cancer`, `NSCLC`, or any cell-line name in the lung-cancer set: A549, H441, H1299, H1395, H1437, H1568, H1793, H1819, H1944, H1975, H2009, H2073, H2086, H2087, H2122, H2228, H2347, H3122, H520, H522, H727, H810, HCC78, HCC95, HCC827, HCC1171, HCC1359, HCC1819, HCC2279, HCC2935, HCC4006, HCC44, NCI-H1437, PC9. |
| **`noncancer_lung`** | Cell-type or description contains any of: `primary lung`, `fetal lung`, `embryonic lung`, `lung organoid`, `BEAS-2B`, `16HBE`, `NHBE`, `HSAEC`, `HBEC`, or `lung tissue` without any cancer keyword. |
| **`unclear`** | Lung-context but neither set above matches. Default for ambiguous annotations. |

Peak validation **does not promote** a pair across classes by aggregation.
Specifically:

- **`peak_validated_in_lung_context`** — `strong_support` exists in **at
  least one `noncancer_lung` experiment**. Strict.
- **`peak_validated_in_cancer_lung_context_only`** — `strong_support`
  exists in **at least one `cancer_lung_line` experiment** *and* zero in
  any `noncancer_lung` experiment. Cancer-line support exists; non-cancer
  support either does not exist or was not tested.
- **`lung_context_source_only`** — at least one experiment shows
  `nearby_support` (peak in window but > 5 kb from TSS); zero
  `strong_support` of any kind. Weaker claim about regulatory binding;
  not promoted to peak-validated.
- **`no_locus_support`** — every checked experiment shows
  `no_local_support` (no peaks within ± 50 kb).
- **`unresolved_due_to_context`** — biosample classification ambiguous
  (all `unclear`) or peak file download failed for all experiments.

For the 21 NKX2-1 experiments, the pre-implementation classification
(based on the cached row metadata) is:

| Class | n | Examples |
|---|---:|---|
| `cancer_lung_line` | 21 | small cell lung cancer (×11), lung adenocarcinoma (×10) |
| `noncancer_lung` | 0 | — |
| `unclear` | 0 | — |

This means **`peak_validated_in_lung_context` cannot be reached for any
NKX2-1 pair in v0** — there is no non-cancer experiment to validate it.
The audit's strongest possible class for any NKX2-1 pair is
`peak_validated_in_cancer_lung_context_only`.

This is the headline finding the audit will produce.

## What result would actually change the scientific direction?

Three plausible outcomes:

1. **All / most pairs validate in cancer (class 2).** Confirms that
   cancer-line ChIP recapitulates the textbook NKX2-1 binding map for
   the canonical alveolar / airway targets. Reframes how the field
   uses cancer-line ChIP as a developmental proxy: the binding sites
   are real, but **the developmental claim is still inferred, not
   directly tested in human public data.** Modest research-direction
   update: prioritise primary lung tissue ChIP-seq as the missing
   piece.

2. **Some pairs fail to validate even in cancer (class 4).** Reveals
   that even the cancer-line "support" is locus-level weak for some
   canonical targets. Significant finding: textbook NKX2-1 → X claims
   may be more dependent on mouse genetics than the field assumes.
   Suggests targeted re-examination of those specific pairs and
   tightens what can be claimed in human-relevant disease modelling.

3. **Mixed (some class 2, some class 3/4).** Most likely outcome.
   Tells us **which specific canonical pairs are best-supported by
   public cancer ChIP** and which are weakly supported even there.
   Useful as a citation map for the field.

Any of these outputs is non-trivial. Outcome (2) would be the strongest
research-direction signal; outcome (1) is the safest prediction; (3) is
the most likely.

## Inputs

- Hardcoded in `scripts/gain_nkx21_audit.py`:
  - The 21 NKX2-1 SRX IDs and their biosample annotations (extracted
    once from `metadata/cache/chipatlas_experimentList.tab`)
  - The 7 target gene TSS coordinates (Ensembl REST, hg38)
  - Cancer-line and non-cancer-line keyword sets
  - ± 50 kb window; 5 kb strong-support cutoff

## Outputs

`metadata/nkx21_peak_audit.csv` — one row per (NKX2-1, target) pair:

| column | meaning |
|---|---|
| regulator | always `NKX2-1` |
| target | one of the 7 |
| target_locus | `chrN:TSS (strand)` |
| n_experiments_total | always 21 in v0 |
| n_cancer_lung | count of cancer-line experiments checked |
| n_noncancer_lung | count of non-cancer experiments checked |
| n_unclear | count of unclear-biosample experiments |
| n_strong_support | how many experiments show a peak ≤ 5 kb from TSS |
| n_strong_support_noncancer | subset of above in non-cancer biosamples |
| n_strong_support_cancer_only | subset in cancer-line biosamples |
| n_nearby_support | peaks within 5–50 kb (no strong) |
| n_no_local_support | no peaks within ± 50 kb |
| biosample_context_summary | short text |
| final_class | one of the 5 |
| justification | why this class fired |

`notes/nkx21_peak_audit.md` — human-readable report:

- Class counts.
- Per-pair detail.
- The headline answer to the user's three questions:
  - How many NKX2-1 target pairs are truly locus-supported?
  - How many are supported only in cancer lung context?
  - Does NKX2-1 still look like the strongest next bridge from
    textbook canon to public-data validation?

## Anti-overclaim rules carried forward

- **Cancer-line support ≠ developmental proof.** Even if all 7 pairs
  validate in cancer ChIP, this does not establish that NKX2-1 binds
  these targets *during lung development*. Cancer cells often deploy
  developmental TFs in dysregulated contexts that may shift binding
  specificity.
- **NKX2-1 is required for survival in many lung adenocarcinomas.**
  The cell lines used here express NKX2-1 because their oncogenic
  program depends on it; this can amplify some binding sites and
  suppress others relative to normal alveolar cells.
- **The Bethyl Laboratories A300-BL4000 antibody** is used in 13 of
  the 21 experiments. Antibody-specific binding artefacts may be
  systematically present.
- **Distance to TSS is not the same as regulatory function.** A peak
  in the proximal promoter is *necessary* but not *sufficient* for
  direct regulation.

## Implementation outline

1. Hardcode the 21 SRX IDs with biosample classification (all 21 are
   `cancer_lung_line` based on pre-implementation probe).
2. For each SRX, GET the bed10 file from
   `chip-atlas.dbcls.jp/data/hg38/eachData/bed10/{srx}.10.bed`
   (~ 50 kB to 4.5 MB each; total budget ~ 30 MB).
3. Parse peaks (BED format: chrom, start, end, ...).
4. For each (target, experiment), compute strong_support / nearby /
   no_local_support tiers.
5. Aggregate per pair, classify, write CSV + Markdown.

Stdlib only (`urllib.request`, `csv`, `argparse`, `pathlib`).
