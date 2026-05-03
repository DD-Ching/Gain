#!/usr/bin/env python3
"""gain evidence-audit-v2 - cross-source audit with peak-level top tier.

Combines three layers per the contract in notes/evidence_model_v2.md:
  - ENCODE TF ChIP-seq (live REST queries)
  - ChIP-Atlas (regulator-level counts from metadata/chipatlas_lookup.csv)
  - Peak intersection results from metadata/peak_intersection_results.csv

Emits metadata/evidence_audit_v2.csv with per-pair classification under
the 6-class v2 hierarchy:
  peak_validated_at_target_locus  >  direct_human_lung_evidence
                                  >  direct_human_non_lung_evidence
                                  >  indirect_accessibility_support  (unpopulated in v2)
                                  >  literature_curation_only
                                  >  unresolved_gap

Stdlib only.
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
DEFAULT_CHIPATLAS = REPO_ROOT / "metadata" / "chipatlas_lookup.csv"
DEFAULT_PEAKS = REPO_ROOT / "metadata" / "peak_intersection_results.csv"
DEFAULT_EXTENDED = REPO_ROOT / "metadata" / "evidence_audit_extended.csv"
DEFAULT_OUT = REPO_ROOT / "metadata" / "evidence_audit_v2.csv"

ENCODE_BASE = "https://www.encodeproject.org/search/"
USER_AGENT = "gain-evidence-audit-v2/0.1 (+https://github.com/DD-Ching/Gain)"

PAIR_FIELDS = ("regulator", "target", "relationship_type")
V2_CLASSES = (
    "peak_validated_at_target_locus",
    "direct_human_lung_evidence",
    "direct_human_non_lung_evidence",
    "indirect_accessibility_support",
    "literature_curation_only",
    "unresolved_gap",
)
OUT_FIELDS = (
    "regulator", "target", "relationship_type",
    "v2_class", "changed_from_extended_audit",
    "encode_n_human_lung", "encode_n_human_other", "encode_n_mouse",
    "chipatlas_n_hg38_total", "chipatlas_n_hg38_lung", "chipatlas_n_hg38_other",
    "peak_intersection_summary", "locus_test_status",
    "justification", "evidence_url",
)


# -------------- ENCODE live queries --------------

def query_encode(params: dict, timeout: float = 15.0) -> int | None:
    url = ENCODE_BASE + "?" + urlencode(params)
    req = urllib.request.Request(
        url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return int(json.load(resp).get("total", 0) or 0)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            try:
                return int(json.load(e).get("total", 0) or 0)
            except Exception:
                return 0
        return None
    except Exception:
        return None


def encode_evidence(regulator: str, sleep: float) -> dict:
    common = {
        "type": "Experiment",
        "assay_title": "TF ChIP-seq",
        "target.label": regulator,
        "format": "json",
        "limit": 1,
    }
    n_lung = query_encode({
        **common,
        "biosample_ontology.term_name": "lung",
        "replicates.library.biosample.donor.organism.scientific_name": "Homo sapiens",
    })
    time.sleep(sleep)
    n_human = query_encode({
        **common,
        "replicates.library.biosample.donor.organism.scientific_name": "Homo sapiens",
    })
    time.sleep(sleep)
    n_mouse = query_encode({
        **common,
        "replicates.library.biosample.donor.organism.scientific_name": "Mus musculus",
    })
    n_other = None
    if n_human is not None and n_lung is not None:
        n_other = max(0, n_human - n_lung)
    return {
        "n_human_lung_chip": n_lung,
        "n_human_other_chip": n_other,
        "n_human_any_chip": n_human,
        "n_mouse_chip": n_mouse,
    }


# -------------- ChIP-Atlas lookup --------------

def load_chipatlas(path: Path) -> dict[str, dict]:
    out: dict[str, dict] = {}
    if not path.exists():
        return out
    with path.open() as f:
        for row in csv.DictReader(f):
            r = (row.get("regulator") or "").strip()
            if not r:
                continue
            def to_int(k: str) -> int:
                v = (row.get(k) or "").strip()
                try:
                    return int(v)
                except ValueError:
                    return 0
            out[r] = {
                "n_hg38_total": to_int("n_hg38_total"),
                "n_hg38_lung": to_int("n_hg38_lung"),
                "n_hg38_other": to_int("n_hg38_other"),
                "n_mm10_total": to_int("n_mm10_total"),
                "n_mm10_lung": to_int("n_mm10_lung"),
            }
    return out


# -------------- Peak intersection lookup --------------

def load_peak_results(path: Path) -> dict[tuple[str, str], dict]:
    out: dict[tuple[str, str], dict] = {}
    if not path.exists():
        return out
    with path.open() as f:
        for row in csv.DictReader(f):
            key = (row["regulator"], row["target"])
            entry = out.setdefault(key, {
                "n_supports": 0, "n_weak": 0, "n_no_support": 0,
                "n_inconclusive": 0, "n_total": 0, "best_url": "",
            })
            interp = (row.get("interpretation") or "").strip()
            entry["n_total"] += 1
            if interp == "supports":
                entry["n_supports"] += 1
            elif interp == "weak_support":
                entry["n_weak"] += 1
            elif interp == "no_locus_support":
                entry["n_no_support"] += 1
            else:
                entry["n_inconclusive"] += 1
            if not entry["best_url"] and row.get("evidence_url"):
                entry["best_url"] = row["evidence_url"]
    return out


def locus_status(per_pair: dict | None) -> tuple[str, str]:
    if not per_pair:
        return "not_tested", "No peak intersection performed for this pair."
    n_s, n_w, n_no, n_t = (per_pair["n_supports"], per_pair["n_weak"],
                          per_pair["n_no_support"], per_pair["n_total"])
    if n_s + n_w > 0:
        return "passed", f"supports={n_s}, weak={n_w}, absent={n_no}, total_experiments={n_t}"
    if n_no > 0:
        return "failed", f"no peaks within +/- 50 kb of TSS in {n_no} of {n_t} experiment(s)"
    return "not_tested", "no usable result rows"


# -------------- Extended audit (for change detection) --------------

def load_extended(path: Path) -> dict[tuple[str, str], str]:
    out: dict[tuple[str, str], str] = {}
    if not path.exists():
        return out
    with path.open() as f:
        for row in csv.DictReader(f):
            out[(row["regulator"], row["target"])] = row.get("merged_class", "")
    return out


# -------------- v2 classifier --------------

def classify_v2(encode: dict, chipatlas: dict, locus_state: str) -> str:
    if locus_state == "passed":
        return "peak_validated_at_target_locus"
    has_lung = (
        (encode.get("n_human_lung_chip") or 0) > 0
        or chipatlas.get("n_hg38_lung", 0) > 0
    )
    if has_lung:
        return "direct_human_lung_evidence"
    has_nonlung = (
        (encode.get("n_human_other_chip") or 0) > 0
        or chipatlas.get("n_hg38_other", 0) > 0
    )
    if has_nonlung:
        return "direct_human_non_lung_evidence"
    # ENCODE checked + ChIP-Atlas checked + nothing found.
    return "literature_curation_only"


def justification(cls: str, regulator: str, target: str,
                  encode: dict, chipatlas: dict,
                  peak_summary: str, locus_state: str) -> str:
    el = encode.get("n_human_lung_chip") or 0
    eo = encode.get("n_human_other_chip") or 0
    cl = chipatlas.get("n_hg38_lung", 0)
    co = chipatlas.get("n_hg38_other", 0)
    ct = chipatlas.get("n_hg38_total", 0)

    if cls == "peak_validated_at_target_locus":
        return (f"Peak intersection result: {peak_summary}. At least one "
                f"ChIP-seq peak overlaps or sits within +/- 50 kb of the "
                f"{target} TSS. Source-level: ENCODE lung={el}, other={eo}; "
                f"ChIP-Atlas lung={cl}, other={co}.")
    if cls == "direct_human_lung_evidence":
        return (f"Lung-context source-level evidence found "
                f"(ENCODE lung={el}, ChIP-Atlas lung={cl}). Locus test "
                f"{locus_state}. Lung-context here means any biosample "
                f"with a 'lung' substring -- INCLUDES lung cancer cell "
                f"lines (e.g. NCI-H441, A549); cancer-vs-primary-tissue "
                f"refinement is a v2.x followup.")
    if cls == "direct_human_non_lung_evidence":
        return (f"Non-lung source-level evidence only "
                f"(ENCODE other={eo}, ChIP-Atlas other={co}; no lung "
                f"hits in either source). Locus test {locus_state}. "
                f"Cross-tissue applicability uncertain.")
    if cls == "indirect_accessibility_support":
        return ("Defined in v2 but not populated; v2 does not implement "
                "motif scanning over lung accessibility data.")
    if cls == "literature_curation_only":
        return (f"All checked sources (ENCODE live + ChIP-Atlas cached) "
                f"report zero TF ChIP-seq for {regulator}. "
                f"Relationship rests on the wet-lab literature; "
                f"absence here is absence of supporting public data, "
                f"not absence of relationship.")
    return f"Unresolved: not all declared sources were checked for {regulator}."


# -------------- Main --------------

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
        prog="gain-evidence-audit-v2",
        description="v2 cross-source audit (ENCODE + ChIP-Atlas + peak intersection).",
    )
    parser.add_argument("--pairs", type=Path, default=DEFAULT_PAIRS)
    parser.add_argument("--chipatlas", type=Path, default=DEFAULT_CHIPATLAS)
    parser.add_argument("--peaks", type=Path, default=DEFAULT_PEAKS)
    parser.add_argument("--extended", type=Path, default=DEFAULT_EXTENDED)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--sleep", type=float, default=0.2)
    args = parser.parse_args(argv)

    try:
        pairs = load_pairs(args.pairs)
    except (FileNotFoundError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    chipatlas = load_chipatlas(args.chipatlas)
    peaks = load_peak_results(args.peaks)
    extended = load_extended(args.extended)

    print(f"loaded {len(pairs)} pairs")
    print(f"  ChIP-Atlas regulators: {len(chipatlas)} "
          f"({sum(1 for r in chipatlas.values() if r['n_hg38_total'] > 0)} with hg38 hits)")
    print(f"  peak intersection (regulator,target) keys: {len(peaks)}")
    print(f"  prior extended-audit rows: {len(extended)}")

    regulators = sorted({row["regulator"] for row in pairs})
    print(f"\n  ENCODE live queries for {len(regulators)} regulator(s)")
    encode_cache: dict[str, dict] = {}
    for i, reg in enumerate(regulators, 1):
        ev = encode_evidence(reg, sleep=args.sleep)
        encode_cache[reg] = ev
        print(f"    [{i}/{len(regulators)}] {reg}: lung={ev['n_human_lung_chip']} "
              f"other={ev['n_human_other_chip']} mouse={ev['n_mouse_chip']}")
        if i < len(regulators):
            time.sleep(args.sleep)

    out_rows: list[dict] = []
    counts: dict[str, int] = {c: 0 for c in V2_CLASSES}
    changed = 0
    for pair in pairs:
        reg, tgt = pair["regulator"], pair["target"]
        ev = encode_cache.get(reg, {})
        ca = chipatlas.get(reg, {})
        pp = peaks.get((reg, tgt))
        loc_state, loc_summary = locus_status(pp)
        cls = classify_v2(ev, ca, loc_state)
        counts[cls] = counts.get(cls, 0) + 1

        prior_class = extended.get((reg, tgt), "")
        # Map prior 6-class extended scheme onto v2 names where they differ.
        # extended -> v2 equivalence:
        #   direct_human_lung_evidence -> direct_human_lung_evidence (same)
        #   direct_human_non_lung_evidence -> direct_human_non_lung_evidence (same)
        #   mouse_supported_only -> direct_human_non_lung_evidence is wrong; treat as different
        #   literature_curation_only -> literature_curation_only (same)
        #   unresolved_public_evidence_gap -> unresolved_gap (same intent, different name)
        #   indirect_accessibility_support -> same
        prior_equiv = {
            "unresolved_public_evidence_gap": "unresolved_gap",
        }.get(prior_class, prior_class)
        change_flag = "yes" if cls != prior_equiv else "no"
        if change_flag == "yes":
            changed += 1

        ev_url = (pp.get("best_url") if pp else "") or \
                 f"https://www.encodeproject.org/search/?type=Experiment&assay_title=TF+ChIP-seq&target.label={reg}&format=json"

        out_rows.append({
            "regulator": reg,
            "target": tgt,
            "relationship_type": pair.get("relationship_type", ""),
            "v2_class": cls,
            "changed_from_extended_audit": change_flag,
            "encode_n_human_lung": ev.get("n_human_lung_chip", ""),
            "encode_n_human_other": ev.get("n_human_other_chip", ""),
            "encode_n_mouse": ev.get("n_mouse_chip", ""),
            "chipatlas_n_hg38_total": ca.get("n_hg38_total", 0),
            "chipatlas_n_hg38_lung": ca.get("n_hg38_lung", 0),
            "chipatlas_n_hg38_other": ca.get("n_hg38_other", 0),
            "peak_intersection_summary": loc_summary,
            "locus_test_status": loc_state,
            "justification": justification(cls, reg, tgt, ev, ca, loc_summary, loc_state),
            "evidence_url": ev_url,
        })

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=OUT_FIELDS)
        w.writeheader()
        for row in out_rows:
            w.writerow(row)

    print(f"\nwrote {args.out.relative_to(REPO_ROOT)}")
    print(f"  generated_at: {datetime.now(timezone.utc).isoformat(timespec='seconds')}")
    print(f"  total pairs:  {len(out_rows)}")
    print(f"\n  v2 class counts:")
    for cls in V2_CLASSES:
        print(f"    {cls}: {counts.get(cls, 0)}")
    print(f"\n  pairs whose class changed vs. extended audit: {changed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
