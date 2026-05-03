# Next-Step Decision

**Date:** 2026-05-03
**Decision:** fix the four ENCODE-related entries in `sources.json` so they
point at real, populated public data, and document the
NKX2-1 / SOX2 / SOX9 ChIP-seq gap explicitly. Then re-run the verifier and
stop. Defer Q1 and Q2 (which require Census + Scanpy) and Q3 (the
evidence-audit script) to a later session.

## What is the unresolved question this addresses?

Indirectly addresses **Q3** (`notes/unresolved_questions.md`): the audit of
which canonical regulator-target relationships are supported by *human*
public data. Specifically, this step records — into the manifest itself —
the first concrete gap finding from that audit:

> NKX2-1, SOX2, and SOX9 have **zero** TF ChIP-seq experiments in ENCODE
> in any human biosample. ENCODE has 6 TF ChIP-seq experiments in lung
> tissue total (5 mouse, 1 human — CTCF). Histone ChIP-seq, ATAC-seq,
> and DNase-seq in lung biosamples exist (59, 5, and 30 experiments
> respectively) and are the only ENCODE-available regulatory signal for
> the lung-developmental TFs.

The current `sources.json` curates as if these TF ChIP datasets exist in
human. They do not. Until that is fixed, every downstream artifact that
trusts the manifest is propagating a false claim.

## What is already known?

- The biological chain (`notes/reality_check.md`).
- That the verifier reported these four entries as failing
  (`metadata/verification.json`).

## What is merely curation?

- The previous `sources.json` rows that named the broken queries.
- The `switch_hierarchy.csv` rows that linked NKX2-1 / SOX2 / SOX9 nodes
  to those (empty) ChIP-seq queries — visually plausible, factually
  pointing at no data.

## What new value will this step add?

1. **A correctness fix.** `sources.json` will stop overstating ENCODE
   coverage for the lung-developmental TFs.
2. **A small, durable, non-trivial fact** entered into the manifest:
   the explicit absence of human NKX2-1 / SOX2 / SOX9 ChIP-seq in
   ENCODE, with citation to the verifier evidence that established it.
3. **Real, populated alternative entries** that point at the
   ENCODE data that *does* exist for lung regulatory analysis: lung
   tissue TF ChIP-seq (any TF), lung Histone ChIP-seq, lung ATAC-seq,
   lung DNase-seq. These give downstream MVPs (Q3 in particular)
   correct pointers to start from.
4. **Honest `evidence_one_liner` updates** in `switch_hierarchy.csv`
   so the rendered report no longer implies that direct ChIP evidence
   exists for these TFs in human lung.

## Why is this the smallest useful move?

- It uses only `urllib`, `csv`, and `json` — no new dependencies.
- It is bounded by the existing manifest schema; no new tooling needed.
- It directly closes the four verifier failures with truthful entries
  rather than hiding them.
- It produces a non-trivial finding (the ChIP gap) that any
  third party reading the repo can reproduce by re-running the
  verifier.
- It explicitly defers Q1 / Q2 (Census + Scanpy work) and Q3 (the
  evidence-audit script) until those questions are explicitly chosen
  on a future session, with eyes-open commitment to the dependency
  add (for Q1/Q2) or the additional script (for Q3).

## Stop conditions for this step

- `sources.json` updated and re-validated.
- `switch_hierarchy.csv` updated to reference the new entries (no
  broken `relevant_source` references).
- `gain_manifest.py` and `gain_switch_explorer.py` re-run; outputs
  regenerated and committed.
- `gain_verify.py` re-run; new `verification.json` shows the previously-
  failing rows now resolve to real data.
- All committed and pushed.
- Report back; do not start Q3 or any Census work in the same session.
