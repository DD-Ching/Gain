# Limitations and Next Methods

Method-level next steps only. No implementation here. Each direction
is sized to be honest about what would be required to extend the
project beyond its v0 stop point — not to recommend that any of them
be undertaken now.

## Limitations of the v0 cycle

The current state has these specific limitations, each of which a
future method could address:

- **No primary human lung tissue TF ChIP-seq.** The chain audit
  established this is a real public-data gap, confirmed by external
  GEO/SRA search. Without such data, the question "does NKX2-1 bind
  SFTPC's proximal promoter in primary AT2 cells?" cannot be answered
  by audit work alone.
- **Bulk-tissue accessibility averages over cell types.** ENCODE's
  13 fetal lung DNase experiments profile *all cells* in fetal lung
  tissue. Cell-type-specific binding (NKX2-1 in AT2 progenitors;
  SOX2 in basal cells) is diluted by surrounding fibroblasts,
  endothelium, and immune cells.
- **Per-pair aggregate counts only.** The audit CSVs record peak
  counts and motif counts per gene-window but not per-base
  accessibility coverage. Per-bp density metrics (motifs per
  accessible bp) are not computable from the existing data.
- **Permissive motif models.** JASPAR PFMs at relative_score ≥ 0.85
  are degenerate — 7–11 bp motifs at that threshold hit hundreds of
  positions per 100-kb window. Stricter thresholds reduce sensitivity
  in unknown ways.
- **No statistical control for the indirect-evidence calibration.**
  The 5-control panel was qualitative. Formal selectivity inference
  requires ~ 50–100 random control genes.
- **All evidence is for human only.** Mouse ChIP-Atlas data (which
  is broader for lung-developmental TFs) was deliberately out of
  scope to keep the developmental claims human-specific.

## Method-level future directions

Six directions, in rough order of decisiveness for the project's
unresolved questions. Each requires either new substrate or new
infrastructure that v0 did not adopt.

### 1. Cell-type-resolved accessibility

**The single highest-leverage method pivot.**

ENCODE's 13 fetal lung DNase experiments are bulk tissue. Single-
cell ATAC-seq (scATAC) from lung tissue, deconvolved into AT2 / AT1
/ basal / secretory / ciliated / fibroblast / endothelial cell-type
tracks, would let the motif + accessibility audit ask:
"in *AT2 cells specifically*, does the NKX2-1 motif occur within
accessible chromatin near SFTPC?" This addresses the bulk-tissue-
averaging confound directly — the most likely cause of the v0
indirect-evidence layer's failure to discriminate.

Substrate exists in publications: cell-type-specific ATAC tracks
from primary fetal lung work (Quach & Farrell 2024, Nikolic 2017,
He 2022). Most are not yet in ENCODE's standardised browser; some
require GEO download + per-cell-type peak calling. Substantial new
infrastructure (likely new dependencies for cell-type
deconvolution).

### 2. Expression-correlation route via CELLxGENE Census

**The natural pivot to the deferred Q1 / Q2 questions.**

Q1 (when do bipotent SOX2/SOX9 progenitors commit?) and Q2 (is the
proximal-distal axis a continuous gradient or discrete switch?) are
real, unresolved, and answerable with primary lung scRNA-seq via
CELLxGENE Census. The substrate is mature — HLCA + He 2022 fetal
lung + Cao 2020 pan-fetal — and well-documented programmatic access
exists.

This is the project's deferred-MVP track. It requires:
- `cellxgene-census` + `tiledbsoma` + `pyarrow` + `pandas` + `numpy` —
  the heaviest dependency stack the project has so far considered
- Single-cell normalisation and analysis decisions (per-cell-type
  averaging, dimensionality reduction, etc.)
- Different analysis idiom than the audit cycle (correlation,
  pseudotime, score distributions vs interval intersection)

It would *not* extend the existing audit machinery — it would build
a parallel analysis surface. Out of scope for the v0 cycle's audit
philosophy but well within the project's overall scope.

### 3. Contact / Hi-C-style evidence

**The right tool for converting "distal candidates" into "regulatory
elements."**

The 5 NKX2-1 chromatin-supported standing distal candidates are
*candidate* regulatory elements. To convert them to *validated*
regulatory elements would require Hi-C, promoter-capture Hi-C, 4C,
or perturbation of the candidate locus with measurement of the
target gene. Public Hi-C data in lung tissue exists (ENCODE has
some); cell-type-specific lung Hi-C is limited.

A focused audit on *just* the 5 standing candidates against any
available lung Hi-C contact map would convert the candidate list
into a much shorter and stronger output. ~ 200 LoC of new
intersection logic; substrate dependency on whatever Hi-C data is
publicly available.

### 4. Primary tissue developmental ChIP — if it ever appears

**The decisive method, but not actionable until external data
appears.**

If a paper deposits primary human lung tissue or fetal lung NKX2-1 /
SOX2 / SOX9 ChIP-seq in GEO, the existing audit machinery applies
unchanged: the same `gain_*_audit.py` + sensitivity + distal-
candidate + histone-filter scripts re-run with the new SRX IDs
slotted in. The audit cycle is mature; it waits on substrate.

A periodic re-check of GEO via the same E-utilities pipeline used
in `notes/nkx21_final_gap.md` would catch new depositions cheaply.
A simple `cron` of the existing search query would alert when new
hits appear.

### 5. Perturbation / wet-lab validation

**Outside the project's substrate but the gold standard for
validation.**

CRISPR knockdown of NKX2-1 in primary AT2 cells (or in iPSC-derived
NKX2-1+ progenitors) followed by RNA-seq of the target genes would
test the textbook claims directly. Several recent organoid /
iPSC-AT2 protocols make this technically tractable. Out of the
project's analytical scope but the most decisive answer to the
substrate-ceiling problem.

The project's standing candidate list (5 NKX2-1 chromatin-supported
distal loci) and the SOX9 ↔ NKX2-1 cross-context binding finding
are exactly the kind of input that would prioritise such a wet-lab
follow-up.

### 6. Stronger statistical control calibration

**A v1 of the indirect-evidence calibration that would make the
"not_salvageable" verdict statistically rigorous.**

The current calibration used 5 control genes. A v1 with 50–100
random non-target genes (drawn from a curated list of "genes
expressed in fetal lung but not in any SOX2 / NKX2-1 / SOX9
literature claim") would let the audit compute formal selectivity
statistics — Mann-Whitney U for canonical-vs-control rank
distributions, Bonferroni-adjusted thresholds, ROC-style analyses.

This would not change the project's verdict (the v0 control
calibration is qualitatively unambiguous — three controls outrank
all canonicals), but it would convert the verdict from a rank-
inspection finding to a publishable statistical claim.

~ 200–300 LoC stdlib + a curated random-gene list (50 lines of
metadata). No new HTTP if random control genes are chosen from
genes already in the project; otherwise small expansion.

## What this notes file is *not*

- Not a roadmap. None of these are committed to do. They are
  honest sizings of what method would be needed to extend the
  project beyond v0.
- Not a list of blocked work. Each direction has a substrate or
  infrastructure dependency that v0 deliberately deferred.
- Not a recommendation for which to pick next. That is the user's
  decision, informed by what new substrate or wet-lab access
  becomes available.
