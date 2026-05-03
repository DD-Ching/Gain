# Evidence Model v2

**Status:** design contract for the v2 audit. Implementation must match
this document; deviations require updating it first.
**Reason for v2:** the v0/v1/extension audits treated ENCODE as the
universe and treated source-level and locus-level evidence as one tier.
Both assumptions are wrong:

1. **ChIP-Atlas materially changes the source-level landscape.** It
   aggregates GEO/SRA TF ChIP that ENCODE does not ingest. Its
   `antigenList.tab` is stdlib-parseable; `experimentList.tab` (~344
   MB) is locally cacheable and can be filtered on tissue context with
   simple grep (`tissue=lung`, etc.).
2. **Peak-level intersection at the target locus is a strictly stronger
   class** than "the regulator has any human ChIP." The v0 peak audit
   on the four `direct_human_non_lung_evidence` pairs showed two
   validate at the locus and two fail.

v2 makes both first-class: ChIP-Atlas is added to the source layer,
and a peak-level tier is added at the top of the hierarchy.

## The six v2 classes (ordered by evidence strength, strongest first)

| # | Class | Trigger |
|---|---|---|
| 1 | **`peak_validated_at_target_locus`** | At least one human ChIP-seq peak from any source (ENCODE, ChIP-Atlas, or imported) overlaps or sits within ± 50 kb of the target gene's hg38 TSS. The locus test must have been *attempted and passed*. |
| 2 | **`direct_human_lung_evidence`** | At least one source reports human TF ChIP-seq for the regulator in **lung-context** biosamples (lung tissue OR lung-derived cell line OR lung cancer line — see lung-context rule below). Locus test either not done, not yet done at scale, or done with mixed/incomplete results. |
| 3 | **`direct_human_non_lung_evidence`** | At least one source reports human TF ChIP-seq for the regulator in **non-lung** biosamples only. Includes pairs whose locus test was attempted and failed (the failure does not promote them, but it does not demote them below this tier either). |
| 4 | **`indirect_accessibility_support`** | No human TF ChIP for the regulator in any source, but lung ATAC-seq / DNase-seq + a TF binding-motif match exists. **Not populated by v2 because v2 does not implement motif scanning.** Defined here to keep the precedence stable for future audits. |
| 5 | **`literature_curation_only`** | All checked sources (ENCODE live, ChIP-Atlas cached) report zero TF ChIP-seq for the regulator. The relationship rests entirely on the wet-lab literature; absence here is absence of supporting public data, **not** absence of relationship. |
| 6 | **`unresolved_gap`** | Cannot conclude: at least one source we declared in scope was not checked. Should be empty for our six regulators in v2 once ChIP-Atlas is integrated, since ChIP-Atlas's coverage is large enough to give a defensible "no-evidence" claim when it reports zero. |

## Exact rules for moving between classes

The classifier evaluates the rules in order; first one that fires wins.

```
def classify_v2(pair):
    locus_result = peak_intersection_for(pair)         # supports / weak / no_support / not_tested
    encode = encode_counts_for(regulator)              # n_human_lung, n_human_other, n_mouse
    chipatlas = chipatlas_counts_for(regulator)        # n_hg38_total, n_hg38_lung, n_hg38_other

    # Rule 1: peak-level validation
    if locus_result in {"supports", "weak_support"}:
        return "peak_validated_at_target_locus"

    # Rule 2: lung source-level evidence anywhere
    if encode["n_human_lung"] > 0 or chipatlas["n_hg38_lung"] > 0:
        return "direct_human_lung_evidence"

    # Rule 3: non-lung human source-level evidence anywhere
    if encode["n_human_other"] > 0 or chipatlas["n_hg38_other"] > 0:
        return "direct_human_non_lung_evidence"

    # Rule 4: accessibility-only (v2 does not populate)
    # if motif_scanning_implemented and lung_atac_or_dnase_exists: ...

    # Rule 5: nothing in any checked source
    if all_sources_checked():
        return "literature_curation_only"

    # Rule 6: incomplete check
    return "unresolved_gap"
```

Notes:

- **Locus failure does not demote.** If a pair's peak intersection
  returned `no_locus_support`, it is *not* "below" `direct_human_non_lung_evidence`;
  it falls through to whatever source-level tier applies and the
  failure is noted in `justification`. v2.x could add a distinct
  `non_lung_chip_does_not_validate_at_locus` class; not needed for v2.
- **Lung+peak combination collapses to peak_validated.** A pair with
  both lung ChIP and a passing locus test is `peak_validated_at_target_locus`,
  not "lung+validated". The locus test is the stronger claim; the
  lung context is recorded in the `justification`.
- **Tissue context for ChIP-Atlas** uses the simple inclusive filter
  `lower(row).contains("lung")`, applied to the experimentList.tab
  rows. This matches lung tissue, lung-derived cell lines (NCI-H441,
  A549, H1299), and lung cancer specimens. The filter is intentionally
  broad to start; v2.x can refine with cell-type ontology mapping.

## What is being audited

The same six regulators, eighteen pairs as v0/v1 — see
`metadata/regulator_target_pairs.csv`:

- NKX2-1 (×7 targets)
- SOX2 (×3)
- SOX9 (×2)
- CTNNB1 (×2)
- SMAD1 (×2)
- GLI2 (×2)

The graph is **not** expanded in v2 — same 18 pairs. The user's
explicit instruction: "do not explode the graph."

## Sources used in v2

| Source | Access | Count level | Locus level |
|---|---|---|---|
| **ENCODE** | live REST API | TF ChIP search by regulator + organism + tissue | downloadable narrowPeak BEDs (already used by `gain_peak_intersection.py` for the SMAD1/GLI2 pairs) |
| **ChIP-Atlas** | local cache of `antigenList.tab` (9 MB) and `experimentList.tab` (~344 MB; gitignored under `metadata/cache/`) | regulator-level totals + tissue filter via inclusive `lung` substring match | per-experiment peak BED files exist at `chip-atlas.dbcls.jp/data/{genome}/eachData/bedNN/{srx}.NN.bed` but **v2 does not download them** (~270 files, 100s of MB); locus-level audit on ChIP-Atlas is v3 |

Cistrome and ReMap remain JS-rendered and out of scope for v2's
programmatic layer. Their per-regulator URLs stay in
`metadata/external_chip_lookups.csv` for manual reference but do not
feed the v2 classifier.

## Sources NOT used in v2 (deliberate scope)

- Cistrome v3 / ReMap (per above; JS-rendered)
- ChIPAtlas peak-level data (deferred to v3)
- Motif scanning (would populate `indirect_accessibility_support`;
  deferred — needs JASPAR or a similar PWM source)
- Co-expression evidence from CELLxGENE Census (separate Q1/Q2 work;
  explicitly deferred per `notes/next_step_decision.md`)
- Mouse ChIP for promotion across species (mouse counts are recorded
  for context but never promote a pair into a "human" class)

## Anti-overclaim rules carried forward

- **Lung-context in ChIP-Atlas is broad.** It includes lung cancer cell
  lines (NCI-H441, A549, H1299) and lung-derived cell lines, not only
  primary lung tissue. The `direct_human_lung_evidence` class therefore
  means "ChIP-seq exists in some lung-related biosample" — strictly
  stronger than non-lung but **weaker than primary lung tissue ChIP**.
  Every justification line for this class must name the lung-context
  refinement that is *not* yet applied (cancer-vs-tissue, primary-vs-line).
- **Peak validation does not equal regulatory function.** A peak within
  ± 50 kb of a target's TSS is necessary but not sufficient for direct
  regulation. The audit reports binding *at the locus*, not regulatory
  effect.
- **Source-level totals do not mean per-pair binding.** A regulator
  with 95 ChIP experiments may bind a particular target in 0 of those
  95 experiments. Source-level evidence is a **prerequisite** for
  testable claims, not a confirmation.

## Output schema (what the v2 audit must emit)

`metadata/evidence_audit_v2.csv` — one row per pair, columns:

| column | meaning |
|---|---|
| regulator | gene symbol |
| target | gene symbol |
| relationship_type | from `regulator_target_pairs.csv` |
| **v2_class** | one of the six classes above |
| **changed_from_extended_audit** | `yes` / `no`, vs `evidence_audit_extended.csv` |
| encode_n_human_lung | live count |
| encode_n_human_other | live count |
| chipatlas_n_hg38_lung | from cached experimentList.tab |
| chipatlas_n_hg38_other | from cached experimentList.tab |
| peak_intersection_summary | inherited from `peak_intersection_results.csv` if available; "not_tested" otherwise |
| locus_test_status | `passed` / `failed` / `not_tested` |
| justification | one short paragraph naming the rule that fired and the relevant counts/caveats |
| evidence_url | best representative URL (lung-context preferred) |

`notes/evidence_audit_v2.md` — human-readable report. Required sections:
- Class counts (v2 totals)
- The transition table: how many pairs changed class vs. the extended
  audit
- The deliverable answer: which links have peak-validated locus-level
  support? Which only source-level lung context? Which only non-lung?
- Headline caveats and what v2 still does not test

## Deliverable goal (matches user's stated requirement)

> For the canonical lung developmental chain, which regulator-target
> links have actual public human locus-level support, and which remain
> mostly textbook canon without strong public support?

The v2 report answers this with:
- Number and identity of pairs in `peak_validated_at_target_locus`
- Number and identity of pairs in `direct_human_lung_evidence`
  (with the "lung context but locus untested" caveat)
- Number and identity of pairs in `direct_human_non_lung_evidence`
  (including pairs whose locus test failed)
- Confirmation of whether `literature_curation_only` is empty after
  ChIP-Atlas integration

The expected pre-audit prediction (to be tested by the v2 run):
- 2 pairs `peak_validated_at_target_locus` (SMAD1 → ID1, SMAD1 → ID2)
- 10 pairs `direct_human_lung_evidence` (all 7 NKX2-1 + 3 SOX2)
- 6 pairs `direct_human_non_lung_evidence` (2 SOX9 + 2 CTNNB1 + 2 GLI2)
- 0 pairs `literature_curation_only`
- 0 pairs `unresolved_gap`
