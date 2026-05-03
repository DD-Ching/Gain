# LungMAP

**Site:** <https://www.lungmap.net/>
**Data Explorer:** <https://data-browser.lungmap.net/>
**API page:** <https://data-browser.lungmap.net/apis>
**Funder:** NHLBI; coordinated by Cincinnati Children's Hospital.

## What it is

The NHLBI Molecular Atlas of Lung Development consortium. Collects and
publishes molecular and imaging data across **lung development** in mouse
and human. Multi-modal: scRNA-seq, multiplexed imaging (OMERO), proteomics
/ mass spec, ontology resources (Lung CellCards).

For the Gain project this is **the highest-signal source for the
developmental window** that adult atlases (HLCA) underweight.

## What problem it solves

- Lung-development-focused data: explicit coverage of embryonic,
  pseudoglandular, canalicular, saccular, and alveolar stages.
- Cross-modal: scRNA-seq paired with imaging and (some) proteomics on the
  same cohorts.
- Lung CellCards: curated cell-type definitions specific to lung biology
  with marker genes, useful as a sanity-check against Census-derived markers.

## What it cannot solve

- Less standardization across datasets than CELLxGENE Census; expect
  per-project metadata drift.
- Smaller integrated cell counts than HLCA — single-cell N is per-project,
  not pooled into a single integrated reference.
- Imaging access is via OMERO (separate workflow from the scRNA-seq stack).

## Programmatic access

- **REST API via Azul Data Browser** (same framework as HCA Data Browser).
  Documented at the API page above. Endpoints follow the Azul shape:
  `/index/projects`, `/index/samples`, `/index/files`.
- Confirmed access pattern: GET requests, JSON responses, faceted filtering
  + pagination.
- **Verify the live LungMAP-specific Azul base URL at use time** — the
  documentation page references a generic Azul service URL; the
  LungMAP-specific subdomain may differ. Cross-check with the
  Network requests visible in the data browser if needed.
- OMERO API for imaging is a separate channel; out of scope for v0.

## Reuse strategy

**Reuse the REST API directly for metadata lookups.** Treat it as a
metadata source for the manifest. Defer image-level work entirely until
there is a proven reason to include it.

**Reuse priority:** high for any developmental-stage manifest entries.
This is the source we cite when answering "what fetal/postnatal lung
dataset exists for stage X?"
