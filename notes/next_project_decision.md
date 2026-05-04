# Next-Project Decision Memo

**Status:** decision memo for the successor project to Gain. **No
implementation in this repo.** The successor project lives in a
separate repository or branch; Gain is frozen here.

**Context.** Gain established a public-data evidence audit + substrate-
gap diagnosis for the canonical lung developmental regulators
(NKX2-1, SOX2, SOX9). The chain hit a public-data substrate ceiling;
the indirect-evidence (motif + accessibility) pivot did not
discriminate at v0 settings. Two future directions remain on the
table from
[`notes/limitations_and_next_methods.md`](limitations_and_next_methods.md).
This memo picks one as the next project.

**User bias** (carried forward from the v0 freeze instruction):

> *"I want the next repo to optimize for actual biological insight,
> not more audit completeness."*

That bias is the dominant criterion in this comparison.

## Option A — Cell-type-resolved accessibility

**What it would do.** Replace ENCODE's bulk-fetal-lung DNase peaks
(the substrate that broke Gain's indirect-evidence layer) with
**cell-type-resolved scATAC** from primary human fetal lung tissue.
For each canonical regulator → target pair, ask: in *AT2 cells
specifically* (or basal cells, or club cells, or fibroblasts), does
the regulator's motif occur within accessible chromatin near the
target's TSS?

**Substrate.** Several recent fetal lung papers publish cell-type-
specific ATAC tracks:
- He et al. 2022 (*Nat Genet*) — fetal lung scATAC + scRNA-seq
- Quach & Farrell 2024 — lung organogenesis trajectories
- Nikolic et al. 2017 (*Cell Stem Cell*) — and its follow-ups
- LungMAP human developmental projects

Most are not yet ingested into ENCODE's standardised browser; some
require GEO download + per-paper processing.

**Pros:**
- Directly addresses the bulk-tissue confound that broke Gain's
  indirect-evidence layer.
- Could rescue the motif + accessibility approach by using the
  right cell type — converting the "not_salvageable" verdict into
  a per-cell-type discriminating signal.
- Stays methodologically continuous with Gain. Same audit framework,
  better substrate.

**Cons:**
- **Substrate is not standardised.** Each paper has different
  scATAC processing pipelines, peak callers, and cell-type
  annotation conventions. Integration is per-paper bespoke work.
- **Significant new infrastructure.** scATAC processing typically
  needs `snapatac2`, `archr`, or `pycisTopic` — not stdlib-only.
- **Doesn't directly answer Q1 or Q2.** Answers a closer-to-Gain
  question: "does motif + accessibility discriminate when given
  the right cell type?" That is **method validation**, not
  biological discovery.
- **Highly likely to surface another negative finding.** Even with
  cell-type-resolved accessibility, the motif degeneracy problem
  persists — relative_score ≥ 0.85 still hits hundreds of positions
  per 100 kb regardless of substrate.

**Honest classification:** **audit completeness, dressed as method
refinement.** Even a successful Option A run would output a refined
version of Gain's indirect-evidence layer — not a new biological
finding. It might rescue Gain's pipeline; it would not answer the
unresolved questions the project actually framed.

## Option B — Expression / CELLxGENE Census route (Q1 + Q2)

**What it would do.** Tackle Q1 and Q2 from
[`notes/unresolved_questions.md`](unresolved_questions.md) directly:

- **Q1:** when and how does the bipotent SOX2/SOX9 co-expressing
  tip cell commit to airway vs alveolar fate in *human* fetal lung?
- **Q2:** is the proximal-distal axis a continuous gradient or a
  discrete switch — and does the answer depend on developmental
  stage?

Both are answerable with primary human lung scRNA-seq via
**CELLxGENE Census**. Substrate:
- HLCA core (Sikkema 2023) — adult reference, ~2.4M cells
- He et al. 2022 fetal lung — staged developmental cells
- Cao et al. 2020 pan-fetal — broader timing context
- LungMAP human developmental scRNA-seq — additional staged donors

All accessible programmatically via `cellxgene-census` Python SDK
with cross-dataset standardised cell-type annotations.

**Pros:**
- **Directly answers the unresolved questions** that motivated
  Gain's existence (`notes/unresolved_questions.md` was written on
  day 2 of the project; Q1 and Q2 have been deferred ever since).
- **Substrate is the most mature in the project's resource list.**
  CELLxGENE Census is standardised, indexed, and well-documented.
  No per-paper bespoke processing.
- **Standard Python idiom.** `cellxgene-census` + `scanpy` +
  `anndata` is well-trodden territory with strong community support.
  No exotic tools.
- **Quantitative scores per cell, not categorical per pair.** Each
  cell gets a SOX2/SOX9 ratio; each commitment branch gets a
  pseudotime; each axis gets a continuous score. Real numbers,
  amenable to visualisation and statistical inference.
- **Produces biological findings.** Q1's answer ("commitment occurs
  at week 14 with intermediate state X") and Q2's answer ("axis is
  continuous in fetal, discrete in adult") are publishable-style
  outcomes — not method-refinement outcomes.

**Cons:**
- **Heaviest dependency stack the project has so far considered.**
  `cellxgene-census` + `tiledbsoma` + `pyarrow` + `pandas` + `numpy`
  + `scanpy` + `scipy`. Breaks the stdlib-only pattern that defined
  every Gain script.
- **Different analysis idiom than Gain.** Single-cell normalisation,
  dimensionality reduction, pseudotime, score distributions — none
  of which use interval intersection. The audit-cycle skill set is
  not directly transferable.
- **Census API has its own quirks.** Slicing large datasets can be
  slow; cell-type annotations vary across upstream studies; per-
  donor biological variation is significant.
- **Bigger commitment.** Building a Q1/Q2 analysis is not a few-
  hundred-LoC script; it's a small research project in its own
  right.

**Honest classification:** **biological insight, real research
question, mature substrate.** A Q1 / Q2 answer is the kind of
finding that has been the implicit goal of the project from the
start.

## Recommendation

**Option B — Expression / CELLxGENE Census route.**

Reasons (ordered by weight):

1. **The user's stated bias decides this.** "Actual biological
   insight, not more audit completeness" rules out Option A
   directly. Option A is method validation — even a successful run
   produces a better indirect-evidence pipeline, not a biological
   finding.
2. **Q1 and Q2 are the unresolved-question seeds the project was
   built to address.** They were written on day 2 of Gain; the
   audit cycle was the deferred-MVP path. The successor project is
   the natural completion of that intention.
3. **Substrate maturity.** CELLxGENE Census is the most polished
   public substrate the project has touched. Option A's substrate
   (cell-type-resolved scATAC) requires per-paper integration work
   that typically dominates the analysis time.
4. **Dependency cost is justified once.** Adding `cellxgene-census`
   + `scanpy` to a successor project is acceptable because the
   biological insight payoff is direct. Adding the same stack to a
   project whose deliverable is a refined indirect-evidence layer
   is harder to justify.

## What the next project's first implementation step should be

In the successor repository (separate repo recommended; new branch
on Gain acceptable):

1. **Bootstrap with the same discipline as Gain v0.** Three planning
   notes first (`notes/evidence_map.md`, `notes/status.md`,
   `notes/next_steps.md`) before any code, per
   `feedback_plan_before_code` (carried over to the new project).
2. **First MVP: Q1 only.** Bipotent SOX2/SOX9 commitment timing in
   He 2022 fetal lung scRNA-seq via Census. Defer Q2 to v0.x.
3. **Define the smallest useful Q1 result up front.** Probably:
   "for each fetal stage in He 2022, what fraction of distal-tip
   cells co-express SOX2 + SOX9 above defined thresholds, and what
   marker genes distinguish the committed-airway vs committed-
   alveolar daughter populations?" One figure + one CSV.
4. **Acknowledge the dep-add cost explicitly** in the new
   project's design notes — `cellxgene-census` + `scanpy` are
   committed dependencies; the new project's scope discipline rules
   become "no additional packages beyond this stack" rather than
   Gain's "stdlib only."

## What the next project should *not* do

- **Not redo Gain's audit cycle.** The chain audit findings are
  preserved here; cite them rather than re-deriving.
- **Not extend to the regulator chain again.** The next project is
  about cell-state biology (commitment, axis continuity), not
  regulator-target binding.
- **Not assume Census + scanpy is a "platform."** Same scope rules
  apply: no generic framework, no dependency unless it clearly
  reduces complexity, no architecture sections longer than working
  code.
- **Not abandon Gain.** Gain's standing outputs (5 NKX2-1 candidate
  loci, audit machinery, substrate-gap diagnosis) remain useful and
  may be cited from the successor project.

## Summary

| Axis | Option A (cell-type ATAC) | Option B (Census expression) |
|---|---|---|
| Answers an unresolved Q1/Q2 question | no — refines audit | **yes — Q1 + Q2 directly** |
| Substrate maturity | per-paper bespoke | **standardised (Census)** |
| Dependency cost vs biological insight | high cost, low insight | **acceptable cost, high insight** |
| Continuity with Gain skills | yes (interval intersection) | partial (new idiom) |
| Likelihood of publishable finding | low | **medium-high** |
| Aligns with user's stated bias | no | **yes** |

**Pick: Option B — CELLxGENE Census expression route, starting with
Q1 (commitment timing in fetal lung).**
