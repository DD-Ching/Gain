# SOX2 Audit — Design

**Status:** design contract for the first-pass SOX2 audit. Reuses the
NKX2-1 audit machinery (peak intersection at hg38 TSS) without
rebuilding. Implementation must match this document; deviations
require updating it first.

**Why now.** The NKX2-1 audit cycle has reached its natural stopping
point — five chromatin-supported candidate loci stand as the standing
output, and the remaining gap is wet-lab-shaped, not audit-shaped.
SOX2 is the next regulator in the chain (proximal/airway side).
Applying the same audit framework to SOX2 lets us reuse the existing
script, classifier, and evidence model with **no new infrastructure**.

## Pre-implementation probe of the SOX2 substrate

ChIP-Atlas hg38 SOX2 TF ChIP-seq experiments: **95** total. Biosample
breakdown from `metadata/cache/chipatlas_experimentList.tab`:

| Category | n | Notes |
|---|---:|---|
| ESC / iPSC pluripotent | 38 | SOX2's canonical Yamanaka context — non-lung |
| Lung-context | **27** | mixed; see split below |
| Neural / brain | 16 | SOX2's other canonical context — non-lung |
| Other (digestive, head/neck, epidermis) | 14 | non-lung |

**The 27 lung-context experiments split further:**

| Sub-category | n | Cell lines / context |
|---|---:|---|
| Lung squamous cell carcinoma | 7 | HCC95, LK-2, KNS-62, NCI-H520, HCC2814 — SOX2 acts as a lineage oncogene |
| Other ArrayExpress "lung cancer" | 4 | ERX2260038-46 |
| Small cell lung cancer | 7 | H29, NCI-H82, NCI-H1836 + SRX2731713 |
| **MRC-5 fibroblast (reprogramming context)** | **8** | SRX1813580–585, SRX2732210–211 — non-cancer fetal lung fibroblast in OSKM/OSvKM Yamanaka-factor reprogramming experiments |
| LK-2 GFP / DNp63 modified | 1 | engineered LK-2; lung squamous |

Important caveats up front:

- **No primary epithelial SOX2 ChIP exists in ChIP-Atlas hg38.** This
  is the same shape as the NKX2-1 audit's central finding.
- **Cancer-line SOX2 ChIP is biologically meaningful, not just artefact.**
  SOX2 is a lineage-defining oncogene in lung squamous cell carcinoma
  (3q26 amplicon) and is required for survival in those lines. The
  binding map in lung squamous lines is a real reflection of SOX2
  biology — but in a *cancer* lineage program, not a *developmental*
  one.
- **MRC-5 SOX2 ChIP is non-physiological.** MRC-5 is a fetal-lung-
  derived **fibroblast** (mesenchymal, not epithelial). The 8 SOX2
  ChIPs in MRC-5 come from OSKM / OSvKM / OSK iPSC-induction
  experiments where SOX2 is overexpressed as a Yamanaka reprogramming
  factor. The bound sites reflect SOX2's pluripotency-induction binding
  preferences, not lung-developmental SOX2.

The substrate is therefore **richer in context types than NKX2-1's
21-experiments-all-lung-adenocarcinoma slice** — but the diversity is
across non-physiological settings, not a primary-tissue slice.

## Lung-focused SOX2 target list

Seven targets, parallel to the NKX2-1 audit's 7. Prioritised toward the
**proximal / airway program** that SOX2 specifies, with two
within-chain regulators:

| Target | hg38 TSS | Strand | Why included |
|---|---|---|---|
| **TP63** | chr3:189,631,389 | + | Basal-cell master TF — most-cited SOX2 → TP63 textbook target |
| **KRT5** | chr12:52,520,530 | − | Basal-cell cytokeratin — canonical airway basal marker |
| **MUC5B** | chr11:1,223,066 | + | Secretory-cell mucin — proximal/secretory program |
| **FOXJ1** | chr17:76,141,245 | − | Ciliated-cell master TF — proximal/ciliated program |
| **SCGB1A1** | chr11:62,405,103 | + | Secretory marker (also a NKX2-1 target — useful for cross-regulator comparison) |
| **NKX2-1** | chr14:36,521,149 | − | Master upstream — does SOX2 bind back at the NKX2-1 locus? |
| **SOX9** | chr17:72,121,020 | + | Distal counterpart — proximal-distal axis question |

The within-chain pairs (NKX2-1, SOX9) aren't strictly "downstream
targets" of SOX2; they're tested because the textbook regulatory
chain claims reciprocal / antagonistic regulation. Including them
addresses a different question per pair than the airway-marker pairs.

## What counts as a meaningful first-pass result

A pair = (SOX2, target). Per pair, the audit produces:

1. **Source-level evidence**: counts across the 27 lung-context
   experiments, split by `lung_cancer_line` (~19) vs
   `non_cancer_lung_reprogramming` (MRC-5, ~8). Plus a context note
   that 38 ESC/iPSC + 16 neural experiments exist outside lung —
   relevant for SOX2 binding-motif validation but **not** for
   lung-developmental claims.
2. **Locus-level evidence**: peak intersection at the target's TSS
   ± 5 kb (proximal) and 5–50 kb (nearby) windows. This is the same
   first-pass shape as `gain_nkx21_audit.py`. Sensitivity sweep and
   distal-candidate tiering are **not** done in v0 — only justified
   if the v0 result is interesting enough to continue.
3. **Class assignment** under the v2-style 5-class system (parallel
   to the NKX2-1 v0 audit):
   - `peak_validated_in_lung_context` (impossible — no primary
     epithelial)
   - `peak_validated_in_cancer_lung_context_only` (≥ 1 cancer-line
     experiment shows peak ≤ 5 kb of TSS; zero non-cancer)
   - **NEW for SOX2:** `peak_validated_in_lung_reprogramming_context_only`
     (≥ 1 MRC-5 reprogramming experiment shows peak ≤ 5 kb; zero
     cancer-line; zero primary). Captures the non-physiological-but-
     non-cancer case.
   - `lung_context_source_only` (only nearby peaks, no proximal)
   - `no_locus_support`
   - `unresolved_due_to_context_mismatch`

The new class avoids merging cancer and MRC-5 evidence under a single
"cancer-only" umbrella when the substrates are biologically distinct.

## Evidence classes likely to matter most for SOX2

| Class | Likely incidence in v0 | Why |
|---|---|---|
| `peak_validated_in_cancer_lung_context_only` | **likely high** for TP63, KRT5 | These are SOX2's canonical squamous targets in lung cancer |
| `peak_validated_in_lung_reprogramming_context_only` | possibly some | MRC-5 OSKM SOX2 binds pluripotency targets primarily; lung-developmental targets less so |
| `lung_context_source_only` | likely a few | Distal binding without proximal |
| `no_locus_support` | likely the within-chain pairs (NKX2-1, SOX9) | Reciprocal binding is more inferred than ChIP-supported |
| `unresolved_due_to_context_mismatch` | low | All 27 experiments are classifiable |

The strongest a priori prediction:
- **TP63** likely passes locus test in lung squamous lines (SOX2
  directly upstream of TP63 in squamous cancer literature).
- **KRT5** likely passes (canonical squamous marker).
- **NKX2-1** likely fails (within-chain reciprocal regulation more
  inferred than ChIP-supported).

These are predictions to test, not findings.

## What would make SOX2 worth continuing vs handing off to SOX9?

**Continue with SOX2 v0.x** (sensitivity sweep, distal candidates,
histone filter — same machinery as NKX2-1) if **any** of:

- ≥ 3 of 7 pairs land in `peak_validated_*` tiers (suggests there is
  enough binding signal to refine).
- The within-chain pairs (NKX2-1, SOX9) show measurable signal, even
  if only nearby — addresses the textbook chain claim directly.
- The MRC-5 reprogramming evidence is meaningfully different from the
  cancer-line evidence at any pair (suggests context-dependent
  binding).

**Hand off quickly to SOX9** if:

- ≤ 2 of 7 pairs validate, and the failures span both cancer-line and
  MRC-5 substrates (suggests the lung-context evidence is too thin
  for follow-up, or that SOX2's lung-context binding is dominated by
  cancer-specific gene programs not on our target list).
- All "passes" cluster on TP63 + KRT5 (canonical squamous) and the
  rest fail (suggests SOX2's public lung-context binding is "the
  squamous oncogene story", which is well-documented and adds
  little).

## Reuse strategy

The cleanest reuse is **sibling import**. New script
`scripts/gain_sox2_audit.py` imports the helpers from
`gain_nkx21_audit.py`:

- `chipatlas_bed_url(srx, threshold)`
- `http_get_bytes(url, timeout)`
- `parse_bed(blob)`
- `peak_distance_to_tss(peaks, target)`
- `classify_per_experiment(distance)`

The new script defines its own `SOX2_EXPERIMENTS` (27 hardcoded SRX IDs
+ biosample subcategory) and `SOX2_TARGETS` (7 hardcoded TSS coords).
The classification logic adapts to add the new
`peak_validated_in_lung_reprogramming_context_only` class. No
modification to `gain_nkx21_audit.py`.

## Inputs / Outputs

**Inputs:**
- Hardcoded SOX2_EXPERIMENTS (27) and SOX2_TARGETS (7) in the script.
- ChIP-Atlas peak BED files at bed10 threshold (q < 10⁻¹⁰), URL
  pattern verified by previous audits.

**Outputs:**
- `metadata/sox2_initial_audit.csv` — one row per (SOX2, target).
  Columns:
  - regulator (always `SOX2`)
  - target
  - target_locus
  - n_experiments_total (always 27)
  - n_cancer_line (~19)
  - n_mrc5_reprogramming (~8)
  - n_proximal_cancer (peak ≤ 5 kb in cancer biosamples)
  - n_proximal_mrc5 (peak ≤ 5 kb in MRC-5 biosamples)
  - n_nearby_cancer
  - n_nearby_mrc5
  - n_no_local_total
  - n_download_failed
  - final_class (one of the 6 classes above)
  - justification
  - evidence_url
- `notes/sox2_initial_audit.md` — report covering the four user-stated
  questions (lung-context evidence? mostly non-lung? proximal-airway
  locus support? more or less grounded than NKX2-1?).

## Anti-overclaim rules

- **Cancer-line SOX2 binding is real but cancer-context.** Lung
  squamous SOX2 acts as a lineage oncogene; binding sites are
  meaningful but reflect cancer biology, not normal lung development.
- **MRC-5 SOX2 ChIP is reprogramming context, not endogenous SOX2.**
  Bound sites reflect SOX2's role in iPSC induction (pluripotency
  network targets), not its lung-developmental role.
- **No primary lung-epithelial SOX2 ChIP exists.** Same gap as NKX2-1.
  No claim about SOX2's developmental binding can be made from this
  audit.
- **The within-chain pairs (NKX2-1, SOX9) are tested for binding, not
  for regulation.** Even a clear locus-level peak does not establish
  that SOX2 regulates NKX2-1 or SOX9.

## Out of scope for v0

- Sensitivity sweep across thresholds (bed05).
- Distal-candidate analysis.
- Histone-mark cross-reference.
- Non-lung SOX2 ChIP (ESC/iPSC, neural, digestive — those are
  catalogued in the source-level summary but not used for locus
  testing in v0).
- Any SOX9 / FGF10 / WNT / BMP / SHH work.
