# Post-Chain Options

**Status:** decision memo. No implementation in this turn.

**Context.** The regulator-audit chain (NKX2-1, SOX2, SOX9) has
reached a public-data substrate ceiling. Continuing to CTNNB1 / SMAD1
/ GLI2 in the same audit pattern would produce diminishing returns
because their substrates are strictly worse (0 lung-context for all
three, and CTNNB1 has 0 ChIP-Atlas hits at all in some past audits).
The next move should change **method**, not just **regulator**. This
memo compares four options on six axes.

## Axis definitions

- **Scientific value:** would executing this option produce a
  *substantively new* finding for the project's stated scope (lung
  developmental control logic)? Or only a structural / infrastructure
  improvement?
- **Dependency cost:** marginal new dependencies (Python packages,
  external services, large-file downloads) relative to the current
  stdlib-only state.
- **Realism:** can this be implemented with the project's
  no-broad-platform / no-heavy-deps rules?
- **Novelty:** does the result add something not already in the
  literature?
- **Busywork risk:** odds that the option drifts into editorial /
  formatting / curation that does not change the project's
  conclusions.
- **What unresolved question it answers:** ties to the standing list
  in `notes/unresolved_questions.md` or to gaps the chain audit
  surfaced.

---

## Option A — Motif scanning + accessibility inference

**What it would do.** Populate the deferred
`indirect_accessibility_support` class that has been defined-but-
unpopulated across all four audits (NKX2-1, SOX2, SOX9, plus the
extended Q3 audit). Concretely:

1. For each (regulator, target) pair currently in `no_locus_support`
   or `lung_context_source_only`, take the target's hg38 promoter ±
   50 kb window.
2. Intersect with **ENCODE lung ATAC-seq + DNase-seq peaks**
   (5 + 30 = 35 lung experiments — already inventoried in
   `metadata/sources.json`).
3. Within those accessible regions, scan for the regulator's binding
   motif using **JASPAR** PWMs.
4. A pair gains `indirect_accessibility_support` if at least one
   accessible peak in lung tissue contains a motif occurrence at a
   biologically plausible score threshold.

**Scientific value:** HIGH. This is the *principled escape from the
substrate ceiling* — instead of relying on cancer-line ChIP, it uses
**primary lung tissue ATAC** (the substrate we have been missing
throughout the project). For every pair currently failing, it asks:
"could the regulator plausibly bind here in lung tissue, given that
the chromatin is accessible and the motif occurs?" Both yes/no
outcomes are substantive — yes corroborates the textbook claim
indirectly; no deepens the data gap.

**Dependency cost:** LOW.
- JASPAR PWM files: ~ few MB total, downloadable as text. Stdlib parse.
- ENCODE ATAC/DNase BEDs: already used by `gain_peak_intersection.py`.
  No new dep.
- hg38 sequence per-target window: fetchable via UCSC DAS
  (`das.cse.ucsc.edu`) or Ensembl REST per-target ± 200 kb (~ 3 MB
  total across 7-9 targets). Stdlib HTTP.
- PWM scoring: ~ 50–100 lines of pure Python. No new dep.

Net: zero new Python packages required. Possibly two small motif
files committed under `metadata/cache/jaspar/` (gitignored if large).

**Realism:** HIGH. Same shape as `gain_nkx21_distal_candidates.py` —
stdlib + HTTP fetch + interval intersection + a small PWM scorer.

**Novelty:** MEDIUM. Motif-scanning-in-accessible-chromatin is a
standard *indirect-evidence* approach. The novelty comes from the
audit-framework wrapping: per-pair evidence-tier results across the
12+ pairs that the chain audit left at `no_locus_support` /
`lung_context_source_only`.

**Busywork risk:** MEDIUM. The implementation is non-trivial (~ 200–
300 LoC for a working v0). If results turn out to be uniformly weak,
the cost-per-insight is poor. Mitigated by running the motif scan on
NKX2-1's 4 failing canonical targets first (SFTPC, SCGB1A1, ABCA3,
FOXA2) — those are the highest-prior pairs where the answer is most
likely to be informative either way.

**Unresolved question it answers:** for each pair currently in
`no_locus_support` (across all three regulators), does motif +
accessibility plausibility exist in **primary lung tissue**? This
directly tests whether the substrate ceiling is the only thing
hiding lung-developmental binding evidence. Across NKX2-1's 4
failing canonical pairs (SFTPC, SCGB1A1, ABCA3, FOXA2) this is the
most-aimed test in the project.

---

## Option B — Expression-correlation / CELLxGENE Census route

**What it would do.** Implement Q1 / Q2 from
`notes/unresolved_questions.md`. For each pair, query CELLxGENE Census
for human primary lung scRNA-seq (HLCA core + He 2022 fetal lung +
Cao 2020 pan-fetal). Compute regulator–target co-expression /
correlation within annotated cell types. Add an
`expression_correlation_support` tier to the v2 framework.

**Scientific value:** MEDIUM-HIGH. Tests a *necessary condition* for
direct regulation: the regulator and target are co-expressed in the
same cells. A negative result is informative ("NKX2-1 and SFTPC are
co-expressed in AT2 cells, as expected — *binding* is the gap, not
expression"). A positive correlation in unexpected cell types could
surface novel co-expression patterns.

**Dependency cost:** HIGH.
- `cellxgene-census` Python package + `tiledbsoma` + `pyarrow`
  + `pandas` + `numpy` — the heaviest dep stack we have ever
  considered for this project.
- This is the dependency add we have been *deliberately deferring*
  throughout (cf. `notes/manual_curation_value_check.md` and the
  scope discipline rules in `AGENTS.md`).
- Census data downloads can be GBs depending on slicing.

**Realism:** MEDIUM. Doable but breaks the "stdlib only" pattern that
has defined every script in the project. The project's `AGENTS.md`
rule "no dependency unless it clearly reduces total complexity"
applies.

**Novelty:** MEDIUM. Co-expression analysis is among the most-used
weak-evidence methods in single-cell biology; per-pair correlation
tables exist in many published HLCA-derived analyses. The novelty is
the audit-framework wrapping, not the method.

**Busywork risk:** HIGH. Census setup + slicing + per-cell-type
correlation has many parameters to tune (which cells, which
normalization, which correlation metric, which p-value adjustment).
Easy to drift into "make the analysis perfect" rather than answer
the binary question.

**Unresolved question it answers:** Q1 and Q2 from
`notes/unresolved_questions.md` (when commitment happens, continuous
vs discrete proximal-distal axis). These are real questions but
**larger** in scope than what the chain audit has been doing — they
are not natural extensions of the audit, they are a separate research
direction on the same project surface.

For our specific failing pairs: Q-B would tell us whether NKX2-1 and
SFTPC are co-expressed in AT2 cells. **They almost certainly are**
(textbook). The headline result is mostly known.

---

## Option C — Resume the repo's infrastructure roadmap

**What it would do.** Pick up items from `notes/roadmap.md` that have
been waiting since v0:

- v1.x verifier hardening (drift report, on-disk cache).
- v0.x manifest hygiene (sort keys, per-source counts, more seed
  entries).
- v2 evidence-map generator (one of the four candidate MVPs that lost
  to the manifest CLI in `notes/mvp_decision.md`).

**Scientific value:** LOW. Infrastructure work that improves
reproducibility / quality but does not directly answer any of the
unresolved questions or change the audit's conclusions.

**Dependency cost:** LOW.

**Realism:** HIGH (we have done infrastructure successfully before).

**Novelty:** LOW. None of these items would produce a publishable
finding.

**Busywork risk:** **VERY HIGH.** The user has flagged this exact
risk multiple times — `notes/feedback_scope_discipline.md` explicitly
prohibits "future architecture" sections longer than the working
code, and `notes/manual_curation_value_check.md` rejected manual
curation precisely because it was bookkeeping. Infrastructure work
in the absence of a specific question is the canonical busywork
pattern.

**Unresolved question it answers:** none directly.

---

## Option D — Stop and preserve current outputs as the main contribution

**What it would do.** Treat the chain audit as the project's primary
contribution. Polish the existing notes for external readability,
write a single project-level summary that ties NKX2-1, SOX2, and
SOX9 together, and stop adding new audits or analyses.

**Scientific value:** MODERATE. The chain audit produced real
findings:

- The cancer-line-only constraint on NKX2-1 / SOX2 / SOX9 lung-
  context ChIP is the **actual public-data state**, not a snapshot
  artefact (confirmed by `notes/nkx21_final_gap.md`).
- 5 NKX2-1 chromatin-supported standing distal candidates, with
  FOXA2 chr20:22,716,796 as the highest-priority follow-up.
- SFTPC and SCGB1A1 robustly lack proximal NKX2-1 binding in
  cancer-line ChIP across both bed10 and bed05.
- The SOX9 ↔ NKX2-1 cross-context bidirectional binding finding at
  the proximal-distal axis loci.
- The SOX2 / SOX9 substrate is structurally less informative than
  NKX2-1's (cancer + reprogramming / cancer-only).

These findings are already documented in the per-cycle notes;
preservation is editorial work plus one project-level summary.

**Dependency cost:** ZERO.

**Realism:** HIGH (but requires editorial discipline to avoid
drifting into perfectionism).

**Novelty:** MODERATE. The chain-audit perspective on public-data
evidence for the canonical lung-developmental regulators is itself
underdiscussed in the field; framing the standing outputs as a
coherent contribution would be useful.

**Busywork risk:** LOW–MEDIUM. Mainly the project-level summary
write-up; rest is preservation. Could drift into "make every doc
publishable-quality" if not bounded.

**Unresolved question it answers:** none new. Codifies what is
already known.

---

## Side-by-side summary

| Axis | A (motif+accessibility) | B (expression/Census) | C (infrastructure) | D (stop & preserve) |
|---|---|---|---|---|
| Scientific value | **HIGH** (new evidence layer at primary lung) | MEDIUM-HIGH (co-expression confirms knowns) | LOW | MODERATE (codifies existing) |
| Dependency cost | LOW (stdlib + small motif file) | **HIGH** (Census + tiledbsoma + pandas) | LOW | ZERO |
| Realism | HIGH | MEDIUM | HIGH | HIGH |
| Novelty | MEDIUM | MEDIUM | LOW | MODERATE |
| Busywork risk | MEDIUM | HIGH | **VERY HIGH** | LOW-MEDIUM |
| Unresolved question | "do failing pairs have lung-tissue motif+accessibility plausibility?" — directly attacks the substrate ceiling | Q1 / Q2 (commitment timing, axis continuity) — different research surface | none | none new |

## Cross-cutting observations

- **Option A is the only option that uses primary lung tissue
  substrate** (via ENCODE's 35 lung ATAC + DNase experiments). Every
  other option either stays in the cancer-line / reprogramming
  substrate (none of them) or shifts to scRNA-seq (B). A is the
  principled answer to the substrate ceiling.
- **Options A and B both claim to "answer unresolved questions" but
  they answer *different* questions.** A answers a binding question
  (does the motif + accessibility align?). B answers a co-expression
  question (do regulator and target appear in the same cells?). A is
  more directly continuous with the chain-audit work; B is closer to
  Q1 / Q2 from the unresolved-questions list.
- **Option D is honest but conservative.** The chain audit findings
  are publishable-style as-is. Stopping after them is defensible and
  has zero risk of drifting. But it accepts the substrate ceiling
  rather than attempting to pierce it.
- **Option C should not win.** It is the project's standing
  anti-pattern.

The decision lives in `notes/post_chain_recommendation.md`.
