#!/usr/bin/env python3
"""gain nkx21-histone-filter - histone-support filter on the 11 strong NKX2-1
distal candidates per notes/nkx21_histone_filter_design.md.

Reads metadata/nkx21_distal_candidates.csv, restricts to strong tier (11
candidates), queries ENCODE lung Histone ChIP-seq, classifies experiments
by biosample (human fetal / human adult / mouse / cancer / unclear) and
mark (active / repressive / other), downloads the active-mark human BED
files, intersects with each candidate locus, applies the four-tier
output system.

Stdlib only. Sibling-imports EXPERIMENTS/TARGETS for completeness but does
not require the NKX2-1 ChIP data (we only need the precomputed candidate
loci).
"""
from __future__ import annotations

import argparse
import csv
import gzip
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# Sibling import (not strictly needed but enforces module sanity)
sys.path.insert(0, str(Path(__file__).parent))
from gain_nkx21_audit import EXPERIMENTS as _NKX_EXPERIMENTS  # noqa: E402,F401

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CANDIDATES = REPO_ROOT / "metadata" / "nkx21_distal_candidates.csv"
DEFAULT_OUT = REPO_ROOT / "metadata" / "nkx21_histone_filtered_candidates.csv"

ENCODE_BASE = "https://www.encodeproject.org"
USER_AGENT = "gain-nkx21-histone-filter/0.1 (+https://github.com/DD-Ching/Gain)"

ACTIVE_MARKS = {"H3K27ac", "H3K4me1", "H3K4me3", "H3K9ac", "H3K4me2"}
REPRESSIVE_MARKS = {"H3K27me3", "H3K9me3"}
GENE_BODY_MARKS = {"H3K36me3"}

UPDATED_TIERS = (
    "strong_distal_candidate_with_chromatin_support",
    "strong_distal_candidate_without_chromatin_support",
    "downgraded_candidate",
    "unresolved_due_to_context_mismatch",
)

OUT_FIELDS = (
    "target", "candidate_locus", "locus_chrom", "locus_start", "locus_end",
    "distance_to_tss_bp", "supporting_nkx21_experiments",
    "n_overlap_h3k27ac_fetal", "n_overlap_h3k27ac_adult",
    "n_overlap_h3k4me1_fetal", "n_overlap_h3k4me1_adult",
    "n_overlap_h3k4me3_fetal", "n_overlap_h3k4me3_adult",
    "n_overlap_h3k9ac_fetal", "n_overlap_h3k9ac_adult",
    "n_overlap_h3k4me2_fetal", "n_overlap_h3k4me2_adult",
    "n_overlap_repressive_fetal", "n_overlap_repressive_adult",
    "n_overlap_active_mouse",
    "histone_evidence_summary", "histone_source_context",
    "updated_tier", "justification",
)


# ----------- ENCODE access -----------

def http_get_json(url: str, timeout: float = 20.0) -> dict | None:
    req = urllib.request.Request(
        url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            try:
                return json.load(e)
            except Exception:
                return None
        return None
    except Exception:
        return None


def http_get_bytes(url: str, timeout: float = 90.0) -> bytes | None:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except Exception as e:
        print(f"  download error {url}: {e}", file=sys.stderr)
        return None


def parse_bed(blob: bytes) -> list[tuple[str, int, int]]:
    """Parse a BED file. Auto-decompresses gzip (ENCODE serves .bed.gz)."""
    data = blob
    if blob[:2] == b"\x1f\x8b":  # gzip magic
        data = gzip.decompress(blob)
    out: list[tuple[str, int, int]] = []
    for line in data.decode("utf-8", errors="replace").splitlines():
        if not line or line.startswith("#") or line.startswith("track"):
            continue
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        try:
            out.append((parts[0], int(parts[1]), int(parts[2])))
        except ValueError:
            continue
    return out


def best_peak_url(experiment_id: str) -> tuple[str | None, str]:
    """Pick a representative narrowPeak/replicated-peaks BED URL."""
    data = http_get_json(f"{ENCODE_BASE}/experiments/{experiment_id}/?format=json")
    if not data:
        return None, "no metadata"
    files = [
        f for f in data.get("files", [])
        if f.get("file_format") == "bed"
        and f.get("assembly") == "GRCh38"
        and f.get("status") in ("released", None)
    ]
    if not files:
        return None, "no GRCh38 BED files"

    def rank(f: dict) -> int:
        ot = (f.get("output_type") or "").lower()
        ft = (f.get("file_type") or "").lower()
        if "replicated peaks" in ot:
            return 0
        if "stable peaks" in ot:
            return 1
        if "pseudoreplicated peaks" in ot:
            return 2
        if ft == "bed narrowpeak":
            return 3
        if ft == "bed broadpeak":
            return 4
        return 5

    files.sort(key=rank)
    chosen = files[0]
    href = chosen.get("href", "")
    full = ENCODE_BASE + href if href.startswith("/") else href
    label = f"{chosen.get('@id', '?')} ({chosen.get('output_type', '?')})"
    return full, label


# ----------- Biosample classification -----------

def classify_biosample(summary: str) -> str:
    s = (summary or "").lower()
    if "mus musculus" in s or "mouse" in s or "musculus" in s:
        return "mouse_lung"
    # Cancer-line keywords
    if any(k in s for k in (
            "adenocarcinoma", "carcinoma", "small cell lung cancer",
            "nsclc", " a549", " h441", " h1299", " h2087", " h3122",
            " h1819", "ncih441", "ncih1299")):
        return "cancer_lung_line"
    if "fetal" in s or "embryo" in s:
        return "human_fetal_lung"
    if "homo sapiens" in s and ("lung" in s or "tissue" in s):
        return "human_adult_lung_tissue"
    return "unclear"


def mark_class(target_label: str) -> str:
    if target_label in ACTIVE_MARKS:
        return "active"
    if target_label in REPRESSIVE_MARKS:
        return "repressive"
    if target_label in GENE_BODY_MARKS:
        return "gene_body"
    return "other"


# ----------- Overlap testing -----------

def overlap_count(peaks: list[tuple[str, int, int]],
                  chrom: str, start: int, end: int) -> int:
    """Count peaks intersecting [start, end] on chrom."""
    n = 0
    for c, s, e in peaks:
        if c != chrom:
            continue
        if e >= start and s <= end:
            n += 1
    return n


# ----------- Tier classifier -----------

def assign_tier(per_mark_counts: dict, candidate_chrom_has_human_active: bool) -> str:
    """Returns one of UPDATED_TIERS."""
    # Sum of any active overlap in human (fetal or adult)
    active_human_overlap = 0
    for mark in ("h3k27ac", "h3k4me1", "h3k4me3", "h3k9ac", "h3k4me2"):
        active_human_overlap += per_mark_counts.get(f"{mark}_fetal", 0)
        active_human_overlap += per_mark_counts.get(f"{mark}_adult", 0)
    repressive_overlap = (per_mark_counts.get("repressive_fetal", 0)
                          + per_mark_counts.get("repressive_adult", 0))
    mouse_active_overlap = per_mark_counts.get("active_mouse", 0)

    if active_human_overlap > 0:
        return "strong_distal_candidate_with_chromatin_support"

    # No active human overlap. If we know human active-mark ChIP exists for
    # the candidate's chromosome (i.e. we tested), it's "without".
    if candidate_chrom_has_human_active:
        # Edge case: only repressive marks in primary tissue → downgraded.
        if repressive_overlap > 0:
            return "downgraded_candidate"
        # Edge case: only mouse active-mark overlap → unresolved.
        if mouse_active_overlap > 0:
            return "unresolved_due_to_context_mismatch"
        return "strong_distal_candidate_without_chromatin_support"

    return "unresolved_due_to_context_mismatch"


def justify(tier: str, target: str, locus: str, counts: dict) -> str:
    base = (f"Counts: H3K27ac fetal={counts.get('h3k27ac_fetal',0)}/"
            f"adult={counts.get('h3k27ac_adult',0)}; "
            f"H3K4me1 fetal={counts.get('h3k4me1_fetal',0)}/"
            f"adult={counts.get('h3k4me1_adult',0)}; "
            f"H3K4me3 fetal={counts.get('h3k4me3_fetal',0)}/"
            f"adult={counts.get('h3k4me3_adult',0)}; "
            f"repressive fetal={counts.get('repressive_fetal',0)}/"
            f"adult={counts.get('repressive_adult',0)}.")
    suffix_caveat = (" Active-mark overlap raises the prior that this is a "
                     "regulatory candidate but does not confirm enhancer "
                     "function, regulatory action on the target, or "
                     "developmental NKX2-1 binding (the supporting NKX2-1 "
                     "ChIP remains cancer-line context).")
    if tier == "strong_distal_candidate_with_chromatin_support":
        return (f"Active-mark histone peak in human lung tissue overlaps "
                f"the {target} candidate at {locus}. {base}{suffix_caveat}")
    if tier == "strong_distal_candidate_without_chromatin_support":
        return (f"Human lung tissue active-mark histone ChIP exists for "
                f"this chromosome but no peak overlaps the {target} "
                f"candidate at {locus}. {base} Lung-bulk-tissue inactivity "
                f"does not preclude cell-type-specific activity.")
    if tier == "downgraded_candidate":
        return (f"Only repressive marks (H3K27me3 / H3K9me3) overlap the "
                f"{target} candidate at {locus} in human lung tissue. {base} "
                f"Polycomb-state at this locus weakens the candidate, but "
                f"repressive marks are dynamic across developmental stages.")
    return (f"Cannot classify {target} candidate at {locus}: human lung "
            f"active-mark coverage may be incomplete on this chromosome, "
            f"or only mouse evidence overlaps. {base}")


# ----------- Main -----------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="gain-nkx21-histone-filter",
        description="Histone-support filter on the 11 strong NKX2-1 distal candidates.",
    )
    parser.add_argument("--candidates", type=Path, default=DEFAULT_CANDIDATES)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--sleep", type=float, default=0.3)
    args = parser.parse_args(argv)

    # 1. Load strong candidates
    with args.candidates.open() as f:
        all_rows = list(csv.DictReader(f))
    strong = [r for r in all_rows if r["candidate_tier"] == "strong_distal_candidate"]
    print(f"loaded {len(all_rows)} candidate rows; "
          f"{len(strong)} strong candidates to filter")

    # 2. Search ENCODE lung histone ChIP
    print("\nQuerying ENCODE lung Histone ChIP-seq...")
    search = http_get_json(
        f"{ENCODE_BASE}/search/?type=Experiment&assay_title=Histone+ChIP-seq"
        f"&biosample_ontology.term_name=lung&format=json&limit=100"
    )
    experiments = search.get("@graph", []) if search else []
    print(f"  {len(experiments)} experiments returned")

    # 3. Classify each experiment
    classified = []
    for e in experiments:
        target_label = (e.get("target") or {}).get("label", "?")
        bs = (e.get("biosample_summary") or "")
        biosample_class = classify_biosample(bs)
        mark = mark_class(target_label)
        classified.append({
            "id": e["@id"],
            "target": target_label,
            "biosample": bs,
            "biosample_class": biosample_class,
            "mark": mark,
            "mark_label": target_label,
        })

    # Distribution summary
    print("\n  Biosample distribution:")
    by_bs: dict[str, int] = {}
    for c in classified:
        by_bs[c["biosample_class"]] = by_bs.get(c["biosample_class"], 0) + 1
    for k, v in sorted(by_bs.items(), key=lambda kv: -kv[1]):
        print(f"    {k}: {v}")
    print("\n  Mark distribution (filtered to active human):")
    active_human = [c for c in classified
                    if c["mark"] == "active"
                    and c["biosample_class"] in ("human_fetal_lung", "human_adult_lung_tissue")]
    repressive_human = [c for c in classified
                        if c["mark"] == "repressive"
                        and c["biosample_class"] in ("human_fetal_lung", "human_adult_lung_tissue")]
    by_mark: dict[str, int] = {}
    for c in active_human:
        by_mark[c["mark_label"]] = by_mark.get(c["mark_label"], 0) + 1
    for k, v in sorted(by_mark.items(), key=lambda kv: -kv[1]):
        print(f"    {k}: {v}")
    print(f"  active_human total: {len(active_human)}")
    print(f"  repressive_human total: {len(repressive_human)}")

    # 4. Download peak BEDs for each kept experiment
    print(f"\nDownloading peak BEDs for {len(active_human) + len(repressive_human)} human experiments...")
    to_test = active_human + repressive_human
    for i, exp in enumerate(to_test, 1):
        url, label = best_peak_url(exp["id"].rstrip("/").rsplit("/", 1)[-1])
        if not url:
            exp["peaks"] = None
            print(f"  [{i:>2}/{len(to_test)}] {exp['id']} ({exp['mark_label']}, {exp['biosample_class']}): NO BED")
            time.sleep(args.sleep)
            continue
        time.sleep(args.sleep)
        blob = http_get_bytes(url)
        if blob is None:
            exp["peaks"] = None
            print(f"  [{i:>2}/{len(to_test)}] {exp['id']} ({exp['mark_label']}, {exp['biosample_class']}): DOWNLOAD FAILED")
        else:
            exp["peaks"] = parse_bed(blob)
            print(f"  [{i:>2}/{len(to_test)}] {exp['id']} ({exp['mark_label']}, {exp['biosample_class']}): {len(exp['peaks']):>5} peaks")
        time.sleep(args.sleep)

    # 5. For each strong candidate, intersect against each kept experiment
    print(f"\nFiltering candidates...")
    out_rows: list[dict] = []
    for cand in strong:
        chrom = cand["locus_chrom"]
        locus_start = int(cand["locus_start"])
        locus_end = int(cand["locus_end"])

        counts = {f"{m}_{ctx}": 0 for m in
                  ("h3k27ac", "h3k4me1", "h3k4me3", "h3k9ac", "h3k4me2")
                  for ctx in ("fetal", "adult")}
        counts["repressive_fetal"] = 0
        counts["repressive_adult"] = 0
        counts["active_mouse"] = 0  # left at 0 (mouse not tested in v0)

        chrom_has_human_active = False

        for exp in to_test:
            peaks = exp.get("peaks")
            if peaks is None:
                continue
            # Does this experiment have any peaks on the candidate's chromosome?
            has_chrom = any(p[0] == chrom for p in peaks)
            n_overlap = overlap_count(peaks, chrom, locus_start, locus_end)

            mark_label_lower = exp["mark_label"].lower()
            ctx = ("fetal" if exp["biosample_class"] == "human_fetal_lung"
                   else "adult" if exp["biosample_class"] == "human_adult_lung_tissue"
                   else None)
            if ctx is None:
                continue

            # Track presence of any human active-mark experiment for the chromosome
            if exp["mark"] == "active" and has_chrom:
                chrom_has_human_active = True

            if n_overlap == 0:
                continue

            if exp["mark"] == "active":
                key = f"{mark_label_lower}_{ctx}"
                counts[key] = counts.get(key, 0) + n_overlap
            elif exp["mark"] == "repressive":
                key = f"repressive_{ctx}"
                counts[key] = counts.get(key, 0) + n_overlap

        tier = assign_tier(counts, chrom_has_human_active)

        # Construct evidence summary
        active_overlaps = []
        for mark in ("h3k27ac", "h3k4me1", "h3k4me3", "h3k9ac", "h3k4me2"):
            for ctx in ("fetal", "adult"):
                v = counts.get(f"{mark}_{ctx}", 0)
                if v > 0:
                    active_overlaps.append(f"{mark}({ctx})={v}")
        rep_summary = []
        for ctx in ("fetal", "adult"):
            v = counts.get(f"repressive_{ctx}", 0)
            if v > 0:
                rep_summary.append(f"repressive({ctx})={v}")
        if active_overlaps:
            evidence_summary = "; ".join(active_overlaps)
        elif rep_summary:
            evidence_summary = "no active overlap; " + "; ".join(rep_summary)
        else:
            evidence_summary = "no overlap with active or repressive marks"

        contexts = []
        for mark in ("h3k27ac", "h3k4me1", "h3k4me3", "h3k9ac", "h3k4me2"):
            if counts.get(f"{mark}_fetal", 0) > 0:
                contexts.append("human_fetal_lung")
            if counts.get(f"{mark}_adult", 0) > 0:
                contexts.append("human_adult_lung_tissue")
        if not contexts:
            histone_source_context = "none"
        else:
            histone_source_context = ",".join(sorted(set(contexts)))

        locus_str = f"{chrom}:{locus_start}-{locus_end}"
        out_rows.append({
            "target": cand["target"],
            "candidate_locus": locus_str,
            "locus_chrom": chrom,
            "locus_start": locus_start,
            "locus_end": locus_end,
            "distance_to_tss_bp": cand["distance_to_tss_bp"],
            "supporting_nkx21_experiments": cand["supporting_experiment_ids"],
            "n_overlap_h3k27ac_fetal": counts["h3k27ac_fetal"],
            "n_overlap_h3k27ac_adult": counts["h3k27ac_adult"],
            "n_overlap_h3k4me1_fetal": counts["h3k4me1_fetal"],
            "n_overlap_h3k4me1_adult": counts["h3k4me1_adult"],
            "n_overlap_h3k4me3_fetal": counts["h3k4me3_fetal"],
            "n_overlap_h3k4me3_adult": counts["h3k4me3_adult"],
            "n_overlap_h3k9ac_fetal": counts["h3k9ac_fetal"],
            "n_overlap_h3k9ac_adult": counts["h3k9ac_adult"],
            "n_overlap_h3k4me2_fetal": counts["h3k4me2_fetal"],
            "n_overlap_h3k4me2_adult": counts["h3k4me2_adult"],
            "n_overlap_repressive_fetal": counts["repressive_fetal"],
            "n_overlap_repressive_adult": counts["repressive_adult"],
            "n_overlap_active_mouse": counts["active_mouse"],
            "histone_evidence_summary": evidence_summary,
            "histone_source_context": histone_source_context,
            "updated_tier": tier,
            "justification": justify(tier, cand["target"], locus_str, counts),
        })

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=OUT_FIELDS)
        w.writeheader()
        for row in out_rows:
            w.writerow(row)

    print(f"\nwrote {args.out.relative_to(REPO_ROOT)}")
    print(f"  generated_at: {datetime.now(timezone.utc).isoformat(timespec='seconds')}")
    print(f"\n  Updated tier distribution:")
    by_tier: dict[str, int] = {t: 0 for t in UPDATED_TIERS}
    for r in out_rows:
        by_tier[r["updated_tier"]] = by_tier.get(r["updated_tier"], 0) + 1
    for t in UPDATED_TIERS:
        print(f"    {t}: {by_tier[t]}")

    print(f"\n  Per-candidate result:")
    for r in out_rows:
        print(f"    {r['target']:<8} {r['candidate_locus']:<28} "
              f"-> {r['updated_tier']}")
        if r['histone_evidence_summary']:
            print(f"        evidence: {r['histone_evidence_summary']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
