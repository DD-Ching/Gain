# Status

**Date:** 2026-05-03
**Phase:** v0 shipped — manifest CLI live and pushed

## Starting state (preserved)

- Repo started from an **empty directory** (`/Users/ddh/Downloads/Gain`).
- **No local source code, datasets, or prior notes were provided.** The only
  inputs were the project brief and the constraints set in-session.
- The project is being built **entirely from public resources**:
  official portals, public APIs, public datasets, public documentation.
  No private data, no embargoed material, no scraped credentials.

## Tooling check

- `git` 2.50.1 — available.
- `gh` 2.88.1 — authenticated as `DD-Ching` with `repo`, `workflow`, `gist`,
  `read:org`.
- `python3` — available; **stdlib only** in v0. No virtualenv, no `pip install`
  yet. Scanpy / scvi-tools / cellxgene-census remain deferred until an MVP
  needs them.

## What exists in the repo right now

```
README.md             user-facing intro and quickstart
AGENTS.md             rules for any AI agent working in this repo
.gitignore

notes/
  evidence_map.md     project goal, scientific scope, resource shortlist, MVP candidates
  status.md           this file
  next_steps.md       ordered actions with exit conditions
  mvp_decision.md     why dataset-manifest CLI is v0; why others are deferred
  limits.md           explicit list of what v0 does NOT do
  roadmap.md          v0.x hygiene, v1 verifier, v1+ deferred MVPs

metadata/
  resource_cellxgene.md      profile: CELLxGENE Census
  resource_hlca_hca.md       profile: HLCA dataset + HCA umbrella
  resource_lungmap.md        profile: LungMAP (Azul REST + OMERO)
  resource_encode.md         profile: ENCODE + SCREEN
  resource_scanpy.md         profile: Scanpy (analysis lib)
  resource_scvi_tools.md     profile: scvi-tools (probabilistic models)
  resource_summary_table.csv cross-resource summary
  sources.json               12-entry hand-curated source-of-truth
  manifest.csv               generated: unified manifest (CSV)
  manifest.json              generated: unified manifest (JSON)
  manifest.md                generated: unified manifest (Markdown table)

scripts/
  gain_manifest.py    stdlib-only CLI; reads sources.json, writes manifest.{csv,json,md}
```

## v0 MVP — shipped

- **Deliverable:** `python3 scripts/gain_manifest.py` produces three manifest
  files in `metadata/`. Verified end-to-end (12 rows written across CSV, JSON,
  and Markdown).
- **Dependencies added:** zero. Stdlib only.
- **Lines of code (CLI):** ~110 in `scripts/gain_manifest.py`. The supporting
  prose in `metadata/`, `notes/`, and `README.md` is intentionally larger
  than the code, but no individual "future architecture" document exceeds
  the working code (per the third scope rule).

## What is decided

- v0 deliverable: dataset-manifest CLI (see `notes/mvp_decision.md`).
- Source-of-truth shape: a single `metadata/sources.json` with `schema_version: "0.1"`.
- Output formats: CSV + JSON + Markdown, written next to the source file and
  committed so they render on GitHub.
- Repo is **public** at <https://github.com/DD-Ching/Gain>.

## What is *not* decided yet

- License (deferred to v1; flagged in `README.md`).
- Whether v1 is the live verifier or one of the deferred MVPs first
  (`notes/roadmap.md` argues for the verifier, but the decision is open).
- Mouse-data scope: only one LungMAP-mouse seed entry; ENCODE mouse lung
  not yet enumerated.
