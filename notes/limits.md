# Limits — what the v0 manifest CLI does *not* do

Recording these explicitly so neither future-us nor anyone reading the repo
mistakes the manifest for something it isn't.

## Curation, not validation

- Entries in `metadata/sources.json` are **pointers**, not validated
  accessions. Each `programmatic_access` URL has been spelled correctly
  and the relevant API documented; **none have been programmatically
  hit and confirmed to return data right now**.
- The `notes` field flags datasets that should be re-verified before use
  (e.g., "Verify Census coverage; if absent, fall back to GEO accession.").
- We have not asserted that any specific dataset_id, accession ID, or
  experiment ID exists in its portal. We name papers and queries; we do
  not name accession IDs we have not personally fetched.

## No live data fetches

- The CLI does **zero HTTP** in v0.
- No download of `.h5ad` files, no Census `obs.read()`, no ENCODE
  `/search/?...&format=json` calls. That is v1 work.

## No analysis

- No expression matrices loaded, no markers computed, no embeddings
  drawn, no trajectory inference.
- No regulator-target inference. The NKX2-1 → SOX2/SOX9 → FGF10/WNT/BMP/SHH
  axis is the *organizing question*, not something v0 *outputs evidence
  about*.

## Coverage gaps in the seed entries

- **Embryonic / pseudoglandular stages** are under-represented; LungMAP
  is the place to fill this in but the v0 entries point at the consortium
  rather than specific stage-resolved projects.
- **Mouse developmental coverage** is one entry (LungMAP mouse). ENCODE
  mouse lung data is not yet enumerated.
- **Spatial transcriptomics** is mentioned only via He 2022; broader
  spatial coverage (Visium, Slide-seq, etc.) is unaddressed.
- **Proteomics / mass-spec** from LungMAP is not included as a separate
  entry; only the umbrella consortium is referenced.

## Scope choices we deliberately made

- **One CLI, one subcommand.** No subcommand framework, no plugin system.
- **Stdlib only.** No PyYAML, no Pydantic, no Click, no Rich. JSON in,
  CSV/JSON/Markdown out.
- **Outputs in-tree.** The generated manifest lives in `metadata/` and is
  committed to git so GitHub browsers can see it without running anything.
- **No tests yet.** The smoke test is "the script runs and produces the
  expected three files." Add real tests when there is a behavior worth
  pinning (e.g., the v1 HTTP fetcher).

## Things that look like features but are intentional non-features

- No `--source CELLxGENE` filter. If you want only Census rows, grep the
  CSV. The manifest is small.
- No interactive UI. The manifest is a file you read; we do not need a
  web app.
- No schema-versioned upgrade path. `schema_version: "0.1"` is in
  `sources.json` so future-us can branch behavior, but we have not
  written any compatibility shim and will not until v0.2 lands.
