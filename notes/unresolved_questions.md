# Unresolved Questions

Three only. Each must stay inside the lung middle-layer control logic
(NKX2-1 / SOX2 / SOX9 / proximal-distal patterning / FGF10 / WNT / BMP /
SHH / airway vs alveolar outcomes), be testable with public data, and
have a defined smallest-useful-next-step.

---

## Q1. When and how does the bipotent SOX2/SOX9 co-expressing tip cell commit to airway vs alveolar fate in *human* fetal lung?

**Why unresolved.** The proximal-distal split via SOX2/SOX9 is textbook
in mouse, but human-specific staging is meaningfully different
(reviewed by Nikolic & Rawlins 2017; further refined by Nikolic et al
2017 *Cell Stem Cell*; He et al 2022 *Nat Genet*). Several groups
report SOX2/SOX9 co-expressing cells in human distal tips well into
the canalicular stage, with no consensus yet on (a) precisely when
commitment becomes irreversible in human, and (b) what intermediate
states sit between the bipotent tip cell and the committed lineages.

**Why it matters.** Human organoid protocols and disease-modelling
systems depend on accurate human-specific commitment timing. If
commitment is later than the mouse-derived models predict, current
organoid stage assignments may be off by days or weeks of in-vitro
differentiation.

**Public data that could test it.**
- He et al 2022 fetal lung scRNA-seq + spatial — staged human samples
  spanning pseudoglandular through canalicular.
- LungMAP human developmental projects — additional staged donors.
- Cao et al 2020 pan-fetal atlas — broader timing context.

**Smallest useful next step.** Pseudotime + branch-point analysis on He
2022 of cells co-expressing SOX2 and SOX9 above defined thresholds:
identify the per-stage fraction of double-positive cells, the inferred
branch points, and the gene programs distinguishing airway-committed
vs alveolar-committed daughters. Stop at one figure + one supplementary
table.

**New infrastructure needed?** Yes — first real data dependencies:
`cellxgene-census`, `scanpy`, `anndata`. **This is a meaningful
dependency add and should not happen casually.** Justifiable only
because the question is genuinely unresolved and the data exists.

---

## Q2. Is the proximal-distal axis a continuous gradient or a discrete switch — and does the answer depend on developmental stage?

**Why unresolved.** Methodologically the field uses both
representations. Continuous "axis scores" (gene-set sum or PCA along
a defined direction) appear in some papers; discrete cell-type labels
("proximal airway basal cell" vs "distal alveolar progenitor") appear
in others. Whether the underlying biology is genuinely continuous
(many cells along a gradient) or genuinely discrete (cells are
clearly one or the other) has not been answered head-on for human
lung at any stage.

**Why it matters.** This determines the right statistical
representation. If the axis is continuous in development and discrete
in adulthood, then pseudotime, RNA-velocity, and cell-state-scoring
methods are appropriate for fetal but not adult work; the reverse
strategy (label transfer from a discrete adult reference) silently
mis-assigns continuous fetal cells. This affects every downstream
trajectory analysis in the field.

**Public data that could test it.**
- HLCA core (adult — likely discrete).
- He et al 2022 fetal lung (likely more continuous).
- LungMAP staged human projects (intermediate timing).

**Smallest useful next step.** Define a 10-gene proximal score
(TP63, KRT5, KRT15, SCGB1A1, MUC5B, BPIFB1, FOXJ1, MUC5AC, NOTCH3,
KRT8) and a 10-gene distal score (SFTPC, SFTPB, SFTPA1, SFTPA2, AGER,
HOPX, PDPN, ABCA3, RTKN2, EPCAM-low). Score every epithelial cell in
HLCA and He 2022. Per dataset and per developmental stage, run
Hartigan's dip test on (proximal_score − distal_score). Report dip
statistic + bootstrap CIs. Stop at one figure (one dip-statistic
plot per stage) and one CSV (per-cell scores).

**New infrastructure needed?** Yes — same dependency stack as Q1
(`cellxgene-census`, `scanpy`, plus `scipy` for the dip test). Same
justification + same caveat.

---

## Q3. Of the canonical regulator-target relationships in the lung-development chain, which are supported by *human* public-data evidence vs. extrapolated from mouse — and where are the data gaps?

**Why unresolved.** Most of the relationships in
`metadata/switch_hierarchy.csv` (and in field-wide reviews) are
mouse-derived. The human-specific evidence base has not been
audited end-to-end. The verifier already surfaced one such gap:
NKX2-1, SOX2, and SOX9 have **zero** TF ChIP-seq experiments in
ENCODE in any human biosample. ENCODE has 6 TF ChIP-seq experiments
in lung tissue total — 5 mouse, 1 human (CTCF). The same audit
across all the canonical relationships has not been done.

**Why it matters.** Cross-species TF binding is approximately 50%
conserved on average; for tissue-specific developmental TFs, transfer
is even less reliable. Knowing exactly which regulator-target claims
in our scope rest on human evidence vs. mouse extrapolation reshapes
what can be claimed in human-relevant disease modelling, organoid
validation, and CRISPR target design. **A documented enumeration of
the gap is itself a contribution.**

**Public data that could test it.**
- ENCODE — TF ChIP-seq, ATAC-seq, DNase-seq, histone ChIP-seq across
  human and mouse, lung biosamples and otherwise.
- CELLxGENE Census — expression correlation between regulator and
  putative target across human cell types and developmental stages.
- PubMed E-utilities — supporting paper count per (TF, target) pair as
  a citation-density signal.

**Smallest useful next step.** A ~150-line Python script
(`scripts/gain_evidence_audit.py`, stdlib + `urllib`) that, for each
(regulator, target) pair currently in `switch_hierarchy.csv`, records:
(a) ENCODE TF ChIP-seq experiments for the regulator in lung biosamples
(human and mouse separately), (b) ENCODE ATAC/DNase peaks within
±50 kb of the target gene's TSS in lung biosamples, (c) presence or
absence of regulator binding-motif occurrences in those peaks
(deferred until v2.x; document as gap for v0). Output a CSV with
per-pair evidence-class labels: `human_chip_supported` /
`mouse_chip_supported` / `accessibility_only` / `motif_only` /
`unsupported_in_public_data`. Stop at the CSV + a one-page summary in
`notes/`.

**New infrastructure needed?** Minimal — the manifest CLI + verifier
+ `urllib`. No Census / Scanpy / scvi-tools. This is the cheapest of
the three questions because it lives at the metadata-and-pointers
layer Gain has already built.

---

## Why exactly three

A longer list dilutes commitment. These three are deliberately chosen
so that:

- Q1 and Q2 are genuinely unresolved biology questions and require a
  real dependency add (Census + Scanpy). They are the right kind of
  work but expensive.
- Q3 is genuinely unresolved as a *data-availability and evidence-
  audit* question and requires no new dependencies. It is the cheapest
  way to produce a non-trivial result and the most natural extension
  of the existing infrastructure.

If only one question can be tackled next, **Q3 wins on cost-to-value**.
If a dependency add is warranted, Q1 and Q2 are the right targets.
