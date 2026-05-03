# Next steps

Ordered. Each step has a clear exit condition.

## 1. Verify tooling — DONE

- `git` available, `gh` authenticated as `DD-Ching`.
- Exit condition: tools confirmed. ✅

## 2. Initialize repo scaffold — IN PROGRESS

- Create `notes/`, `metadata/`, `scripts/` (done).
- Write `notes/evidence_map.md`, `notes/status.md`, `notes/next_steps.md` (done).
- `git init`, initial commit of the scaffold + planning notes.
- Decide on remote: create `DD-Ching/Gain` on GitHub (or rename) and push.
- Exit condition: scaffold visible on GitHub at a known URL.

## 3. Inventory existing tools & datasets

Goal: a one-screen-per-resource set of notes in `metadata/` answering, for each
of the resources in `evidence_map.md`:

- access pattern (HTTP API? Python client? bulk download?)
- auth required? license?
- what query gets us "human lung, developmental stages, NKX2-1/SOX2/SOX9 expression"?
- what is the actual returned shape (anndata, BED, JSON manifest)?
- known gotchas (rate limits, schema drift, deprecated endpoints)

Order of attack:
1. CELLxGENE Census — most leverage, single SDK
2. LungMAP API — most developmental signal
3. HLCA on CELLxGENE — concrete reference dataset
4. Human fetal lung atlases — confirm Census coverage vs upstream
5. ENCODE / SCREEN — only if MVP needs regulatory data

Exit condition: `metadata/resource_*.md` files exist for at least the first
three; we can answer "can the dataset-manifest CLI be built on Census + LungMAP
alone?" with yes/no.

## 4. Choose one MVP

Pick exactly one of the four candidates in `evidence_map.md`. Default leaning:
**dataset-manifest CLI**, because it is the smallest concrete artifact that
unlocks every other candidate.

Decision criteria:
- ships in ≤ a few hundred lines of project-specific code
- adds at most one or two dependencies (Census SDK + maybe `requests`)
- produces an output a domain expert can immediately evaluate
- does not duplicate something already shipped by Census/LungMAP/Scanpy

Exit condition: `notes/mvp.md` written, naming the chosen deliverable, its
inputs, its outputs, and its non-goals.

## 5. Implement the MVP

Only after step 4. Work in `scripts/` first; promote to a package layout only
when there is a second consumer of the code.

## Constraints carried forward

- No generic framework if a project-specific script will do.
- No dependency added unless it clearly reduces total complexity.
- No "future architecture" section longer than the actual working code.
- Verify any cited resource (URL, endpoint, dataset accession) against its
  current state before relying on it — public portals drift.
