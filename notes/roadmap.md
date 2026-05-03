# Roadmap

Ordered by *what unblocks the most downstream value*, not by what is
fastest. Every item must justify itself against the three scope rules.

## v0.x — manifest hygiene

Small, mechanical extensions to the CLI that came out of building it.

- [ ] `gain_manifest.py --validate` mode that exits non-zero on schema
      errors without writing outputs. Useful in pre-commit / CI.
- [ ] Stable row sort key (currently insertion-order from JSON).
- [ ] Per-source counts in the CLI's stdout summary
      (`5 CELLxGENE Census, 3 LungMAP, 4 ENCODE, 1 SCREEN`).
- [ ] Add the missing seed entries called out in
      [limits.md](limits.md): more LungMAP stage-resolved projects,
      mouse ENCODE lung data, spatial / proteomics rows.

## v1 — the live verifier

The single most valuable upgrade: turn each `programmatic_access` URL into
something the CLI can *actually hit* and report status on.

- [ ] `gain_manifest.py --verify` flag: for every row, GET the URL (or
      run the documented Python query), record HTTP status, response
      shape signature, and timestamp into `metadata/verification.json`.
- [ ] Honor ENCODE's 10 GET/sec rate limit; back off on 429.
- [ ] On-disk response cache under `metadata/cache/<source>/` (gitignored).
- [ ] Document divergences between the curated `sources.json` and the
      live portal state in a "drift" report.

This is the smallest change that converts the manifest from *editorial
claim* to *grounded evidence*.

## v1+ — the deferred MVPs

In the order they become tractable once v1 lands:

- **lung-switch-explorer** — given a CELLxGENE Census query for fetal
  lung, plot SOX2/SOX9 ratio and NKX2-1 expression along annotated
  developmental stage. Identify the proximal-vs-distal bifurcation.
  Mostly Scanpy on top of Census; value is the framing + reproducibility.
- **marker-to-regulator linker** — take cell-type markers from
  CELLxGENE → intersect with ENCODE TF ChIP-seq peaks and SCREEN cCREs
  in lung biosamples → ranked plausible upstream regulators. Requires
  the SCREEN endpoint stability work explicitly deferred from v0.
- **evidence-map generator** — given a regulatory claim
  ("NKX2-1 → FGF10"), assemble: ENCODE peaks at the locus, Census
  expression correlation across lung cell types, supporting PubMed IDs.
  Highest user-facing value; build only after the verifier exists,
  because every line of evidence must point at something we know to be
  current.

## What is not on the roadmap

- A web UI.
- A REST API of our own.
- A "Gain platform" or any other word that ends in -platform.
- A novel scoring metric, integration method, or annotation system.
- Re-implementations of any tool listed in `metadata/resource_*.md`.

If any of those start sneaking in, push back to the three scope rules
in [AGENTS.md](../AGENTS.md).
