# Q3 Evidence Audit — Extended (ENCODE + Cistrome + ReMap)

**Audit run:** 2026-05-03 (UTC)
**Inputs:**
[`metadata/regulator_target_pairs.csv`](../metadata/regulator_target_pairs.csv)
+ [`metadata/external_chip_lookups.csv`](../metadata/external_chip_lookups.csv)
**Output:**
[`metadata/evidence_audit_extended.csv`](../metadata/evidence_audit_extended.csv)
**Script:** [`scripts/gain_evidence_audit_extended.py`](../scripts/gain_evidence_audit_extended.py)
**Design contract:** [`notes/q3_extension_design.md`](q3_extension_design.md)

## Framing correction (the headline of this run)

The ENCODE-only audit ([`notes/evidence_audit.md`](evidence_audit.md))
reported **14 / 18** pairs as `literature_curation_only`. With the
correctly-extended scoping in place, the right phrasing is:

| ENCODE-only audit said | Extended audit says |
|---|---|
| 14 pairs are `literature_curation_only` (no public evidence) | 14 pairs are `unresolved_public_evidence_gap` (ENCODE has no evidence; Cistrome and ReMap not yet checked) |

The extended audit **explicitly does not** claim these pairs have no
public evidence. Until Cistrome and ReMap are looked up — manually,
in v0 — we cannot conclude that.

## Class counts

### ENCODE-only (baseline; same as previous run)

| Class | Count |
|---|---:|
| `direct_human_evidence` | 0 |
| `indirect_human_evidence` | 4 |
| `mouse_supported_only` | 0 |
| `literature_curation_only` | 14 |

### Merged (6-class scheme)

| Class | Count | Pairs |
|---|---:|---|
| `direct_human_lung_evidence` | **0** | — |
| `direct_human_non_lung_evidence` | **4** | SMAD1→ID1, SMAD1→ID2, GLI2→PTCH1, GLI2→GLI1 |
| `indirect_accessibility_support` | 0 | unpopulated by v0 (no motif scanning) |
| `mouse_supported_only` | 0 | — |
| `literature_curation_only` | 0 | — *(no pair has a fully checked external lookup yet)* |
| `unresolved_public_evidence_gap` | **14** | All NKX2-1, SOX2, SOX9, CTNNB1 pairs |

## How many pairs changed class after adding Cistrome / ReMap?

**Zero, *with the v0 lookup file empty*.** Because every (regulator,
source) row in `metadata/external_chip_lookups.csv` is currently
`lookup_required` (URL filled in, counts blank), the merged class for
every pair without a positive ENCODE signal is
`unresolved_public_evidence_gap` — not `literature_curation_only`.

This is a **structural** correction rather than a substantive one. The
architecture for layering Cistrome and ReMap is in place; the counts
still need to be filled in. Once a curator visits the URLs in
`external_chip_lookups.csv` and records counts, the audit can
distinguish between "no public evidence found across all three sources"
(`literature_curation_only`) and "we haven't fully checked"
(`unresolved_public_evidence_gap`).

## Strongest pairs (no change from ENCODE-only)

Same four pairs as the ENCODE-only audit, since Cistrome / ReMap
counts are still uncurated:

| Pair | ENCODE n_human_other | Pathway |
|---|---:|---|
| SMAD1 → ID1 | 3 | BMP effector → canonical target |
| SMAD1 → ID2 | 3 | BMP effector → canonical target |
| GLI2 → PTCH1 | 1 | SHH effector → feedback target |
| GLI2 → GLI1 | 1 | SHH effector → feedback target |

All four remain `direct_human_non_lung_evidence` — none have lung
human ChIP, all four rest on non-lung tissues. The class name in the
extended audit (`direct_human_non_lung_evidence`) is more precise than
the ENCODE-only label (`indirect_human_evidence`); same evidence
substrate, sharper terminology.

## Gaps that remain truly empty across *all checked* public resources

**None can be confirmed yet.** v0's external lookups are uncurated, so
"checked all resources and found nothing" cannot be claimed for any
pair. After a curator fills in the Cistrome / ReMap counts, this
section will list the pairs whose `merged_class = literature_curation_only`
— pairs where ENCODE, Cistrome, and ReMap all report zero
TF ChIP-seq.

The expected subset, to be confirmed: the 7 NKX2-1 pairs are the
highest-likelihood `literature_curation_only` candidates because
NKX2-1 ChIP is genuinely rare across all repositories. SOX2 and SOX9
likely have substantial **non-lung** ChIP in Cistrome and ReMap (SOX2
is heavily ChIP'd in ESC and neural contexts in GEO), so they may
move from `unresolved_public_evidence_gap` to
`direct_human_non_lung_evidence` once curated.

## Are NKX2-1 / SOX2 / SOX9 the largest public evidence holes?

**Pending external lookup.** Initial expectation, to be verified:

- **NKX2-1**: likely remains the largest hole. ENCODE = 0; Cistrome
  and ReMap also expected to be near-zero or zero given the absence
  of NKX2-1 ChIP in the published GEO record. **Strong v0 prediction
  to confirm.**
- **SOX2**: ENCODE = 0; Cistrome and ReMap **likely have substantial
  non-lung counts** (ESC and neural tissues are heavily covered).
  Once curated, SOX2 pairs will probably move to
  `direct_human_non_lung_evidence`. The question becomes whether any
  lung-context SOX2 ChIP exists.
- **SOX9**: ENCODE = 0; Cistrome and ReMap likely have some non-lung
  ChIP (skeletal, cartilage, gut). Status of lung-context coverage
  unknown.
- **CTNNB1**: ENCODE = 0; Cistrome and ReMap likely also low — the
  technical difficulty of β-catenin ChIP is real and not specific to
  ENCODE. Likely stays in `unresolved_public_evidence_gap` or
  promotes to `direct_human_non_lung_evidence` with low counts.

## Important rules carried forward

- **Do not overclaim from one source.** The previous audit's "14
  literature_curation_only" was overclaim from ENCODE alone; this
  extended audit corrects it to "unresolved" pending external lookup.
- **Do not merge human and mouse carelessly.** The classifier keeps
  them separate; mouse evidence promotes a pair to
  `mouse_supported_only`, never to a human class.
- **Do not treat non-lung human evidence as lung evidence.** The
  classes `direct_human_lung_evidence` and `direct_human_non_lung_evidence`
  are distinct and ordered by strength accordingly.
- **Absence of supporting public data ≠ absence of relationship.**
  Every justification line in the CSV avoids language conflating these.

## Reproducing the audit

```sh
python3 scripts/gain_evidence_audit_extended.py
```

Stdlib only. Hits ENCODE live for the 6 regulators × 3 organism /
tissue queries = 18 GETs (~4-6 s with 0.2 s sleep). Reads external
lookups from `metadata/external_chip_lookups.csv`. Prints the side-by-
side ENCODE-only and merged class counts plus the change-from-baseline
count.

## Next step (deferred, not done in this turn)

Manually look up each `(regulator, source)` URL in
`metadata/external_chip_lookups.csv`, record the four counts
(`n_human_total`, `n_human_lung`, `n_mouse_total`, `n_mouse_lung`) and
`lookup_date`, commit the curated CSV, and re-run the audit. That run
will produce the first set of merged classifications that can claim
`literature_curation_only` honestly.

A v0.x option: write a small browser-driven scraper (Selenium /
Playwright) for ReMap and Cistrome v3. Out of scope for v0 because it
requires a non-stdlib dependency and the user's "no broad platform
building" constraint.
