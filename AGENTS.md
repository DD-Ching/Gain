# AGENTS.md

Guidance for AI coding agents (Claude Code, Cursor, etc.) working in this repo.

## What this repo is

Open-source research-engineering on lung developmental control logic. Read
[README.md](README.md) for the user-facing summary and
[notes/evidence_map.md](notes/evidence_map.md) for the scientific scope.

## Read these before changing anything substantive

In order:

1. [notes/evidence_map.md](notes/evidence_map.md)
2. [notes/status.md](notes/status.md)
3. [notes/mvp_decision.md](notes/mvp_decision.md)
4. [notes/limits.md](notes/limits.md)
5. [notes/roadmap.md](notes/roadmap.md)

If the task is non-trivial, **update the planning notes first**, then
implement. Tiny edits / bug fixes can skip the planning ritual but should
update `notes/status.md` if the repo state changed.

## Hard rules

1. **Never build a generic framework if a project-specific script will do.**
2. **Never add a dependency unless it clearly reduces total complexity.**
3. **Never write a "future architecture" section longer than the actual
   working code.**

Corollary: prefer stdlib. Default deliverable shape is a single Python
script in `scripts/` with a clear CLI entrypoint. Promote to a package
only when there is a second real consumer.

## Commit discipline

- Small, scoped commits with imperative-mood subjects.
- One logical change per commit (e.g., "add LungMAP and ENCODE inventory",
  not "add a bunch of stuff").
- Keep planning notes in lockstep with code: when behavior changes,
  update `notes/status.md` and `notes/roadmap.md` in the same commit.

## How to run the v0 MVP

```sh
python3 scripts/gain_manifest.py
```

That's the whole thing. No virtualenv needed. No install step.

## Adding a new resource entry

Edit [metadata/sources.json](metadata/sources.json), then re-run the CLI
to regenerate `metadata/manifest.{csv,json,md}`. Required fields are
enforced by the CLI's validator — invalid rows fail loudly.

## Curation honesty

Entries in `sources.json` are **pointers, not validated accessions**.
Every entry's portal-side state must be re-verified at the moment of use.
This is documented in the file and in `notes/limits.md`. Do not silently
upgrade a pointer to a claim of correctness — write a verifier first.

## When to reach outside the repo

- Use the public APIs documented in `metadata/resource_*.md`.
- Honor rate limits (ENCODE: 10 GET/sec).
- Cache HTTP responses to disk under `metadata/cache/<source>/` if and
  when live queries land in v1; do not commit large caches.
