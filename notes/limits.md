# Limits — what the current artifacts do *not* do

Recording these explicitly so neither future-us nor anyone reading the repo
mistakes the manifest, verifier, or switch-hierarchy explorer for something
they aren't.

## Curation, not validation

- Entries in `metadata/sources.json` and edges in
  `metadata/switch_hierarchy.csv` are **pointers**, not validated
  accessions. The verifier (`scripts/gain_verify.py`) probes whether the
  URL responds at all; it does **not** check that the URL returns the
  *right* data.
- The `notes` field in `sources.json` flags datasets that should be
  re-verified before use (e.g., "Verify Census coverage; if absent,
  fall back to GEO accession.").
- We have not asserted that any specific dataset_id, accession ID, or
  experiment ID exists in its portal. We name papers and queries; we do
  not name accession IDs we have not personally fetched.

## What the verifier does and does not catch

- **Catches:** unreachable URLs, 4xx/5xx status codes, timeouts, TLS
  errors, content-type changes (recorded in `verification.json`), rate-
  limit responses (429).
- **Does not catch:** schema drift inside a 200 OK payload (e.g., a
  field renamed from `target.label` to `target.genes.symbol`), data
  staleness (a portal serving last year's snapshot), or licensing
  changes. Those still require human attention.
- The first live run found **3 ENCODE TF-ChIP search URLs returning 404
  and SCREEN returning 429** — see `metadata/verification.json`. Those
  are documented in `notes/roadmap.md` as v0.x hygiene items, not
  silently masked.

## No analysis on data, only on metadata

- No expression matrices loaded, no markers computed, no embeddings
  drawn, no trajectory inference.
- The switch-hierarchy explorer joins **hand-curated edges** to
  manifested sources; it does not derive node-source links from
  expression statistics or regulator-binding evidence. The
  `evidence_one_liner` per row is editorial, not computational.
- No regulator-target inference. The NKX2-1 → SOX2/SOX9 → FGF10/WNT/BMP/SHH
  axis is the *organizing question*, not something the current artifacts
  *output evidence about* in a quantitative sense.

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
- **Switch-hierarchy node coverage** is the nine canonical players in
  the NKX2-1 → SOX2/SOX9 → FGF10/WNT/BMP/SHH chain. Adjacent regulators
  (FOXA2, GATA6, ID2, ETV5, BMP receptors, FGFR2b) are deliberately
  left out of v1.5 to keep curation honest.

## Scope choices we deliberately made

- **One script per concern.** Three scripts, no subcommand framework,
  no plugin system, no shared CLI parser.
- **Stdlib only.** No PyYAML, no Pydantic, no Click, no Rich, no
  requests. JSON / CSV in, CSV / JSON / Markdown out.
- **Outputs in-tree.** Generated manifests, verification reports, and
  the switch-hierarchy report all live in the repo so GitHub browsers
  can see them without running anything.
- **No tests yet.** The smoke test is "each script runs and produces
  the expected output files." Add real tests when there is behavior
  worth pinning (e.g., when the verifier grows a drift-classification
  rule, or when the manifest schema changes).

## Things that look like features but are intentional non-features

- No `--source CELLxGENE` filter on the manifest CLI. If you want only
  Census rows, grep the CSV. The manifest is small.
- No automatic re-verification on commit. Run `gain_verify.py`
  manually; we have not added a CI job because there is nothing in CI
  yet.
- No interactive UI. Each output is a file you read.
- No schema-versioned upgrade path. `schema_version: "0.1"` is in
  `sources.json` so future-us can branch behavior, but we have not
  written any compatibility shim and will not until v0.2 lands.
