# Gain

Open-source research-engineering on the **middle-layer control logic of human
lung development**:

```
NKX2-1  ->  SOX2 / SOX9  ->  FGF10 / WNT / BMP / SHH  ->  airway / alveolar programs
```

The goal is not to derive new biology. The goal is to make this regulatory
backbone **queryable, evidence-grounded, and reproducible** against existing
public data — without rebuilding atlases, single-cell pipelines, or
regulatory-element registries.

## What ships today

Three small, stdlib-only CLIs. No package install. No new dependencies.
No framework.

| Script | Reads | Writes | Purpose |
|---|---|---|---|
| [`scripts/gain_manifest.py`](scripts/gain_manifest.py) | [`metadata/sources.json`](metadata/sources.json) | [`metadata/manifest.{csv,json,md}`](metadata/) | Aggregate the hand-curated lung-development source list into one unified manifest in three formats. |
| [`scripts/gain_verify.py`](scripts/gain_verify.py) | [`metadata/sources.json`](metadata/sources.json) | [`metadata/verification.json`](metadata/verification.json) | Probe every source URL live; record HTTP status, content type, and any error. Surfaces drift between curated pointers and reality. |
| [`scripts/gain_switch_explorer.py`](scripts/gain_switch_explorer.py) | [`metadata/switch_hierarchy.csv`](metadata/switch_hierarchy.csv) + [`metadata/sources.json`](metadata/sources.json) | [`notes/switch_hierarchy.md`](notes/switch_hierarchy.md) | Render the gene/pathway hierarchy (NKX2-1 / SOX2 / SOX9 / FGF10 / WNT / BMP / SHH / airway / alveolar) joined with the manifest into a per-node evidence report. |

## Quickstart

Requires only Python 3.9+.

```sh
python3 scripts/gain_manifest.py          # build the manifest
python3 scripts/gain_verify.py            # probe sources live
python3 scripts/gain_switch_explorer.py   # render the hierarchy report
```

Each script supports `--help`. Useful overrides:

```sh
# Manifest: just the Markdown table, written to a custom directory
python3 scripts/gain_manifest.py --formats md --out-dir /tmp/gain-out

# Verifier: longer per-request timeout, slower pacing for picky portals
python3 scripts/gain_verify.py --timeout 20 --sleep 1.0

# Switch explorer: render to a different output path
python3 scripts/gain_switch_explorer.py --out /tmp/switch.md
```

## Repository layout

```
notes/      planning artifacts + generated reports (read these first)
metadata/   curated inputs, generated outputs, resource profiles
scripts/    three stdlib-only CLIs (manifest / verify / switch-explorer)
```

## Where to read next

In order:

1. [notes/evidence_map.md](notes/evidence_map.md) — project goal, scientific
   scope, the public resources that matter, and the candidate MVPs.
2. [notes/mvp_decision.md](notes/mvp_decision.md) — why the manifest CLI was
   chosen as v0 and why the alternatives were deferred.
3. [notes/switch_hierarchy.md](notes/switch_hierarchy.md) — the rendered
   per-gene / per-pathway evidence report (the v1.5 output most users
   actually want to read).
4. [metadata/](metadata/) — six per-resource profiles (`resource_*.md`), the
   cross-resource summary CSV, and the curated inputs (`sources.json`,
   `switch_hierarchy.csv`).
5. [notes/limits.md](notes/limits.md) — what this v0/v1/v1.5 explicitly does *not* do.
6. [notes/roadmap.md](notes/roadmap.md) — what is next (v0.x hygiene, v1.x
   verifier hardening, v2 deferred MVPs).

## Constraints baked into this repo

- **No generic framework if a project-specific script will do.**
- **No dependency unless it clearly reduces total complexity.**
- **No "future architecture" section longer than the actual working code.**

These are why v0 is one script, stdlib only, and why you will not find
unused abstractions in `scripts/`.

## Status

Bootstrapped 2026-05-03. Live at <https://github.com/DD-Ching/Gain>.
v0 (manifest CLI), v1 (live URL verifier), and v1.5 (switch-hierarchy
explorer) all shipped on the same day. See [notes/status.md](notes/status.md)
for the current snapshot.

## License

To be added. Current contents are curation + small stdlib scripts; treat
them as the moral equivalent of public-domain inventory work until a
license file lands.
