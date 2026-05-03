# Q3 Extension — Cross-Resource Evidence Audit Design

**Question:** is the picture from `notes/evidence_audit.md` (ENCODE-only) the
**actual** picture of public ChIP-seq evidence for the canonical
lung-developmental regulatory chain — or does adding **Cistrome DB** and
**ReMap** materially fill the gap?

**Important framing correction.** The ENCODE-only audit's correct claim is:

> Within ENCODE, direct public TF-binding evidence for the canonical
> lung-development chain is largely absent.

It is **not**:

> Public human ChIP evidence for the canonical lung-development chain is
> essentially empty.

ENCODE is one repository. Cistrome and ReMap aggregate published ChIP-seq
data from GEO and ArrayExpress that ENCODE does not ingest. Until those
are checked, "essentially empty" is overclaim.

## Scope (what this extension does)

For the same 18 regulator-target pairs in
`metadata/regulator_target_pairs.csv`, classify evidence **per source**
across three repositories, then assign a final merged class.

In scope:
- ENCODE TF ChIP-seq (live, REST, already implemented).
- ReMap 2022 (curated GEO + ArrayExpress + ENCODE ChIP-seq / ChIP-exo /
  DAP-seq; 8,103 human datasets, 1,210 TFs).
- Cistrome DB (≈45,000 human + 44,000 mouse samples in v3).
- UCSC track hubs: **only** referenced if a stably parseable summary
  link exists for a specific regulator. Not used as a primary source in
  v0; left as a placeholder in design.

Explicitly out of scope (v0):
- Peak intersection with the target gene's locus (still v2.x).
- Motif scanning (still v2.x).
- ChIPAtlas (a fourth aggregator) — left for a possible v0.x extension
  if the three above turn out to be insufficient.
- Bulk download + local parsing of ReMap or Cistrome catalog files.
  (Multi-MB downloads; would need careful caching; out of scope for the
  smallest-useful version.)

## Data-access reality

Confirmed during design (2026-05-03):

- **ENCODE REST API**: live, programmatic, JSON. Already used by
  `gain_evidence_audit.py`.
- **ReMap REST API**: documented at `/api_v1/...` but currently redirects
  to port 802 which is closed externally; effectively unreachable from
  a stdlib HTTP client. The web search UI works but is JS-rendered;
  counts populate via AJAX calls whose backend URL is not visible in
  the served HTML.
- **Cistrome DB Toolkit**: web UI works over HTTP (HTTPS cert is broken).
  Cistrome v3 browser at `db3.cistrome.org` is reachable but lacks an
  obvious JSON endpoint.

**Implication for v0.** Stdlib-only programmatic counts are feasible for
ENCODE only. For ReMap and Cistrome, v0 records:

1. The **per-regulator lookup URL** (constructed deterministically from
   the regulator symbol).
2. Whatever **hand-curated counts** are recorded in
   `metadata/external_chip_lookups.csv` (a new file). Empty rows are
   treated as "lookup_required" — *not* as "zero results".

This means **v0 cannot definitively assign `literature_curation_only`
to any pair whose ReMap / Cistrome cells are uncurated**. Such pairs
land in a new class `unresolved_public_evidence_gap` instead — which is
honest: we have not checked those repositories programmatically, so the
absence is not yet established.

## Six final merged classes

Defined in the precedence order used by the merge logic. Each pair
receives the **highest-strength** class that applies after combining
ENCODE live counts with curated ReMap / Cistrome counts.

1. **`direct_human_lung_evidence`** — at least one source has
   ≥1 human TF ChIP-seq experiment in lung biosample(s) for the regulator.
2. **`direct_human_non_lung_evidence`** — no lung ChIP, but at least one
   source has ≥1 human TF ChIP-seq in a non-lung biosample for the
   regulator. Cross-tissue applicability uncertain.
3. **`indirect_accessibility_support`** — no human TF ChIP in any source,
   but lung ATAC-seq and/or DNase-seq exists (always true for lung in
   ENCODE); flagged as a class when motif-scanning would be the next
   plausible step. **v0 does not implement motif scanning**, so this
   class is documented but unpopulated; pairs that would qualify fall
   through to a lower-strength class.
4. **`mouse_supported_only`** — only mouse TF ChIP-seq exists in any
   checked source.
5. **`literature_curation_only`** — every checked source has zero hits
   for the regulator (ENCODE confirmed live; Cistrome and ReMap
   confirmed via curated entries with explicit zero counts). The pair is
   in literature curation but unsupported by checked public-data
   repositories.
6. **`unresolved_public_evidence_gap`** — ENCODE confirms no hits, but
   Cistrome and/or ReMap counts are missing from
   `external_chip_lookups.csv`. The audit cannot conclude whether public
   evidence exists; user action (manual lookup) is required.

The user's specification listed `direct_human_lung_evidence` and
`direct_human_non_lung_evidence` as separate classes; this design
preserves that distinction and adds explicit `unresolved_public_evidence_gap`
to match the v0 access reality.

## Strict rules carried forward

- Do not overclaim from any single source.
- Do not merge human and mouse counts.
- Do not treat non-lung human ChIP as lung evidence.
- "Absence of supporting public data" ≠ "absence of relationship."
  Every justification line must avoid language like "unsupported",
  "no relationship", or "contradicted." Use "not corroborated by
  the checked sources" or "no public ChIP found in {sources_checked}."

## Inputs

1. `metadata/regulator_target_pairs.csv` — unchanged from v0 audit.
2. `metadata/sources.json` — unchanged.
3. **New:** `metadata/external_chip_lookups.csv` — hand-curatable file
   with rows per (regulator, source). Schema:

| column | meaning |
|---|---|
| regulator | gene symbol, matches `regulator_target_pairs.csv` |
| source | `cistrome` or `remap` |
| organism | `human` or `mouse` |
| tissue_filter | `any` or `lung` |
| n_experiments | integer ≥ 0, or empty if not yet looked up |
| lookup_url | the URL that should display the count |
| lookup_date | ISO date, or empty |
| notes | optional free text |

In v0 the file is seeded with the URL and `n_experiments` left empty;
running the audit script reads whatever values exist and treats blanks
as "lookup_required" (which drives the `unresolved_public_evidence_gap`
class for affected pairs).

## Outputs

`metadata/evidence_audit_extended.csv`. One row per pair.

| column group | columns |
|---|---|
| identification | regulator, target, relationship_type |
| ENCODE | encode_class, encode_n_human_lung, encode_n_human_other, encode_n_mouse |
| Cistrome | cistrome_n_human_total, cistrome_n_human_lung, cistrome_n_mouse, cistrome_url, cistrome_lookup_status |
| ReMap | remap_n_human_total, remap_n_human_lung, remap_n_mouse, remap_url, remap_lookup_status |
| merge | merged_class, merged_class_changed_from_encode_only, justification |

`merged_class_changed_from_encode_only` is `yes` / `no`, derived by
running the audit's classifier with ENCODE-only inputs vs. all three
sources. This directly answers the user's "how many pairs changed
class after adding Cistrome/ReMap" report question.

`notes/evidence_audit_extended.md`. Human-readable report:

- Class counts (final merged), and the v0 ENCODE-only counts side by side.
- Which pairs changed class and what they changed from / to.
- Pairs that remain `unresolved_public_evidence_gap` after v0 — i.e.,
  where manual Cistrome / ReMap lookup is the next step.
- Pairs that are confirmed-empty across all checked sources.
- Whether NKX2-1, SOX2, SOX9 remain the largest gaps once external
  curation is filled in.
- The framing-correction reminder.

## Edge cases

- **External lookups CSV missing entirely** → all Cistrome / ReMap fields
  default to `lookup_status=missing`, all pairs except ENCODE-positive
  fall into `unresolved_public_evidence_gap`.
- **External lookups CSV present but row missing for a regulator** →
  treated as `lookup_status=lookup_required` for that source.
- **External lookups CSV row has `n_experiments=0`** → treated as
  confirmed zero hits for that source / organism / tissue_filter.
- **Conflict between sources** (e.g., ENCODE has lung ChIP but Cistrome
  has zero) → trust the higher count; if ENCODE has lung ChIP that
  Cistrome should have ingested, log the discrepancy in `notes`.

## What v0 of the extension is *not*

- Not a peak-level evidence validator. Same v0 limitation as the
  ENCODE-only audit: existence of experiments, not validated binding
  at the target locus.
- Not a comprehensive multi-repository audit. Three sources are not
  exhaustive (ChIPAtlas, ENCODE Imputed Tracks, GTRD, JASPAR-CHIPSeq are
  all out).
- Not an automated ReMap / Cistrome scraper. Hand-curated entries are
  the deliberate v0 trade-off; full programmatic access for those two
  repositories is a v0.x candidate.

## Implementation outline

1. Build `metadata/external_chip_lookups.csv` with one row per
   (regulator, source, organism, tissue_filter) combination. Schema
   above. Rows with empty `n_experiments` are explicit lookup placeholders.
2. Extend `scripts/gain_evidence_audit.py` logic into a new
   `scripts/gain_evidence_audit_extended.py`:
   - Reuse `regulator_evidence()` for ENCODE live counts.
   - New `external_evidence(regulator, source)` that reads
     `external_chip_lookups.csv`.
   - New `merge_classes(encode, cistrome, remap)` implementing the
     six-class precedence above.
   - Run ENCODE-only classification per pair, then merged classification,
     and record both for the change-detection column.
3. Output extended CSV + Markdown report.

Stdlib only.
