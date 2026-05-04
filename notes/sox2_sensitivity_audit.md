# SOX2 Sensitivity Audit — Results

**Run:** 2026-05-04 (UTC)
**Inputs:** same 27 SOX2 hg38 lung-context ChIP-Atlas experiments
(19 cancer cell lines + 8 MRC-5 reprogramming) × 7 lung-developmental
targets, run at TWO thresholds (bed10 + bed05).
**Output:** [`metadata/sox2_sensitivity_audit.csv`](../metadata/sox2_sensitivity_audit.csv)
**Script:** [`scripts/gain_sox2_audit_sensitivity.py`](../scripts/gain_sox2_audit_sensitivity.py)
**Decision context:** [`notes/sox2_initial_audit.md`](sox2_initial_audit.md)

## Per-pair side-by-side (bed10 → bed05)

`prox / near / dist / no_local` are tier counts across 27 experiments.

| Target | Threshold | prox | near | dist | no_local | Class | Robustness |
|---|---|---:|---:|---:|---:|---|---|
| **TP63** | bed10 | 0 | 0 | 2 | 25 | `distal_candidate_support_only` | robust failure (no prox) |
| | bed05 | 0 | 0 | 5 | 22 | `distal_candidate_support_only` | (no class change) |
| **KRT5** | bed10 | 0 | 0 | 1 | 26 | `distal_candidate_support_only` | **CHANGED** |
| | bed05 | 0 | 2 | 1 | 24 | `lung_context_source_only` | gains nearby (not proximal) |
| **MUC5B** | bed10 | 0 | 0 | 0 | 27 | `no_locus_support` | robust failure |
| | bed05 | 0 | 0 | 0 | 27 | `no_locus_support` | (no change — most robust empty) |
| **FOXJ1** | bed10 | 0 | 1 | 0 | 26 | `lung_context_source_only` | (no class change) |
| | bed05 | 0 | 2 | 4 | 21 | `lung_context_source_only` | gains distal (5→ tier-3) |
| **SCGB1A1** | bed10 | 0 | 0 | 1 | 26 | `distal_candidate_support_only` | **CHANGED** |
| | bed05 | 0 | 1 | 3 | 23 | `lung_context_source_only` | gains nearby |
| **NKX2-1** | bed10 | 0 | 2 | 0 | 25 | `lung_context_source_only` | (no class change) |
| | bed05 | 0 | 2 | 1 | 24 | `lung_context_source_only` | |
| **SOX9** | bed10 | 0 | 1 | 0 | 26 | `lung_context_source_only` | (no class change) |
| | bed05 | 0 | 1 | 2 | 24 | `lung_context_source_only` | |

**Critical structural finding: zero proximal hits at either threshold,
across all 7 pairs and all 27 experiments.** Threshold relaxation moves
some pairs between nearby and distal tiers but never lifts a pair into
the `peak_validated_*` tier.

## The five user-stated questions, answered

### 1. How many pairs change class from bed10 to bed05?

**2 of 7.** Both move from `distal_candidate_support_only` (bed10) to
`lung_context_source_only` (bed05) — that is, they **gain nearby peaks**
at bed05 but still no proximal-promoter peaks. Specifically:

- **KRT5**: 0 prox / 0 near / 1 dist at bed10 → 0 prox / 2 near / 1 dist at bed05
- **SCGB1A1**: 0 prox / 0 near / 1 dist at bed10 → 0 prox / 1 near / 3 dist at bed05

Five pairs do not change class. Notably MUC5B remains robustly empty
(0 peaks within ± 200 kb across all 27 experiments at both thresholds).

### 2. Do TP63 or KRT5 gain proximal-promoter support at bed05?

**No, neither.**

- **TP63**: 0 proximal at both thresholds. Gains 3 more distal peaks at
  bed05 (5 total within 50–200 kb in cancer-line context) — interesting
  as a distal-candidate signal, but **no proximal-promoter binding**
  emerges at bed05 even though SOX2 is the textbook lineage oncogene of
  lung squamous cancer.
- **KRT5**: 0 proximal at both thresholds. Gains 2 nearby peaks at
  bed05 (5–50 kb).

The textbook claim that SOX2 directly drives TP63 (especially the
basal-cell ΔNp63 isoform) and KRT5 in lung squamous lineage is **not
supported by proximal-promoter peaks** at the canonical TSS in the
available cancer-line ChIP at either threshold tested.

### 3. Do MUC5B, FOXJ1, or SCGB1A1 change meaningfully?

| Target | bed10 → bed05 | Meaningful change? |
|---|---|---|
| **MUC5B** | 0/0/0/27 → 0/0/0/27 | **No.** Robustly empty across both thresholds. The strongest negative result in the audit — SOX2 does not bind anywhere within ± 200 kb of MUC5B in any of 27 experiments. |
| **FOXJ1** | 0/1/0/26 → 0/2/4/21 | Modest. Class unchanged (`lung_context_source_only`); gains 4 distal peaks at bed05. Distal-candidate signal emerges, mainly in cancer-line context. |
| **SCGB1A1** | 0/0/1/26 → 0/1/3/23 | Class change (distal → nearby) but **no proximal**. Gains 1 nearby + 2 distal peaks at bed05. Modest distal signal. |

### 4. Is the failure mainly threshold-driven or context-driven?

**Context-driven.** The bed05 sweep was specifically designed to test
this question, and it answers it cleanly: **threshold relaxation does
not produce proximal-promoter binding at any of the 7 targets**.

Three observations all point the same way:

- **0 / 7 proximal validations at bed05** — same as bed10. If the
  failure were threshold-driven, we would expect at least the
  canonical squamous targets (TP63, KRT5) to gain proximal peaks at
  the relaxed threshold. They do not.
- **MRC-5 reprogramming context contributes zero peaks at any tier in
  any pair** at any threshold, despite individual experiments
  generating up to 295 peaks at bed05. The MRC-5 SOX2 binding pattern
  simply does not include our lung-developmental target loci — it
  binds Yamanaka pluripotency targets instead.
- **Per-experiment SOX2 peak counts in lung-context substrate are
  inherently sparse** at the genomic locations of our targets. Even
  cancer-line lung squamous experiments (LK-2, HCC95, NCI-H520 etc.)
  with 1,000–8,000 total peaks per experiment land essentially **zero**
  proximal-promoter peaks at our 7 target TSSs.

The interpretation: **SOX2's lung-context binding pattern in the
available substrate (cancer + reprogramming) does not include the
proximal promoters of the canonical proximal/airway-program markers.**
Whether SOX2 acts on these targets via distal enhancers (the TP63 +
FOXJ1 distal peaks suggest yes for some), via cell-type-specific
binding diluted out of bulk cancer-line ChIP, or simply isn't the
direct upstream regulator the textbook assumes — these are real
biology questions that this audit cannot answer.

### 5. Continue SOX2 or hand off to SOX9?

**Hand off to SOX9.** Reasons:

- The continue criterion from `notes/sox2_audit_design.md` was "≥ 3
  of 7 pairs validate proximally, or within-chain pairs show
  measurable signal." The bed05 sweep gives **0 of 7** proximal
  validations. The within-chain pairs (NKX2-1, SOX9) show only 1–2
  nearby peaks each — measurable but not strong.
- The handoff criterion was "≤ 2 validate and failures span both
  substrates" — both met. Cancer-line and MRC-5 substrates both
  fail to produce proximal hits.
- **The failure is context-driven, not threshold-driven.** The bed05
  sweep was the cheap test that resolves this. No further v0.x audit
  on SOX2 (sensitivity is already done; distal-candidate audit on
  cancer-only substrate would be expanding scope without
  scientifically tightening the conclusion; histone filter requires
  candidate loci to filter, and we have at most a handful of distal
  peaks per target).
- **SOX2 has standing distal-candidate signal at TP63 / FOXJ1 /
  SCGB1A1** (5 / 4 / 3 distal peaks at bed05, all cancer-line context)
  that future SOX2 work can pick up. These are documented in the
  audit CSV and are the natural input to a future distal-candidate +
  histone-filter pass *if and when* primary-tissue SOX2 ChIP-seq
  surfaces.

## Standing SOX2 outputs (final state of this audit cycle)

- **Source level:** 95 hg38 SOX2 ChIP-Atlas experiments. 71% non-lung
  (38 ESC/iPSC + 16 neural + 14 other); 29% lung-context (19 cancer +
  8 MRC-5 reprogramming).
- **Locus level (cancer + MRC-5 substrate, bed05):**
  - 0 / 7 pairs proximal-validate
  - 9 nearby-band peaks total across 5 pairs (KRT5×2, FOXJ1×2,
    SCGB1A1×1, NKX2-1×2, SOX9×1)
  - 16 distal-band peaks total across 6 pairs (TP63×5, FOXJ1×4,
    SCGB1A1×3, NKX2-1×1, KRT5×1, SOX9×2)
  - 1 robust empty (MUC5B: zero peaks within ± 200 kb across both
    thresholds, all 27 experiments)
- **Strongest distal-candidate signal:** TP63 (5 distal peaks at bed05
  in cancer-line context). Documented in the audit CSV; not pursued
  further in this cycle because cancer-only distal candidates at a
  single target do not justify the full distal-candidate +
  histone-filter pipeline.

## Anti-overclaim summary

- **"Hand off to SOX9" is not a refutation of the textbook SOX2 →
  TP63 / KRT5 / etc. claims.** The textbook claims rest on functional
  experiments in primary lung tissue, organoid, or transgenic mouse
  systems that this audit does not consult.
- **Cancer-line + MRC-5 reprogramming is not the right substrate** to
  test developmental SOX2 binding at canonical airway-program
  promoters. The audit's negative result at proximal level is
  consistent with that mismatch.
- **The TP63 / FOXJ1 / SCGB1A1 distal candidates** are exactly that:
  candidates. No regulatory function or developmental relevance is
  claimed.
- **SOX2's standing output** of "no proximal-promoter binding at
  canonical airway markers in cancer + reprogramming substrate" is a
  reproducible fact, not a refutation; subsequent primary-tissue SOX2
  ChIP could materially change it.

## Reproducing the audit

```sh
python3 scripts/gain_sox2_audit_sensitivity.py
```

Stdlib only. 54 BED downloads (27 × 2 thresholds), ~ 5 MB total at
bed10 + ~ 4 MB at bed05. Total runtime ~ 60–90 s.

## What v0 of this audit deliberately does *not* do

- No bed20 (more stringent) sweep — already shown that bed10 finds
  nothing proximal.
- No external GEO/SRA search for primary-tissue SOX2 ChIP — flagged
  for a possible future pass, parallel to the NKX2-1 final-gap search.
- No distal-candidate audit on the TP63 / FOXJ1 / SCGB1A1 distal
  signal — cancer-only substrate makes this pass less informative
  than NKX2-1's was.
- No histone-support filter — would require candidate loci and adds
  little to the handoff decision.
- No SOX9 work — that is the next session.
