# Roadmap

Ordered by *what unblocks the most downstream value*, not by what is
fastest. Every item must justify itself against the three scope rules.

## v0 — manifest CLI ✅ shipped

`scripts/gain_manifest.py` reads `metadata/sources.json` and writes
`metadata/manifest.{csv,json,md}`. Twelve seed entries.

## v1 — live verifier ✅ shipped

`scripts/gain_verify.py` probes every `programmatic_access` URL in
`sources.json`, records status / content-type / declared length / head
bytes / error, and writes `metadata/verification.json` with a summary.
Stdlib only; 0.2s inter-request sleep keeps us under ENCODE's 10 GET/sec.

**First-run findings** (committed in `verification.json`): 8/12 sources
return 200; the three ENCODE TF-ChIP search URLs return 404 (the
`target.label` query shape needs updating) and SCREEN returned 429
(bot-detection / rate-limit). Both are real drift the manifest alone
could not have caught.

## v1.5 — switch-hierarchy explorer ✅ shipped

`metadata/switch_hierarchy.csv` (30 hand-curated rows linking
NKX2-1 / SOX2 / SOX9 / FGF10 / WNT / BMP / SHH / airway_program /
alveolar_program to relevant manifest sources) +
`scripts/gain_switch_explorer.py` (validates that every link resolves
against `sources.json`, joins in modality/stage/tissue, renders
`notes/switch_hierarchy.md`).

## v0.x — manifest hygiene (open)

Small mechanical extensions that make the existing CLIs nicer.

- [ ] Fix the ENCODE TF-ChIP URLs in `sources.json` based on the
      verification.json drift (likely `target.genes.symbol=NKX2-1`
      or similar; verify against the live ENCODE search before
      committing).
- [ ] Diagnose SCREEN 429: switch to the documented GraphQL endpoint
      with appropriate headers, or back off and try a different entry.
- [ ] `gain_manifest.py --validate` mode that exits non-zero on schema
      errors without writing outputs. Useful in pre-commit / CI.
- [ ] Stable row sort key in the manifest output (currently
      insertion-order from JSON).
- [ ] Per-source counts in the manifest CLI's stdout summary
      (`5 CELLxGENE Census, 3 LungMAP, 4 ENCODE, 1 SCREEN`).
- [ ] Add the missing seed entries called out in
      [limits.md](limits.md): more LungMAP stage-resolved projects,
      mouse ENCODE lung data, spatial / proteomics rows.

## v1.x — verifier hardening (open)

- [ ] On-disk response cache under `metadata/cache/<source>/`
      (gitignored, already in place via `.gitignore`).
- [ ] Markdown drift report (`notes/drift.md`) auto-generated from
      `verification.json` showing only the failed rows with a one-line
      remediation hint per row.
- [ ] Optional `--only-failed` mode for re-checking just the
      previously-failing URLs (useful while iterating on fixes).

## v2+ — the remaining deferred MVPs

In the order they become tractable now that v0/v1/v1.5 are live:

- **lung-switch-explorer (live data)** — extend `gain_switch_explorer`
  beyond the curated CSV: given a CELLxGENE Census query for fetal
  lung, plot SOX2/SOX9 ratio and NKX2-1 expression along annotated
  developmental stage and identify the proximal-distal bifurcation
  point. Mostly Scanpy on top of Census; first real dependency add.
- **marker-to-regulator linker** — take cell-type markers from
  CELLxGENE → intersect with ENCODE TF ChIP-seq peaks and SCREEN
  cCREs in lung biosamples → ranked plausible upstream regulators.
  Blocked on the SCREEN endpoint fix above.
- **evidence-map generator** — given a regulatory claim
  ("NKX2-1 → FGF10"), assemble: ENCODE peaks at the locus, Census
  expression correlation across lung cell types, supporting PubMed
  IDs. Highest user-facing value; needs the verifier to be
  rock-solid first since every assembled line of evidence must point
  at something we know to be current.

## What is not on the roadmap

- A web UI.
- A REST API of our own.
- A "Gain platform" or any other word that ends in -platform.
- A novel scoring metric, integration method, or annotation system.
- Re-implementations of any tool listed in `metadata/resource_*.md`.

If any of those start sneaking in, push back to the three scope rules
in [AGENTS.md](../AGENTS.md).
