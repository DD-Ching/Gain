# SOX9 Audit — Design

**Status:** design contract for the first-pass SOX9 audit. Reuses the
NKX2-1 / SOX2 audit machinery (peak intersection at hg38 TSS) without
rebuilding. Implementation must match this document; deviations
require updating it first.

**Why now.** SOX9 is the third regulator in the proximal/distal pair
(SOX2 = proximal/airway; SOX9 = distal/tip/alveolar). The audit
machinery is mature; the question is what it surfaces for SOX9 given
the substrate.

## Pre-implementation probe of the SOX9 substrate

ChIP-Atlas hg38 SOX9 TF ChIP-seq experiments: **27** total. Biosample
distribution from the cached `experimentList.tab`:

| Tissue / context | n |
|---|---:|
| **Lung-context** | **0** |
| Prostate cancer (LNCAP, VCaP) | 9 |
| ESC-derived retinal cells | 6 |
| Breast cancer (MCF-7) | 4 |
| Colon cancer (HT-29, LoVo) | 4 |
| Pancreas cancer (PANC-1) | 2 |
| ESC-derived pancreatic cells | 1 |
| Lymphoma (KARPAS-422) | 1 |

**Two structural facts** that shape the audit:

1. **Zero lung-context experiments.** SOX9 ChIP-Atlas hg38 has *no*
   lung biosamples — neither cancer-line nor primary tissue, neither
   in lung adenocarcinoma nor in lung organoid context. This is a
   sharper baseline than SOX2 (27 lung-context with a cancer + MRC-5
   split) or NKX2-1 (21 lung-context, all cancer).
2. **All 27 experiments are non-lung.** The substrate divides cleanly
   into 20 cancer cell lines (prostate / breast / colon / pancreas /
   lymphoma) + 7 ESC-derived cells (retinal x6, pancreatic x1).
   Notably, **no skeletal / cartilage / chondrocyte experiments**
   appear in the hg38 SOX9 ChIP-Atlas slice — surprising given SOX9's
   canonical chondrocyte master-regulator role.

## What this means for the audit

The lung-tier classes are **structurally unreachable** for SOX9 v0:

- `peak_validated_in_lung_context` — impossible, no lung experiments.
- `peak_validated_in_cancer_lung_context_only` — impossible.
- `peak_validated_in_lung_reprogramming_context_only` — impossible.
- `lung_context_source_only` — impossible.

The audit can only test **whether SOX9's binding map in non-lung
contexts (prostate, breast, colon, pancreas, ESC-retinal) places peaks
at the canonical lung-developmental target TSSs**. Two new SOX9-specific
classes capture this:

- **`peak_validated_in_non_lung_context_only`** — at least one non-lung
  experiment shows SOX9 peak ≤ 5 kb of TSS. Cross-context binding
  evidence; the binding site is real but the tissue context is wrong
  for the lung-developmental claim.
- **`non_lung_context_source_only`** — peaks within 5–50 kb in non-lung
  experiments only; no proximal anywhere.

Plus the standard threshold-irrelevant classes:

- `distal_candidate_support_only` — 50–200 kb peaks only.
- `no_locus_support` — no peaks within 200 kb at any threshold.
- `unresolved_due_to_context_mismatch` — if downloads fail.

The full class precedence for SOX9 v0:

1. `peak_validated_in_lung_context` — unreachable
2. `peak_validated_in_cancer_lung_context_only` — unreachable
3. `peak_validated_in_lung_reprogramming_context_only` — unreachable
4. **`peak_validated_in_non_lung_context_only`** *(new)*
5. `lung_context_source_only` — unreachable
6. **`non_lung_context_source_only`** *(new)*
7. `distal_candidate_support_only`
8. `no_locus_support`
9. `unresolved_due_to_context_mismatch`

## Lung-focused SOX9 target list

Seven targets, distal/alveolar-emphasis, with two within-chain
regulators — parallel to NKX2-1's and SOX2's lists:

| Target | hg38 TSS | Strand | Why included |
|---|---|---|---|
| **SFTPC** | chr8:22,156,913 | + | AT2 alveolar surfactant — within-chain (was NKX2-1's worst pair) |
| **SFTPB** | chr2:85,668,741 | − | AT2 alveolar surfactant — was NKX2-1's *best* pair |
| **ID2** | chr2:8,678,845 | + | Distal tip co-marker, canonical SOX9 partner in fetal lung |
| **HOPX** | chr4:56,681,877 | − | AT1 alveolar marker (homeodomain-only) |
| **AGER** | chr6:32,184,344 | − | AT1 alveolar marker (RAGE) |
| **NKX2-1** | chr14:36,521,149 | − | Within-chain master upstream |
| **SOX2** | chr3:181,711,925 | + | Within-chain proximal counterpart — proximal-distal axis |

The five canonical airway markers from the SOX2 audit (TP63, KRT5,
MUC5B, FOXJ1, SCGB1A1) are **not** included — those are proximal/
airway program markers and the relevant regulator is SOX2, not SOX9.
Including them would test SOX9's binding to non-canonical targets,
which dilutes the audit.

## What counts as a meaningful first-pass result

For each of 7 (SOX9, target) pairs:

1. **Source-level evidence:** counts across the 27 non-lung
   experiments, split into `non_lung_cancer` (20) vs `esc_derived`
   (7). Plus the explicit zero-lung-experiments fact.
2. **Locus-level evidence:** peak intersection at the target's TSS
   ± 5 kb (proximal) and 5–50 kb (nearby) windows at bed10 only.
   Sensitivity sweep deferred to v0.x if v0 surfaces signal.
3. **Class assignment** under the v9-class system above.

## Evidence classes likely to matter most for SOX9

| Class | Likely incidence | Rationale |
|---|---|---|
| `peak_validated_in_non_lung_context_only` | possibly some | SOX9 in chondrocyte / colon / pancreas binds widely; lung markers may have shared regulatory regions |
| `non_lung_context_source_only` | possibly some | nearby-band hits without proximal |
| `distal_candidate_support_only` | a few | analogous to SOX2's distal-band signal |
| `no_locus_support` | likely several | non-lung SOX9 is unlikely to bind specifically at lung-developmental promoters |

A priori prediction:
- **SFTPC** and **SFTPB** likely fail in non-lung context — these are
  alveolar-specific genes that non-lung tissues shouldn't be
  transcribing.
- **HOPX** and **AGER** likely fail similarly.
- **ID2** is BMP/SMAD-regulated and broadly expressed — non-lung
  SOX9 might bind near it.
- **NKX2-1** is mostly lung/thyroid/neural — non-lung SOX9 might bind
  if there is shared regulatory architecture across endoderm-derived
  tissues.
- **SOX2** is broadly expressed in stem/progenitor contexts — possibly
  some signal.

## What would justify continuing SOX9 vs handing off?

**Continue with SOX9 v0.x** (sensitivity sweep, distal candidates,
histone filter, external GEO/SRA search) if **any** of:

- ≥ 2 of 7 pairs validate proximally in non-lung context (i.e., `peak_validated_in_non_lung_context_only` ≥ 2). This would justify a primary-tissue SOX9 ChIP search in GEO.
- Strong distal-band signal at the alveolar markers (SFTPC, SFTPB,
  HOPX, AGER), parallel to NKX2-1's distal-candidate pattern. If
  ABCA3-class distal signal appears at SOX9's alveolar markers, that
  is a real distal-candidate finding.
- Within-chain pairs (NKX2-1, SOX2) show proximal binding —
  reciprocal regulation evidence.

**Hand off to FGF10 or downstream** (the next regulator in the chain)
if:

- All 7 pairs land in `no_locus_support` or `non_lung_context_source_only`
  with ≤ 2 nearby peaks — suggests SOX9's non-lung ChIP is not
  informative for lung-developmental targets.
- The non-lung locus signal is dominated by ESC-retinal context (not
  developmental-relevant) and absent from cancer-line context (where
  SOX9 has more peaks per experiment).

The handoff threshold is **looser** for SOX9 than for SOX2 because
the substrate is non-lung throughout — the audit's information
ceiling is lower.

## Reuse strategy

Sibling import. New script `scripts/gain_sox9_audit.py` imports:

- From `gain_nkx21_audit`: `chipatlas_bed_url`, `http_get_bytes`,
  `parse_bed`, `peak_distance_to_tss`, `classify_per_experiment`.

The new script defines its own `SOX9_EXPERIMENTS` (27 hardcoded SRX
IDs + tissue subcategory) and `SOX9_TARGETS` (7 hardcoded TSS coords).
Classification logic adapts to the SOX9-specific class set above.
**No modification to `gain_nkx21_audit.py` or `gain_sox2_audit.py`.**

## Inputs / Outputs

**Inputs:**
- Hardcoded `SOX9_EXPERIMENTS` (27) and `SOX9_TARGETS` (7) in the script.
- ChIP-Atlas peak BED files at bed10 threshold (q < 10⁻¹⁰).

**Outputs:**

`metadata/sox9_initial_audit.csv` — one row per (SOX9, target):

| column | meaning |
|---|---|
| regulator | always `SOX9` |
| target | one of the 7 |
| target_locus | `chr:tss (strand)` |
| n_experiments_total | always 27 |
| n_non_lung_cancer | always 20 |
| n_esc_derived | always 7 |
| n_proximal_cancer (non-lung) | peak ≤ 5 kb in cancer biosamples |
| n_proximal_esc | peak ≤ 5 kb in ESC-derived biosamples |
| n_nearby_cancer (non-lung) | 5–50 kb in cancer |
| n_nearby_esc | 5–50 kb in ESC |
| n_no_local_total | 0 peaks within 50 kb |
| n_download_failed | per-pair |
| final_class | one of the 9 classes above |
| justification | short text |
| evidence_url | ChIP-Atlas SOX9 search |

`notes/sox9_initial_audit.md` — report covering the four user-stated
questions (lung-context evidence? mostly non-lung? distal/alveolar
locus support? more or less grounded than SOX2?).

## Anti-overclaim rules

- **Non-lung SOX9 ChIP is non-lung ChIP.** Even a clear locus-level
  peak at a lung target's TSS in prostate or colon cancer ChIP is
  *cross-context binding evidence*, not lung-developmental
  validation.
- **No primary lung-epithelial SOX9 ChIP exists.** Same gap as NKX2-1
  and SOX2 (and even worse: no cancer-lung ChIP either). The standing
  caveat is the strictest of the three regulators audited.
- **The lung-tier classes are unreachable** in v0 because the
  substrate doesn't include lung biosamples. Reaching them would
  require new public data deposition.
- **ESC-retinal SOX9 ChIP is far from lung development.** The
  6 hESC-derived retinal experiments use SOX9 in eye-development
  context; binding sites there are extremely unlikely to inform lung-
  developmental claims.

## Out of scope for v0

- Sensitivity sweep across thresholds (bed05 / bed20).
- Distal-candidate analysis.
- Histone-mark cross-reference.
- External GEO/SRA search — only if v0 surfaces enough signal to
  justify it. Otherwise the same "no primary tissue ChIP exists"
  conclusion likely applies.
- FGF10 / WNT / BMP / SHH / downstream work — those follow SOX9's
  decision.
