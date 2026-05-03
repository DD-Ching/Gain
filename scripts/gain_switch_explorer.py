#!/usr/bin/env python3
"""gain switch-explorer - render the lung switch-hierarchy CSV joined against the manifest.

Reads:
  metadata/switch_hierarchy.csv   (gene/pathway -> source links, hand-curated)
  metadata/sources.json           (the manifest, source-of-truth for modality/stage)

Validates that every relevant_source in switch_hierarchy.csv matches a
dataset_name in sources.json. Emits notes/switch_hierarchy.md grouped by
node, with each node's metadata header and a per-source evidence table.

Stdlib only.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import OrderedDict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_HIERARCHY = REPO_ROOT / "metadata" / "switch_hierarchy.csv"
DEFAULT_SOURCES = REPO_ROOT / "metadata" / "sources.json"
DEFAULT_OUT = REPO_ROOT / "notes" / "switch_hierarchy.md"

REQUIRED_HIERARCHY_FIELDS = (
    "node",
    "node_type",
    "regulatory_layer",
    "proximal_distal",
    "output_program",
    "developmental_relevance",
    "role_status",
    "relevant_source",
    "evidence_one_liner",
)

# Ordering for the report; nodes outside this list are appended in
# their first-seen order from the CSV.
NODE_ORDER = (
    "NKX2-1",
    "SOX2",
    "SOX9",
    "FGF10",
    "WNT",
    "BMP",
    "SHH",
    "airway_program",
    "alveolar_program",
)


def load_hierarchy(path: Path) -> list[dict]:
    with path.open() as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError(f"{path}: empty CSV (no header)")
        missing = [f for f in REQUIRED_HIERARCHY_FIELDS if f not in reader.fieldnames]
        if missing:
            raise ValueError(f"{path}: missing required columns {missing}")
        rows = list(reader)
    if not rows:
        raise ValueError(f"{path}: no data rows")
    return rows


def load_sources(path: Path) -> dict[str, dict]:
    with path.open() as f:
        data = json.load(f)
    sources = data.get("sources")
    if not isinstance(sources, list) or not sources:
        raise ValueError(f"{path}: 'sources' must be a non-empty list")
    by_name: dict[str, dict] = {}
    for s in sources:
        name = s.get("dataset_name")
        if not name:
            continue
        by_name[name] = s
    return by_name


def validate_links(rows: list[dict], sources_by_name: dict[str, dict]) -> None:
    errors = []
    for i, row in enumerate(rows):
        empty = [f for f in REQUIRED_HIERARCHY_FIELDS if not row.get(f, "").strip()]
        if empty:
            errors.append(f"row {i + 2}: empty fields {empty}")
            continue
        link = row["relevant_source"]
        if link not in sources_by_name:
            errors.append(
                f"row {i + 2}: relevant_source {link!r} does not match any "
                f"dataset_name in sources.json"
            )
    if errors:
        raise ValueError("switch_hierarchy.csv validation failed:\n  " + "\n  ".join(errors))


def group_by_node(rows: list[dict]) -> "OrderedDict[str, list[dict]]":
    grouped: "OrderedDict[str, list[dict]]" = OrderedDict()
    for node in NODE_ORDER:
        grouped[node] = []
    for row in rows:
        node = row["node"]
        if node not in grouped:
            grouped[node] = []
        grouped[node].append(row)
    return OrderedDict((n, rs) for n, rs in grouped.items() if rs)


def md_cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ").strip()


def render_summary_table(grouped: "OrderedDict[str, list[dict]]") -> list[str]:
    header = (
        "| Node | Type | Layer | Proximal/Distal | Output | Dev. Relevance "
        "| Role Status | # Sources |"
    )
    sep = "| --- | --- | --- | --- | --- | --- | --- | --- |"
    lines = [header, sep]
    for node, rows in grouped.items():
        first = rows[0]
        lines.append(
            "| " + " | ".join(md_cell(c) for c in (
                node,
                first["node_type"],
                first["regulatory_layer"],
                first["proximal_distal"],
                first["output_program"],
                first["developmental_relevance"],
                first["role_status"],
                str(len(rows)),
            )) + " |"
        )
    return lines


def render_node_section(node: str, rows: list[dict], sources_by_name: dict[str, dict]) -> list[str]:
    first = rows[0]
    lines = [
        f"## {node}",
        "",
        f"- **Type:** {first['node_type']}",
        f"- **Regulatory layer:** {first['regulatory_layer']}",
        f"- **Proximal/distal:** {first['proximal_distal']}",
        f"- **Output program:** {first['output_program']}",
        f"- **Developmental relevance:** {first['developmental_relevance']}",
        f"- **Role status:** {first['role_status']}",
        "",
        "| Source | Modality | Stage | Tissue | Evidence |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        src = sources_by_name[row["relevant_source"]]
        lines.append(
            "| " + " | ".join(md_cell(c) for c in (
                row["relevant_source"],
                src.get("modality", ""),
                src.get("stage", ""),
                src.get("tissue", ""),
                row["evidence_one_liner"],
            )) + " |"
        )
    lines.append("")
    return lines


def render_markdown(grouped: "OrderedDict[str, list[dict]]", sources_by_name: dict[str, dict]) -> str:
    lines: list[str] = [
        "# Lung Switch-Hierarchy Explorer",
        "",
        "Generated by `scripts/gain_switch_explorer.py` from "
        "`metadata/switch_hierarchy.csv` joined against `metadata/sources.json`.",
        "",
        "Each node is a gene or pathway in the regulatory chain "
        "**NKX2-1 -> SOX2/SOX9 -> FGF10/WNT/BMP/SHH -> airway/alveolar programs**. "
        "For each node, the table lists the public sources that bear on that node, "
        "annotated with modality, developmental stage, and a one-line evidence summary.",
        "",
        "**Role status legend:** `well_established` (broad consensus in the lung "
        "developmental literature) / `partial` (multiple lines of evidence but "
        "context-dependent or contested details) / `unclear` (no robust public-data "
        "support in this scope yet).",
        "",
        "## Summary",
        "",
        *render_summary_table(grouped),
        "",
    ]
    for node, rows in grouped.items():
        lines.extend(render_node_section(node, rows, sources_by_name))
    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="gain-switch-explorer",
        description="Render the lung switch-hierarchy CSV joined against the manifest.",
    )
    parser.add_argument("--hierarchy", type=Path, default=DEFAULT_HIERARCHY,
                        help=f"path to switch_hierarchy.csv (default: {DEFAULT_HIERARCHY.relative_to(REPO_ROOT)})")
    parser.add_argument("--sources", type=Path, default=DEFAULT_SOURCES,
                        help=f"path to sources.json (default: {DEFAULT_SOURCES.relative_to(REPO_ROOT)})")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT,
                        help=f"output Markdown path (default: {DEFAULT_OUT.relative_to(REPO_ROOT)})")
    args = parser.parse_args(argv)

    try:
        rows = load_hierarchy(args.hierarchy)
        sources_by_name = load_sources(args.sources)
        validate_links(rows, sources_by_name)
    except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    grouped = group_by_node(rows)
    md = render_markdown(grouped, sources_by_name)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(md)

    print(f"wrote {args.out.relative_to(REPO_ROOT)}")
    print(f"  nodes:   {len(grouped)}")
    print(f"  edges:   {len(rows)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
