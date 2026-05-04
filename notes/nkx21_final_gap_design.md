# NKX2-1 Final-Gap Search — Design

**Status:** design contract for a narrow existence-and-usability audit.
This is **not** a literature review or a re-analysis. The single
question: **does any usable non-cancer human NKX2-1 (TTF-1) ChIP-seq
source exist outside the ChIP-Atlas hg38 snapshot we have already
audited?**

If yes → flag it; recommend one more integration pass before handing
off to SOX2 / SOX9.

If no → confirm that the cancer-line-only constraint we have been
working under is actually the public-data state, and hand off.

## What is in scope

Search only for sources that satisfy *all* of:

- **Regulator: NKX2-1** (a.k.a. **TTF-1**, **TITF1**) — accept any of
  these synonyms.
- **Assay: ChIP-seq.** ChIP-exo and CUT&RUN / CUT&Tag accepted as
  near-substitutes; flagged separately.
- **Organism: human (*Homo sapiens*).** Mouse and other organisms
  excluded — this audit is specifically about closing the human-
  primary-tissue gap.
- **Biosample category: non-cancer**, ideally one of:
  - primary human lung tissue
  - fetal / embryonic human lung
  - human lung organoid (iPSC-derived or primary-derived)
  - AT2 / alveolar epithelial cells (sorted, primary or organoid)
  - bronchial / airway epithelial primary cells (NHBE, HSAEC, HBEC)

Cancer cell line entries (the 21 already-known ChIP-Atlas hits) are
explicitly **excluded** — they are the baseline, not the goal.

## What is *out* of scope

- Mouse NKX2-1 ChIP (regardless of biosample).
- Thyroid NKX2-1 ChIP (NKX2-1 is also a thyroid TF; non-lung context).
- ATAC-seq / DNase-seq / Histone ChIP for lung tissue (already
  inventoried in `metadata/sources.json` and used in the histone
  filter).
- A full literature scan, paper-by-paper. The audit only records
  sources we can verify exist with metadata.
- Any re-analysis, peak calling, or downstream comparison. v0 is
  existence + usability only.

## Search strategy

Three lightweight, programmatic approaches in parallel:

1. **NCBI GEO via E-utilities** (`eutils.ncbi.nlm.nih.gov`). Stdlib
   urllib hits to the public esearch endpoint. Query DB = `gds`
   (GEO datasets), with a targeted boolean for NKX2-1 / TTF-1 / TITF1
   ChIP-seq human, restricted to recent publication windows.
2. **NCBI SRA via E-utilities** (DB = `sra`). Same boolean.
3. **WebSearch** for "NKX2-1 ChIP-seq primary lung", "TTF-1 ChIP fetal
   lung", "AT2 cell NKX2-1 ChIP", "lung organoid NKX2-1 ChIP" —
   targeted phrases to surface recent papers / dataset accessions.

**Stopping condition.** As soon as I can answer the audit question
with a clear yes / no / partial, stop. Do not exhaustively enumerate
hits.

## What counts as a "hit" worth recording

A search result becomes a row in `metadata/nkx21_external_search.csv`
if:

- It names a specific accession (GSE / SRX / SRP / PRJNA) **and**
- The associated experiment is plausibly **NKX2-1 ChIP-seq in human
  non-cancer lung context**, based on title or sample description.

A search result is NOT a hit if it is:

- A computational paper that reuses an existing ChIP-Atlas accession
  (would already be in our list).
- A meta-analysis or review without a new accession.
- An NKX2-1-related paper that uses a different assay (RNA-seq,
  scRNA-seq, knockdown without ChIP).

## What counts as "usable"

For each hit, record three signals:

1. **Raw data downloadable?** GEO/SRA accession returns 200 with
   metadata; ideally the raw BED / BAM / FASTQ is publicly hosted.
2. **Post-ChIP-Atlas snapshot?** ChIP-Atlas's antigenList.tab snapshot
   typically lags upstream GEO by 6–18 months. Hits with public dates
   in 2024 or later are likely post-snapshot; older hits should be in
   ChIP-Atlas already (cross-check against our 21 SRX list).
3. **Worth integrating next?** Editorial judgement: yes / no /
   maybe. A "yes" requires (a) non-cancer biosample confirmed by
   abstract or sample description, (b) raw data available, (c) post-
   snapshot.

## Output schema

`metadata/nkx21_external_search.csv` — one row per hit:

| column | meaning |
|---|---|
| accession | GSE / SRX / SRP / PRJNA / paper DOI |
| paper_title_or_dataset_title | short title |
| sample_type | e.g. `primary_lung_tissue`, `fetal_lung`, `lung_organoid`, `AT2_cells`, `airway_epithelial`, `mixed`, `unclear` |
| organism | `human` / `non-human` |
| cancer_status | `non-cancer` / `cancer` / `unclear` |
| developmental_window | `fetal` / `adult` / `organoid` / `mixed` / `unclear` |
| raw_data_apparently_available | `yes` / `no` / `unclear` |
| likely_post_chipatlas_snapshot | `yes` / `no` / `unclear` |
| in_existing_chipatlas_set | `yes` / `no` (cross-checked against the 21 SRX list) |
| worth_integrating_next | `yes` / `maybe` / `no` |
| rationale | one short line |
| source_url | the GEO/SRA/DOI URL used to verify |

If zero hits qualify, the CSV is written with the header row only;
the report explains what was searched and why nothing qualified.

## Output report

`notes/nkx21_final_gap.md`:

- The 3 user-stated questions, answered:
  - Was a usable non-cancer human NKX2-1 ChIP source found?
  - Does FOXA2 still remain the strongest next bridge target?
  - Does NKX2-1 deserve one more integration pass, or hand off?
- Brief summary of what was searched and what was found.
- For each `worth_integrating_next == yes` hit (if any): why.
- Recommendation: integrate or hand off.

## Anti-overclaim rules

- **Abstracts overstate.** Do not record "NKX2-1 ChIP in fetal AT2
  cells" unless the dataset metadata explicitly confirms the assay
  and biosample. If only the abstract suggests it, mark
  `cancer_status=unclear` and `worth_integrating_next=maybe`.
- **Recency does not equal relevance.** A 2025 paper is post-snapshot,
  but if it uses A549 cells the dataset is not the gap-filler we are
  looking for.
- **Single-experiment claims need caution.** Even if one usable hit is
  found, integrating one experiment cannot establish the
  developmental claim — but it does converts the audit from "all
  cancer-line" to "≥ 1 non-cancer", which is a meaningful evidence-
  state change.
- **Synonyms checked.** Both "NKX2-1" and "TTF-1" / "TITF1" must be
  searched; older deposits often used the latter.

## What v0 of this audit deliberately does *not* do

- No download of raw BED / FASTQ files. Accession existence is the
  audit's deliverable; integration is a separate (potential) followup.
- No paper-level full-text reading. Title, abstract, and sample-
  metadata only.
- No re-running of any existing audit — the previous CSVs stand.
- No cross-species lift-over.

## Implementation outline

A small one-shot script — no need for a long-lived tool. Could be a
Bash / curl pipeline + Python parsing, or a single Python script.
Per cadence rule: extend cleanly. The cleanest extension is a new
sibling script under `scripts/` whose only job is to issue the
E-utilities queries and emit the CSV. **No new infrastructure.**
