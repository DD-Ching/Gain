# HLCA & HCA

Two separate but related resources — one is a dataset, the other is the
consortium / broader portal it sits inside.

## HLCA — Human Lung Cell Atlas

**Reference:** Sikkema, Strobl, *et al.*, "An integrated cell atlas of the
human lung in health and disease," *Nature Medicine* 29:1563-1577, 2023.

### What it is

A **scANVI-integrated reference atlas** of ~2.4M cells from ~486 individuals,
combining 14 published datasets. Maintained as the standard reference for
adult human lung cell identity. Provides "core" (healthy) and "extended"
(disease) annotations.

### What problem it solves

- Standardized cell-type annotations (~58 cell types in the v1 core).
- Reference for label transfer onto new lung datasets (using scANVI).
- Fast comparison across donors and disease states.

### What it cannot solve

- **Developmentally biased toward adult.** Embryonic / fetal lung is *not*
  the focus — we still need fetal atlases (He 2022, Cao 2020) for the
  NKX2-1 → SOX2/SOX9 switch period.
- Doesn't include regulatory-element data.
- Annotation is shaped by integration choices — query carefully.

### Programmatic access

- Discover via **CELLxGENE Census** (`tissue_general == 'lung'`,
  filter to the HLCA core/extended `dataset_id`s).
- Direct download of the integrated `.h5ad` from the CELLxGENE Discover
  collection page.
- scANVI label-transfer model is published; can be re-loaded with scvi-tools.

### Reuse strategy

**Reuse directly.** HLCA is the de-facto adult-lung reference; we should
*name and pin* the HLCA dataset IDs in our manifest, not re-curate.

**Reuse priority:** high — if and only if the chosen MVP cares about adult
lung. For pure developmental work, HLCA is a baseline, not the focus.

---

## HCA — Human Cell Atlas

**Site:** <https://data.humancellatlas.org/>

### What it is

The umbrella consortium for cross-organ human single-cell atlases. Provides
the **HCA Data Browser** (built on the Azul framework) for project-level
metadata + bulk file download.

### What problem it solves

- Cross-organ context (when we want to ask "is this lung-specific or shared
  with other endoderm-derived tissues?").
- Centralized download of project-level matrix files.
- Source of multiple human fetal-lung scRNA-seq projects (those projects
  also typically appear in CELLxGENE Census).

### What it cannot solve

- HCA itself is metadata + file delivery, **not** a query layer over cell
  annotations — for that, use CELLxGENE Census.
- Per-project schemas differ; harmonization is the user's problem unless
  the project was also ingested into Census.

### Programmatic access

- Azul REST API (project / sample / file endpoints, JSON responses).
- Pagination + faceted filtering documented at the Data Browser API page
  (verify exact base URL at use time — Azul instance subdomains change).

### Reuse strategy

**Reuse via Census first.** Only hit the HCA Azul API directly if a
needed dataset is *not* in Census, or if we need file-level download
provenance.

**Reuse priority:** medium — fallback for datasets Census doesn't index.
