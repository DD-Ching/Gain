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

## What v0 ships

A single, stdlib-only CLI: `gain_manifest.py`.

It reads a hand-curated [metadata/sources.json](metadata/sources.json) of
lung-development-relevant datasets and tracks (CELLxGENE Census, LungMAP,
ENCODE/SCREEN) and emits a unified manifest in CSV, JSON, and Markdown.

The published outputs live next to the source:

- [metadata/manifest.csv](metadata/manifest.csv)
- [metadata/manifest.json](metadata/manifest.json)
- [metadata/manifest.md](metadata/manifest.md)

That's it. No package install. No new dependencies. No framework.

## Quickstart

Requires only Python 3.9+.

```sh
python3 scripts/gain_manifest.py
```

Output:

```
wrote 12 entries to:
  metadata/manifest.csv
  metadata/manifest.json
  metadata/manifest.md
```

Other useful invocations:

```sh
# Just the Markdown table, written to a custom directory
python3 scripts/gain_manifest.py --formats md --out-dir /tmp/gain-out

# Use an alternate sources file (e.g. while editing)
python3 scripts/gain_manifest.py --sources my-draft-sources.json
```

`python3 scripts/gain_manifest.py --help` lists every flag.

## Repository layout

```
notes/      planning artifacts (read these first)
metadata/   curated source list, generated manifest, resource profiles
scripts/    project-specific scripts (currently: the manifest CLI)
```

## Where to read next

In order:

1. [notes/evidence_map.md](notes/evidence_map.md) — project goal, scientific
   scope, the public resources that matter, and the candidate MVPs.
2. [notes/mvp_decision.md](notes/mvp_decision.md) — why the manifest CLI is
   the v0 and why the others are deferred.
3. [metadata/](metadata/) — six per-resource profiles
   (`resource_*.md`), the cross-resource summary CSV, and the curated
   sources file the CLI reads.
4. [notes/limits.md](notes/limits.md) — what this v0 explicitly does *not* do.
5. [notes/roadmap.md](notes/roadmap.md) — the next extensions.

## Constraints baked into this repo

- **No generic framework if a project-specific script will do.**
- **No dependency unless it clearly reduces total complexity.**
- **No "future architecture" section longer than the actual working code.**

These are why v0 is one script, stdlib only, and why you will not find
unused abstractions in `scripts/`.

## Status

Bootstrapped 2026-05-03. Live at <https://github.com/DD-Ching/Gain>.
v0 (manifest CLI) ships in the same commit set as this README.

## License

To be added with v1. v0 is curation + a small script; treat it as the
moral equivalent of public-domain inventory work until a license file
lands.
