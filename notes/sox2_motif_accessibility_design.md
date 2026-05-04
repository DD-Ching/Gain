# SOX2 Motif + Accessibility Audit (with Control Calibration) — Design

**Status:** design contract for the second motif+accessibility audit
plus a paired control calibration. Implementation must match this
document; deviations require updating it first.

**Why now.** The NKX2-1 motif+accessibility audit returned 4-of-4
positives at the strongest indirect tier
(`indirect_accessibility_support_in_fetal_lung_tissue`). That is a
striking result, but **it could equally reflect a true rescue of the
substrate ceiling OR a high false-positive rate inherent to the
method**. Until that ambiguity is resolved, expanding to SOX2 alone
risks compounding it.

This audit therefore does **two things together**:

1. **SOX2 expansion** — test whether the indirect-evidence layer
   rescues SOX2's failing canonical pairs the way it rescued
   NKX2-1's.
2. **Control calibration** — run the *SOX2 motif* against a small
   panel of non-SOX2-target genes to estimate the false-positive
   rate of the method itself.

If SOX2 targets pass at ≥ 4 / 5 *and* controls pass at ≤ 2 / 5, the
method is **selective enough** to use across the chain. If controls
also pass at 4–5 / 5, the method is **too permissive** and the
NKX2-1 4-of-4 result must be re-interpreted accordingly.

## Substrate (reused; no new downloads needed)

Same as NKX2-1 motif+accessibility audit:

- **15 ENCODE human lung accessibility experiments** (13 fetal DNase
  + 1 adult DNase + 1 adult ATAC). Already verified.
- **UCSC API** for hg38 sequence per-target ± 50 kb window.
- **JASPAR Elixir** for motif PFM.

## Motif

**SOX2 motif: JASPAR MA0143.5** (verified 2026-05-04). 11-bp PFM
capturing the canonical SOX HMG box sequence (consensus around
**CATTGT**). MA0143.4 is the prior version; MA0143.5 is current.

Threshold: same as NKX2-1 audit — `relative_score >= 0.85`.

## Targets (5 SOX2 + 5 controls)

### SOX2 canonical proximal/airway targets (per user instruction)

The 5 canonical SOX2 → airway program targets, **minus** the
within-chain pairs (NKX2-1, SOX9 — these are not SOX2 → airway,
they're testing reciprocal regulation and are out of scope for this
calibration audit):

| Target | hg38 TSS | Strand | Why included |
|---|---|---|---|
| **TP63** | chr3:189,631,389 | + | Basal-cell master TF — most-cited SOX2 → TP63 textbook target |
| **KRT5** | chr12:52,520,530 | − | Basal-cell cytokeratin — canonical airway basal marker |
| **MUC5B** | chr11:1,223,066 | + | Secretory-cell mucin — proximal/secretory program |
| **FOXJ1** | chr17:76,141,245 | − | Ciliated-cell master TF — proximal/ciliated program |
| **SCGB1A1** | chr11:62,405,103 | + | Secretory marker (also an NKX2-1 target — useful for cross-regulator comparison; here scanned with the *SOX2* motif, which is different from NKX2-1's) |

### Control panel (5 genes)

The control panel mixes three classes of "should-not-be-SOX2-targets":

| Control | hg38 TSS | Strand | Class | Rationale |
|---|---|---|---|---|
| **GAPDH** | chr12:6,534,012 | + | housekeeping | Ubiquitously expressed; accessible everywhere; not a SOX2 target. Baseline control. |
| **ACTB** | chr7:5,563,902 | − | housekeeping | Same. Baseline control. |
| **HBA1** | chr16:176,680 | + | blood-specific | Erythrocyte-restricted; should NOT have SOX2 motif support in lung context if the method is selective. Strong negative-control candidate. |
| **HBB** | chr11:5,229,395 | − | blood-specific | Same as HBA1. Independent gene + chromosome. |
| **SFTPC** | chr8:22,156,913 | + | lung but wrong-program | Lung-expressed (alveolar AT2 marker) but **not a SOX2 target** — SOX2 specifies proximal/airway, SFTPC is distal/alveolar. Tests *within-tissue* specificity: does the method distinguish SOX2's program from non-SOX2 lung programs? |

**Why this control mix is balanced:**

- 2 housekeeping (GAPDH, ACTB): chromatin-accessible everywhere; expected to have many lung peaks but not SOX2-program-specific. If SOX2 motif scores high here in fetal lung accessibility, the method is permissive at the *baseline* level.
- 2 blood-specific (HBA1, HBB): tissue-restricted to erythroid lineage. If SOX2 motif scores high here in fetal lung accessibility data, the method is permissive at the *tissue* level (blood promoters may have low accessibility in lung — testing this).
- 1 lung-but-wrong-program (SFTPC): the most stringent control. Lung-expressed in fetal AT2 progenitors so chromatin is accessible; not in SOX2's proximal/airway program. If SOX2 motif scores high here, the method cannot distinguish *between* lung programs.

## Method (unchanged from NKX2-1 audit)

For each of 10 genes (5 SOX2 targets + 5 controls):

1. Fetch hg38 sequence ± 50 kb of TSS (UCSC API).
2. Scan SOX2 PWM (MA0143.5) both strands at relative_score ≥ 0.85.
3. For each of 15 ENCODE lung accessibility experiments, retrieve
   peak BED, retain peaks overlapping the gene's window.
4. Intersect motif occurrences with accessible peaks, splitting by
   fetal vs adult.

## Output classes (unchanged from NKX2-1 audit)

Same 5-class scheme; both SOX2 targets and controls scored against
the same classifier:

1. `indirect_accessibility_support_in_fetal_lung_tissue`
2. `indirect_accessibility_support_in_adult_lung_tissue_only`
3. `motif_in_accessible_chromatin_negative`
4. `unresolved_no_lung_accessibility`
5. `error`

## Decision rule (built into the audit)

After the two runs (SOX2 audit + control audit), compare the
positive-class rates:

- **`positive_rate(targets)` = fraction of SOX2 targets in classes 1 or 2.**
- **`positive_rate(controls)` = fraction of controls in classes 1 or 2.**
- **Selectivity ratio = `positive_rate(targets) / positive_rate(controls)`** (or "infinity" if controls = 0).

Decision matrix:

| Targets pass | Controls pass | Interpretation |
|---|---|---|
| ≥ 4 / 5 | ≤ 2 / 5 | **Method is selective.** Indirect-evidence layer is informative. NKX2-1 4-of-4 result is corroborated as a real signal. Continue with SOX2 distal-locus refinement or NKX2-1 distal refinement. |
| ≥ 4 / 5 | 3–4 / 5 | **Method is partially selective.** Targets > controls but the gap is small. Indirect-evidence layer needs harder threshold or stricter motif models before claims are safe. Stop or refine method. |
| ≥ 4 / 5 | 5 / 5 | **Method is too permissive.** Re-interpret NKX2-1 4-of-4 as not selective; the method finds positives everywhere. Stop and pivot. |
| ≤ 2 / 5 | ≤ 2 / 5 | **Method is selective but SOX2 targets fail at the indirect layer too.** SOX2 substrate-driven failure confirmed; not threshold-driven. Stop the chain. |
| ≤ 2 / 5 | ≥ 3 / 5 | **Method is permissive AND SOX2 targets fail.** Most informative result — the indirect layer hits the wrong genes. Strong negative for the method. Stop and re-think. |

## Anti-overclaim rules carried forward

- **Indirect ≠ binding.** Same caveat as NKX2-1 audit.
- **Even a fully selective method is still indirect.** If targets pass
  and controls fail, the method *distinguishes* canonical targets
  from non-targets in lung accessibility — but doesn't *validate*
  binding.
- **The control panel is small.** 5 controls is enough to estimate
  whether the method is roughly selective or roughly permissive; it
  is not a rigorous null distribution. A v1 with a larger random
  gene panel (e.g., 100 random genes) would be a tighter calibration.

## Outputs

`metadata/sox2_motif_accessibility_audit.csv` — same schema as
NKX2-1 audit; one row per of 5 SOX2 targets.

`metadata/motif_accessibility_control_audit.csv` — same schema; one
row per of 5 control genes.

`notes/sox2_motif_accessibility_audit.md` — SOX2 results + per-pair
detail.

`notes/motif_accessibility_control_audit.md` — control results +
side-by-side comparison with SOX2 targets and the prior NKX2-1
results, plus the selectivity verdict.

## Implementation

Two new scripts, both stdlib-only, both sibling-importing helpers
from `gain_motif_accessibility_audit.py`:

- `scripts/gain_sox2_motif_accessibility_audit.py`
- `scripts/gain_motif_accessibility_control_audit.py`

Each is a thin wrapper around the existing helpers (
`fetch_jaspar_pfm`, `pfm_to_log_odds`, `fetch_hg38_window`,
`scan_pwm`, `best_lung_peak_file_url`, plus the `EXPERIMENTS` and
`classify` from the NKX2-1 script). The only differences per script:

- Motif ID (NKX2-1 = MA1994.2; SOX2 = MA0143.5)
- Target list (5 SOX2 canonical / 5 controls)
- Output CSV path

Estimated ~ 100–150 LoC each (most logic is imported). Total
runtime ~ 3 minutes for both runs together.

## Out of scope

- Other regulators (NKX2-1 already done; SOX9 deferred).
- Larger control panels (5 is enough for v0; a 100-gene random panel
  is v1 calibration work).
- Threshold sensitivity (only relative_score ≥ 0.85; no sweep).
- Multi-motif models (only MA0143.5 for SOX2; no MA0143.4 sanity check).
- Cell-type-deconvolved accessibility.
