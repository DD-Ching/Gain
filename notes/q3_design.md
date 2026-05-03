# Q3 Evidence Audit — Design

**Question being addressed.** *Of the canonical regulator-target relationships
in the lung-development chain, which are supported by **human** public-data
evidence vs. extrapolated from mouse — and where are the data gaps?*
(See `notes/unresolved_questions.md`.)

This document is the design contract for the v0 audit. Implementation must
match it; deviations require updating this doc first.

## Audit scope

In scope:
- **TF → target gene pairs** in the NKX2-1 / SOX2 / SOX9 / FGF10 / WNT /
  BMP / SHH / airway / alveolar regulatory chain, where the regulator is a
  **transcription factor** (not a ligand or pathway).
- Human evidence sourced from **ENCODE** TF ChIP-seq, supplemented by lung
  ATAC-seq and DNase-seq counts (for context, not classification).
- Mouse TF ChIP-seq from ENCODE, treated as cross-species evidence only.
- Literature support is *implicit*: every audited pair is in
  `metadata/regulator_target_pairs.csv`, which by construction is
  literature-curated.

Explicitly out of scope (v0):
- **Ligand → target relationships.** FGF10 / BMP4 / WNT-ligands / SHH-ligand
  are not TFs and cannot be ChIP-seq'd; they need a different audit shape.
  We use the downstream effector TFs (CTNNB1 for canonical WNT, SMAD1 for
  BMP, GLI2 for SHH) instead. FGF10 has no clean effector substitute and
  is excluded from v0.
- **Peak intersection with the target gene's locus.** v0 classifies based
  on whether a regulator has *any* TF ChIP experiment in the relevant
  biosample category, not whether that experiment's peaks overlap the
  target gene. Real "this regulator binds this target's locus" inference
  is v1+ work that needs BED parsing.
- **Motif scanning.** v0 does not scan for the regulator's binding motif
  in lung accessible chromatin. The `accessibility_only_support` class is
  defined but cannot be populated by v0 (see classes below).
- **Co-expression evidence** (regulator and target expressed in the same
  cells). Requires CELLxGENE Census + Scanpy; deferred per
  `notes/next_step_decision.md`.
- **Non-ENCODE ChIP repositories** (e.g., GEO ChIPAtlas, Cistrome,
  ReMap). v0 is ENCODE-only.

## Evidence classes

Five classes, ordered by evidence strength. Each pair is assigned the
**highest-strength applicable** class.

1. **`direct_human_evidence`** — A human TF ChIP-seq experiment exists for
   the regulator in a **lung** biosample. The strongest class; if assigned,
   the relationship can be tested against real human lung data with peak
   intersection (v1 work).
2. **`indirect_human_evidence`** — A human TF ChIP-seq experiment exists
   for the regulator in a **non-lung** biosample. Cross-tissue applicability
   is uncertain; binding is plausibly informative for the same locus but
   tissue-specific cofactors may not match.
3. **`mouse_supported_only`** — TF ChIP-seq for the regulator exists only
   in **mouse** (lung or otherwise). Cross-species transfer is ~50%
   reliable on average; tissue-specific developmental TFs lower.
4. **`accessibility_only_support`** — *(Defined but not populated by v0.)*
   No regulator TF ChIP exists, but lung ATAC-seq or DNase-seq could be
   combined with motif scanning to test the relationship. v0 skips this
   class because motif scanning is not implemented; pairs that would
   qualify fall through to class 5.
5. **`literature_curation_only`** — The relationship is in the
   literature-curated `regulator_target_pairs.csv` but no ENCODE evidence
   in any of the above categories exists for the regulator. **This is not
   a claim that the relationship is wrong** — it is a claim that the
   public-data record currently does not corroborate it.

## Important rule: do not present missing evidence as negative evidence

`literature_curation_only` means **"absence of supporting public data"**,
not **"absence of the relationship"**. The relationship may be entirely
real and well-established in the wet-lab literature; the audit only
records what *public data* in *one specific repository* (ENCODE) supports.

Every output must make this distinction visible to the reader. The
`evidence_audit.md` summary should state this rule prominently and the
CSV's `justification` column should never use language like "no
relationship" or "unsupported"; the correct phrasing is
"no ENCODE TF ChIP found for this regulator" or similar.

## Inputs

`metadata/regulator_target_pairs.csv` (new file in this turn). Schema:

| column | meaning |
|---|---|
| regulator | gene symbol of the upstream TF |
| target | gene symbol of the putative downstream gene |
| relationship_type | one of: `master_to_progenitor`, `master_to_output`, `progenitor_to_output`, `pathway_effector_to_target` |
| from_layer | regulatory layer of the regulator |
| to_layer | regulatory layer of the target |
| literature_summary | one-sentence textbook summary; cited in the audit's `justification` when class is `literature_curation_only` |

The pairs are hand-curated for v0. ~18 pairs spanning NKX2-1, SOX2, SOX9,
CTNNB1, SMAD1, GLI2 as regulators.

## Outputs

`metadata/evidence_audit.csv`. Schema:

| column | meaning |
|---|---|
| regulator | from input |
| target | from input |
| relationship_type | from input |
| evidence_class | one of the 5 classes defined above |
| species_with_evidence | `human` / `mouse` / `none` (driven by where ENCODE counts > 0) |
| source_type | `TF_ChIP-seq` / `TF_ChIP-seq+lung_accessibility` / `none` |
| tissue_relevance | `lung` / `non-lung` / `n/a` |
| n_human_lung_chip | count of human TF ChIP in lung biosamples for the regulator |
| n_human_other_chip | count of human TF ChIP in non-lung biosamples |
| n_mouse_chip | count of mouse TF ChIP (any tissue) |
| justification | one short line explaining the class assignment, citing counts |
| evidence_url | the ENCODE search URL whose result drove the class assignment (or n/a) |

`notes/evidence_audit.md`. Human-readable summary:

- One-sentence framing of the question.
- Counts per class (e.g., `direct_human_evidence: 0 / 18`).
- Strongest pairs (highest evidence class).
- Weakest pairs (literature-only).
- The most striking gaps (regulators with zero ChIP evidence anywhere).
- The non-evidence-vs-non-relationship reminder.

## Edge cases

- **Regulator has zero TF ChIP in any species/tissue** → `literature_curation_only`.
  This will be the class for NKX2-1, SOX2, SOX9, CTNNB1 based on the
  pre-implementation probe.
- **Regulator has TF ChIP only in non-lung human tissue** →
  `indirect_human_evidence`. The justification must name the tissue
  context (or "multiple non-lung tissues") and warn about cross-tissue
  applicability.
- **Regulator has TF ChIP in mouse only** → `mouse_supported_only`. (None
  of our pre-probed regulators currently fall here, but the rule must
  exist.)
- **Regulator name is ambiguous** (e.g., NKX2-1 vs Nkx2-1 vs NKX2.1) →
  v0 uses the human gene symbol exactly as `target.label` in ENCODE.
  The pre-probe verified `NKX2-1` is the correct casing for human ENCODE.
- **Pair appears in `regulator_target_pairs.csv` more than once** → v0
  treats each row as a separate audit entry; deduplication is the
  curator's responsibility.
- **ENCODE returns 404 (zero results)** → counted as 0, not as an error.
  The verifier already established this is ENCODE's normal behavior for
  empty result sets.
- **HTTP failure or timeout on a query** → the audit logs the error and
  marks the pair as `error` (not a real class). v0 retries once with a
  longer timeout.

## What counts as human evidence

- **Counts as direct human evidence:** any human TF ChIP-seq experiment in
  a lung biosample with the regulator as `target.label`. Released or
  in-progress; v0 does not filter on `status`.
- **Counts as indirect human evidence:** any human TF ChIP-seq experiment
  in a non-lung biosample with the regulator as `target.label`.

## What does NOT count as human evidence (in v0)

- Histone ChIP-seq (H3K4me3, H3K27ac, etc.) — these mark active regulatory
  regions but do not identify the specific TF binding. Excluded from
  classification but lung histone counts will appear in the audit's
  context section.
- ATAC-seq / DNase-seq — accessibility, not TF identity. Same treatment as
  histone marks.
- ChIP-seq in *C. elegans* / *Drosophila* / non-mammalian biosamples (the
  one SOX2 hit anywhere in ENCODE TF ChIP is in *C. elegans*, and it is
  ignored for this audit).
- Co-expression in scRNA-seq.
- ATAC + motif (would qualify for `accessibility_only_support` if motif
  scanning were implemented; v0 does not implement it).
- Literature without underlying public data.

## Implementation outline

1. Read `metadata/regulator_target_pairs.csv`.
2. For each unique regulator, issue **three** ENCODE GET queries:
   - `assay_title=TF+ChIP-seq&target.label=<R>&biosample_ontology.term_name=lung&format=json` → human-or-other lung
     *(refine: filter by organism for human-lung specifically)*
   - `assay_title=TF+ChIP-seq&target.label=<R>&replicates.library.biosample.donor.organism.scientific_name=Homo+sapiens&format=json` → human any tissue
   - `assay_title=TF+ChIP-seq&target.label=<R>&replicates.library.biosample.donor.organism.scientific_name=Mus+musculus&format=json` → mouse any tissue
3. Cache regulator-level counts in memory; one set of counts per
   regulator drives all its pairs.
4. Apply the precedence rules; write the CSV.
5. Render the Markdown summary.

Stdlib only. `urllib.request` + `json` + `csv` + `argparse`. No new
dependencies.

## What v0 is *not*

- Not a regulatory-relationship validator. v0 cannot say "yes, NKX2-1
  binds the SFTPC promoter in human lung" — it can only say
  "an ENCODE TF ChIP-seq experiment that *could* test that exists / does
  not exist."
- Not a comprehensive evidence audit. ENCODE is one of multiple public
  ChIP repositories. ChIPAtlas / Cistrome / ReMap may have additional
  experiments outside ENCODE's scope.
- Not a substitute for peer-reviewed literature claims. The audit
  contextualises literature against public data; it does not arbitrate.
