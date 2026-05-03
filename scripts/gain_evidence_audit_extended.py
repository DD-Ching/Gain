#!/usr/bin/env python3
"""gain evidence-audit-extended - cross-resource version of the Q3 audit.

Adds Cistrome and ReMap as parallel evidence layers alongside ENCODE.
ENCODE counts are queried live via REST. Cistrome and ReMap counts are
read from a hand-curatable metadata/external_chip_lookups.csv (because
their programmatic endpoints are not currently reachable from a
stdlib-only client; see notes/q3_extension_design.md).

Outputs metadata/evidence_audit_extended.csv with per-source columns
plus a final merged class drawn from the six-class scheme defined in
notes/q3_extension_design.md.

Stdlib only. No motif scanning. No peak intersection. v0 of the
extension.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PAIRS = REPO_ROOT / "metadata" / "regulator_target_pairs.csv"
DEFAULT_EXTERNAL = REPO_ROOT / "metadata" / "external_chip_lookups.csv"
DEFAULT_OUT = REPO_ROOT / "metadata" / "evidence_audit_extended.csv"

ENCODE_BASE = "https://www.encodeproject.org/search/"
USER_AGENT = "gain-evidence-audit-extended/0.1 (+https://github.com/DD-Ching/Gain)"

PAIR_FIELDS = (
    "regulator", "target", "relationship_type",
    "from_layer", "to_layer", "literature_summary",
)

EXTERNAL_FIELDS = (
    "regulator", "source",
    "n_human_total", "n_human_lung", "n_mouse_total", "n_mouse_lung",
    "lookup_url_human", "lookup_url_mouse", "lookup_date", "notes",
)

OUT_FIELDS = (
    "regulator", "target", "relationship_type",
    "encode_class", "encode_n_human_lung", "encode_n_human_other", "encode_n_mouse",
    "cistrome_n_human_total", "cistrome_n_human_lung", "cistrome_n_mouse_total", "cistrome_n_mouse_lung",
    "cistrome_url", "cistrome_lookup_status",
    "remap_n_human_total", "remap_n_human_lung", "remap_n_mouse_total", "remap_n_mouse_lung",
    "remap_url", "remap_lookup_status",
    "merged_class", "merged_class_changed_from_encode_only", "justification",
)

ENCODE_CLASSES = (
    "direct_human_evidence", "indirect_human_evidence",
    "mouse_supported_only", "literature_curation_only",
)
MERGED_CLASSES = (
    "direct_human_lung_evidence",
    "direct_human_non_lung_evidence",
    "indirect_accessibility_support",
    "mouse_supported_only",
    "literature_curation_only",
    "unresolved_public_evidence_gap",
)


# ---------- ENCODE live queries (mirrors gain_evidence_audit.py) ----------

def query_encode(params: dict, timeout: float = 15.0) -> tuple[int | None, str]:
    url = ENCODE_BASE + "?" + urlencode(params)
    req = urllib.request.Request(
        url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.load(resp)
            return int(data.get("total", 0) or 0), url
    except urllib.error.HTTPError as e:
        if e.code == 404:
            try:
                return int(json.load(e).get("total", 0) or 0), url
            except Exception:
                return 0, url
        return None, url
    except Exception:
        return None, url


def encode_evidence(regulator: str, sleep: float) -> dict:
    common = {
        "type": "Experiment",
        "assay_title": "TF ChIP-seq",
        "target.label": regulator,
        "format": "json",
        "limit": 1,
    }
    n_lung, _ = query_encode({
        **common,
        "biosample_ontology.term_name": "lung",
        "replicates.library.biosample.donor.organism.scientific_name": "Homo sapiens",
    })
    time.sleep(sleep)
    n_human_any, _ = query_encode({
        **common,
        "replicates.library.biosample.donor.organism.scientific_name": "Homo sapiens",
    })
    time.sleep(sleep)
    n_mouse, _ = query_encode({
        **common,
        "replicates.library.biosample.donor.organism.scientific_name": "Mus musculus",
    })
    n_human_other = None
    if n_human_any is not None and n_lung is not None:
        n_human_other = max(0, n_human_any - n_lung)
    return {
        "n_human_lung_chip": n_lung,
        "n_human_any_chip": n_human_any,
        "n_human_other_chip": n_human_other,
        "n_mouse_chip": n_mouse,
    }


# ---------- External lookups (Cistrome / ReMap, hand-curated) ----------

def load_external(path: Path) -> dict[tuple[str, str], dict]:
    """Returns {(regulator, source): row_dict}. Empty/missing → empty dict."""
    if not path.exists():
        return {}
    out: dict[tuple[str, str], dict] = {}
    with path.open() as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            return {}
        missing = [c for c in EXTERNAL_FIELDS if c not in reader.fieldnames]
        if missing:
            print(f"warning: {path.name} missing columns: {missing}", file=sys.stderr)
        for row in reader:
            key = (row.get("regulator", "").strip(), row.get("source", "").strip().lower())
            if not key[0] or not key[1]:
                continue
            out[key] = row
    return out


def parse_int_or_none(value: str) -> int | None:
    if value is None or str(value).strip() == "":
        return None
    try:
        return int(str(value).strip())
    except ValueError:
        return None


def external_status(row: dict) -> str:
    """curated | partial | lookup_required."""
    if not row:
        return "lookup_required"
    counts = [parse_int_or_none(row.get(c)) for c in
              ("n_human_total", "n_human_lung", "n_mouse_total", "n_mouse_lung")]
    if all(c is not None for c in counts):
        return "curated"
    if any(c is not None for c in counts):
        return "partial"
    return "lookup_required"


# ---------- Classifiers ----------

def classify_encode(ev: dict) -> str:
    nl = ev.get("n_human_lung_chip") or 0
    no = ev.get("n_human_other_chip") or 0
    nm = ev.get("n_mouse_chip") or 0
    if nl > 0:
        return "direct_human_evidence"
    if no > 0:
        return "indirect_human_evidence"
    if nm > 0:
        return "mouse_supported_only"
    return "literature_curation_only"


def has_evidence_dim(value: int | None) -> bool:
    return value is not None and value > 0


def classify_merged(encode_ev: dict, ext_rows: dict[str, dict]) -> tuple[str, bool]:
    """Return (merged_class, all_external_sources_fully_curated)."""
    sources = ("cistrome", "remap")
    statuses = {s: external_status(ext_rows.get(s, {})) for s in sources}
    all_curated = all(statuses[s] == "curated" for s in sources)

    cistrome = ext_rows.get("cistrome", {})
    remap = ext_rows.get("remap", {})

    has_human_lung = (
        has_evidence_dim(encode_ev.get("n_human_lung_chip"))
        or has_evidence_dim(parse_int_or_none(cistrome.get("n_human_lung")))
        or has_evidence_dim(parse_int_or_none(remap.get("n_human_lung")))
    )
    if has_human_lung:
        return "direct_human_lung_evidence", all_curated

    def nonlung_human(row: dict) -> int | None:
        total = parse_int_or_none(row.get("n_human_total"))
        lung = parse_int_or_none(row.get("n_human_lung"))
        if total is None:
            return None
        if lung is None:
            return total
        return max(0, total - lung)

    has_human_nonlung = (
        has_evidence_dim(encode_ev.get("n_human_other_chip"))
        or has_evidence_dim(nonlung_human(cistrome))
        or has_evidence_dim(nonlung_human(remap))
    )
    if has_human_nonlung:
        return "direct_human_non_lung_evidence", all_curated

    has_mouse = (
        has_evidence_dim(encode_ev.get("n_mouse_chip"))
        or has_evidence_dim(parse_int_or_none(cistrome.get("n_mouse_total")))
        or has_evidence_dim(parse_int_or_none(remap.get("n_mouse_total")))
    )
    if has_mouse:
        return "mouse_supported_only", all_curated

    # No positive evidence anywhere we checked.
    if all_curated:
        return "literature_curation_only", True
    return "unresolved_public_evidence_gap", False


def justify(merged: str, encode_ev: dict, ext_rows: dict, statuses: dict) -> str:
    nl = encode_ev.get("n_human_lung_chip", 0) or 0
    no = encode_ev.get("n_human_other_chip", 0) or 0
    nm = encode_ev.get("n_mouse_chip", 0) or 0
    s_summary = ", ".join(f"{k}={v}" for k, v in statuses.items())
    if merged == "direct_human_lung_evidence":
        return (f"At least one source reports human lung TF ChIP-seq for the "
                f"regulator. ENCODE: lung={nl}. External lookup status: {s_summary}.")
    if merged == "direct_human_non_lung_evidence":
        return (f"No human lung TF ChIP found in any checked source; human "
                f"non-lung TF ChIP exists. ENCODE: human_other={no}. "
                f"External lookup status: {s_summary}. Cross-tissue applicability uncertain.")
    if merged == "mouse_supported_only":
        return (f"No human TF ChIP in any checked source; mouse TF ChIP exists. "
                f"ENCODE: mouse={nm}. External lookup status: {s_summary}. "
                f"Cross-species transfer caveat applies.")
    if merged == "literature_curation_only":
        return ("All checked sources (ENCODE live, Cistrome curated, ReMap "
                "curated) report zero TF ChIP-seq. Relationship rests on the "
                "wet-lab literature; absence here is absence of supporting "
                "public data, not absence of relationship.")
    return ("ENCODE confirms no relevant TF ChIP-seq, but Cistrome and/or "
            f"ReMap counts are not yet curated (status: {s_summary}). "
            "Manual lookup at the URLs in metadata/external_chip_lookups.csv "
            "is required before any conclusion about absence can be drawn.")


def load_pairs(path: Path) -> list[dict]:
    with path.open() as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError(f"{path}: empty CSV (no header)")
        missing = [c for c in PAIR_FIELDS if c not in reader.fieldnames]
        if missing:
            raise ValueError(f"{path}: missing required columns {missing}")
        rows = list(reader)
    if not rows:
        raise ValueError(f"{path}: no data rows")
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="gain-evidence-audit-extended",
        description="Cross-resource Q3 audit (ENCODE live + Cistrome/ReMap curated).",
    )
    parser.add_argument("--pairs", type=Path, default=DEFAULT_PAIRS,
                        help=f"path to regulator_target_pairs.csv (default: {DEFAULT_PAIRS.relative_to(REPO_ROOT)})")
    parser.add_argument("--external", type=Path, default=DEFAULT_EXTERNAL,
                        help=f"path to external_chip_lookups.csv (default: {DEFAULT_EXTERNAL.relative_to(REPO_ROOT)})")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT,
                        help=f"output CSV (default: {DEFAULT_OUT.relative_to(REPO_ROOT)})")
    parser.add_argument("--sleep", type=float, default=0.2,
                        help="seconds between ENCODE requests (default: 0.2)")
    args = parser.parse_args(argv)

    try:
        pairs = load_pairs(args.pairs)
    except (FileNotFoundError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    external = load_external(args.external)
    if external:
        print(f"loaded {len(external)} external lookup row(s) from {args.external.relative_to(REPO_ROOT)}")
    else:
        print(f"no external lookups found at {args.external} — all Cistrome/ReMap "
              f"cells will be lookup_required")

    regulators = sorted({row["regulator"] for row in pairs})
    print(f"\nauditing {len(pairs)} pair(s) across {len(regulators)} regulator(s)")
    print(f"  regulators: {', '.join(regulators)}\n")

    encode_cache: dict[str, dict] = {}
    for i, reg in enumerate(regulators, 1):
        print(f"  [{i}/{len(regulators)}] ENCODE live for {reg}...")
        encode_cache[reg] = encode_evidence(reg, sleep=args.sleep)
        ev = encode_cache[reg]
        print(f"      human_lung={ev['n_human_lung_chip']}  "
              f"human_other={ev['n_human_other_chip']}  "
              f"mouse={ev['n_mouse_chip']}")
        if i < len(regulators):
            time.sleep(args.sleep)

    out_rows = []
    encode_class_counts: dict[str, int] = {c: 0 for c in ENCODE_CLASSES}
    merged_class_counts: dict[str, int] = {c: 0 for c in MERGED_CLASSES}
    changed = 0

    for pair in pairs:
        reg = pair["regulator"]
        ev = encode_cache.get(reg, {})

        ext_rows = {
            "cistrome": external.get((reg, "cistrome"), {}),
            "remap": external.get((reg, "remap"), {}),
        }
        statuses = {s: external_status(ext_rows[s]) for s in ("cistrome", "remap")}

        enc_class = classify_encode(ev)
        merged, _ = classify_merged(ev, ext_rows)

        # "Changed from encode-only baseline" tracks whether the merged class
        # is in the same evidence-tier as the ENCODE-only class. ENCODE-only
        # uses 4 classes; merged uses 6. We map ENCODE-only -> merged-equivalent
        # and compare.
        encode_only_equiv = {
            "direct_human_evidence": "direct_human_lung_evidence",
            "indirect_human_evidence": "direct_human_non_lung_evidence",
            "mouse_supported_only": "mouse_supported_only",
            "literature_curation_only": "unresolved_public_evidence_gap",  # because v0 hasn't checked external sources
        }[enc_class]
        changed_flag = "yes" if merged != encode_only_equiv else "no"
        if changed_flag == "yes":
            changed += 1

        encode_class_counts[enc_class] += 1
        merged_class_counts[merged] += 1

        out_rows.append({
            "regulator": reg,
            "target": pair["target"],
            "relationship_type": pair["relationship_type"],
            "encode_class": enc_class,
            "encode_n_human_lung": ev.get("n_human_lung_chip", ""),
            "encode_n_human_other": ev.get("n_human_other_chip", ""),
            "encode_n_mouse": ev.get("n_mouse_chip", ""),
            "cistrome_n_human_total": ext_rows["cistrome"].get("n_human_total", ""),
            "cistrome_n_human_lung": ext_rows["cistrome"].get("n_human_lung", ""),
            "cistrome_n_mouse_total": ext_rows["cistrome"].get("n_mouse_total", ""),
            "cistrome_n_mouse_lung": ext_rows["cistrome"].get("n_mouse_lung", ""),
            "cistrome_url": ext_rows["cistrome"].get("lookup_url_human", ""),
            "cistrome_lookup_status": statuses["cistrome"],
            "remap_n_human_total": ext_rows["remap"].get("n_human_total", ""),
            "remap_n_human_lung": ext_rows["remap"].get("n_human_lung", ""),
            "remap_n_mouse_total": ext_rows["remap"].get("n_mouse_total", ""),
            "remap_n_mouse_lung": ext_rows["remap"].get("n_mouse_lung", ""),
            "remap_url": ext_rows["remap"].get("lookup_url_human", ""),
            "remap_lookup_status": statuses["remap"],
            "merged_class": merged,
            "merged_class_changed_from_encode_only": changed_flag,
            "justification": justify(merged, ev, ext_rows, statuses),
        })

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=OUT_FIELDS)
        w.writeheader()
        for row in out_rows:
            w.writerow(row)

    print()
    print(f"wrote {args.out.relative_to(REPO_ROOT)}")
    print(f"  audited at: {datetime.now(timezone.utc).isoformat(timespec='seconds')}")
    print(f"  total pairs: {len(out_rows)}")
    print(f"\n  ENCODE-only class counts:")
    for cls in ENCODE_CLASSES:
        print(f"    {cls}: {encode_class_counts[cls]}")
    print(f"\n  Merged class counts (6-class scheme):")
    for cls in MERGED_CLASSES:
        print(f"    {cls}: {merged_class_counts[cls]}")
    print(f"\n  Pairs whose class changed from ENCODE-only baseline: {changed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
