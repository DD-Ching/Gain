# SOX9 Initial Audit — Results

**Run:** 2026-05-04 (UTC)
**Inputs:** 27 SOX9 hg38 ChIP-Atlas experiments (20 non-lung cancer
cell lines + 7 ESC-derived) × 7 lung-developmental targets
**Output:** [`metadata/sox9_initial_audit.csv`](../metadata/sox9_initial_audit.csv)
**Script:** [`scripts/gain_sox9_audit.py`](../scripts/gain_sox9_audit.py)
**Design contract:** [`notes/sox9_audit_design.md`](sox9_audit_design.md)

## Per-pair results (bed10, q < 10⁻¹⁰, ± 5 kb proximal cutoff)

`prox(c+e)` = proximal hits in non-lung cancer / ESC contexts.
`near(c+e)` = 5–50 kb hits.

| Pair | prox cancer | prox ESC | near cancer | near ESC | no_local | Class |
|---|---:|---:|---:|---:|---:|---|
| SOX9 → **ID2** | **1** | 0 | 2 | 0 | 24 | **`peak_validated_in_non_lung_context_only`** |
| SOX9 → AGER | 0 | 0 | **6** | 0 | 21 | `non_lung_context_source_only` |
| SOX9 → SFTPC | 0 | 0 | 3 | 0 | 24 | `non_lung_context_source_only` |
| SOX9 → SFTPB | 0 | 0 | 0 | 0 | 27 | `no_locus_support` |
| SOX9 → HOPX | 0 | 0 | 0 | 0 | 27 | `no_locus_support` |
| SOX9 → NKX2-1 | 0 | 0 | 0 | 0 | 27 | `no_locus_support` |
| SOX9 → SOX2 | 0 | 0 | 0 | 0 | 27 | `no_locus_support` |

Class counts:

| Class | Count |
|---|---:|
| `peak_validated_in_non_lung_context_only` | **1** (ID2) |
| `non_lung_context_source_only` | 2 (AGER, SFTPC) |
| `no_locus_support` | 4 (SFTPB, HOPX, NKX2-1, SOX2) |

The lung-tier classes (`peak_validated_in_lung_context`,
`peak_validated_in_cancer_lung_context_only`,
`peak_validated_in_lung_reprogramming_context_only`,
`lung_context_source_only`) are **structurally unreachable** because
the substrate has zero lung experiments.

The ESC-derived context (7 retinal + pancreatic experiments)
contributes **zero peaks at any tier in any pair** — same pattern as
SOX2's MRC-5 reprogramming context. ESC-retinal SOX9 binds
eye-development targets, not lung-developmental ones.

## The four user-stated questions, answered

### 1. Does SOX9 have any lung-context public binding evidence?

**No.** ChIP-Atlas hg38 has **zero** lung-context SOX9 ChIP-seq
experiments — neither cancer-line nor primary tissue, neither in
lung adenocarcinoma nor in lung organoid context. Of the three
regulators audited (NKX2-1, SOX2, SOX9), SOX9 has the strictest
"no lung substrate" baseline.

### 2. Is the evidence mostly non-lung?

**Entirely non-lung.** 100% of the 27 hg38 SOX9 ChIP experiments are
non-lung biosamples:

| Sub-context | n | Type |
|---|---:|---|
| Prostate cancer (LNCAP, VCaP) | 9 | cancer cell line |
| ESC-derived retinal cells | 6 | developmental but eye, not lung |
| Breast cancer (MCF-7) | 4 | cancer cell line |
| Colon cancer (HT-29, LoVo) | 4 | cancer cell line |
| Pancreas cancer (PANC-1) | 2 | cancer cell line |
| ESC-derived pancreatic cells | 1 | developmental endoderm |
| Lymphoma (KARPAS-422) | 1 | cancer cell line |

20 cancer + 7 ESC-derived = 27 non-lung total. Notably, **no skeletal
/ chondrocyte / cartilage SOX9 ChIP** in the hg38 slice despite SOX9's
canonical chondrocyte master-regulator role — that work appears to
be predominantly mouse / older microarray data not in ChIP-Atlas hg38.

### 3. Do any distal/alveolar targets show locus-level support?

**Mixed but modest.** Restricted to *non-lung-context* support
(lung-tier classes are unreachable for SOX9 in v0):

| Target | Status | Detail |
|---|---|---|
| **ID2** | proximal hit (1 peak in non-lung cancer ≤ 5 kb of TSS) | Distal tip co-marker; broadly BMP/SMAD-regulated. Cross-context binding is plausible because ID2 is broadly expressed beyond lung. |
| **AGER** | nearby cluster (6 cancer-line peaks within 5–50 kb) | AT1 alveolar marker. Strongest nearby signal in the audit. Surprising for a non-lung substrate at a lung-specific gene. |
| **SFTPC** | nearby cluster (3 cancer-line peaks within 5–50 kb) | AT2 alveolar surfactant. Modest cross-context signal. |
| **SFTPB** | no support | AT2 surfactant. Robustly empty. |
| **HOPX** | no support | AT1 marker. Robustly empty. |
| **NKX2-1** | no support | Within-chain master. Robustly empty. |
| **SOX2** | no support | Within-chain proximal counterpart. Robustly empty. |

**The within-chain pairs (NKX2-1, SOX2) are completely empty** —
SOX9 ChIP in any non-lung context shows zero peaks within 50 kb of
either NKX2-1 or SOX2. This is a clean structural result: SOX9's
non-lung binding map does not engage the master / proximal-counterpart
regulator loci at any tier in this substrate.

The single proximal hit (ID2) and the AGER + SFTPC nearby clusters
are the only positive signals.

### 4. Does SOX9 look more or less publicly grounded than SOX2?

**Less grounded at source level; comparable at locus level.**

| Metric | SOX2 v0 (27 lung-context) | SOX9 v0 (27 non-lung) |
|---|---|---|
| ChIP-Atlas hg38 total | 95 | 27 |
| Lung-context experiments | 27 | **0** |
| Pairs proximal-validating (any context) | 0 / 7 (bed10) | **1 / 7** (ID2, in non-lung cancer) |
| Pairs with nearby support | 3 / 7 | 2 / 7 |
| Pairs with no peaks within 50 kb | 4 / 7 | 4 / 7 |

SOX9's source-level coverage is much narrower (27 vs 95 experiments).
But at the locus level **SOX9 v0 has 1 proximal hit (ID2 in non-lung
cancer) where SOX2 v0 had zero**. The hit is in the wrong tissue
context to validate any developmental claim, but the audit machinery
did surface something.

**Caveat that flips this interpretation:** SOX2's audit at bed05 also
returned 0 proximal hits — i.e., the SOX2 result was robust to threshold
relaxation, suggesting context-driven failure. SOX9's bed05 sweep is
deferred to v0.x; it's possible additional non-lung proximal hits
emerge. Until then, the "1 vs 0" comparison should be interpreted at
matched bed10 only.

## Continue with SOX9 v0.x or hand off?

The design's continue criteria from `notes/sox9_audit_design.md`:

- ≥ 2 of 7 pairs validate proximally in non-lung context: **not met** (1).
- Strong distal-band signal at alveolar markers: AGER's 6 nearby is
  modest, SFTPC's 3 is weak.
- Within-chain pairs show binding: **clearly not** — NKX2-1 and SOX2
  are completely empty.

The design's handoff criteria:

- All 7 land in no_locus_support / non_lung_context_source_only with
  ≤ 2 nearby peaks total: **not met** (11 nearby + 1 proximal = 12 hits).

The result sits between continue and handoff, similar to SOX2's
post-bed10 state. The cheapest decision-grade test is the same as for
SOX2: **one bed05 sensitivity sweep**, sibling-imported parallel to
`gain_sox2_audit_sensitivity.py`. If bed05 brings additional proximal
hits at SFTPC / SFTPB / HOPX / AGER (the distal/alveolar markers),
continue. If it doesn't, hand off — the substrate is non-lung, the
yield is structural, and further v0.x work would not change the
substrate ceiling.

**Recommended:** one bed05 pass on SOX9, then decide. Same script
shape as `gain_sox2_audit_sensitivity.py`, ~ 30 lines of extension,
no new infrastructure.

If the user prefers to skip the bed05 pass and hand off directly,
**the standing SOX9 outputs preserve enough signal for any future
work**:

- ID2 proximal hit (chr2:8,678,845 region) — cross-context candidate.
- AGER nearby cluster (6 cancer-line peaks within 5–50 kb of chr6:32,184,344).
- SFTPC nearby cluster (3 cancer-line peaks within 5–50 kb of chr8:22,156,913).

These can be revisited if and when primary-tissue SOX9 ChIP-seq
surfaces.

## Anti-overclaim summary

- **All evidence is non-lung-context.** Zero lung experiments exist
  for SOX9 in ChIP-Atlas hg38. Cross-context binding (proximal in
  prostate cancer, nearby in colon cancer, etc.) does not validate
  any lung-developmental claim.
- **The single ID2 proximal hit is interesting but cancer-context.**
  ID2 is a BMP/SMAD-pathway target broadly expressed across many
  tissues; SOX9 binding near it in cancer cell lines is consistent
  with shared regulatory architecture, not with lung-developmental
  validation.
- **The AGER / SFTPC nearby clusters are surprising.** AT1 (AGER)
  and AT2 (SFTPC) markers should not be strongly transcribed in
  non-lung tissues — the nearby SOX9 peaks may reflect chromatin
  accessibility at these loci that exists across tissues, with SOX9
  bound there opportunistically. This is a *candidate* observation
  worth noting; it is *not* evidence for SOX9 → AGER / SFTPC
  regulation in lung development.
- **Within-chain emptiness is real.** Zero SOX9 peaks at NKX2-1 or
  SOX2 loci within 50 kb in 27 non-lung experiments is a robust
  negative finding for the cross-context reciprocal-binding
  hypothesis at this substrate.

## What v0 of this audit deliberately does *not* do

- bed05 / bed20 sensitivity sweep (deferred to v0.x).
- Distal-candidate audit (50–200 kb window).
- Histone-mark cross-reference.
- External GEO / SRA search for primary-lung SOX9 ChIP — flagged for
  a future pass parallel to NKX2-1's final-gap search.
- Mouse SOX9 ChIP integration (mm10 substrate, requires lift-over).
- FGF10 / WNT / BMP / SHH / downstream work — depends on SOX9's
  decision and the broader chain audit cycle's status.

## Reproducing the audit

```sh
python3 scripts/gain_sox9_audit.py
```

Stdlib only. 27 BED downloads (~ 3 MB total at bed10), ~ 30 s runtime.
