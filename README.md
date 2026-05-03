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

Four small, stdlib-only CLIs. No package install. No new dependencies.
No framework.

| Script | Reads | Writes | Purpose |
|---|---|---|---|
| [`scripts/gain_manifest.py`](scripts/gain_manifest.py) | [`metadata/sources.json`](metadata/sources.json) | [`metadata/manifest.{csv,json,md}`](metadata/) | Aggregate the hand-curated lung-development source list into one unified manifest in three formats. |
| [`scripts/gain_verify.py`](scripts/gain_verify.py) | [`metadata/sources.json`](metadata/sources.json) | [`metadata/verification.json`](metadata/verification.json) | Probe every source URL live; record HTTP status, content type, and any error. Surfaces drift between curated pointers and reality. |
| [`scripts/gain_switch_explorer.py`](scripts/gain_switch_explorer.py) | [`metadata/switch_hierarchy.csv`](metadata/switch_hierarchy.csv) + [`metadata/sources.json`](metadata/sources.json) | [`notes/switch_hierarchy.md`](notes/switch_hierarchy.md) | Render the gene/pathway hierarchy (NKX2-1 / SOX2 / SOX9 / FGF10 / WNT / BMP / SHH / airway / alveolar) joined with the manifest into a per-node evidence report. |
| [`scripts/gain_evidence_audit.py`](scripts/gain_evidence_audit.py) | [`metadata/regulator_target_pairs.csv`](metadata/regulator_target_pairs.csv) | [`metadata/evidence_audit.csv`](metadata/evidence_audit.csv) | **Q3 audit.** For each TF→target pair in the lung-development chain, query ENCODE for human-lung / human-other / mouse TF ChIP-seq and assign an evidence class. Surfaces what the public ChIP record actually supports vs. what is mouse-extrapolated or literature-curated. |

## Quickstart

Requires only Python 3.9+.

```sh
python3 scripts/gain_manifest.py          # build the manifest
python3 scripts/gain_verify.py            # probe sources live
python3 scripts/gain_switch_explorer.py   # render the hierarchy report
python3 scripts/gain_evidence_audit.py    # run the Q3 ENCODE evidence audit
```

Each script supports `--help`. Useful overrides:

```sh
# Manifest: just the Markdown table, written to a custom directory
python3 scripts/gain_manifest.py --formats md --out-dir /tmp/gain-out

# Verifier: longer per-request timeout, slower pacing for picky portals
python3 scripts/gain_verify.py --timeout 20 --sleep 1.0

# Switch explorer: render to a different output path
python3 scripts/gain_switch_explorer.py --out /tmp/switch.md

# Evidence audit: slower pacing if ENCODE rate-limits
python3 scripts/gain_evidence_audit.py --sleep 0.5
```

## Repository layout

```
notes/      planning artifacts + generated reports (read these first)
metadata/   curated inputs, generated outputs, resource profiles
scripts/    three stdlib-only CLIs (manifest / verify / switch-explorer)
```

## Where to read next

In order:

1. [notes/reality_check.md](notes/reality_check.md) — what is curated
   infrastructure here vs. what would count as genuine added value.
2. [notes/unresolved_questions.md](notes/unresolved_questions.md) — the
   three middle-layer questions Gain is actually trying to answer.
3. [notes/evidence_audit.md](notes/evidence_audit.md) — **the Q3 result**:
   classification of 18 canonical TF→target pairs by ENCODE evidence class,
   with the most important missing-evidence gaps named.
4. [notes/q3_design.md](notes/q3_design.md) — the audit's design contract
   (scope, classes, edge cases, what counts vs. doesn't count as evidence).
5. [notes/switch_hierarchy.md](notes/switch_hierarchy.md) — per-gene /
   per-pathway evidence report joined with the manifest.
6. [metadata/](metadata/) — per-resource profiles, curated inputs,
   generated outputs.
7. [notes/limits.md](notes/limits.md) — what the current artifacts do *not* do.
8. [notes/roadmap.md](notes/roadmap.md) — what is next.

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
