# Q3 Evidence Audit — Results

**Audit run:** 2026-05-03 (UTC)
**Input:** [metadata/regulator_target_pairs.csv](../metadata/regulator_target_pairs.csv) — 18 hand-curated TF→target pairs
**Output:** [metadata/evidence_audit.csv](../metadata/evidence_audit.csv) — full per-pair classification + counts + URLs
**Script:** [scripts/gain_evidence_audit.py](../scripts/gain_evidence_audit.py) — stdlib only, queries ENCODE
**Design contract:** [notes/q3_design.md](q3_design.md)

## Question

*Of the canonical regulator-target relationships in the lung-development
chain, which are supported by **human** public-data evidence vs.
extrapolated from mouse — and where are the data gaps?*

## How the classification works (v0)

For each unique regulator, the audit issues three ENCODE search queries and
counts experiments matching `target.label=<regulator>`:

- **Human lung** TF ChIP-seq (filtered to `Homo sapiens` + `lung`)
- **Human, any tissue** TF ChIP-seq
- **Mouse, any tissue** TF ChIP-seq

The pair's class is the **highest-strength** that applies, in this
precedence: `direct_human_evidence` (human lung ChIP exists) >
`indirect_human_evidence` (human non-lung ChIP exists) >
`mouse_supported_only` (only mouse ChIP exists) > `literature_curation_only`
(no ENCODE TF ChIP in any species/tissue for the regulator).

A fifth class, `accessibility_only_support`, is defined in `q3_design.md`
but **not populated by v0** because v0 does not implement motif scanning.

**Critical reminder:** `literature_curation_only` means *the public ENCODE
record currently does not corroborate this relationship*. It does **not**
mean the relationship is wrong, contested, or unsupported in the wet-lab
literature. Most pairs in this class are textbook-canonical claims.

## Class counts (n = 18 pairs)

| Class | Count | % | Pairs |
|---|---:|---:|---|
| `direct_human_evidence` | 0 | 0% | — |
| `indirect_human_evidence` | 4 | 22% | SMAD1→ID1, SMAD1→ID2, GLI2→PTCH1, GLI2→GLI1 |
| `mouse_supported_only` | 0 | 0% | — |
| `literature_curation_only` | 14 | 78% | All NKX2-1, SOX2, SOX9, CTNNB1 pairs |

## Strongest pairs (relatively)

The four `indirect_human_evidence` pairs are the strongest in the audit:

| Pair | Human ChIP (any tissue) | Notes |
|---|---:|---|
| **SMAD1 → ID1** | 3 | BMP-pathway effector; canonical SMAD-driven target. Human ChIP exists in non-lung biosamples and would need cross-tissue validation for lung-developmental claims. |
| **SMAD1 → ID2** | 3 | Same SMAD1 ChIPs as above. |
| **GLI2 → PTCH1** | 1 | SHH-pathway effector; canonical feedback target. Single human ChIP outside lung context. |
| **GLI2 → GLI1** | 1 | Same single GLI2 ChIP. SHH-pathway feedback loop. |

None of these are *direct* human lung evidence — they all require the
caveat that binding observed in non-lung tissues may or may not transfer
to lung-developmental contexts. But they have *some* human ChIP signal,
which is more than any other pair in the audit.

## Weakest pairs (literature-only, in v0 reckoning)

All 14 pairs involving **NKX2-1, SOX2, SOX9, or CTNNB1** as the regulator
fell into `literature_curation_only`. These are not weak biological
claims — they are the **most well-established** developmental regulatory
relationships in the lung literature. They are weak in *one specific
sense only*: the ENCODE TF ChIP-seq record does not currently corroborate
them, because **no TF ChIP-seq has been done for these factors in ENCODE
in any species or tissue**.

| Regulator | Pairs (n) | Human ChIP | Mouse ChIP |
|---|---:|---:|---:|
| **NKX2-1** | 7 | 0 | 0 |
| **SOX2** | 3 | 0 | 0 |
| **SOX9** | 2 | 0 | 0 |
| **CTNNB1** | 2 | 0 | 0 |

## Most important missing human evidence

In order of impact on the lung-developmental literature:

1. **NKX2-1.** Master regulator of lung epithelial identity; cited in
   essentially every lung-developmental review for the past three decades.
   ENCODE has zero TF ChIP-seq experiments for NKX2-1 in any species,
   any biosample. Every claim about which alveolar / airway / progenitor
   genes NKX2-1 directly binds is currently outside the ENCODE-public-data
   record. This is the single largest gap.
2. **SOX2 / SOX9.** The textbook proximal/distal progenitor marker pair.
   ENCODE has zero TF ChIP-seq for either in any species. (One *C. elegans*
   `sox-2` hit was excluded as out-of-scope.) Most published claims about
   SOX2 / SOX9 binding in lung come from antibody-based work in primary
   tissue or organoids that did not flow into ENCODE.
3. **CTNNB1 (β-catenin).** Canonical WNT-pathway effector. Zero TF ChIP
   in ENCODE. Partly a technical artefact — β-catenin is hard to ChIP
   without high-stringency validation — but the field's claims about
   β-catenin-driven lung-developmental targets rest on indirect evidence
   (target-gene reporter assays, co-IP, downstream activation assays).
4. **Lung tissue context for *every* regulator.** Even SMAD1 and GLI2,
   which have human ChIP, have **zero** lung-biosample ChIP. Every
   evidence-class assignment in this audit that isn't `literature_curation_only`
   is `indirect` precisely because no lung-tissue ChIP exists.

## What this audit does *not* claim

- It does **not** validate or invalidate any of the 18 regulatory
  relationships. Whether NKX2-1 binds SFTPC's promoter in human lung is a
  separate, biologically settled question; the audit only asks whether
  a publicly available ENCODE ChIP-seq experiment exists that could be
  used to test it computationally.
- It does **not** survey non-ENCODE ChIP repositories (ChIPAtlas,
  Cistrome, ReMap, individual GEO depositions). A pair classified
  `literature_curation_only` here may have ample non-ENCODE ChIP support.
- It does **not** check peak intersection with the target gene's locus.
  Even for the four `indirect_human_evidence` pairs, the audit does not
  verify that the regulator's ChIP peaks fall near the target gene; that
  is v1 work (BED file parsing).
- It does **not** consider co-expression evidence (would require
  CELLxGENE Census + Scanpy; deferred).

## What it does establish

A reproducible, scriptable, factual baseline:

> Of the eighteen most canonical regulator-target relationships in the
> NKX2-1 / SOX2 / SOX9 / CTNNB1 / SMAD1 / GLI2 chain, **none** have
> direct ENCODE-public-data support in human lung tissue. **Four** have
> some human TF ChIP-seq evidence in non-lung tissues. **Fourteen** rest
> entirely on literature curation.

This is a real, durable, reproducible fact about the public-data
ecosystem. Re-running the audit against a future ENCODE snapshot will
detect any change. Any project building on these relationships in
human-lung contexts can use this baseline to identify which links need
wet-lab support and which have public-data scaffolding to lean on.

## Reproducing the audit

```sh
python3 scripts/gain_evidence_audit.py
```

Stdlib only. Honors a 0.2 s sleep between ENCODE requests; total
runtime ~4-6 seconds for 6 regulators × 3 queries = 18 GET calls.
