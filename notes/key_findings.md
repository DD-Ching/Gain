# Key Findings

Concise list of what this repo has genuinely established. Each
finding is reproducible from a script in `scripts/` and a CSV in
`metadata/`. None of these are biological discoveries; they are
evidence-audit findings about the public-data record.

## Substrate-gap findings

- **ENCODE has zero TF ChIP-seq experiments for NKX2-1, SOX2, SOX9,
  or CTNNB1 in any biosample** (verified by `gain_verify.py` +
  `gain_evidence_audit.py`). The "ENCODE absence" is not the same as
  "public-data absence" — but it was the project's first surprise
  and the seed of the chain audit.

- **Public human lung-developmental-context ChIP for the canonical
  middle-layer regulators is a real gap.** The external-source
  search (NCBI GEO + SRA E-utilities, summarised in
  [`notes/nkx21_final_gap.md`](nkx21_final_gap.md)) confirms the
  cancer-line-only / non-lung-only constraint we worked under is
  the actual public-data state — not a ChIP-Atlas snapshot artefact.

## Per-regulator findings

- **NKX2-1 produced the strongest audit outputs** because its
  ChIP-Atlas substrate (21 lung adenocarcinoma + small-cell lung
  cancer experiments) is large enough for proximal + distal +
  histone-supported analyses. SFTPB, SOX2, SOX9 validate proximally
  in cancer ChIP at bed10; SFTPC, SCGB1A1, ABCA3, FOXA2 do not.

- **SFTPC and SCGB1A1 robustly lack proximal NKX2-1 binding** even
  at the relaxed bed05 threshold across 21 cancer cell line ChIP
  experiments — the most surprising single finding of the chain
  audit, given these are the most-cited NKX2-1 textbook targets.
  Both have substantial *distal* peak signal (50–200 kb), suggesting
  if NKX2-1 acts on them in cancer-line context it may do so via
  distal regulatory elements, not proximal promoters.

- **SOX2 and SOX9 hit substrate / context ceilings faster than
  NKX2-1.** SOX2's lung-context substrate is dominated by lung
  squamous cancer + MRC-5 OSKM-reprogramming experiments — neither
  is endogenous epithelial SOX2. SOX9 has zero lung-context
  experiments at all in ChIP-Atlas hg38.

- **Bidirectional cross-context binding at the SOX9 ↔ NKX2-1
  proximal-distal axis loci.** NKX2-1 → SOX9 has 3 cancer-line
  proximal hits (NKX2-1 audit); SOX9 → NKX2-1 has 1 proximal +
  1 nearby at bed05 (SOX9 audit). Cross-context only — not lung-
  developmental — but a small genuine cross-regulator signal.

## Standing candidate outputs

- **5 NKX2-1 chromatin-supported candidate loci** remain the best
  standing biological candidates the project produced. From the
  histone filter pass on cancer-line distal peaks:
  - **FOXA2 chr20:22,716,796** (strongest single locus across the
    audit)
  - FOXA2 chr20:22,390,152
  - SCGB1A1 chr11:62,497,136
  - SCGB1A1 chr11:62,534,332
  - ABCA3 chr16:2,155,403

  These are *candidates* — not validated regulatory elements. They
  are the first list to test if/when primary lung developmental
  NKX2-1 ChIP-seq is published.

## Method-level (negative) findings

- **Bulk fetal lung motif + accessibility at v0 settings is too
  permissive to serve as a reliable indirect evidence tier.** In a
  5-target × 5-control calibration with the SOX2 motif, all 10
  genes cross the categorical positive class. Quantitative
  refinement (motif-capture-rate × cross-donor-consistency) does not
  separate them — three controls outrank all canonical SOX2 targets,
  and TP63 (canonical) sits between two blood-specific controls.

- **The previously-claimed "4 of 4 NKX2-1 indirect rescue" must be
  softened.** It is consistent with both true rescue and method
  permissiveness; the calibration shows method permissiveness is at
  least partly operating, and we cannot currently distinguish the
  two without cell-type-resolved accessibility or per-bp density
  methods that need new data.

- **The indirect layer does discriminate one thing:** extremely
  tissue-restricted (RBC) genes (HBA1, HBB) score clearly below any
  lung-expressed gene. That bar is too low for regulator-target
  validation but is a real (modest) discriminative signal.

## Infrastructure findings

- **Stdlib + sibling-import is enough for substantial bioinformatic
  audits.** Eighteen scripts, no new Python packages, ~ 60 MB of
  cached data (gitignored), full reproducibility from any clean
  checkout with Python ≥ 3.9 and internet access.

- **The 5-class evidence model + peak-intersection + sensitivity
  sweep + distal-candidate tiering + histone-support filter pipeline
  applies uniformly to any TF with primary-tissue ChIP** — and is
  ready to be re-run when such data appears.

## What this repo is *not*

- Not a biological discovery effort. The textbook NKX2-1 → SFTPC,
  SOX2 → TP63, etc. claims rest on functional / promoter-reporter /
  lineage-tracing evidence outside this project's substrate. Those
  claims stand unaltered.
- Not a regulatory-element validator. The 5 standing distal
  candidates are *candidates*; functional validation requires Hi-C /
  promoter-capture / perturbation in primary lung-relevant cells.
- Not a substitute for primary-tissue ChIP. The indirect layer's
  failure to discriminate is a strong argument that ChIP itself —
  in the right substrate — is the missing piece, not a methodological
  workaround.
