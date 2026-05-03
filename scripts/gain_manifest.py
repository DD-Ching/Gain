#!/usr/bin/env python3
"""gain manifest - aggregate lung-development resource metadata into one manifest.

Reads a curated JSON sources file and writes a unified manifest in CSV, JSON,
and Markdown. Stdlib only. No live API calls in v0.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SOURCES = REPO_ROOT / "metadata" / "sources.json"
DEFAULT_OUT_DIR = REPO_ROOT / "metadata"

FIELDS = (
    "source",
    "dataset_name",
    "modality",
    "stage",
    "tissue",
    "access_method",
    "programmatic_access",
    "reuse_priority",
    "notes",
)


def load_sources(path: Path) -> tuple[dict, list[dict]]:
    with path.open() as f:
        data = json.load(f)
    sources = data.get("sources")
    if not isinstance(sources, list) or not sources:
        raise ValueError(f"{path}: top-level 'sources' must be a non-empty list")
    return data, sources


def validate(rows: list[dict]) -> None:
    errors = []
    for i, row in enumerate(rows):
        if not isinstance(row, dict):
            errors.append(f"row {i}: not an object")
            continue
        missing = [f for f in FIELDS if not row.get(f)]
        if missing:
            errors.append(f"row {i} ({row.get('dataset_name', '?')}): missing/empty {missing}")
    if errors:
        raise ValueError("sources.json validation failed:\n  " + "\n  ".join(errors))


def write_csv(rows: list[dict], path: Path) -> None:
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in FIELDS})


def write_json(meta: dict, rows: list[dict], path: Path) -> None:
    payload = {k: v for k, v in meta.items() if k != "sources"}
    payload["sources"] = rows
    with path.open("w") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")


def write_markdown(rows: list[dict], path: Path) -> None:
    def cell(value: object) -> str:
        return str(value).replace("|", "\\|").replace("\n", " ").strip()

    header = "| " + " | ".join(FIELDS) + " |"
    sep = "| " + " | ".join("---" for _ in FIELDS) + " |"
    lines = [header, sep]
    for row in rows:
        lines.append("| " + " | ".join(cell(row.get(f, "")) for f in FIELDS) + " |")
    path.write_text("\n".join(lines) + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="gain-manifest",
        description="Aggregate lung-development resource metadata into one manifest.",
    )
    parser.add_argument(
        "--sources", type=Path, default=DEFAULT_SOURCES,
        help=f"path to sources.json (default: {DEFAULT_SOURCES.relative_to(REPO_ROOT)})",
    )
    parser.add_argument(
        "--out-dir", type=Path, default=DEFAULT_OUT_DIR,
        help=f"output directory (default: {DEFAULT_OUT_DIR.relative_to(REPO_ROOT)})",
    )
    parser.add_argument(
        "--formats", default="csv,json,md",
        help="comma-separated outputs to write; choose from csv,json,md (default: csv,json,md)",
    )
    args = parser.parse_args(argv)

    try:
        meta, rows = load_sources(args.sources)
    except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    try:
        validate(rows)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    formats = {f.strip() for f in args.formats.split(",") if f.strip()}
    unknown = formats - {"csv", "json", "md"}
    if unknown:
        print(f"error: unknown formats: {sorted(unknown)}", file=sys.stderr)
        return 2

    args.out_dir.mkdir(parents=True, exist_ok=True)

    written: list[Path] = []
    if "csv" in formats:
        out = args.out_dir / "manifest.csv"
        write_csv(rows, out)
        written.append(out)
    if "json" in formats:
        out = args.out_dir / "manifest.json"
        write_json(meta, rows, out)
        written.append(out)
    if "md" in formats:
        out = args.out_dir / "manifest.md"
        write_markdown(rows, out)
        written.append(out)

    print(f"wrote {len(rows)} entries to:")
    for w in written:
        try:
            rel = w.relative_to(Path.cwd())
        except ValueError:
            rel = w
        print(f"  {rel}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
