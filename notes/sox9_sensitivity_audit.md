# SOX9 Sensitivity Audit — Results

**Run:** 2026-05-04 (UTC)
**Inputs:** same 27 SOX9 hg38 ChIP-Atlas experiments (20 non-lung
cancer + 7 ESC-derived; zero lung) × 7 lung-developmental targets,
run at TWO thresholds (bed10 + bed05) with FOUR proximity tiers
(proximal ≤ 5 kb, nearby 5–50 kb, distal_candidate 50–200 kb,
no_local > 200 kb).
**Output:** [`metadata/sox9_sensitivity_audit.csv`](../metadata/sox9_sensitivity_audit.csv)
**Script:** [`scripts/gain_sox9_audit_sensitivity.py`](../scripts/gain_sox9_audit_sensitivity.py)
**Decision context:** [`notes/sox9_initial_audit.md`](sox9_initial_audit.md)

## Per-pair side-by-side (bed10 → bed05)

| Target | Threshold | prox | near | dist | no_local | Class | Robustness |
|---|---|---:|---:|---:|---:|---|---|
| **SFTPC** | bed10 | 0 | 3 | 0 | 24 | `non_lung_context_source_only` | (no class change) |
| | bed05 | 0 | 5 | 2 | 20 | `non_lung_context_source_only` | gains 2 near + 2 dist |
| **SFTPB** | bed10 | 0 | 0 | 2 | 25 | `distal_candidate_support_only` | **CHANGED** |
| | bed05 | 0 | 1 | 9 | 17 | `non_lung_context_source_only` | gains 1 near + 7 more dist |
| **ID2** | bed10 | **1** | 2 | 0 | 24 | `peak_validated_in_non_lung_context_only` | (no class change) |
| | bed05 | **3** | 0 | 1 | 23 | `peak_validated_in_non_lung_context_only` | strengthens (1→3 proximal) |
| **HOPX** | bed10 | 0 | 0 | 0 | 27 | `no_locus_support` | **CHANGED** |
| | bed05 | 0 | 0 | 3 | 24 | `distal_candidate_support_only` | gains distal only |
| **AGER** | bed10 | 0 | 6 | 0 | 21 | `non_lung_context_source_only` | (no class change) |
| | bed05 | 0 | 7 | 0 | 20 | `non_lung_context_source_only` | gains 1 more nearby |
| **NKX2-1** | bed10 | 0 | 0 | 0 | 27 | `no_locus_support` | **CHANGED** |
| | bed05 | **1** | 1 | 0 | 25 | `peak_validated_in_non_lung_context_only` | **gains proximal hit + nearby** |
| **SOX2** | bed10 | 0 | 0 | 0 | 27 | `no_locus_support` | (no class change) |
| | bed05 | 0 | 0 | 0 | 27 | `no_locus_support` | robust empty |

Class distribution at bed05:

| Class | Count |
|---|---:|
| `peak_validated_in_non_lung_context_only` | 2 (ID2, NKX2-1) |
| `non_lung_context_source_only` | 3 (SFTPC, SFTPB, AGER) |
| `distal_candidate_support_only` | 1 (HOPX) |
| `no_locus_support` | 1 (SOX2) |

All evidence remains **non-lung** at bed05. The lung-tier classes are
still structurally unreachable — no lung experiments exist in
ChIP-Atlas hg38 SOX9.

## The five user-stated questions, answered

### 1. How many pairs change class from bed10 to bed05?

**3 of 7.** All three move *up* the hierarchy:

- **SFTPB**: `distal_candidate_support_only` → `non_lung_context_source_only`
  (gains 1 nearby peak)
- **HOPX**: `no_locus_support` → `distal_candidate_support_only`
  (gains 3 distal peaks)
- **NKX2-1**: `no_locus_support` → `peak_validated_in_non_lung_context_only`
  (gains 1 proximal peak + 1 nearby — the most consequential
  threshold-driven change in the audit)

The other four (SFTPC, ID2, AGER, SOX2) keep their bed10 class but
gain additional supporting peaks within their existing tiers.

### 2. Do SFTPC, SFTPB, AGER, or HOPX gain proximal support at bed05?

**No.** None of the four alveolar / airway markers gain proximal
(≤ 5 kb of TSS) peaks at bed05:

| Alveolar marker | bed10 prox | bed05 prox | Note |
|---|---:|---:|---|
| SFTPC | 0 | 0 | gains 2 nearby + 2 distal at bed05 |
| SFTPB | 0 | 0 | gains 1 nearby + 7 more distal |
| AGER | 0 | 0 | gains 1 more nearby |
| HOPX | 0 | 0 | gains 3 distal (still no nearby or proximal) |

Threshold relaxation broadens the distal/nearby support for these
targets but **does not produce proximal-promoter binding** for any of
them. The two new proximal hits at bed05 (ID2, NKX2-1) are at
within-chain regulators, not at alveolar markers.

### 3. Does the alveolar-side evidence become meaningfully stronger?

**Modestly, but only at distal/nearby tiers.** Total across the four
alveolar/airway markers (SFTPC, SFTPB, AGER, HOPX):

| Tier | bed10 total | bed05 total | Change |
|---|---:|---:|---|
| Proximal (≤ 5 kb) | 0 | 0 | unchanged (zero) |
| Nearby (5–50 kb) | 9 | 13 | +4 (SFTPC ×2, SFTPB ×1, AGER ×1) |
| Distal (50–200 kb) | 2 | 14 | +12 (SFTPB ×7, SFTPC ×2, HOPX ×3) |
| no_local | 97 | 81 | -16 |

Distal-band signal grows substantially (SFTPB now has 9 distal
candidate peaks at bed05; HOPX gains 3 from a previous total of 0).
Nearby signal grows modestly. **Proximal signal stays at zero across
all four alveolar markers.**

This is consistent with the same pattern observed in the NKX2-1 audit
(SFTPC / SCGB1A1 / ABCA3 / FOXA2 had distal but not proximal peaks)
and in the SOX2 audit (TP63 had distal but not proximal). For SOX9,
**SFTPB's 9 distal peaks at bed05 is the strongest single-target
distal-candidate signal in the audit**, comparable to NKX2-1's
distal-candidate finding for ABCA3.

### 4. Is the SOX9 picture threshold-limited or substrate-limited?

**Substrate-limited, not threshold-limited.** Three observations all
point the same way:

- **0 / 4 alveolar markers gain proximal support at bed05.** If the
  failure were threshold-driven, at least one alveolar target should
  gain a proximal peak at the relaxed threshold. None do.
- **The 2 proximal hits at bed05 (ID2, NKX2-1) are at within-chain
  regulators, not at alveolar markers.** ID2 is broadly BMP-regulated
  beyond lung; NKX2-1 itself is a master regulator with broadly
  accessible chromatin. These are not lung-developmental-specific
  binding events.
- **ESC-derived context (7 retinal + pancreatic experiments)
  contributes zero peaks at any tier in any pair at any threshold**,
  despite individual experiments generating up to 3,274 peaks at
  bed05. ESC-derived SOX9 binds eye-development and pancreatic-
  endoderm targets, not lung-developmental targets.

The structural finding is robust: **SOX9 ChIP-Atlas hg38 has zero
lung-context experiments**, and threshold relaxation cannot
manufacture lung-context signal from a non-lung substrate. The
alveolar markers (SFTPC, SFTPB, AGER, HOPX) are exactly the targets
that should be transcribed in lung but not in the non-lung tissues
SOX9 was profiled in — so the locus-level absence of proximal SOX9
binding at these markers in non-lung substrate is **expected**, not
a refutation of textbook claims.

### 5. Continue SOX9 or stop the regulator-audit chain here?

**Stop the regulator-audit chain here.**

The continue criteria from `notes/sox9_audit_design.md`:

- ≥ 2 of 7 proximal validations in non-lung context: **met (2: ID2,
  NKX2-1)** — but both are within-chain regulators, not alveolar
  targets. The intent of the criterion was to surface enough signal
  to justify a primary-tissue ChIP search; this signal is at the
  wrong targets.
- Strong distal-band signal at alveolar markers: **partial.** SFTPB
  has 9 distal peaks at bed05 — moderate signal. But pursuing this
  via a distal-candidate audit would replicate NKX2-1's pipeline on
  a non-lung substrate, and the histone-filter pass would be
  meaningless because the candidates would be in non-lung-relevant
  chromatin.
- Within-chain pairs show binding: **mixed.** NKX2-1 gains 1 proximal
  + 1 nearby at bed05 (cross-context support for SOX9 → NKX2-1
  binding); SOX2 remains robustly empty across both thresholds.

The handoff criteria:

- All 7 land in `no_locus_support` / `non_lung_context_source_only`
  with ≤ 2 nearby total: **partially.** SOX2 is the only no_locus;
  there are 13 nearby + 2 proximal + 14 distal hits across the other
  six pairs.

The result sits between continue and handoff, similar to where SOX2
landed after its sensitivity sweep. **The deciding consideration is
substrate**: SOX9 has zero lung-context experiments, the bed05 sweep
just confirmed the failure is substrate-driven, and continuing into
SOX9 v0.x (distal-candidate audit, histone filter, GEO/SRA search)
would recreate the NKX2-1 pipeline on a strictly worse substrate.

## Stopping the regulator-audit chain — broader rationale

After three regulators (NKX2-1, SOX2, SOX9), the audit cycle has
reached a substrate ceiling that the next regulators in the chain
cannot escape:

| Regulator | hg38 ChIP-Atlas | Lung-context | Status |
|---|---:|---:|---|
| NKX2-1 | 21 | 21 (all cancer LUAD/SCLC) | audit cycle complete; 5 chromatin-supported standing candidates |
| SOX2 | 95 | 27 (cancer + MRC-5 reprogramming) | audit cycle complete; 0 proximal validations at bed05 |
| SOX9 | 27 | 0 | audit cycle complete; 2 cross-context proximal hits at bed05 |
| FGF10 | n/a (ligand) | n/a | not auditable by ChIP — needs different method |
| CTNNB1 (β-catenin / WNT) | 78 | 0 | substrate same shape as SOX9 (non-lung only) |
| SMAD1 (BMP) | 42 | 0 | substrate same shape; 3 ENCODE non-lung |
| GLI2 (SHH) | 4 | 0 | substrate even smaller |

**The chain's downstream effectors all share SOX9's substrate
constraint** — non-lung ChIP only. Continuing past SOX9 means doing
the same audit on shrinking and similarly-non-lung substrates, with
diminishing returns per regulator. The audit machinery is mature; the
constraint is now the public-data ecosystem.

The natural next moves (none of which require continuing the
regulator chain in the current form):

1. **Pivot to a different question.** The dataset-manifest CLI's v0.x
   roadmap (live verifier hardening, evidence-map generator,
   lung-switch-explorer) addresses different parts of the project's
   scope.
2. **Revisit the chain when primary-tissue ChIP appears.** The 5
   chromatin-supported NKX2-1 candidates + the SOX9 cross-context
   proximal hits are the standing "candidate set" for any future
   refresh.
3. **Try motif scanning + accessibility inference.** Several deferred
   audits (`indirect_accessibility_support` class, lung ATAC + JASPAR
   motif overlap) would produce new tier 4 signal at the loci where
   ChIP fails. This is the principled escape from the substrate
   ceiling.
4. **Try expression-correlation evidence via CELLxGENE Census.** Q1
   and Q2 from `notes/unresolved_questions.md` were deferred for this
   reason.

## Standing SOX9 outputs (final state of this audit cycle)

- **Source-level:** 27 hg38 ChIP-Atlas experiments. 100% non-lung
  (20 cancer + 7 ESC-derived). Zero skeletal/cartilage hg38 ChIP
  despite SOX9's canonical chondrocyte role.
- **Locus-level (non-lung substrate, bed05):**
  - 2 / 7 pairs proximal-validate in non-lung cancer context (ID2, NKX2-1)
  - 3 pairs nearby-only (SFTPC, SFTPB, AGER)
  - 1 pair distal-only (HOPX)
  - 1 robust empty (SOX2)
- **Strongest distal-candidate signal:** SFTPB (9 distal peaks at
  bed05 in non-lung cancer). Documented; not pursued further given
  substrate.
- **Most actionable cross-context finding:** SOX9 → NKX2-1 proximal
  hit at bed05 + 1 nearby. Combined with NKX2-1 → SOX9 finding from
  the NKX2-1 audit (cancer-line proximal hits), this is **bidirectional
  cross-context evidence for the proximal-distal axis regulators
  binding each other's loci**. Cross-context only — not lung-
  developmental — but a small genuine cross-regulator signal.

## Anti-overclaim summary

- **All evidence remains non-lung.** Whether at bed10 or bed05, no
  lung-context substrate exists. Cross-context binding does not
  validate lung-developmental claims.
- **The 2 proximal hits at bed05 (ID2, NKX2-1) are cancer-context.**
  ID2 is broadly expressed; NKX2-1's locus may be accessible in many
  cell types. Neither hit establishes lung-developmental binding.
- **The SFTPB 9-distal-peak signal at bed05 is an observation, not
  evidence of regulation.** Distal-band proximity does not establish
  regulatory contact. Functional validation would require Hi-C in the
  relevant cell types — and "the relevant cell types" for lung
  development are precisely what this substrate lacks.
- **Stopping the chain is not a refutation of SOX9's developmental
  role.** SOX9 is a well-established distal-tip regulator in lung
  development; the audit cycle simply cannot test that claim with
  current public ChIP data, and further v0.x audits would not
  change that.

## Reproducing the audit

```sh
python3 scripts/gain_sox9_audit_sensitivity.py
```

Stdlib only. 54 BED downloads (27 × 2 thresholds), ~ 11 MB total at
bed05 + ~ 3 MB at bed10. Total runtime ~ 60–90 s.
