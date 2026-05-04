# Motif + Accessibility Quantitative Refinement — Result

**Run:** 2026-05-04 (UTC)
**Inputs:** existing CSVs only (no new HTTP) —
- [`metadata/nkx21_motif_accessibility_audit.csv`](../metadata/nkx21_motif_accessibility_audit.csv)
- [`metadata/sox2_motif_accessibility_audit.csv`](../metadata/sox2_motif_accessibility_audit.csv)
- [`metadata/motif_accessibility_control_audit.csv`](../metadata/motif_accessibility_control_audit.csv)
**Output:** [`metadata/motif_accessibility_quant_refinement.csv`](../metadata/motif_accessibility_quant_refinement.csv)
**Script:** [`scripts/gain_motif_accessibility_quant.py`](../scripts/gain_motif_accessibility_quant.py)
**Design contract:** [`notes/motif_accessibility_quant_design.md`](motif_accessibility_quant_design.md)

## Verdict (headline)

**`not_salvageable`.** Under all four normalised metrics computed
from the existing per-pair counts, canonical SOX2 targets and
controls are **fully interleaved**. Three of five controls outrank
all SOX2 canonical targets; one canonical (TP63) sits between two
blood-specific controls.

## Ranked SOX2 + control panel (combined_quant_score, descending)

| Rank | Gene | Category | capture | density | consistency | combined |
|---:|---|---|---:|---:|---:|---:|
| 1 | **ACTB** | control: housekeeping | 0.7585 | 0.5048 | 0.9231 | **0.7001** |
| 2 | **SFTPC** | control: lung wrong-program | 0.2105 | 0.3609 | 1.0000 | 0.2105 |
| 3 | **GAPDH** | control: housekeeping | 0.2109 | 0.3837 | 0.9231 | 0.1946 |
| 4 | SCGB1A1 | sox2_canonical | 0.1573 | 0.3155 | 1.0000 | 0.1573 |
| 5 | FOXJ1 | sox2_canonical | 0.1375 | 0.3053 | 1.0000 | 0.1375 |
| 6 | MUC5B | sox2_canonical | 0.1719 | 0.2621 | 0.7692 | 0.1323 |
| 7 | KRT5 | sox2_canonical | 0.0615 | 0.4706 | 0.8462 | 0.0521 |
| 8 | **HBB** | control: blood-specific | 0.0316 | 0.3571 | 0.4615 | 0.0146 |
| 9 | **TP63** | sox2_canonical | 0.0296 | 0.4516 | 0.3846 | **0.0114** |
| 10 | **HBA1** | control: blood-specific | 0.0179 | 0.0667 | 0.2308 | **0.0041** |

Canonical SOX2 score range: **0.0114 – 0.1573.**
Control score range: **0.0041 – 0.7001** (full superset of canonical range).

The three top ranks are controls. The two bottom ranks are blood
controls + TP63 (canonical). The SOX2 canonical targets are
distributed at ranks 4, 5, 6, 7, and 9 — interleaved with controls
throughout.

## NKX2-1 targets (cross-motif; reported with caveat)

The NKX2-1 audit used the NKX2-1 motif (MA1994.2, 7-bp). The control
audit used the SOX2 motif (MA0143.5, 11-bp). Direct numeric comparison
between these is methodologically weak — different motifs have
different baseline occurrence rates. The NKX2-1 target metrics under
their own motif:

| NKX2-1 target | capture | density | consistency | combined |
|---|---:|---:|---:|---:|
| FOXA2 | 0.2441 | 0.6019 | 0.9231 | **0.2253** |
| SCGB1A1 | 0.1836 | 0.2798 | 0.8462 | 0.1553 |
| SFTPC | 0.1717 | 0.2556 | 0.8462 | 0.1453 |
| ABCA3 | 0.1289 | 0.5789 | 0.6154 | 0.0793 |

NKX2-1 target combined-score range: 0.0793 – 0.2253. Under the
SOX2-motif-scored control range (0.0041 – 0.7001), NKX2-1 targets
land between HBB (0.015) and SFTPC (0.211), broadly overlapping the
controls' middle band. ACTB (0.700) outranks every NKX2-1 target.

**Caveat applies.** A proper apples-to-apples test would re-scan the
controls under the NKX2-1 motif — but that would require new HTTP and
is forbidden by this audit's scope. The observation that NKX2-1
targets fall in the same range as SOX2-motif controls is consistent
with the SOX2 finding and does not contradict the verdict.

## The four user-stated questions, answered

### 1. Do SOX2 targets separate from controls under normalized scoring?

**No.** Under every metric computed (capture rate, motif density per
fetal peak, cross-donor consistency, combined score), SOX2 canonical
targets are fully interleaved with controls. The combined-score
ranking puts ACTB (housekeeping control) at #1, SFTPC (lung wrong-
program control) at #2, and GAPDH (housekeeping control) at #3 —
**all above every SOX2 canonical target.** TP63 (canonical) is at
#9, between two blood controls.

### 2. Do TP63 / KRT5 become meaningfully stronger?

**No.** Quantitative refinement does not rescue them.

- **TP63** combined_quant_score = 0.0114. This is **below HBB
  (0.0146)**, a blood control, and only just above HBA1 (0.0041),
  the other blood control. TP63 ranks #9 of 10 in the SOX2 + control
  panel.
- **KRT5** combined_quant_score = 0.0521. Above the blood controls
  but below all three other controls (housekeeping + lung wrong-
  program). Ranks #7 of 10.

If anything, TP63 looks *worse* than HBB under quantitative scoring
— it has fewer supporting fetal donors (5 vs 6) and a lower motif
capture rate (0.030 vs 0.032).

### 3. Does the NKX2-1 set remain stronger than controls under the same refined metric?

**Cross-motif comparison; weaker conclusion.** NKX2-1 targets'
combined scores (0.0793 – 0.2253) overlap the middle of the
SOX2-motif control range (0.0041 – 0.7001):

- ABCA3 (0.0793): below GAPDH/SFTPC/ACTB controls; above blood
  controls and 2 SOX2 targets.
- SFTPC (0.1453): in the SOX2 canonical range; below GAPDH/SFTPC
  controls.
- SCGB1A1 (0.1553): in the SOX2 canonical range.
- FOXA2 (0.2253): the highest NKX2-1 target; still below ACTB
  control (0.700) and similar to SFTPC control (0.211).

Under the imperfect cross-motif comparison, NKX2-1 targets do
**not** appear cleanly above controls. A proper test (controls
re-scanned with the NKX2-1 motif) would require forbidden HTTP, but
nothing in this comparison rescues the previous "4 of 4 NKX2-1
rescue" headline.

### 4. Is the indirect layer salvageable with quantitative refinement, or should it be considered too non-selective at bulk-lung scale?

**Not salvageable** with the v0 setup (motif at relative_score ≥ 0.85
+ bulk fetal lung accessibility + per-pair aggregate counts). Three
observations:

1. **Bulk fetal lung accessibility is too broad.** With 60,000–
   420,000 peaks per fetal experiment, almost any locus that's
   transcribed in fetal lung shows hundreds of accessible peaks in a
   ± 50 kb window. Motif occurrences within those peaks are a
   property of *being expressed in fetal lung*, not of being
   regulated by the specific TF.
2. **Per-pair aggregate counts cannot recover per-bp specificity.**
   A normalised metric like motifs-per-accessible-bp could in
   principle separate canonical targets from controls if it
   accounted for accessibility coverage saturating different
   genomic windows differently. But that requires per-peak widths,
   which are not in the existing CSVs and cannot be re-fetched
   under this audit's "no new HTTP" rule.
3. **The categorical 5/5-vs-5/5 result is robust to threshold
   relaxation.** Even at quantitative scoring, canonicals do not
   move above controls. The method cannot discriminate at the
   bulk-lung scale.

The indirect-evidence layer **does** discriminate one thing: it
clearly separates strongly-tissue-restricted (RBC) genes from
"any-lung-expressed gene". But that bar is too low for regulator-
target validation. Cell-type-specific accessibility (AT2-cell-
specific, club-cell-specific, basal-cell-specific) might be the
next legitimate refinement — but acquiring such data is out of
scope for this audit cycle and likely requires new pipelines.

## Recommendation: stop and summarize

Per the user's stated rule for this audit: *"if the quantitative
refinement still fails to separate targets from controls, stop and
recommend project-summary mode."* That condition is met.

The chain audit + the indirect-evidence calibration together form a
coherent project contribution:

- **Chain audit findings** (NKX2-1 / SOX2 / SOX9 v0 + sensitivity +
  distal-candidate + histone-filter passes) — established that
  primary-tissue ChIP for the canonical lung-developmental
  regulators is missing from public databases, with documented
  cancer-line / non-lung substrate as the only available evidence.
- **External-source search** — confirmed the absence is real, not
  a snapshot artefact.
- **5 NKX2-1 standing chromatin-supported distal candidates** —
  the audit cycle's positive deliverable.
- **Indirect-evidence calibration** (this turn + prior) — shows
  that bulk-lung motif + accessibility cannot serve as a
  discriminating indirect layer at v0 settings; further refinement
  requires either cell-type-specific accessibility or per-bp
  density methods that need new data.

The standing project recommendation is now **summarize the chain
audit + calibration findings as the v0 deliverable**, document the
indirect-evidence layer's failure-to-discriminate as itself a
finding, and either pause or pivot the project to a fundamentally
different method (cell-type-deconvolved accessibility, or expression-
correlation via Census per Q1/Q2).

## Anti-overclaim summary

- **`not_salvageable` does NOT mean SOX2/NKX2-1 don't bind their
  targets in lung development.** It means the v0 motif+accessibility
  method at bulk-lung scale cannot tell us either way.
- **The textbook claims for NKX2-1 → SFTPC and SOX2 → TP63 stand
  unaltered.** They rest on functional / promoter-reporter / lineage-
  tracing evidence that this audit does not consult.
- **The control panel is small (5 genes).** A v1 calibration would
  use 50–100 random controls. v0's verdict is qualitative ("clearly
  interleaved"), not statistical.

## Reproducing this refinement

```sh
python3 scripts/gain_motif_accessibility_quant.py
```

Stdlib only. **No HTTP.** Reads the three existing audit CSVs;
writes one output CSV; runtime under 1 second.
