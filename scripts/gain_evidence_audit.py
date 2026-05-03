#!/usr/bin/env python3
"""gain evidence-audit - classify regulator-target pairs by ENCODE evidence class.

Reads:
  metadata/regulator_target_pairs.csv  (literature-curated audit input)

Writes:
  metadata/evidence_audit.csv          (per-pair evidence class + counts + URLs)

For each unique regulator in the input, issues three ENCODE search queries
(human lung TF ChIP, human any-tissue TF ChIP, mouse any-tissue TF ChIP),
caches the counts, and applies the class precedence defined in
notes/q3_design.md:

  direct_human_evidence > indirect_human_evidence > mouse_supported_only
  > literature_curation_only

Stdlib only. No motif scanning, no peak intersection — v0 only checks
regulator-level evidence existence. Per-(regulator, target) peak
intersection is v1+ work.
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
DEFAULT_OUT = REPO_ROOT / "metadata" / "evidence_audit.csv"

ENCODE_BASE = "https://www.encodeproject.org/search/"
USER_AGENT = "gain-evidence-audit/0.1 (+https://github.com/DD-Ching/Gain)"

PAIR_FIELDS = (
    "regulator", "target", "relationship_type",
    "from_layer", "to_layer", "literature_summary",
)

OUT_FIELDS = (
    "regulator", "target", "relationship_type",
    "evidence_class", "species_with_evidence", "source_type",
    "tissue_relevance",
    "n_human_lung_chip", "n_human_other_chip", "n_mouse_chip",
    "justification", "evidence_url",
)

CLASSES = (
    "direct_human_evidence",
    "indirect_human_evidence",
    "mouse_supported_only",
    "literature_curation_only",
    # accessibility_only_support is defined in notes/q3_design.md but not
    # populated by v0 (no motif scanning).
)


def query_encode(params: dict, timeout: float = 15.0) -> tuple[int | None, str]:
    """Issue a GET against ENCODE search; return (total_count_or_none, url).

    ENCODE returns HTTP 404 with a JSON body when a search has zero results.
    We treat that as count=0, not as an error (per q3_design.md edge cases).
    """
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
                body = json.load(e)
                return int(body.get("total", 0) or 0), url
            except Exception:
                return 0, url
        return None, url
    except Exception:
        return None, url


def regulator_evidence(regulator: str, sleep: float) -> dict:
    """Three counts (+ URLs) per regulator: human lung, human any, mouse any."""
    common = {
        "type": "Experiment",
        "assay_title": "TF ChIP-seq",
        "target.label": regulator,
        "format": "json",
        "limit": 1,
    }

    n_lung, url_lung = query_encode({
        **common,
        "biosample_ontology.term_name": "lung",
        "replicates.library.biosample.donor.organism.scientific_name": "Homo sapiens",
    })
    time.sleep(sleep)

    n_human_any, url_human = query_encode({
        **common,
        "replicates.library.biosample.donor.organism.scientific_name": "Homo sapiens",
    })
    time.sleep(sleep)

    n_mouse, url_mouse = query_encode({
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
        "url_lung": url_lung,
        "url_human": url_human,
        "url_mouse": url_mouse,
    }


def classify(ev: dict) -> tuple[str, str, str, str, str]:
    """Return (evidence_class, species_with_evidence, source_type,
    tissue_relevance, evidence_url)."""
    if ev["n_human_lung_chip"] and ev["n_human_lung_chip"] > 0:
        return ("direct_human_evidence", "human", "TF_ChIP-seq",
                "lung", ev["url_lung"])
    if ev["n_human_other_chip"] and ev["n_human_other_chip"] > 0:
        return ("indirect_human_evidence", "human", "TF_ChIP-seq",
                "non-lung", ev["url_human"])
    if ev["n_mouse_chip"] and ev["n_mouse_chip"] > 0:
        return ("mouse_supported_only", "mouse", "TF_ChIP-seq",
                "n/a (cross-species)", ev["url_mouse"])
    return ("literature_curation_only", "none", "none", "n/a", "n/a")


def justify(cls: str, regulator: str, ev: dict) -> str:
    nl = ev["n_human_lung_chip"]
    nh = ev["n_human_any_chip"]
    no = ev["n_human_other_chip"]
    nm = ev["n_mouse_chip"]
    if cls == "direct_human_evidence":
        return (f"{nl} human TF ChIP-seq experiment(s) for {regulator} in lung "
                f"biosamples found in ENCODE; classification reflects "
                f"availability, not validated peak intersection at this target.")
    if cls == "indirect_human_evidence":
        return (f"No human lung TF ChIP for {regulator}; {no} human TF ChIP "
                f"experiment(s) in non-lung biosamples found ({nh} total human "
                f"experiments). Cross-tissue applicability uncertain.")
    if cls == "mouse_supported_only":
        return (f"No human TF ChIP for {regulator}; {nm} mouse TF ChIP "
                f"experiment(s) found. Cross-species transfer caveat applies.")
    return (f"No ENCODE TF ChIP-seq found for {regulator} in any species or "
            f"tissue. Relationship is literature-curated; absence here is "
            f"absence of supporting public data, not absence of relationship.")


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
        prog="gain-evidence-audit",
        description="Classify regulator-target pairs by ENCODE evidence class.",
    )
    parser.add_argument("--pairs", type=Path, default=DEFAULT_PAIRS,
                        help=f"path to regulator_target_pairs.csv (default: {DEFAULT_PAIRS.relative_to(REPO_ROOT)})")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT,
                        help=f"output CSV (default: {DEFAULT_OUT.relative_to(REPO_ROOT)})")
    parser.add_argument("--sleep", type=float, default=0.2,
                        help="seconds to sleep between ENCODE requests (default: 0.2)")
    args = parser.parse_args(argv)

    try:
        pairs = load_pairs(args.pairs)
    except (FileNotFoundError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    regulators = sorted({row["regulator"] for row in pairs})
    print(f"auditing {len(pairs)} pair(s) across {len(regulators)} regulator(s)")
    print(f"  regulators: {', '.join(regulators)}")
    print()

    cache: dict[str, dict] = {}
    for i, reg in enumerate(regulators, 1):
        print(f"  [{i}/{len(regulators)}] querying ENCODE for {reg}...")
        cache[reg] = regulator_evidence(reg, sleep=args.sleep)
        ev = cache[reg]
        print(f"      human_lung={ev['n_human_lung_chip']}  "
              f"human_any={ev['n_human_any_chip']}  "
              f"mouse={ev['n_mouse_chip']}")
        if i < len(regulators):
            time.sleep(args.sleep)

    out_rows = []
    class_counts: dict[str, int] = {c: 0 for c in CLASSES}
    error_rows = 0
    for row in pairs:
        reg = row["regulator"]
        ev = cache.get(reg, {})
        if any(ev.get(k) is None for k in (
                "n_human_lung_chip", "n_human_any_chip", "n_mouse_chip")):
            cls = "error"
            species = "n/a"
            stype = "n/a"
            tissue = "n/a"
            url = ev.get("url_human", "n/a")
            justification = (f"Network or HTTP error querying ENCODE for "
                             f"{reg}; counts unavailable. Re-run the audit.")
            error_rows += 1
        else:
            cls, species, stype, tissue, url = classify(ev)
            class_counts[cls] = class_counts.get(cls, 0) + 1
            justification = justify(cls, reg, ev)

        out_rows.append({
            "regulator": reg,
            "target": row["target"],
            "relationship_type": row["relationship_type"],
            "evidence_class": cls,
            "species_with_evidence": species,
            "source_type": stype,
            "tissue_relevance": tissue,
            "n_human_lung_chip": ev.get("n_human_lung_chip", ""),
            "n_human_other_chip": ev.get("n_human_other_chip", ""),
            "n_mouse_chip": ev.get("n_mouse_chip", ""),
            "justification": justification,
            "evidence_url": url,
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
    for cls in CLASSES:
        print(f"    {cls}: {class_counts.get(cls, 0)}")
    if error_rows:
        print(f"    error: {error_rows}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
