# Evidence Audit v2 — Results

**Run:** 2026-05-03 (UTC)
**Inputs:** [`metadata/regulator_target_pairs.csv`](../metadata/regulator_target_pairs.csv)
+ [`metadata/chipatlas_lookup.csv`](../metadata/chipatlas_lookup.csv)
+ [`metadata/peak_intersection_results.csv`](../metadata/peak_intersection_results.csv)
**Output:** [`metadata/evidence_audit_v2.csv`](../metadata/evidence_audit_v2.csv)
**Script:** [`scripts/gain_evidence_audit_v2.py`](../scripts/gain_evidence_audit_v2.py)
**Design contract:** [`notes/evidence_model_v2.md`](evidence_model_v2.md)

## Deliverable answer

**For the canonical lung developmental chain, which regulator-target links
have actual public human locus-level support, and which remain mostly
textbook canon without strong public support?**

| Class | n | Pairs |
|---|---:|---|
| **`peak_validated_at_target_locus`** (locus-level support exists) | **2** | SMAD1 → ID2 (strongest), SMAD1 → ID1 (cell-type-dependent) |
| **`direct_human_lung_evidence`** (lung-context source-level; locus untested) | **10** | NKX2-1 → SFTPC, SFTPB, SCGB1A1, ABCA3, SOX2, SOX9, FOXA2; SOX2 → KRT5, TP63, MUC5B |
| **`direct_human_non_lung_evidence`** (only non-lung source; locus failed or untested) | **6** | SOX9 → SFTPC, ID2; CTNNB1 → AXIN2, LEF1; GLI2 → PTCH1 (locus failed), GLI2 → GLI1 (locus failed) |
| `indirect_accessibility_support` | 0 | (defined but unpopulated — no motif scanning in v2) |
| `literature_curation_only` | **0** | — |
| `unresolved_gap` | **0** | — |

**Locus-level support is currently demonstrated for 2 of 18 pairs**, both
on the BMP arm. The remaining 16 pairs have only source-level evidence —
strong for 10 (lung-context ChIP exists), weaker for 6 (non-lung only).
**No pair lands in `literature_curation_only` once ChIP-Atlas is folded
in** — the previous "literature-only" bucket from the ENCODE-only audit
was an artefact of repository scoping, not a real evidence gap.

## How v2 changed vs the extended (ENCODE + uncurated) audit

**16 of 18 pairs changed class.** This is the structural reframe ChIP-
Atlas integration produced.

| From (extended) | To (v2) | n | Reason |
|---|---|---:|---|
| `unresolved_public_evidence_gap` | `direct_human_lung_evidence` | 10 | NKX2-1 (21 lung) + SOX2 (27 lung) hits in ChIP-Atlas |
| `unresolved_public_evidence_gap` | `direct_human_non_lung_evidence` | 4 | SOX9 (27 non-lung) + CTNNB1 (78 non-lung) hits in ChIP-Atlas |
| `direct_human_non_lung_evidence` | `peak_validated_at_target_locus` | 2 | SMAD1 → ID1/ID2 passed peak intersection on at least one ENCODE experiment |
| (no change) | `direct_human_non_lung_evidence` | 2 | GLI2 → PTCH1, GLI2 → GLI1 — locus test failed; stays at source-level class |

The unchanged pairs (GLI2's two) are themselves a meaningful finding:
**both canonical SHH-pathway pairs failed the locus test in the only
human GLI2 ChIP available**, and ChIP-Atlas has only 4 GLI2 experiments
total (with no lung context). This is a real and citable absence at the
locus, not an unresolved gap.

## Per-class detail and caveats

### `peak_validated_at_target_locus` (2 pairs)

Both on the BMP arm, both validated against ENCODE peak files:

| Pair | Validation evidence |
|---|---|
| **SMAD1 → ID2** | 3/3 ENCODE experiments at minimum weak; K562 and GM12878 supports (peak overlap and 3 kb proximity); HepG2 weak at 13.6 kb. **Strongest pair in the audit.** |
| **SMAD1 → ID1** | 1/3 supports (K562 peak overlaps TSS); 1/3 weak (HepG2, 13.9 kb); 1/3 absent (GM12878, 322 kb). Cell-type-dependent. |

Caveat: all three SMAD1 ChIP experiments are in non-lung biosamples
(HepG2, GM12878, K562). Lung-context SMAD1 binding has not been
peak-tested.

### `direct_human_lung_evidence` (10 pairs)

The "lung context exists, locus not yet tested" tier:

| Regulator | n pairs | ChIP-Atlas lung experiments | Caveats |
|---|---:|---:|---|
| NKX2-1 | 7 | 21 (all hg38 ChIPs are in lung-context) | 21/21 are in lung biosamples; predominantly **lung adenocarcinoma cell lines** (NCI-H441, A549). Lung-developmental primary-tissue ChIP is not specifically isolated yet. |
| SOX2 | 3 | 27 of 95 hg38 ChIPs match the 'lung' substring | 27 lung-context vs 68 ESC/neural in ChIP-Atlas. Per-pair peak intersection at KRT5, TP63, MUC5B has not been done; this is the natural v3 step. |

Caveat carried forward: "lung context" in v2 means the experiment row
contains the substring "lung" — covers lung tissue, lung cancer lines,
lung-derived primary cells. The cancer-vs-tissue refinement is a v2.x
followup.

### `direct_human_non_lung_evidence` (6 pairs)

Source exists; lung context absent or locus test failed:

| Pair | n_total ChIP | locus test |
|---|---:|---|
| SOX9 → SFTPC | 27 (all non-lung) | not tested |
| SOX9 → ID2 | 27 (all non-lung) | not tested |
| CTNNB1 → AXIN2 | 78 (all non-lung) | not tested |
| CTNNB1 → LEF1 | 78 (all non-lung) | not tested |
| GLI2 → PTCH1 | 4 (all non-lung) + 1 ENCODE | **failed** (no peaks within ± 50 kb of TSS in HEK293) |
| GLI2 → GLI1 | 4 (all non-lung) + 1 ENCODE | **failed** (nearest peak ~ 1.5 Mb from TSS) |

The two GLI2 pairs are the audit's clearest case where a textbook claim
is **not corroborated at the target locus** by the available human ChIP.
Caveats: only 1 ENCODE experiment, in unstimulated HEK293 (not SHH-
active), non-lung. ChIP-Atlas has 3 additional non-ENCODE GLI2
experiments not yet peak-tested.

## Headline answer for the deliverable goal

> **For the canonical lung-developmental chain, locus-level public-data
> support presently exists for 2 of 18 audited regulator → target links
> (SMAD1 → ID1 and SMAD1 → ID2 on the BMP arm).**
>
> **The remaining 16 links are not "textbook canon without public
> support" — once ChIP-Atlas is folded in, 14 of them have at least
> source-level human ChIP evidence, including 10 with lung-context
> ChIP (predominantly lung cancer cell lines, not primary developmental
> tissue). 2 pairs (GLI2 → PTCH1, GLI2 → GLI1) have non-lung ChIP that
> *failed* the locus test, which is a substantive but not final
> negative finding.**
>
> **Zero pairs land in `literature_curation_only`. The previous "no
> public evidence anywhere" claim from the ENCODE-only audit was a
> repository-scope artefact, now corrected.**

## Caveats and what v2 still does *not* do

- **Lung-context filter is inclusive.** "Lung" in the experimentList.tab
  row matches lung tissue, lung cancer cell lines, and lung-derived
  primary cells. Distinguishing developmental primary tissue from
  cancer cell lines is a v2.x refinement.
- **Peak intersection is ENCODE-only in v2.** The 267 ChIP-Atlas hg38
  experiments for our 6 regulators have not been peak-tested. This is
  v3 work and is the most likely next move that produces real new
  insight.
- **No motif scanning.** `indirect_accessibility_support` stays
  unpopulated.
- **No co-expression evidence.** Q1 and Q2 in
  `notes/unresolved_questions.md` are still deferred.
- **Mouse counts unused.** ChIP-Atlas mm10 counts and ENCODE mouse ChIP
  counts are recorded but never promote a pair into a "human" class.
  Cross-species transfer is its own evidence path that v2 deliberately
  does not perform.
- **Cistrome and ReMap remain unused.** They are JS-rendered and
  programmatically inaccessible from stdlib in our setting; their
  per-regulator URLs sit in `metadata/external_chip_lookups.csv` for
  manual reference. ChIP-Atlas substantially overlaps both.

## Reproducing the audit

```sh
python3 scripts/gain_evidence_audit_v2.py
```

Stdlib only. ~18 ENCODE GETs (6 regulators × 3 queries) at 0.2 s sleep
≈ 4-6 s total. Reads:
- `metadata/regulator_target_pairs.csv`
- `metadata/chipatlas_lookup.csv` (committed)
- `metadata/peak_intersection_results.csv` (committed)
- `metadata/evidence_audit_extended.csv` (committed; for change detection)

Writes:
- `metadata/evidence_audit_v2.csv` (committed)

The cached `metadata/cache/chipatlas_experimentList.tab` (~205 MB)
underlying the chipatlas_lookup.csv counts is **not** committed (it is
gitignored under `metadata/cache/`); to re-derive the counts after a
ChIP-Atlas refresh, re-download
[`https://chip-atlas.dbcls.jp/data/metadata/experimentList.tab`](https://chip-atlas.dbcls.jp/data/metadata/experimentList.tab)
into the cache, then re-grep with the same case-insensitive 'lung'
substring filter.
