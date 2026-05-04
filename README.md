# Gain

> **Public-data evidence audit + substrate-gap diagnosis for human
> lung developmental regulators.** Stdlib-only. v0 cycle complete.

A reproducible audit of the middle-layer control logic of human lung
development:

```
NKX2-1  ->  SOX2 / SOX9  ->  FGF10 / WNT / BMP / SHH  ->  airway / alveolar programs
```

The goal is not to derive new biology — the textbook claims for
NKX2-1 → SFTPC, SOX2 → TP63, etc. rest on functional / promoter-
reporter / lineage-tracing evidence outside this project's scope.
The goal is to **make those claims queryable, evidence-grounded, and
reproducible against existing public ChIP / accessibility data**, and
to surface honestly where the public-data record does or does not
support them.

## Project status

**v0 cycle complete (2026-05-04). Frozen as an evidence-audit /
substrate-gap repo.** The audit machinery is mature; the constraint
reached is the public-data ecosystem. Future scientific questions
move to a separate repository; see
[`notes/next_project_decision.md`](notes/next_project_decision.md).

### Start here (in order)

1. **[`notes/project_summary.md`](notes/project_summary.md)** — full
   narrative for a new researcher (project goal, what was built, what
   was learned per regulator, why the chain stopped, why the
   indirect-evidence layer was tested + failed, standing outputs).
2. **[`notes/key_findings.md`](notes/key_findings.md)** — concise
   bullet list of what is genuinely established.
3. **[`notes/limitations_and_next_methods.md`](notes/limitations_and_next_methods.md)**
   — six method-level future directions sized honestly.
4. **[`notes/next_project_decision.md`](notes/next_project_decision.md)**
   — decision memo for the successor project (cell-type ATAC vs
   CELLxGENE Census), with a recommended pick.

## What this repo establishes

1. **A real public-data substrate gap.** No primary human lung
   tissue ChIP-seq exists for NKX2-1, SOX2, SOX9, CTNNB1, SMAD1, or
   GLI2 in ChIP-Atlas hg38 — confirmed via NCBI GEO + SRA E-utilities
   external search. The "ENCODE absence" we initially observed
   widens to a "primary-tissue-substrate absence" across the chain's
   regulators.
2. **Per-regulator audits** of NKX2-1, SOX2, SOX9 against the
   available cancer / non-lung / reprogramming substrate, with
   sensitivity sweeps and distal-candidate analyses where the
   substrate supported them.
3. **5 NKX2-1 chromatin-supported standing distal candidates**
   (FOXA2 ×2, SCGB1A1 ×2, ABCA3 ×1) — the project's positive
   biological output. Candidates not validated regulatory elements;
   listed in `notes/project_summary.md`.
4. **A negative finding about indirect-evidence methods.** Bulk
   fetal lung motif + accessibility at v0 settings (relative_score
   ≥ 0.85 + ENCODE 13 fetal lung DNase + per-pair categorical
   classifier) cannot discriminate canonical SOX2 targets from
   housekeeping / blood-specific / lung-wrong-program controls. A
   paired control calibration showed all 5 SOX2 canonicals and all
   5 controls cross the same positive class; a quantitative
   refinement on the existing counts produced the same verdict.
5. **A reusable audit framework.** 18 stdlib-only scripts (no Python
   packages added). Five-class evidence model, peak-intersection
   logic, sensitivity sweep, distal-candidate tiering, histone-
   support filter, motif + accessibility scan, quantitative
   refinement. **All ready to apply uniformly to any TF whose
   primary-tissue ChIP becomes available.**

## What this repo is not

- Not a biological discovery effort. The textbook claims stand
  unaltered.
- Not a regulatory-element validator — the 5 standing candidates
  are *candidates*; functional validation requires Hi-C / 4C /
  perturbation in primary lung-relevant cells.
- Not a substitute for primary-tissue ChIP. The indirect-evidence
  layer's failure to discriminate is a strong argument that ChIP
  itself, in the right substrate, is the missing piece — not a
  methodological workaround.

## Quickstart

Requires only Python 3.9+ and internet access.

The three foundation CLIs:

```sh
python3 scripts/gain_manifest.py          # build the resource manifest
python3 scripts/gain_verify.py            # probe source URLs live
python3 scripts/gain_switch_explorer.py   # render the regulatory chain report
```

The Q3 evidence audit family (chain audit's first concrete answer):

```sh
python3 scripts/gain_evidence_audit.py    # ENCODE-only first pass
python3 scripts/gain_evidence_audit_v2.py # ChIP-Atlas integrated, six-class
```

The per-regulator chain audit cycle (NKX2-1 / SOX2 / SOX9):

```sh
python3 scripts/gain_nkx21_audit.py                # 21 cancer ChIPs x 7 targets
python3 scripts/gain_nkx21_audit_sensitivity.py    # bed10 + bed05 sweep
python3 scripts/gain_nkx21_distal_candidates.py    # candidate-locus tiering
python3 scripts/gain_sox2_audit.py                 # 27 lung-context (cancer + MRC-5)
python3 scripts/gain_sox2_audit_sensitivity.py
python3 scripts/gain_sox9_audit.py                 # 27 non-lung (no lung substrate)
python3 scripts/gain_sox9_audit_sensitivity.py
```

The indirect-evidence (motif + accessibility) cycle:

```sh
python3 scripts/gain_motif_accessibility_audit.py            # NKX2-1 motif x lung
python3 scripts/gain_sox2_motif_accessibility_audit.py       # SOX2 motif x lung
python3 scripts/gain_motif_accessibility_control_audit.py    # control panel
python3 scripts/gain_motif_accessibility_quant.py            # quant refinement (no HTTP)
```

Each script supports `--help`. All are stdlib-only and sibling-
importable. The companion CSVs and notes for each audit live in
`metadata/` and `notes/` respectively.

## Repository layout

```
notes/      planning notes, audit designs, audit reports, project summary
metadata/   curated inputs (sources.json, switch_hierarchy.csv, regulator_target_pairs.csv,
            chipatlas_lookup.csv) + generated outputs (manifest, verification, audit CSVs)
            + cache/ (gitignored: ChIP-Atlas TSVs, JASPAR PFMs)
scripts/    18 stdlib-only audit scripts
```

## Standing biological output

The project's **five standing chromatin-supported distal candidate
loci** for NKX2-1 (from cancer-line ChIP + ENCODE lung histone
filter):

| Locus | Target | Distance to TSS | Why |
|---|---|---:|---|
| **chr20:22,716,796–22,717,928** | **FOXA2** | −131,907 bp | strongest single locus; 7 NKX2-1 ChIPs at bed10, H3K27ac + H3K4me1 in adult lung tissue |
| chr20:22,463,535–22,464,025 | FOXA2 | +121,675 bp | second-strongest FOXA2 candidate |
| chr11:62,497,136–62,497,594 | SCGB1A1 | +92,262 bp | canonical airway histone marks present |
| chr11:62,534,332–62,534,655 | SCGB1A1 | +129,390 bp | distant but consistently supported |
| chr16:2,155,403–2,155,753 | ABCA3 | +185,171 bp | sole ABCA3 candidate retained after histone filter |

These are *candidates*. Every one of the project's anti-overclaim
caveats applies. They become testable when primary lung
developmental ChIP-seq becomes available, when Hi-C / promoter-
capture data is brought into scope, or as part of a perturbation
experiment.

## Constraints carried throughout the project

- **No generic framework if a project-specific script will do.**
- **No dependency unless it clearly reduces total complexity.**
- **No "future architecture" section longer than the actual working
  code.**

These are why every script is stdlib-only and why scripts share
helpers via sibling import rather than a packaged framework.

## License

To be added. Current contents are curation + small stdlib scripts;
treat them as the moral equivalent of public-domain inventory work
until a license file lands.
