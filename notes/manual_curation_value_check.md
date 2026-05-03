# Manual Curation Value Check

**Question:** is the deferred manual lookup pass for the 12
`(regulator, source)` URLs in `metadata/external_chip_lookups.csv`
actually worth doing — or is it bookkeeping disguised as completeness?

This note answers the user's value-check criteria honestly, including
**concrete predictions** of what the curation would produce so that
the answer is testable rather than handwaved.

## What exact conclusion would become possible only after the manual pass?

The manual pass converts each `unresolved_public_evidence_gap` row into
either:
- a confirmed `literature_curation_only` (zero across all three sources), or
- a promotion to `direct_human_non_lung_evidence` / occasionally
  `direct_human_lung_evidence` / `mouse_supported_only`.

**Specifically:** the audit could legitimately *assert* that NKX2-1
has no public TF ChIP-seq anywhere (currently it can only assert it
has none in ENCODE), and could quantify the substantial non-lung ChIP
substrate for SOX2 and SOX9 that the field uses as proxies.

## What biological question would that conclusion help answer?

Honestly: **it would not directly answer any of Q1, Q2, or Q3 in
`notes/unresolved_questions.md`.** The conclusion is structural ("the
absence is real, not an artefact of looking at one repository"), not
biological. Two indirect contributions:

- It would let downstream users of the audit cite a definitive
  "no-evidence-anywhere" claim for NKX2-1 with confidence — useful when
  designing new wet-lab experiments or scoping new ChIP-seq depositions.
- It would quantify the "non-lung human evidence" substrate the field
  routinely uses as a proxy for lung-developmental TF binding (SOX2 in
  ESC, SOX9 in cartilage). That quantification is mildly useful.

Neither of these is a *finding* about lung developmental control logic.

## How likely is it that the result changes the main research direction?

**Low.** Concrete predictions:

| Regulator | Predicted Cistrome+ReMap (human total) | Expected merged class after curation |
|---|---|---|
| NKX2-1 | 0 or near-zero (consistent with ENCODE) | `literature_curation_only` |
| SOX2 | hundreds (ESC, neural) | `direct_human_non_lung_evidence` |
| SOX9 | tens (skeletal, cartilage, gut) | `direct_human_non_lung_evidence` |
| CTNNB1 | low across all (technical) | `literature_curation_only` or low-count `direct_human_non_lung_evidence` |
| SMAD1 | already 3 in ENCODE; +modest in others | `direct_human_non_lung_evidence` (no class change) |
| GLI2 | already 1 in ENCODE; +modest in others | `direct_human_non_lung_evidence` (no class change) |

**Probability the headline ("NKX2-1 / SOX2 / SOX9 lack direct human
lung-context TF ChIP") changes: very low.** The lung-tissue ChIP gap
is not specific to ENCODE; it reflects a real absence of lung-context
ChIP-seq depositions in any aggregated public repository. Cistrome and
ReMap *aggregate* GEO; they do not *generate* new experiments.

**Probability the research direction changes: very low.** The Q3 audit
already established the actionable claim ("no direct lung evidence;
work toward lung-tissue ChIP, motif scanning, or accessibility-based
inference"). Manual curation refines but does not redirect.

## Smallest manual effort that would test the prediction

Look up **only NKX2-1** on Cistrome v3 and ReMap (2 URLs). Five
minutes of human time. If NKX2-1 reports zero in both, the central
prediction is confirmed and the broader pass is mostly bookkeeping. If
NKX2-1 reports non-zero, the prediction is broken and the broader pass
becomes more interesting.

## What would make manual curation NOT worth doing?

Any of:

1. **The result is predictable from existing knowledge.** Largely true
   here — see the prediction table above.
2. **The cost is high relative to insight.** Twelve JS-heavy portal
   visits at ~3-5 minutes each = ~45-60 minutes of human time, plus
   re-running the audit and re-writing the report. ~1-2 hours total
   for a structural correction we can already articulate without
   doing the work.
3. **The same effort spent elsewhere would produce more insight.** The
   counter-proposal (Option B in `notes/option_decision.md`) is to do
   peak-level intersection on the 4 `direct_human_non_lung_evidence`
   pairs we already have ENCODE coordinates for. That work
   *can change a pair's class to `unsupported-at-target-locus`* —
   genuinely new information, not curation.
4. **The portals' counts may drift.** Cistrome and ReMap are reissued
   periodically. A point-in-time hand-curated count is staler than a
   live API call would be; locking it into the repo without a way to
   refresh it is asymmetric in the wrong direction.

All four of these apply to varying degrees. (4) is mildest; (1)–(3)
all bite.

## What would make manual curation worth doing anyway?

- If a single regulator's curated count (especially NKX2-1's) showed
  unexpected non-zero values, that would be a real surprise and
  should redirect attention. **Mitigation:** the smallest-effort test
  above (look up NKX2-1 only) tests this in 5 minutes.
- If a publication or grant claim required a "checked all major
  ChIP repositories" assertion, the curation would be the cheapest
  way to support it. **Mitigation:** the v0 extension already states
  the limitation honestly; readers can check themselves via the URLs.

## Bottom line

The manual curation produces structural completeness, not biological
insight. The value-per-hour is low. The same effort applied to
peak-level intersection on the 4 `direct_human_non_lung_evidence`
pairs (which we *can* do programmatically with ENCODE peak BED files)
produces something genuinely new — a yes/no validation of those four
canonical claims at the target locus.

**Recommendation:** do the 5-minute NKX2-1-only sanity check, and only
escalate to a full curation pass if that sanity check produces a
surprise. Otherwise, skip and move to the alternative.
