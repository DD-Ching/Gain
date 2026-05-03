# Status

**Date:** 2026-05-03
**Phase:** bootstrap

## Starting state

- Repo started from an **empty directory** (`/Users/ddh/Downloads/Gain`).
- **No local source code, datasets, or prior notes were provided.** The only
  inputs are the project brief and the constraints in this session.
- The project will be built **entirely from public resources**:
  official portals, public APIs, public datasets, and public documentation.
  No private data, no embargoed material, no scraped credentials.

## Tooling check

- `git` 2.50.1 — available
- `gh` 2.88.1 — authenticated as `DD-Ching` with `repo`, `workflow`, `gist`,
  `read:org` scopes
- Python / Scanpy / scvi-tools: not yet checked; deferred until MVP is chosen
  (we don't install dependencies before knowing we need them)

## What exists in the repo right now

```
notes/        # planning artifacts (this file lives here)
metadata/     # for downstream dataset manifests, schemas
scripts/      # for downstream small project-specific scripts
```

That's it. There is intentionally no code, no dependency manifest, no CI
configuration yet. Those get added when there is a concrete reason for them.

## What is *not* decided yet

- The single MVP deliverable (four candidates listed in `evidence_map.md`).
- The repo's GitHub remote — local commit will land first; remote creation is
  a separate, explicit step.
- Language stack beyond "almost certainly Python" given the scientific
  ecosystem (Scanpy, scvi-tools, tiledbsoma).
