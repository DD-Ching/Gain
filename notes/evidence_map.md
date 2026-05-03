# Evidence Map

## Project goal

Build a small, useful, open-source research-engineering contribution around the
**middle-layer control logic of human lung development**. Use existing public
data, portals, and tools — do not reinvent atlases, single-cell pipelines, or
regulatory-element databases. Ship one concrete artifact that fills a real gap
between "raw data exists" and "the question I want to answer is one command away."

## Scientific scope

The regulatory backbone we want to make tractable:

```
NKX2-1
   │  (master lung-epithelial identity)
   ▼
SOX2 / SOX9
   │  (proximal vs distal progenitor fate)
   ▼
FGF10 · WNT · BMP · SHH
   │  (mesenchyme ↔ epithelium signalling)
   ▼
airway program  /  alveolar program
```

We are not trying to re-derive this network. We are trying to make it
**queryable, evidence-grounded, and reproducible** at the level of public
human (and where appropriate mouse) data.

Out of scope for v0:
- novel wet-lab biology
- novel statistical methods
- disease cohorts (IPF, COVID, cancer) unless they directly clarify development

## Public resources to inspect first

Before writing code, we audit what already exists. These are the entry points.

### Single-cell / tissue atlases

- **HLCA — Human Lung Cell Atlas** (Sikkema et al., *Nat Med* 2023)
  - integrated reference of adult human lung, ~2.4M cells, ~486 individuals
  - hosted on CELLxGENE; built with scvi-tools/scANVI
  - check: developmental coverage is thin — adult-biased
- **HCA — Human Cell Atlas** (umbrella)
  - lookup point for cross-organ standardized datasets
- **Human fetal lung atlases**
  - He et al. 2022 (*Nat Genet*) — fetal lung scRNA-seq + spatial
  - Cao et al. 2020 (*Science*) — pan-fetal cell atlas
  - check for organoid + primary-tissue concordance
- **LungMAP** (lungmap.net)
  - NIH consortium; mouse + human developmental data
  - has scRNA-seq, IF imaging, mass-spec; documented REST API
  - probably the highest-signal source for *developmental* lung
- **CELLxGENE Census** (cellxgene.cziscience.com/census)
  - programmatic standardized access via tiledbsoma (Python + R)
  - lets us pull tissue=lung, dev_stage=fetal, etc., without per-portal scraping

### Regulatory genomics

- **ENCODE** (encodeproject.org)
  - ChIP-seq, ATAC-seq, RNA-seq across human + mouse tissues/lines
  - check for NKX2-1, SOX2, SOX9, FGF10-locus regulatory data
- **SCREEN / cCREs** (screen.wenglab.org)
  - candidate cis-regulatory elements indexed across ENCODE
  - good for "what regulatory elements sit near gene X in lung tissue?"

### Tooling we will reuse, not rebuild

- **Scanpy** — standard scRNA-seq analysis
- **scvi-tools** — probabilistic models (scVI, scANVI) — already powers HLCA
- **anndata / tiledbsoma** — data containers for (1) and Census

Anything we add must beat what these already provide for our specific question.

## Initial guesses of useful deliverables

Four candidate MVPs. Each will be sized in `next_steps.md` and one chosen.

1. **Dataset-manifest CLI** — `gain inventory`
   - small Python CLI that queries CELLxGENE Census + LungMAP API and emits a
     machine-readable manifest (YAML/JSON) of lung datasets:
     accession, donor count, n_cells, dev_stage, tissue region, license, URI
   - filter on developmental relevance to the NKX2-1/SOX2/SOX9 axis
   - pain it removes: today this is manual portal-clicking
   - smallest viable scope; high reuse leverage for the next three ideas

2. **Lung-switch-explorer**
   - given a Census query, plot the SOX2/SOX9 ratio (and NKX2-1 expression)
     along annotated developmental stage / pseudotime
   - identify the proximal-vs-distal bifurcation point
   - mostly Scanpy on top of existing data; value is the framing + reproducibility

3. **Marker-to-regulator linker**
   - take cell-type markers (from CELLxGENE) → intersect with ENCODE TF ChIP-seq
     peaks and SCREEN cCREs in lung tissue → produce a ranked list of plausible
     upstream regulators per cell state
   - lung-specific, but the harder dependency stack

4. **Evidence-map generator**
   - given a regulatory claim ("NKX2-1 → FGF10"), assemble: ENCODE peaks at the
     locus, expression correlation in HLCA + fetal data, supporting PubMed IDs
   - highest user-facing value, highest scope risk; likely a v1, not v0

Selection bias: prefer the one with the highest ratio of
*(decision-grade output) / (lines of code + new dependencies)*.
That points at #1 first, with #2 as the natural follow-on.
