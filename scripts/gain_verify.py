#!/usr/bin/env python3
"""gain verify - probe each source URL in sources.json and record what comes back.

Records HTTP status, content type, declared content length, response-head size,
and any error per source row. Output is metadata/verification.json. Stdlib only.
Honors a configurable inter-request sleep (default 0.2s) so we sit well under
ENCODE's 10 GET/sec limit even when looping fast.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SOURCES = REPO_ROOT / "metadata" / "sources.json"
DEFAULT_OUT = REPO_ROOT / "metadata" / "verification.json"

USER_AGENT = "gain-verify/0.1 (+https://github.com/DD-Ching/Gain)"
HEAD_BYTES = 4096


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def check_url(url: str, timeout: float) -> dict:
    started = utcnow_iso()
    req = urllib.request.Request(
        url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"}
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            head = resp.read(HEAD_BYTES)
            declared = resp.headers.get("Content-Length")
            try:
                declared_int = int(declared) if declared is not None else None
            except ValueError:
                declared_int = None
            return {
                "status_code": resp.status,
                "content_type": resp.headers.get_content_type(),
                "declared_content_length": declared_int,
                "head_bytes_read": len(head),
                "ok": 200 <= resp.status < 400,
                "error": None,
                "checked_at": started,
            }
    except urllib.error.HTTPError as e:
        return {
            "status_code": e.code,
            "content_type": None,
            "declared_content_length": None,
            "head_bytes_read": 0,
            "ok": False,
            "error": f"HTTPError: {e.reason}",
            "checked_at": started,
        }
    except Exception as e:  # urllib.error.URLError, socket.timeout, ssl errors, ...
        return {
            "status_code": None,
            "content_type": None,
            "declared_content_length": None,
            "head_bytes_read": 0,
            "ok": False,
            "error": f"{type(e).__name__}: {e}",
            "checked_at": started,
        }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="gain-verify",
        description="Probe each programmatic_access URL in sources.json and record reachability.",
    )
    parser.add_argument(
        "--sources", type=Path, default=DEFAULT_SOURCES,
        help=f"path to sources.json (default: {DEFAULT_SOURCES.relative_to(REPO_ROOT)})",
    )
    parser.add_argument(
        "--out", type=Path, default=DEFAULT_OUT,
        help=f"output JSON path (default: {DEFAULT_OUT.relative_to(REPO_ROOT)})",
    )
    parser.add_argument(
        "--timeout", type=float, default=10.0,
        help="per-request timeout in seconds (default: 10.0)",
    )
    parser.add_argument(
        "--sleep", type=float, default=0.2,
        help="seconds to sleep between requests (default: 0.2)",
    )
    args = parser.parse_args(argv)

    try:
        with args.sources.open() as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"error: cannot read {args.sources}: {e}", file=sys.stderr)
        return 2

    rows = data.get("sources")
    if not isinstance(rows, list) or not rows:
        print(f"error: {args.sources}: 'sources' must be a non-empty list", file=sys.stderr)
        return 2

    results = []
    ok_count = 0
    print(f"verifying {len(rows)} sources (timeout={args.timeout}s, sleep={args.sleep}s)")
    for i, row in enumerate(rows, 1):
        url = row.get("programmatic_access", "")
        name = row.get("dataset_name", "?")
        if not url:
            results.append({
                "source": row.get("source"),
                "dataset_name": name,
                "url": None,
                "result": {
                    "status_code": None, "content_type": None,
                    "declared_content_length": None, "head_bytes_read": 0,
                    "ok": False, "error": "no programmatic_access URL",
                    "checked_at": utcnow_iso(),
                },
            })
            print(f"  [{i:>2}/{len(rows)}] SKIP (no URL): {name}")
            continue

        result = check_url(url, timeout=args.timeout)
        results.append({
            "source": row.get("source"),
            "dataset_name": name,
            "url": url,
            "result": result,
        })
        status = result["status_code"] if result["status_code"] is not None else "ERR"
        marker = "OK " if result["ok"] else "BAD"
        print(f"  [{i:>2}/{len(rows)}] {marker} {status} {name}")
        if result["ok"]:
            ok_count += 1

        if i < len(rows):
            time.sleep(args.sleep)

    payload = {
        "schema_version": "0.1",
        "verified_at": utcnow_iso(),
        "summary": {
            "total": len(rows),
            "ok": ok_count,
            "failed": len(rows) - ok_count,
        },
        "results": results,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")

    print(f"\nwrote {args.out.relative_to(REPO_ROOT)}")
    print(f"  ok:     {payload['summary']['ok']}")
    print(f"  failed: {payload['summary']['failed']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
