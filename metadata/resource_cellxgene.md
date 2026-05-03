# CELLxGENE Census

## What it is

A **standardized programmatic access layer** over the CZ CELLxGENE Discover
corpus of single-cell RNA-seq datasets. Built on the SOMA specification via
TileDB-SOMA. Exposed as long-term-supported snapshot releases (e.g.
`2025-11-08`).

Backed by **Chan Zuckerberg Initiative**.

## What problem it solves

- Removes per-portal scraping: one query returns standardized cell-by-gene
  matrices and aligned cell metadata across hundreds of datasets.
- Standardizes cell-type, tissue, disease, and developmental-stage ontology
  fields (CL, UBERON, HsapDv).
- Provides typed Python (`cellxgene-census`) and R clients backed by Arrow,
  pandas, AnnData, Seurat, and SingleCellExperiment.

## What it cannot solve

- **No regulatory genomics data.** scRNA-seq only — no ChIP-seq, ATAC-seq,
  or cCREs. Use ENCODE/SCREEN for that.
- **No spatial / imaging data** (spatial support is incoming for select
  datasets but not the focus).
- Developmental coverage is **inherited from underlying datasets** — most
  cells are adult, fetal/embryonic coverage is partial. Filter on
  `development_stage_ontology_term_id` to find what exists.
- **Duplicate cells** across datasets — must filter `is_primary_data == True`
  for cleaner analyses.

## Programmatic access

```python
import cellxgene_census
with cellxgene_census.open_soma(census_version="stable") as census:
    obs = census["census_data"]["homo_sapiens"].obs.read(
        value_filter="tissue_general == 'lung'",
        column_names=["cell_type", "development_stage", "dataset_id",
                      "donor_id", "is_primary_data"],
    ).concat().to_pandas()
```

- Python: `pip install cellxgene-census` (depends on `tiledbsoma`)
- R: dedicated R API
- Snapshots versioned by date; "stable" pins the current LTS

Verified URL: <https://chanzuckerberg.github.io/cellxgene-census/>

## Reuse strategy

**Reuse directly. Do not wrap.** Census is the canonical entry point for
adult and (some) developmental human lung scRNA-seq. Our role is to *cite
specific Census queries* in the manifest, not to abstract Census away.

**Reuse priority for Gain:** highest. Plan to make this the primary scRNA-seq
source for any MVP that needs expression data.
