# Post-Chain Recommendation

**Status:** recommendation memo. No implementation.
**Inputs:** [`notes/post_chain_options.md`](post_chain_options.md)

## Recommendation

**Option A — motif scanning + accessibility inference.**

This is the highest insight-per-effort move from where the chain
audit currently sits.

## Why A beats the others

### A vs B (expression-correlation / Census)

- **A directly attacks the substrate ceiling.** The chain audit's
  central finding is that lung-context TF ChIP is missing for the
  regulators that matter (zero lung experiments for SOX9, all-
  cancer for NKX2-1, cancer + reprogramming for SOX2). Option A is
  the only option that brings a *primary lung tissue substrate*
  (ENCODE's 35 lung ATAC + DNase experiments — already inventoried
  in `metadata/sources.json`) into the project.
- **B answers a different question.** Co-expression in primary lung
  scRNA-seq is a necessary-but-not-sufficient condition for binding;
  the headline answers ("NKX2-1 and SFTPC co-expressed in AT2
  cells", etc.) are mostly already in the textbook. The novelty of
  B is in tooling, not in finding.
- **B's dependency cost is the heaviest in the project's history.**
  CELLxGENE Census + `tiledbsoma` + `pyarrow` + `pandas` breaks the
  stdlib-only pattern that has defined every script. The project's
  scope-discipline rule ("no dependency unless it clearly reduces
  total complexity") applies — B does not clearly reduce complexity;
  it adds a different kind.
- **A is stdlib-able.** PWM scanning is ~ 50–100 lines; sequence
  fetching via UCSC DAS / Ensembl REST is stdlib HTTP; ATAC BEDs are
  already used by `gain_peak_intersection.py`.

If A produces no signal at all, B is the natural next move (with
eyes-open dependency commitment). But A is cheaper, faster, and
directly continuous with the chain audit's standing pairs.

### A vs C (infrastructure)

The user's standing rule: "do not resume generic infrastructure
unless it clearly supports a specific unresolved question."
Infrastructure work that is not tied to a question is the project's
named anti-pattern. A is tied to a specific question (does motif +
accessibility align for the failing pairs in lung tissue); C is not.

### A vs D (stop and preserve)

D is defensible. The chain audit has produced real findings, and a
project-level summary of NKX2-1 / SOX2 / SOX9 together would be a
real contribution. But D accepts the substrate ceiling rather than
piercing it, and the project's operating mode has been to ask
"what's the smallest next step that adds genuine insight" — not
"what is enough to publish what we have."

A produces ~ 12+ new pair-level evidence-tier results (the failing
pairs from across all three regulator audits). Each is either
positive ("motif + accessibility plausibility exists") or negative
("even motif + accessibility cannot rescue this pair"). Both
outcomes are substantive. The marginal effort is ~ 200–300 LoC of
stdlib Python plus a few MB of motif data — comparable to or less
than `gain_nkx21_distal_candidates.py`.

D remains valuable as a *follow-on* to A — once A surfaces what
indirect evidence exists, the standing-outputs summary is more
informative.

## Why I recommend A *with one constraint*

A's busywork risk is real if executed broadly. The constraint:

- **Run A first on NKX2-1's 4 robustly-failing canonical pairs**
  (SFTPC, SCGB1A1, ABCA3, FOXA2). These are the highest-prior
  pairs where motif + accessibility plausibility is most
  decision-relevant. They are also the pairs where the textbook
  claims are strongest, so a positive result corroborates 30 years
  of consensus indirectly, and a negative result is a real
  research-direction-changing finding.
- If those four produce signal, **expand to SOX2's failing pairs**
  (TP63, KRT5, MUC5B + SCGB1A1) as a v0.x. Each is independently
  decision-relevant.
- If those four produce no signal, **do not expand** — the
  conclusion is "motif + accessibility cannot rescue these pairs",
  which is itself a clear stopping point. Hand off and consider
  D + B together as a longer-horizon plan.

This constrained A is the smallest possible useful pass that
directly tests whether the substrate ceiling is the binding
constraint or whether the gap is deeper.

## What exact first implementation step would follow if approved

**1. Write `notes/motif_accessibility_audit_design.md`** — design
contract before any code. Required content:

- Scope: NKX2-1 only, 4 targets (SFTPC, SCGB1A1, ABCA3, FOXA2).
- Inputs: ENCODE lung ATAC + DNase BED files (URL pattern same as
  `gain_peak_intersection.py`); JASPAR NKX2-1 PWM (download once).
  hg38 sequence per-target ± 50 kb window via UCSC DAS or Ensembl
  REST.
- Output classes: a new evidence tier
  `indirect_accessibility_support_in_lung_tissue` between
  `direct_human_non_lung_evidence` and `lung_context_source_only`
  in the v2 hierarchy. Plus the absence variant
  `motif_in_accessible_chromatin_negative` as a substantive
  negative finding.
- Threshold rules: motif score threshold (JASPAR's standard
  `relative_score >= 0.85` cutoff is the default starting point).
  Window: ATAC peak that overlaps the target's promoter ± 50 kb.
- Stop-and-decide rule baked in: after the 4 NKX2-1 pairs, if
  ≥ 2 land in the new positive class, expand to SOX2's failing
  pairs; otherwise stop.

**2. Implement `scripts/gain_motif_accessibility_audit.py`** —
sibling import of helpers, ~ 200–300 LoC stdlib. Reuse the BED
parsing, HTTP fetching, and interval intersection from existing
scripts. Add PWM scoring as a new ~ 50-line block.

**3. Run on NKX2-1's 4 canonical failing pairs.** Output:
`metadata/nkx21_motif_accessibility_audit.csv` and
`notes/nkx21_motif_accessibility_audit.md`.

**4. Stop and report**, parallel to every previous audit
checkpoint. The report answers: how many of the 4 pairs gain
indirect-accessibility support? Does that change the standing
candidate ranking? Does it justify expanding to SOX2's failing
pairs?

That single sequence (design → implement → run → report → stop) is
the same shape every audit cycle has used. No new infrastructure,
no broad platform, no dependency add beyond a few-MB JASPAR motif
file.

## Caveats baked into the recommendation

- **Motif + accessibility plausibility is not binding.** Motifs are
  degenerate; accessibility is bulk; both have false-positive rates.
  The new tier explicitly says "plausibility", not "validation".
- **The result might be uniformly weak.** If motif scores are low
  across the 4 pairs even within accessible regions, the conclusion
  is "even the indirect-evidence layer doesn't rescue this" — which
  is a real conclusion, just a negative one.
- **5 ENCODE lung ATAC + 30 DNase is a thin substrate.** Per the
  manifest. False negatives are possible if the relevant
  cell-type-specific accessible regions are diluted by bulk lung
  tissue averaging. A v1 of this audit could add primary AT2-cell
  ATAC if/when published. But v0 with bulk lung is the right
  starting point.
- **JASPAR PWMs are point-estimate motif models.** They miss
  cell-type-specific binding partners and structural variants. The
  audit is "consistent with binding under standard motif assumptions",
  not "binding occurs".

## Bottom line

**A** is the highest insight-per-effort move because it uses
primary lung tissue ATAC (the substrate the chain audit has been
missing), it stays stdlib-able, it directly addresses the substrate
ceiling, and it produces both yes/no outcomes that meaningfully
update the project's findings. Constrained scope (NKX2-1's 4 pairs
first; expand only on positive signal) keeps the busywork risk in
check.

If A produces signal: expand to SOX2's failing pairs as v0.x;
the chain audit's standing outputs gain a new evidence layer.

If A produces no signal: stop. The substrate ceiling has been
pierced and re-confirmed. D becomes the natural follow-on
(project-level summary), and B becomes a future-horizon option
that requires explicit dependency commitment.

Awaiting approval before any implementation.
