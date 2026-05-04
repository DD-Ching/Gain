# NKX2-1 Final-Gap Search — Result

**Run:** 2026-05-04 (UTC)
**Output:** [`metadata/nkx21_external_search.csv`](../metadata/nkx21_external_search.csv)
**Design contract:** [`notes/nkx21_final_gap_design.md`](nkx21_final_gap_design.md)

## The deliverable answers

### Was a usable non-cancer human NKX2-1 ChIP-seq source found?

**No.** The audit's target — primary human lung tissue / fetal lung /
lung organoid / AT2-cell NKX2-1 ChIP-seq, deposited and downloadable
— **does not exist in GEO or SRA** as of these searches.

Three searches were run in parallel:

1. **NCBI GEO E-utilities** with `(NKX2-1 OR TTF-1 OR TITF1)[Title] +
   ChIP-seq + Homo sapiens[Organism]`. 27 GEO series total.
2. **NCBI SRA E-utilities** with the same boolean. 256 SRA records.
3. **Targeted WebSearch** for "NKX2-1 ChIP-seq primary AT2 fetal lung
   organoid 2024-2026".

After cross-checking and deduplication, there are **four candidate
series whose titles or summaries hinted at the gap-filler we want**.
Each fails on inspection:

| Accession | Why it failed |
|---|---|
| **GSE239270** (2025) | Title mentions FOXA2 + NKX2-1 + CTCF + P300 + H3K27ac + H3K4me1 reprogramming. **Summary clarifies it is castration-resistant prostate adenocarcinoma → NEPC transdifferentiation plus LUAD-to-SCLC**. Cancer context, not primary tissue. |
| **GSE84273** (2019) | Series name promises "Human Alveolar Cell Epigenomes". **Inspection of the 16 samples shows FAIRE-seq + H3K27ac ChIP + H3K4me1 ChIP + RNA-seq across primary AT2 / transitional / AT1 cells — but ZERO NKX2-1 ChIP-seq samples**. Useful for orthogonal histone work; does not close this gap. |
| **GSE83310** (2017) | iPSC-derived NKX2-1+ progenitors + week-21 human fetal lung + neural NKX2-1+ controls. **Assay is Affymetrix microarray expression profiling, not ChIP-seq**. Beautiful expression-correlation substrate; off-target for this audit. |
| **GSE23043** (2011) | "Chip-on-chip analysis of direct Nkx2.1 target genes in proliferating and differentiating epithelium in mouse lung development." **Mouse, not human; ChIP-on-chip microarray, not ChIP-seq.** Out of scope on both axes. |

The remaining 23 of 27 GEO series are **cancer cell line NKX2-1
ChIP-seq** — A549, NCI-H441, NCI-H1299, NCI-H209, NCI-H3122,
NCI-H2087, HCC1819, the SRX12008* small-cell-lung-cancer series, etc.
These are the substrate already in `metadata/cache/chipatlas_*.tab` and
audited by the four previous NKX2-1 audits (`gain_nkx21_audit*.py`).

The 256 SRA records map back to the same 27 GEO series (multi-
replicate experiments inflate the SRA count). Confirmed by
spot-checking SRX UIDs against the 21 SRX list in
`scripts/gain_nkx21_audit.py`.

The targeted WebSearch surfaced organoid and AT2-cell papers from
2022–2025 that use **scRNA-seq, ATAC-seq, or ChIP-qPCR** — not
genome-wide NKX2-1 ChIP-seq. No 2024-2026 paper deposited a primary-
tissue NKX2-1 ChIP-seq dataset.

**Bottom line:** the cancer-line-only constraint we have been working
under is the **actual public-data state**, not an artefact of the
ChIP-Atlas snapshot. The NKX2-1 audit's previous caveats — "developmental
binding remains untested in human public data" — stand without
revision.

### Does FOXA2 still remain the strongest next bridge target?

**Yes.** Nothing in this audit changes the histone-filtered ranking.
The strongest single candidate locus remains **FOXA2 chr20:22,716,796–
22,717,928** (NKX2-1 bed10=7 + 3 H3K27ac peaks + 2 H3K4me1 peaks in
human adult lung tissue), per
[`notes/nkx21_histone_filtered_candidates.md`](nkx21_histone_filtered_candidates.md).

Two FOXA2 strong candidates retain chromatin support; ABCA3 has only
1 retained; SCGB1A1 has 2 retained; SFTPC has 0. FOXA2's emergence as
the highest-priority follow-up target is a robust finding from the
histone filter and is **independent** of whether new primary-tissue
NKX2-1 ChIP exists.

### Does NKX2-1 deserve one more integration pass, or hand off to SOX2 / SOX9?

**Hand off.** The NKX2-1 audit cycle has reached the end of what can
be done with current public data:

- v0 ENCODE-only audit established the cancer-context ChIP gap.
- ChIP-Atlas integration broadened the source layer.
- Peak-level intersection on the SMAD1/GLI2 indirect pairs validated
  the audit machinery.
- The proximal-promoter NKX2-1 audit + sensitivity sweep + distal-
  candidate audit + histone-support filter together produced 5
  chromatin-supported candidate loci across 4 targets (FOXA2 ×2,
  SCGB1A1 ×2, ABCA3 ×1).
- This final gap search confirms that **no primary-tissue NKX2-1
  ChIP-seq exists publicly** to close the cancer-vs-developmental
  separation.

The remaining gap can only be closed by **new wet-lab ChIP-seq** in
primary AT2 / fetal lung / lung organoid contexts. That is not a
public-data audit problem; it is a wet-lab problem. The audit machinery
can immediately apply itself to **SOX2 and SOX9** with no new design
work, and those audits will likely surface different evidence
landscapes (SOX2 has 95 hg38 ChIP-Atlas experiments — many in
ESC/neural; SOX9 has 27, many in skeletal/cartilage). The bridge work
should continue along the regulatory chain rather than re-litigating
NKX2-1's developmental data gap.

The 5 chromatin-supported NKX2-1 candidates are now the **standing
candidate set** for any future primary-tissue NKX2-1 ChIP integration:
when such data appears (in some future ChIP-Atlas refresh or new
deposition), the test is straightforward — do the new peaks fall on
those 5 loci?

## Caveats and what this audit deliberately does *not* claim

- **Search exhaustiveness.** Three searches across GEO, SRA, and a
  targeted web search are not equivalent to a full literature review.
  A primary-tissue NKX2-1 ChIP-seq dataset deposited with an
  unconventional title (e.g. "AT2-specific transcription factor
  binding map") might not have surfaced. **However:** none of the
  obvious queries surface anything. The probability that a substantial
  primary-tissue NKX2-1 ChIP-seq dataset is hiding in plain sight is
  low.
- **Recent preprints.** bioRxiv / medRxiv preprints not yet indexed by
  GEO are not covered. A 2026 preprint with primary-tissue NKX2-1
  ChIP-seq may exist but be invisible to this audit.
- **Non-public data.** Consortia-internal data (LungMAP, Human Cell
  Atlas, individual labs' unreleased data) are out of scope by
  definition.
- **The "no usable source" conclusion is a present-tense claim.** It
  describes what is in GEO/SRA today; it does not claim no such data
  exists in the world.

## Reproducing this audit

```sh
# E-utilities, no auth required
curl 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gds&term=(NKX2-1[Title]+OR+TTF-1[Title]+OR+TITF1[Title])+AND+ChIP-seq+AND+homo+sapiens[Organism]&retmax=50&retmode=json'
curl 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=sra&term=(NKX2-1+OR+TTF-1)+AND+ChIP-seq+AND+homo+sapiens[Organism]&retmax=300&retmode=json'

# Targeted-biosample variants
curl 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gds&term=NKX2-1+primary+lung+AND+ChIP-seq+AND+homo+sapiens[Organism]&retmode=json'
curl 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gds&term=NKX2-1+lung+organoid+AND+ChIP-seq+AND+homo+sapiens[Organism]&retmode=json'
```

No script committed for this audit (the searches are one-shot enough
that codifying them adds no value); the CSV records the meaningful
hits and their evaluation.

## What changed and what didn't

**Changed:** the project's understanding of the public-data state.
Before this pass, the cancer-line-only constraint could plausibly have
been a ChIP-Atlas snapshot artefact. After this pass, that explanation
is ruled out — the constraint reflects the actual GEO/SRA state.

**Did not change:** the candidate ranking. FOXA2 remains the strongest
follow-up target; ABCA3 weakens after histone filtering; SFTPC remains
the weakest. The 5 chromatin-supported candidates retain their tier
and ranking from the histone-filter pass.
