# scvi-tools

**Site:** <https://docs.scvi-tools.org/>
**Install:** `pip install scvi-tools`
**Part of:** scverse; primarily developed by the Yosef Lab.
**Stack:** PyTorch, PyTorch Lightning, Pyro.

## What it is

Probabilistic models for single-cell omics, packaged as a coherent library.
Headline models: **scVI** (denoising / latent-space VAE), **scANVI**
(semi-supervised label transfer — used to build HLCA), **totalVI** (CITE-seq),
plus several others.

## What problem it solves

- Reference-based label transfer onto a new dataset (scANVI + HLCA model
  → automatic cell-type annotations on new lung samples).
- Batch-corrected latent representations for integrating multi-donor or
  multi-study cohorts.
- Reproducible inference instead of bespoke per-paper integration scripts.

## What it cannot solve

- No data; bring your own AnnData.
- GPU strongly recommended for non-trivial datasets; CPU works for tiny
  data and inference but training is slow.
- Models are powerful but opaque — not a substitute for understanding
  the underlying biology.

## Programmatic access

Python library; no HTTP API. Typical scANVI label-transfer flow:

```python
import scvi
scvi.model.SCANVI.prepare_query_anndata(query_adata, reference_model)
vae_q = scvi.model.SCANVI.load_query_data(query_adata, reference_model)
vae_q.train(max_epochs=20, plan_kwargs={"weight_decay": 0.0})
query_adata.obs["predicted_labels"] = vae_q.predict()
```

## Reuse strategy

**Reuse directly when needed. Do not wrap.** No project-specific
abstraction over scvi-tools is justified for v0.

**Reuse priority:**
- dataset-manifest CLI v0 → **not needed.**
- lung-switch-explorer / marker-to-regulator → medium (label transfer
  onto new lung data may be useful).
- Add only when a concrete script demands it.
