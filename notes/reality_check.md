# Reality Check

**Date:** 2026-05-03
**Purpose:** explicit separation of *known biology* / *what this repo has
curated* / *what is still unresolved* / *what would count as genuine added
value*. Written before any v2 work to prevent drift into "clean curation
without scientific value."

## What is already known biology

The middle-layer chain Gain studies is essentially textbook material in
mouse and very-late-stage human:

- **NKX2-1 (TTF-1)** is the master regulator of lung epithelial identity.
  Established for ≥30 years. NKX2-1 knockout in mouse → lung agenesis;
  loss-of-function in human → brain-lung-thyroid syndrome.
- **SOX2 marks proximal airway** progenitors; **SOX9 marks distal tip**
  progenitors. The proximal-distal split via SOX2/SOX9 is a textbook fact
  (reviews: Rawlins 2009; Nikolic & Rawlins 2017; Whitsett, Morrisey,
  Hogan groups).
- **FGF10 (mesenchymal) → FGFR2b (distal epithelial)** drives branching
  morphogenesis. Bellusci 1997 and many follow-ups in mouse.
- **Canonical WNT/β-catenin** promotes distal/alveolar fate; non-canonical
  WNT/PCP shapes branching geometry.
- **BMP4** patterns the proximal-distal axis; BMP antagonists (Noggin,
  Gremlin) modulate the dose.
- **SHH** is epithelial → mesenchymal; SHH knockout in mouse causes lung
  agenesis.
- **Adult cell-type endpoints** (basal, secretory, ciliated, neuro-
  endocrine; AT1, AT2; ionocytes) are well-defined in HLCA-class
  references.

**None of this is in dispute.** Anything Gain "discovers" along these
lines is rediscovering decades-old consensus.

## What this repo has only curated or organized

Every artifact built so far is **infrastructure or editorial**, not
discovery:

- `metadata/sources.json` — pointers at public portals; no new data.
- `metadata/manifest.{csv,json,md}` — same data, three formats.
- `metadata/resource_*.md` (six files) — summaries of the portals,
  written from public docs.
- `metadata/switch_hierarchy.csv` — the textbook chain transcribed into
  a 30-row CSV with one-liner evidence summaries from the literature.
- `notes/switch_hierarchy.md` — the same CSV joined against the manifest
  and rendered as Markdown. Visually nice. **Not a discovery.**
- `metadata/verification.json` — live URL probe. Checks reachability,
  nothing else.

The repo has produced **two small factual contributions** that came
out of doing the curation honestly:

1. **The verifier surfaced that NKX2-1, SOX2, and SOX9 have zero TF
   ChIP-seq experiments in ENCODE in any human biosample.** SOX2 has
   exactly one hit, and it is in *C. elegans*. NKX2-1 and SOX9 have
   none anywhere. (Confirmed by direct probes during this review.)
2. **ENCODE has only 6 TF ChIP-seq experiments in lung tissue total
   (5 mouse, 1 human — the human one is CTCF, not a lung-developmental
   TF).** Plus 59 histone ChIP-seq, 5 ATAC-seq, 30 DNase-seq.

These are public-data-availability facts, not biology. But they are
**non-trivial** because they bound what every "marker-to-regulator
linker" or "evidence-map generator" plan can actually accomplish in
the lung-developmental scope using ENCODE alone. They are worth
publishing as such.

## What is still unresolved

The genuinely open questions live one level below the textbook chain.
See `notes/unresolved_questions.md` for three concrete candidates. They
share a common shape:

- *In human (not mouse)*, with what timing, in which intermediate cell
  states, and along what quantitative gradients does the regulatory
  chain actually execute?
- And, where the literature relies on mouse → human extrapolation, what
  does the human public-data evidence actually support?

## What would count as genuine added value

Concrete decision rule for any future Gain artifact:

- **Discovery:** a quantitative claim about human lung developmental
  control logic that is *not* already in the textbook reviews and that
  is *grounded in public data* a third party can re-run.
  Example: "the SOX2/SOX9 dip in He 2022 fetal lung is bimodal at
  pseudoglandular stage (Hartigan's dip p=X) but unimodal at
  canalicular (p=Y), suggesting commitment is still reversible later
  than mouse-derived models predict."
- **Negative-space contribution:** a documented, reproducible
  enumeration of *what public data exists vs. is missing* for a
  specific question, useful enough that other groups change their
  plans. The two ENCODE facts above are an embryonic example.
- **Reproducibility upgrade:** taking a regulator-target claim that is
  in the literature but never coded against public data, writing a
  small script that re-derives the supporting evidence, and either
  confirming or surfacing a gap.

What does **not** count:

- Re-curated lists of papers, ontologies, or gene markers.
- Visualisations of textbook claims.
- "Platform" or "framework" code without a specific question it
  answers.
- Anything that mistakes neat presentation for new knowledge.
