# NKX2-1 Locus Audit — Results

**Run:** 2026-05-03 (UTC)
**Inputs:** 21 NKX2-1 hg38 ChIP-seq experiments from ChIP-Atlas (bed10
peak files; q < 10⁻¹⁰)
**Targets:** SFTPC, SFTPB, SCGB1A1, ABCA3, SOX2, SOX9, FOXA2 (hg38
TSS, Ensembl)
**Output:** [`metadata/nkx21_peak_audit.csv`](../metadata/nkx21_peak_audit.csv)
**Script:** [`scripts/gain_nkx21_audit.py`](../scripts/gain_nkx21_audit.py)
**Design contract:** [`notes/nkx21_audit_design.md`](nkx21_audit_design.md)

## The deliverable answers

**How many NKX2-1 target pairs are truly locus-supported (in non-cancer
lung context)?**

> **0 of 7.** Class `peak_validated_in_lung_context` is structurally
> unreachable in v0 — all 21 NKX2-1 hg38 ChIP-seq experiments in
> ChIP-Atlas are in lung cancer cell lines (small cell lung cancer × 11,
> lung adenocarcinoma lines × 10: A549, NCI-H441, NCI-H3122, NCI-H1819,
> NCI-H2087). **Zero non-cancer / primary / fetal NKX2-1 ChIP exists
> in any major public repository.**

**How many pairs are supported only in cancer lung context?**

> **3 of 7.** SFTPB, SOX2, SOX9 land in `peak_validated_in_cancer_lung_context_only`.
> Cancer-line ChIP shows NKX2-1 peaks within 5 kb of these target TSSs
> in multiple experiments (SFTPB: 7/21; SOX2: 3/21; SOX9: 3/21).

**Does NKX2-1 still look like the strongest next bridge from textbook
canon to public-data validation?**

> **Less than expected.** Three of seven canonical pairs validate even
> at the cancer-line locus level; **four of seven do not have strong
> locus support even in cancer lines**, including the most-cited
> textbook NKX2-1 targets — SFTPC (the canonical alveolar surfactant),
> SCGB1A1 (CC10/CCSP, the canonical airway secretory marker), ABCA3
> (alveolar lipid transporter), and FOXA2 (cooperative TF). Either
> the textbook claims rest more on mouse genetics + correlation than
> public human ChIP, the cancer-line context misses these specific
> binding events, or the bed10 threshold is too stringent. NKX2-1 is
> still the right place to bridge from canon to data, but the audit
> shows the bridge is incomplete in human public data, not just
> "lung context exists."

## Per-pair detail

For each pair, columns:
- `Strong`: experiments with NKX2-1 peak within 5 kb of TSS
- `Nearby`: peaks within 5–50 kb of TSS but not within 5 kb
- `No_local`: zero peaks within ± 50 kb

| Pair | Strong / 21 | Nearby | No_local | Class |
|---|---:|---:|---:|---|
| NKX2-1 → **SFTPB** | **7** | 12 | 2 | `peak_validated_in_cancer_lung_context_only` |
| NKX2-1 → **SOX2** | 3 | 2 | 16 | `peak_validated_in_cancer_lung_context_only` |
| NKX2-1 → **SOX9** | 3 | 2 | 16 | `peak_validated_in_cancer_lung_context_only` |
| NKX2-1 → SFTPC | 0 | 3 | 18 | `lung_context_source_only` |
| NKX2-1 → SCGB1A1 | 0 | 5 | 16 | `lung_context_source_only` |
| NKX2-1 → ABCA3 | 0 | 4 | 17 | `lung_context_source_only` |
| NKX2-1 → FOXA2 | 0 | 3 | 18 | `lung_context_source_only` |

## Class distribution

| Class | Count |
|---|---:|
| `peak_validated_in_lung_context` | **0** |
| `peak_validated_in_cancer_lung_context_only` | **3** |
| `lung_context_source_only` | **4** |
| `no_locus_support` | 0 |
| `unresolved_due_to_context` | 0 |

## What is genuinely surprising

The pre-implementation prediction (in `notes/nkx21_audit_design.md`)
guessed Outcome 1 (most pairs validate in cancer) as the safest
prediction and Outcome 2 (some pairs fail in cancer) as the most
research-direction-changing. **The actual result is Outcome 2.**

The four `lung_context_source_only` pairs are the most cited
NKX2-1 target relationships in the lung biology literature:

- **NKX2-1 → SFTPC.** The textbook reference for NKX2-1 direct
  regulation. Bohinski et al. 1994 mapped a TTF-1 binding site in
  the proximal SFTPC promoter. Yet in 21 NKX2-1 ChIP experiments —
  including A549 and NCI-H441 lines that express SFTPC at varying
  levels — **zero have a peak within 5 kb of the SFTPC TSS at
  q < 10⁻¹⁰**. Three experiments show peaks 5–50 kb away.
- **NKX2-1 → SCGB1A1.** Same picture (0 strong, 5 nearby, 16 no
  local). The canonical airway secretory marker.
- **NKX2-1 → ABCA3.** 0 / 4 / 17. Alveolar lipid transporter.
- **NKX2-1 → FOXA2.** 0 / 3 / 18. Cooperative TF.

Three pairs *do* validate at this strict cancer-line threshold:

- **NKX2-1 → SFTPB.** 7 of 21 (33%). Strongest result in the audit.
- **NKX2-1 → SOX2.** 3 of 21 (14%). Within-chain regulator.
- **NKX2-1 → SOX9.** 3 of 21 (14%). Within-chain regulator.

The within-chain regulatory pairs (SOX2, SOX9) and the surfactant B
pair validate; the surfactant C / CC10 / lipid-transporter pairs do
not. There may be a real biological pattern here — or a technical
threshold artefact.

## Caveats — read these before drawing conclusions

1. **Cancer-line ChIP is not developmental ChIP.** The 21 experiments
   are NKX2-1+ lung adenocarcinoma and small-cell lung cancer lines,
   which deploy NKX2-1 as part of an oncogenic program. Binding sites
   may be amplified, suppressed, or shifted relative to developmental
   alveolar / airway cells.
2. **bed10 (q < 10⁻¹⁰) is a stringent threshold.** ChIP-Atlas also
   publishes bed05 (q < 10⁻⁵) and bed20 (q < 10⁻²⁰). At bed05, more
   moderate-strength peaks would surface; some `lung_context_source_only`
   pairs might promote. Re-running at bed05 is a v1 step worth
   considering — but the bed05 files for some experiments are 5–8 MB
   each (~ 100,000+ peaks per experiment), and the false-positive rate
   rises proportionally.
3. **The "strong" cutoff (5 kb of TSS) is a defensible default but not
   universal.** Some NKX2-1 sites are 5–20 kb upstream (the SFTPC
   TTF-1 element is in the proximal promoter, but many NKX2-1
   regulatory elements are distal enhancers).
4. **Peak detection ≠ regulatory function.** A peak at a target's
   locus is necessary but not sufficient for direct regulation. The
   converse is also true: absence of a peak at a stringent threshold
   does not preclude regulatory binding at lower stringency.
5. **Antibody bias.** 13 of 21 experiments use the Bethyl Laboratories
   A300-BL4000 antibody. Antibody-specific epitope effects could
   systematically shift binding profiles.
6. **NKX2-1 expression varies across the cell lines.** Lines that
   under-express NKX2-1 (versus AT2 cells) will produce weaker ChIP
   signals overall, which can move strong peaks into the "nearby"
   bin. Per-experiment normalisation is out of scope for v0.

## What changes the recommended research direction

The audit reframes the gap. Before today, the gap was:

> "No public NKX2-1 ChIP exists in lung-developmental context."

After today, the gap is sharper:

> "Lung-context NKX2-1 ChIP exists, but only in cancer cell lines.
> Even in those cell lines, four of the seven most cited textbook
> NKX2-1 targets — including SFTPC, SCGB1A1, and ABCA3 — lack
> strong proximal-promoter peaks at the standard high-confidence
> threshold."

That second framing is more actionable. Three follow-up moves are
plausible:

- **Re-run at bed05** (q < 10⁻⁵, more permissive) on the same 21
  experiments. If the four failing pairs gain strong support,
  threshold was the issue. If they still fail, the gap is
  substantive.
- **Look for primary lung tissue NKX2-1 ChIP outside ChIP-Atlas.**
  Recent papers (e.g., AT2-cell-specific ChIP-seq from Treutlein /
  Morrisey / Whitsett groups, post-2022) may not yet be ingested by
  ChIP-Atlas. A targeted PubMed + GEO search with explicit accession
  capture would resolve this.
- **Treat the 4 failing pairs as candidates for re-examination.** The
  textbook claim that NKX2-1 directly regulates SFTPC's proximal
  promoter may rest more heavily on classical promoter-reporter
  assays (Bohinski 1994 era) than on genome-wide binding evidence.
  This is a small but real literature-vs-data gap.

## Reproducing this audit

```sh
python3 scripts/gain_nkx21_audit.py
```

Stdlib only. 21 BED downloads from ChIP-Atlas (~ 25 MB total at
bed10), ~ 0.3 s sleep between, total runtime ~ 30–60 s.

## What v0 of this audit deliberately does *not* do

- No bed05 / bed20 sweep across thresholds.
- No primary-tissue ChIP search outside ChIP-Atlas.
- No expansion to other regulators (SOX2, SOX9, CTNNB1, SMAD1, GLI2)
  — per the user's "do not expand beyond NKX2-1" constraint.
- No motif scanning.
- No per-cell-line meta-analysis (peak count normalisation,
  antibody-of-origin grouping).

These are all candidates for a v1 of the NKX2-1 audit if the headline
finding (4/7 textbook pairs lack strong cancer-line support) survives
peer-style scrutiny.
