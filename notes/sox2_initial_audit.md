# SOX2 Initial Audit — Results

**Run:** 2026-05-04 (UTC)
**Inputs:** 27 SOX2 hg38 lung-context ChIP-Atlas experiments (19 cancer
cell lines + 8 MRC-5 reprogramming biosamples) × 7 lung-developmental
targets.
**Output:** [`metadata/sox2_initial_audit.csv`](../metadata/sox2_initial_audit.csv)
**Script:** [`scripts/gain_sox2_audit.py`](../scripts/gain_sox2_audit.py)
**Design contract:** [`notes/sox2_audit_design.md`](sox2_audit_design.md)

## Per-pair results (bed10, q < 10⁻¹⁰, ± 5 kb proximal cutoff)

`prox(c+m)` = proximal hits in cancer / MRC-5 contexts; `near(c+m)` =
5–50 kb hits.

| Pair | prox cancer | prox MRC-5 | near cancer | near MRC-5 | no_local | Class |
|---|---:|---:|---:|---:|---:|---|
| SOX2 → TP63 | 0 | 0 | 0 | 0 | 27 | `no_locus_support` |
| SOX2 → KRT5 | 0 | 0 | 0 | 0 | 27 | `no_locus_support` |
| SOX2 → MUC5B | 0 | 0 | 0 | 0 | 27 | `no_locus_support` |
| SOX2 → FOXJ1 | 0 | 0 | 1 | 0 | 26 | `lung_context_source_only` |
| SOX2 → SCGB1A1 | 0 | 0 | 0 | 0 | 27 | `no_locus_support` |
| SOX2 → NKX2-1 | 0 | 0 | 2 | 0 | 25 | `lung_context_source_only` |
| SOX2 → SOX9 | 0 | 0 | 1 | 0 | 26 | `lung_context_source_only` |

Class distribution:

| Class | Count |
|---|---:|
| `peak_validated_in_lung_context` | 0 (unreachable in v0) |
| `peak_validated_in_cancer_lung_context_only` | **0** |
| `peak_validated_in_lung_reprogramming_context_only` | **0** |
| `lung_context_source_only` | 3 |
| `no_locus_support` | 4 |
| `unresolved_due_to_context_mismatch` | 0 |

## The four user-stated questions, answered

### 1. Does SOX2 have any lung-context public binding evidence?

**Source level: yes — substantial.** ChIP-Atlas hg38 SOX2 has 95
experiments total, of which 27 are lung-context (19 lung-cancer cell
lines + 8 MRC-5 reprogramming experiments). That is more lung-context
substrate than NKX2-1 had (21 experiments, all lung adenocarcinoma).

**Locus level: minimal.** Across all 27 lung-context experiments at
bed10 + ± 5 kb proximal cutoff, **zero proximal-promoter peaks** were
found at any of the 7 lung-developmental targets. Three pairs show
1–2 peaks within the 5–50 kb nearby band; the other four show no
peaks within 50 kb of the TSS.

### 2. Is the evidence mostly non-lung / ESC / neural?

**Source-level: yes.** Of the 95 hg38 SOX2 ChIP experiments:

| Context | n | % |
|---|---:|---:|
| ESC / iPSC pluripotent | 38 | 40% |
| Lung-context | 27 | 28% |
| Neural / brain | 16 | 17% |
| Other (digestive, head/neck, epidermis) | 14 | 15% |

The majority (71%) of SOX2 ChIP is **non-lung**, dominated by the
canonical Yamanaka (ESC/iPSC) and neural-development contexts where
SOX2 plays its other major roles. The lung-context substrate is
biased toward **cancer** (lung squamous + small-cell lung cancer; ~70%
of lung-context) rather than developmental contexts.

The MRC-5 reprogramming experiments are technically "lung-context" but
the biology is reprogramming (SOX2 acting as a Yamanaka factor in
fetal lung fibroblasts), not endogenous lung-developmental SOX2 in
epithelial cells. Their contribution at our target loci is **zero**
proximal hits and zero nearby hits — consistent with the
interpretation that MRC-5 SOX2 binds pluripotency targets, not
lung-program targets.

### 3. Do any proximal-airway targets have locus-level support?

**No.** None of TP63, KRT5, MUC5B, FOXJ1, or SCGB1A1 — the five
canonical proximal/airway program markers — have **any** SOX2 peak
within ± 5 kb of their TSS in any of the 27 lung-context experiments
at bed10.

This is the most surprising result of the audit, given the textbook
status of SOX2 → TP63 and SOX2 → KRT5 in lung squamous cancer
literature. Three plausible explanations (in order of likely
contribution):

1. **bed10 is too stringent for SOX2.** SOX2 ChIP signal-to-noise is
   typically lower than NKX2-1 ChIP — visible in the per-experiment
   peak counts (H29 = 7 peaks, H1836 = 7 peaks, MRC-5 endogenous = 6
   peaks at bed10, vs thousands for NKX2-1 lung adenocarcinoma
   experiments). A bed05 sweep is the obvious next test.
2. **SOX2 binds distal enhancers, not proximal promoters, at these
   target genes.** TP63 in particular has a 266 kb gene body and
   alternative promoters (TAp63 vs ΔNp63 — the latter is the
   basal-cell isoform); SOX2's binding may be at distal enhancers or
   at the ΔNp63 internal promoter rather than the canonical TAp63
   TSS used here. This would parallel the NKX2-1 distal-candidate
   finding for SFTPC / SCGB1A1 / ABCA3 / FOXA2.
3. **The cancer-line / MRC-5 substrate is too narrow for the
   developmental claim.** This is the standing limitation across all
   SOX2 audits in this project; nothing in v0 changes it.

The within-chain pairs (NKX2-1, SOX9) show 1–2 nearby peaks each — a
hint of distal regulatory engagement at the proximal-distal axis
loci, but not enough to validate at promoter level.

### 4. Does SOX2 look more or less publicly grounded than NKX2-1?

**Less grounded at this first pass.** Side-by-side first-pass
comparison (both at bed10, ± 5 kb proximal cutoff):

| Metric | NKX2-1 v0 (7 targets, 21 cancer LUAD/SCLC) | SOX2 v0 (7 targets, 27 cancer + MRC-5) |
|---|---|---|
| Pairs validating proximally | **3 / 7** (SFTPB, SOX2, SOX9) | **0 / 7** |
| Pairs with nearby support only | 4 / 7 | 3 / 7 (FOXJ1, NKX2-1, SOX9) |
| Pairs with no peaks within 50 kb | 0 / 7 | **4 / 7** (TP63, KRT5, MUC5B, SCGB1A1) |
| Source-level lung-context experiments | 21 | 27 |

NKX2-1 had a clear "cancer-line proximal hit" signal at multiple
canonical targets even at bed10. SOX2 does not. This is consistent
with the per-experiment peak count distribution: most SOX2 lung-
context experiments produce only 6–50 peaks at bed10, vs NKX2-1
experiments often producing 1,000–50,000 peaks at bed10.

**Caveat.** "Less grounded" here means **less proximal-promoter
binding signal at our 7 targets at the bed10 threshold in this
substrate**. It does not mean SOX2 is less biologically important —
SOX2's lung-developmental role is at least as well-established as
NKX2-1's. The audit's information ceiling is the same as before:
cancer-line ChIP does not test the developmental claim.

## Recommendation

The continue / handoff criteria from the design:

- **Continue with SOX2** if ≥ 3 of 7 pairs validate proximally, or
  within-chain pairs show measurable signal.
- **Hand off to SOX9** if ≤ 2 of 7 validate and the failures span
  both substrates.

The current result is right at the threshold:

- 0 / 7 validate proximally → would normally trigger handoff.
- But within-chain pairs (NKX2-1: 2 nearby; SOX9: 1 nearby) do show
  *some* signal that a bed05 / distal sweep would clarify.
- The pattern (low peak counts per experiment, no proximal hits) is
  more consistent with **threshold-driven** than with
  **substrate-driven** failure.

**Recommended:** one cheap sensitivity sweep (bed05, same script
adapted) before deciding. If bed05 brings TP63 / KRT5 in as proximal
hits in cancer-line context, continue with SOX2 along the same NKX2-1
audit cycle path (sensitivity → distal candidates → histone filter).
If bed05 stays empty, hand off to SOX9 — SOX2's lung-developmental
public-data state is then "thinner than NKX2-1's" in a way that no
public-data audit can fix.

This recommendation is **the smallest possible decision-grade next
step** and is consistent with the rule "do not build new
infrastructure unless unavoidable" — the existing
`gain_nkx21_audit_sensitivity.py` is the template; a parallel
`gain_sox2_audit_sensitivity.py` would be a sibling import, no design
work needed.

## Anti-overclaim summary

- **Cancer-line SOX2 binding is real but cancer-context.** Lung
  squamous SOX2 is a lineage oncogene; the binding map is meaningful
  but cancer biology, not normal lung development.
- **MRC-5 SOX2 ChIP is reprogramming context.** Reflects SOX2's role
  as a Yamanaka factor in fibroblasts, not as a lung-developmental
  TF in epithelial cells.
- **No primary lung-epithelial SOX2 ChIP exists in ChIP-Atlas hg38.**
  Same gap as NKX2-1; the GEO/SRA search done for NKX2-1 in the
  preceding session showed the absence is real, not a snapshot
  artefact. Whether the same is true for SOX2 specifically requires
  one more E-utilities search if SOX2 is continued.
- **Locus failure at bed10 is not refutation.** The textbook SOX2 →
  TP63 / KRT5 claims rest substantially on functional and chromatin-
  accessibility evidence in primary tissue and organoid contexts,
  which this audit cannot test.

## Reproducing this audit

```sh
python3 scripts/gain_sox2_audit.py
```

Stdlib only. 27 BED downloads from ChIP-Atlas (~ 1.6 MB total at
bed10), ~ 30 s runtime.
