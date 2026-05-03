# Peak Intersection — 4 indirect_human_evidence pairs

**Audit run:** 2026-05-03 (UTC)
**Script:** [`scripts/gain_peak_intersection.py`](../scripts/gain_peak_intersection.py)
**Output:** [`metadata/peak_intersection_results.csv`](../metadata/peak_intersection_results.csv)
**Window:** ± 50 kb around the target gene's TSS (hg38, Ensembl-derived)

## Question

Of the four pairs that the Q3 audit classified as
`direct_human_non_lung_evidence` because their regulator has human TF
ChIP-seq in non-lung biosamples, **does any of those ChIP support the
canonical regulatory link at the target gene's locus?**

## Method (v0)

1. Pull each experiment's "conservative IDR thresholded peaks" BED file
   from the ENCODE REST API (4 experiments → 4 BED files, GRCh38).
2. For each `(experiment, target)` test, count peaks whose interval
   overlaps the ± 50 kb window around the target's TSS, and record the
   nearest-peak distance (0 if any peak spans the TSS).
3. Assign an interpretation per test:
   - `supports`: peak overlaps the TSS (distance = 0) **or** ≥ 1 peak
     within 5 kb of the TSS.
   - `weak_support`: ≥ 1 peak within ± 50 kb but > 5 kb from the TSS.
   - `no_locus_support`: no peaks within ± 50 kb.
   - `inconclusive`: no peaks on the target's chromosome at all.

Stdlib only (`urllib.request`, `gzip`, `csv`, `json`).

## Results, per pair

### SMAD1 → ID1 — mixed, cell-type-dependent

| Experiment | Cell | Peaks in window | Nearest-peak (bp) | Interpretation |
|---|---|---:|---:|---|
| ENCSR213QOZ | HepG2 (liver) | 9 | 13,902 | weak_support |
| ENCSR813DCK | GM12878 (B-cell) | 0 | 322,233 | no_locus_support |
| ENCSR038DJJ | K562 (leukaemia) | 6 | **0 (overlaps TSS)** | **supports** |

Aggregate: 1 supports / 1 weak / 1 absent across 3 experiments.
Interpretation: SMAD1 binds at or near the ID1 TSS in K562 and within
14 kb in HepG2; in GM12878 the nearest peak is 322 kb away. The link
is supported but **cell-type-dependent**, not universal.

### SMAD1 → ID2 — strongest pair, robust across all 3 experiments

| Experiment | Cell | Peaks in window | Nearest-peak (bp) | Interpretation |
|---|---|---:|---:|---|
| ENCSR213QOZ | HepG2 | 1 | 13,614 | weak_support |
| ENCSR813DCK | GM12878 | 3 | 3,086 | **supports** |
| ENCSR038DJJ | K562 | 3 | **0 (overlaps TSS)** | **supports** |

Aggregate: 2 supports / 1 weak / 0 absent across 3 experiments.
Interpretation: SMAD1 ChIP peaks fall within 14 kb of the ID2 TSS in
*every* checked human cell line, with peak overlap in K562 and a 3 kb
nearest peak in GM12878. **The canonical BMP→SMAD1→ID2 link is the
best-supported pair in this audit.**

### GLI2 → PTCH1 — no locus support in the only available human GLI2 ChIP

| Experiment | Cell | Peaks in window | Nearest-peak (bp) | Interpretation |
|---|---|---:|---:|---|
| ENCSR978EQY | HEK293 | 0 | 63,764 | no_locus_support |

Aggregate: 0 supports / 0 weak / 1 absent across 1 experiment.
Interpretation: in the only public human GLI2 TF ChIP-seq in ENCODE,
no peaks fall within ± 50 kb of the PTCH1 TSS. The nearest peak is
~ 64 kb away — outside the canonical regulatory-element distance for
direct binding. **The textbook GLI2 → PTCH1 link is not supported by
the available human ENCODE peak data at this locus.**

### GLI2 → GLI1 — no locus support; nearest peak is ~ 1.5 Mb away

| Experiment | Cell | Peaks in window | Nearest-peak (bp) | Interpretation |
|---|---|---:|---:|---|
| ENCSR978EQY | HEK293 | 0 | 1,458,168 | no_locus_support |

Aggregate: 0 supports / 0 weak / 1 absent across 1 experiment.
Interpretation: the canonical SHH-feedback target GLI1 is even further
from any GLI2 peak than PTCH1 is. **Strong absence at the target locus.**

## Caveats and what this audit does *not* claim

- **Single-experiment dependence.** GLI2 has only 1 human TF ChIP in
  ENCODE. A "no locus support" finding from one experiment is weaker
  than from three; the result might flip if more experiments exist
  (ChIP-Atlas reports 4 GLI2 hg38 experiments — see
  `notes/sanity_check_result.md`; three of those are non-ENCODE and
  not yet checked at peak level).
- **HEK293 may not be SHH-active.** Unstimulated HEK293 cells have
  baseline (low) SHH-pathway activity. If GLI2 binds canonical targets
  primarily under SHH stimulation, an unstimulated HEK293 ChIP may not
  capture those bound sites. The "no support" finding for GLI2 → PTCH1
  / GLI1 in HEK293 is **not equivalent** to "GLI2 does not bind these
  loci in lung development."
- **Cell-line non-lung context.** All four experiments are in HepG2,
  GM12878, K562, HEK293 — none lung. SMAD1 and GLI2 may bind different
  (or shifted) genomic locations in lung-developmental contexts. This
  audit can only test what public data exists, which is non-lung.
- **Window choice.** ± 50 kb is a defensible default for cis-regulatory
  binding (covers proximal promoter and most enhancers). Genuine
  long-range loops (> 50 kb) would be missed.

## How many of the 4 pairs gained stronger support after peak intersection?

**Two:** SMAD1 → ID1 (one supporting cell line) and SMAD1 → ID2 (two
supporting cell lines, all three experiments at minimum weak).

The two GLI2 pairs **did not** gain support — the available human GLI2
ChIP data does not corroborate the canonical SHH-feedback links at the
target loci within ± 50 kb. With caveats above (single experiment,
HEK293, non-lung), this is a real and citable finding rather than a
final negative claim.

## Strongest and weakest pair

- **Strongest:** **SMAD1 → ID2.** Three out of three experiments show
  peaks within 14 kb of the TSS, with two showing peak overlap or sub-
  3 kb proximity. This is now `peak_validated_at_target_locus` (a tier
  above `direct_human_non_lung_evidence`).
- **Weakest:** **GLI2 → GLI1.** Single human ENCODE GLI2 experiment
  has no peaks within ± 50 kb; nearest peak ~ 1.5 Mb away. The
  textbook claim is not corroborated at the target locus.

## Does this change the recommended research direction?

Yes, in three concrete ways:

1. **The audit's classification scheme should grow a new top tier.**
   `peak_validated_at_target_locus` (or `direct_human_non_lung_evidence_validated_at_locus`)
   is a class strictly above `direct_human_non_lung_evidence`. SMAD1 →
   ID2 belongs there immediately; SMAD1 → ID1 is a candidate (cell-type-
   dependent). This is a v2.x audit-script change, ~30 lines.
2. **The SHH-pathway pairs need a different evidence path.** A single
   non-stimulated HEK293 ChIP is the wrong substrate. Concrete next
   steps: (a) check the 3 non-ENCODE GLI2 hg38 experiments in
   ChIP-Atlas for peak-level support; (b) consider GLI3 as the
   alternative SHH effector in lung contexts; (c) accept that direct
   peak-level evidence may simply be unavailable for SHH-pathway
   lung-developmental targets and switch to motif + accessibility
   inference.
3. **The "indirect_human_evidence" label is now too coarse.** The
   audit's previous v0 found 4 pairs at this tier and treated them
   uniformly. Peak intersection splits them sharply: 2 pairs validate
   at the target locus, 2 pairs do not. The audit should propagate
   this distinction.

The bigger picture remains: the lung-developmental regulatory chain
(NKX2-1 / SOX2 / SOX9 / CTNNB1) still has zero ENCODE TF ChIP, and
the ChIP-Atlas finding shows that broader public ChIP exists for those
regulators in non-lung contexts. The natural sequence from here is:

1. Add ChIP-Atlas as a fourth audit source (extends
   `gain_evidence_audit_extended.py`).
2. Re-run peak intersection on the 21 NKX2-1 / 95 SOX2 / 27 SOX9 /
   78 CTNNB1 / 42 SMAD1 / 4 GLI2 ChIP-Atlas experiments at the
   canonical target loci.
3. The result is the first end-to-end "what does the public-data
   record actually support" audit for the lung-developmental
   regulatory chain.

That is a much bigger session and is **not v0 work**. The smallest
useful artifact for this turn is the four-pair peak audit committed
here.

## Reproducing this audit

```sh
python3 scripts/gain_peak_intersection.py
```

Stdlib only. ~10 ENCODE GETs (4 experiment metadata + 4 BED downloads
+ a couple of probes). Total runtime ~ 10-20 s. Output:
[`metadata/peak_intersection_results.csv`](../metadata/peak_intersection_results.csv).
