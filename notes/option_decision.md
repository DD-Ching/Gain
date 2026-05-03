# Option Decision — Manual Curation vs. Peak-Level Validation

Two options on the table. Each is sized below; the second is recommended.

---

## Option A — Continue the manual curation pass (12 lookup URLs)

**What it produces.** Counts in
`metadata/external_chip_lookups.csv` for every (regulator, source);
the `unresolved_public_evidence_gap` rows resolve to either
`literature_curation_only` or `direct_human_non_lung_evidence`.

**Expected value:** structural completeness of the audit. Lets us state
"checked ENCODE + Cistrome + ReMap; no public ChIP for NKX2-1 anywhere"
as a definitive claim rather than a strong prediction.

**Expected effort:** ~1-2 hours of human-portal time + 30 min of
re-running and re-writing. Not technically hard; just tedious. The
smallest viable shortcut (NKX2-1-only sanity test) is ~5 minutes.

**Expected novelty:** **low.** All concrete predictions are in
`notes/manual_curation_value_check.md`. None are surprising. The audit
already names the gap; the curation just signs it.

**Risk of becoming busywork:** **high.** Twelve point-in-time counts
of repositories that update independently and that we cannot re-fetch
programmatically. The output dates faster than the question requires.

---

## Option B — Peak-level intersection on the 4 `direct_human_non_lung_evidence` pairs

**What it produces.** For the four pairs whose regulator has
non-zero ENCODE TF ChIP-seq (SMAD1→ID1, SMAD1→ID2, GLI2→PTCH1,
GLI2→GLI1), download the peak BED files referenced by the ENCODE
experiment metadata and compute whether any peaks fall within ±50 kb
of the target gene's TSS (hg38). Output: per-pair, per-experiment yes
/ no / nearest-peak-distance. New audit class for pairs whose peaks
do *not* land at the target locus: `non_lung_chip_does_not_support_at_target_locus`.

**Expected value:** **first concrete validation step in the project.**
The Q3 audit said "evidence exists"; this asks "does the evidence
support the canonical pair specifically?" If the answer is yes, the
four pairs become genuinely defensible from public data alone. If
the answer is no, the canonical claim is uncorroborated by available
human ChIP — a real and citable finding.

**Expected effort:** ~150 lines of Python, stdlib only
(`urllib.request` + `gzip` + `csv` + hard-coded gene coordinates for
the 4 targets). 4 ENCODE experiments → ~4-8 BED files (~MB each).
Two ENCODE GETs per experiment for the file metadata, then download.
Maybe 1 hour to write + 5 minutes to run.

**Expected novelty:** **medium.** Each individual pair (SMAD1→ID1
etc.) has been examined in the BMP/SHH literature; whether the
*specific public ENCODE peaks* support the link in human contexts has
likely never been computed in a single citable script.

**Risk of becoming busywork:** **low.** The output is one concrete
yes/no statement per pair. Even a "yes, peaks land near the target"
result strengthens four downstream claims; even a "no, peaks do not
land near the target" result is a non-trivial honest finding.

---

## Comparison

| Criterion | Option A (curation) | Option B (peak intersection) |
|---|---|---|
| Insight per hour | low | medium-high |
| Output type | counts (bookkeeping) | yes/no validations (testable claims) |
| Reproducible from script | partly (URLs only) | fully (script + downloads) |
| Could change the headline | very unlikely | yes, in either direction |
| Stays lightweight | yes (manual but tedious) | yes (~150 LOC stdlib) |
| Uses already-built artifacts | yes (the lookup CSV scaffold) | yes (the 4 indirect pairs from the audit) |
| Risk of busywork | high | low |

---

## Recommendation

**Option B**, with one cheap concession to Option A: do the
**NKX2-1-only sanity check** (5 minutes, two clicks) before locking in
the recommendation, in case the central prediction is wrong. That
single lookup tests whether the rest of the curation is needed at all.

If the NKX2-1 sanity check confirms the prediction (Cistrome and ReMap
near-zero), proceed straight to Option B and skip the rest of Option
A. If the sanity check surprises us (NKX2-1 with substantial counts
somewhere), reconsider — but that outcome is also a finding worth
reporting in its own right.

**Why Option B over Option A:**

1. Option B produces a **testable scientific claim** ("the SMAD1→ID1
   relationship is / is not supported by ENCODE peaks at the ID1
   locus") rather than a bookkeeping statement.
2. Option B is **fully scripted** and re-runnable; Option A's outputs
   age the moment the underlying portals re-release.
3. Option B works on **the only pairs in the audit that have any
   evidence to validate**; it is the natural next step from
   `direct_human_non_lung_evidence`.
4. Option B respects the user's rule: *"the next step that most
   increases real insight per unit effort."* Curation increases
   completeness, not insight.
5. The headline risk (NKX2-1 / SOX2 / SOX9 are the largest holes) is
   robust across all three sources because the gap reflects an absence
   of *upstream depositions*, not an absence of *aggregation*.

**Option B in one sentence:** turn four `direct_human_non_lung_evidence`
labels into either four validated regulator-target relationships or
four falsified canonical claims, using publicly available ENCODE peak
files and stdlib Python — same access surface as the audit, materially
sharper conclusion.
