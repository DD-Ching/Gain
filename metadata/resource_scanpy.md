# Scanpy

**Site:** <https://scanpy.readthedocs.io/>
**Install:** `pip install scanpy` (also on conda-forge)
**Part of:** scverse ecosystem; sponsored by NumFOCUS.

## What it is

The standard-of-care Python toolkit for scRNA-seq analysis. Built jointly
with **AnnData**, the annotated data-matrix container that the entire
scverse stack speaks. Handles preprocessing, embedding, clustering,
differential expression, trajectory inference, and visualization.

## What problem it solves

- Pre-built `sc.pp`, `sc.tl`, `sc.pl` functions for the routine scRNA-seq
  workflow.
- AnnData round-trips with CELLxGENE Census, scvi-tools, and most
  modern single-cell tools — zero glue code needed.
- Scales into the millions of cells with optional Dask backing.

## What it cannot solve

- Not a data source — bring your own AnnData (typically from Census).
- Not opinionated about *which* method to use; the user chooses
  PCA/Harmony/scVI/etc.
- Visualizations are static matplotlib; not built for interactive UIs.

## Programmatic access

It *is* a Python library — you import it. No HTTP API.

Common shape:
```python
import scanpy as sc
adata = sc.read_h5ad("hlca.h5ad")
sc.pp.normalize_total(adata)
sc.pp.log1p(adata)
sc.pp.highly_variable_genes(adata, n_top_genes=3000)
sc.tl.pca(adata)
sc.pp.neighbors(adata)
sc.tl.umap(adata)
```

## Reuse strategy

**Reuse directly. Do not wrap.** If we need analysis routines on AnnData,
they go in `scripts/` as small Scanpy-using scripts, not abstractions
over Scanpy.

**Reuse priority:** depends on MVP. For dataset-manifest CLI v0:
**not needed** (no analysis happens — only metadata aggregation). For
lung-switch-explorer or evidence-map: high.
