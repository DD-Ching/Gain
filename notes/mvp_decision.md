# MVP Decision

**Date:** 2026-05-03
**Decision:** build the **dataset-manifest CLI** (`gain manifest`).
The other three candidates are deferred to v1.

## Why this MVP wins

The dataset-manifest CLI is the **smallest concrete artifact that would
unblock every other candidate.** Each of the deferred MVPs starts with the
same question: *"what lung-development-relevant datasets exist, and how do
I get them?"* — a question no single portal answers today.

It also matches all the project's stated criteria:

- **Useful immediately** — emits a single manifest file that a domain
  expert can grep, sort, and cite. No infrastructure required to consume.
- **No wheel reinvention** — the CLI does not re-derive cell type
  annotations, re-implement Census queries, or shadow the Azul Browser.
  It curates pointers and structured metadata; the heavy lifting stays in
  CELLxGENE Census, LungMAP, and ENCODE.
- **Minimal dependency burden** — Python stdlib only for v0. No PyYAML,
  no Pydantic, no SDKs. The CLI reads a JSON sources file and writes
  CSV/JSON/Markdown outputs.
- **Built from public metadata first** — every field is verifiable from
  publicly cited URLs already enumerated in `metadata/resource_*.md`.
- **Extensible** — v1 can add live API queries (Census `obs.read()`,
  LungMAP `/index/projects`, ENCODE `/search/`) to *refresh* the curated
  source file rather than replace the manifest abstraction. The same
  output schema serves later MVPs as their input.

## Why the others are deferred

- **Evidence-map generator** — high user-facing value, but requires
  literature integration (PubMed E-utilities), multi-source synthesis,
  and an evidence-grading rubric we have not designed. Premature.
- **Lung-switch-explorer** — requires *downloading* and *analyzing* data,
  not just metadata. Brings in Scanpy + scvi-tools + AnnData containers
  + plotting. Worthwhile but not v0 — and easier to scope once the
  manifest tells us which fetal datasets exist with sufficient NKX2-1 /
  SOX2 / SOX9 coverage.
- **Marker-to-regulator linker** — depends on SCREEN/ENCODE peak data
  and on having a reliable list of cell-type markers. The marker list
  comes from the manifested datasets; the regulator side needs SCREEN
  endpoint stability work we explicitly deferred.

The pattern: every deferred MVP has the manifest as a *prerequisite*.
Build the prerequisite first.

## Smallest possible useful version

**`gain manifest`** — one Python script, stdlib only.

### Inputs

- `metadata/sources.json` — a hand-curated, version-controlled list of
  lung-development-relevant datasets and tracks. Each entry has the
  fields enumerated below. This file is the project's editorial output
  and is the place we encode domain judgment.

### Outputs

- `metadata/manifest.csv` — one row per dataset/track, fields:
  `source, dataset_name, modality, stage, tissue, access_method,
  programmatic_access, reuse_priority, notes`.
- `metadata/manifest.json` — same data as JSON for downstream tooling.
- `metadata/manifest.md` — same data rendered as a Markdown table for
  humans browsing the repo on GitHub.

### CLI shape

```
gain manifest --out-dir metadata/
```

One subcommand. One example command in the README. `--help` shows the
options. No subcommand frameworks (Click, Typer); `argparse` is enough.

### Non-goals for v0

- No live API queries — sources are curated by hand.
- No download of actual data files; only metadata.
- No new ontology or schema — fields chosen to be human-meaningful.
- No tests beyond a smoke test that the CLI runs end-to-end.
- No packaging, no `setup.py`, no PyPI release. Run the script directly
  with `python scripts/gain_manifest.py`.
