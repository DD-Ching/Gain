# NKX2-1 Distal Candidates — Results

**Run:** 2026-05-04 (UTC)
**Inputs:** same 21 NKX2-1 hg38 ChIP-Atlas experiments × 2 thresholds
(bed05 + bed10) as the sensitivity audit; 4 targets (SFTPC, SCGB1A1,
ABCA3, FOXA2)
**Output:** [`metadata/nkx21_distal_candidates.csv`](../metadata/nkx21_distal_candidates.csv)
**Script:** [`scripts/gain_nkx21_distal_candidates.py`](../scripts/gain_nkx21_distal_candidates.py)
**Design contract:** [`notes/nkx21_distal_candidate_design.md`](nkx21_distal_candidate_design.md)

## Summary

After greedy-merging NKX2-1 ChIP peaks within ± 200 kb of each
target's TSS (1 kb merge gap), restricted to the 50–200 kb distal
band, pooled across all 21 experiments and both thresholds:

| Target | Total loci | strong | moderate | weak | low_priority |
|---|---:|---:|---:|---:|---:|
| **SFTPC** | 17 | **1** | 3 | 3 | 10 |
| **SCGB1A1** | 26 | **3** | 7 | 8 | 8 |
| **ABCA3** | 29 | **4** | 3 | 11 | 11 |
| **FOXA2** | 29 | **3** | 5 | 9 | 12 |
| **Sum** | 101 | **11** | 18 | 31 | 41 |

**11 strong distal candidates** identified across the four targets,
plus **18 moderate** candidates. These are the loci worth flagging for
Hi-C / chromatin-contact / functional follow-up; the 31 weak and 41
low-priority candidates are not.

## The 11 strong distal candidates (ranked)

Sorted by `n_experiments_at_bed10` (high-confidence support count):

| Target | Locus (hg38) | Distance to TSS | Band | bed10 | bed05 | Pattern |
|---|---|---:|---|---:|---:|---|
| **FOXA2** | chr20:22,463,535–22,464,025 | +121,675 | 100–200 kb downstream | **8** | 12 | concentrated |
| **ABCA3** | chr16:2,490,817–2,491,230 | −150,274 | 100–200 kb upstream | **7** | 9 | concentrated |
| **FOXA2** | chr20:22,716,796–22,717,928 | −131,907 | 100–200 kb upstream | **7** | 8 | moderately_concentrated |
| **SCGB1A1** | chr11:62,497,136–62,497,594 | +92,262 | 50–100 kb downstream | **6** | 6 | concentrated |
| **ABCA3** | chr16:2,231,273–2,231,642 | +109,292 | 100–200 kb downstream | **5** | 8 | concentrated |
| **ABCA3** | chr16:2,399,387–2,399,683 | −58,786 | 50–100 kb upstream | **5** | 5 | concentrated |
| **SCGB1A1** | chr11:62,326,687–62,326,970 | −78,275 | 50–100 kb upstream | **5** | 6 | concentrated |
| **FOXA2** | chr20:22,390,152–22,390,606 | +195,076 | 100–200 kb downstream | **5** | 5 | concentrated |
| **SFTPC** | chr8:22,092,696–22,093,238 | −63,946 | 50–100 kb upstream | **5** | 7 | concentrated |
| **ABCA3** | chr16:2,155,403–2,155,753 | +185,171 | 100–200 kb downstream | **3** | 7 | concentrated |
| **SCGB1A1** | chr11:62,534,332–62,534,655 | +129,390 | 100–200 kb downstream | **3** | 10 | concentrated |

All 11 are supported entirely by `cancer_lung_line` biosamples (no
non-cancer experiments exist for NKX2-1 in ChIP-Atlas hg38). Ten of
eleven are `concentrated` (peaks converge within < 1 kb), one is
`moderately_concentrated`. None scattered.

## Which target has the strongest distal-candidate case?

The picture depends on the metric:

| Metric | Winner |
|---|---|
| Most **strong** candidates | **ABCA3** (4) |
| Single highest-support locus | **FOXA2** (chr20:22,463,535 — bed10=8, bed05=12) |
| Most moderate-or-better candidates | **SCGB1A1** (10 = 3 + 7) |

**Best overall case: ABCA3.** Four strong concentrated candidates,
all flanking the gene at distances 50–200 kb (one within 50–100 kb).
Multiple cell-line families contribute (visible in the SRX
distribution behind the support counts). If exactly one of the four
targets gets Hi-C / promoter-capture follow-up first, ABCA3 is the
highest-yield bet.

**Honourable mention: FOXA2.** The single strongest locus in the
audit (FOXA2 chr20:22,463,535, bed10=8/21, bed05=12/21). If the
question is "which individual locus is the best distal-candidate
element," FOXA2's downstream cluster wins.

## Which target still looks weakest?

**SFTPC.** Only 1 strong + 3 moderate distal candidates total — fewer
than half the count of any other target. The single strong candidate
(chr8:22,092,696, 50–100 kb upstream) is solid (bed10=5, concentrated)
but stands alone; SFTPC has no multi-strong-candidate cluster. This
is consistent with the sensitivity audit: SFTPC was the most robustly
weak target in the proximal-promoter test, and it remains the weakest
even after extending to the distal band.

## Caveats — read these before drawing conclusions

- **Candidates are candidates.** Every "strong" locus is a *candidate*
  regulatory element. None of the audit's outputs claim that any peak
  is an enhancer or that NKX2-1 binding at any of these loci regulates
  the target gene.
- **Cancer-line ChIP, again.** Every supporting experiment is a lung
  cancer cell line. The candidate list reflects what NKX2-1 binds in
  those contexts; it does not establish what NKX2-1 binds during lung
  development.
- **Distance ≠ contact.** Genomic proximity (50–200 kb) is necessary
  but not sufficient for regulatory contact with the target's
  promoter. Hi-C / 4C / promoter-capture data is required to confirm
  physical interaction.
- **A549 + lentiviral overexpression caveat.** Two of the 21
  experiments (SRX2164786, SRX2164788) overexpress NKX2-1 from a
  lentivirus in A549 cells. SRX2164786 contributes a
  disproportionately large peak count (53,092 at bed10). Strong
  candidates supported *primarily* by these two experiments may
  reflect overexpression artefact rather than physiological binding;
  the audit does not currently flag this in the tier rule, but
  curators should review the `supporting_experiment_ids` column for
  any candidate before lab follow-up.
- **Greedy merge is order-sensitive.** The 1 kb merge gap is a
  defensible default but not the only choice; tighter (e.g., 200 bp)
  merging would split some loci into multiple candidates, looser
  merging would collapse some.

## Should NKX2-1 get one more focused pass after this?

**Yes — one more.** Two concrete, lightweight followups are
naturally next:

1. **Cross-reference the 11 strong + 18 moderate candidate loci
   against ENCODE lung tissue histone ChIP-seq.** ENCODE has 59 lung
   Histone ChIP experiments (recorded in `metadata/sources.json`).
   Candidates that overlap H3K27ac or H3K4me1 peaks in any lung
   biosample become significantly more credible regulatory candidates;
   those without histone-mark support are more likely to be cancer-
   context-specific noise. This is a stdlib-only ENCODE-API +
   peak-overlap pass, similar in scope to
   `scripts/gain_peak_intersection.py`.
2. **Search GEO / NCBI for primary lung tissue or AT2-cell NKX2-1
   ChIP-seq deposited after the ChIP-Atlas snapshot.** The systemic
   absence of non-cancer NKX2-1 ChIP in ChIP-Atlas may reflect a
   stale snapshot rather than a true gap. Recent papers from
   Treutlein / Whitsett / Morrisey groups are the highest-yield
   candidates.

Either follow-up keeps the project narrow, lightweight, and grounded
in public data. After that, NKX2-1 should hand off to the broader
chain (SOX2 / SOX9 next; FGF10 / WNT / BMP / SHH later) — the audit
machinery is now mature enough to apply uniformly.

## What this audit does *not* claim

- No enhancer claim for any locus.
- No regulatory-mechanism claim for any locus.
- No claim that NKX2-1 directly regulates SFTPC, SCGB1A1, ABCA3, or
  FOXA2 through these candidate elements.
- No claim that "strong" tier candidates are functional; they warrant
  follow-up, not action.
- No claim that the 41 low-priority candidates are not real
  regulatory elements; they may be, but cancer-line single-experiment
  support does not justify lab investment over the better-supported
  candidates.

## Reproducing this audit

```sh
python3 scripts/gain_nkx21_distal_candidates.py
```

Stdlib only. 42 BED downloads (~ 60 MB total at bed05 + bed10),
~ 60–90 s runtime.
