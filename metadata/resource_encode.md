# ENCODE & SCREEN

Two related portals from the ENCODE Project family. ENCODE is the raw-assay
catalog; SCREEN is a curated cCRE registry built on top.

## ENCODE

**Site:** <https://www.encodeproject.org/>
**API help:** <https://www.encodeproject.org/help/rest-api/>

### What it is

The ENCyclopedia Of DNA Elements: ChIP-seq, ATAC-seq, DNase-seq, RNA-seq
and other functional genomics assays across human and mouse tissues, cell
lines, and primary cells. JSON-everywhere REST API; the same URLs the web
app uses are usable as a script.

### What problem it solves

For Gain specifically:
- Find ChIP-seq experiments targeting **NKX2-1, SOX2, SOX9**, or partners
  (FGF10, WNT/BMP/SHH effectors) in lung-relevant biosamples.
- Find chromatin-accessibility (ATAC/DNase) tracks in fetal lung where
  available.

### What it cannot solve

- Not a cell-resolved atlas; bulk and pooled assays dominate. Pair with
  CELLxGENE Census for cell-type context.
- Lung-development-specific TF ChIP-seq coverage is **patchy** — many of
  the TFs we care about have ChIP only in non-lung lines, or only in
  mouse, or not at all. Inventory must capture what is *missing*, not
  pretend everything is there.
- Coordinate systems and assembly versions vary; always check `assembly`.

### Programmatic access

- REST search: `GET https://www.encodeproject.org/search/?...&format=json`
- Filtering verified to work for `assay_title=ChIP-seq`,
  `target.label=NKX2-1`, etc., with operators `!=`, `*`, `gt`, `lt`.
- No auth required for read access.
- **Rate limit: 10 GET/sec per user.** Honor it with backoff.

### Reuse strategy

**Reuse directly via REST.** Do not wrap unless a real consumer exists.
Cache responses locally (on-disk JSON) in `metadata/cache/encode/` to stay
under the rate limit.

---

## SCREEN

**Site:** <https://screen.wenglab.org/>
**Source:** Wenglab (Weng Lab); part of the ENCODE-funded effort.

### What it is

**S**earch **C**andidate c**R**egulatory **E**lements by E**N**CODE: the
curated **cCRE registry** derived from ENCODE assays. Browseable per gene,
per cell type, and per genome region. Versioned (V3-era at last check;
verify at use time).

### What problem it solves

- "What candidate cis-regulatory elements sit near gene X in tissue Y?"
  — without re-deriving from raw ENCODE peaks.
- Bridges ENCODE (raw assays) and a useable element-level annotation.

### What it cannot solve

- Lung-specific cell-type cCREs depend on the underlying ENCODE coverage —
  fetal-lung resolution is limited.
- Not a quantitative effect-size predictor; classification is presence /
  classification, not regulatory-effect inference.

### Programmatic access

- Public web UI at the URL above; **a programmatic API exists** (historically
  GraphQL at `api.wenglab.org`). The exact endpoint moves between SCREEN
  versions — **verify at the moment of use** rather than hardcoding.
- Bulk cCRE files downloadable from the SCREEN site for offline analysis.

### Reuse strategy

**Reuse directly when needed; defer until v1.** SCREEN is the right answer
for the marker-to-regulator linker idea, not the dataset-manifest CLI.

**Reuse priority for Gain v0:** low. **For v1+:** high if marker-to-regulator
or evidence-map MVPs are pursued.
