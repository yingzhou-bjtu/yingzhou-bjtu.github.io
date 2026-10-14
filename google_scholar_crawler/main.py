#!/usr/bin/env python3
"""Fetch Google Scholar metadata for the homepage badge data."""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_OUTPUT_DIR = Path("results")
SCHOLAR_ID_ENV = "GOOGLE_SCHOLAR_ID"
OUTPUT_DIR_ENV = "GOOGLE_SCHOLAR_OUTPUT_DIR"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--scholar-id",
        default=os.environ.get(SCHOLAR_ID_ENV, ""),
        help=f"Google Scholar author ID. Defaults to ${SCHOLAR_ID_ENV}.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(os.environ.get(OUTPUT_DIR_ENV, DEFAULT_OUTPUT_DIR)),
        help=f"Directory for generated JSON files. Defaults to ${OUTPUT_DIR_ENV} or results/.",
    )
    return parser.parse_args(argv)


def fetch_author(scholar_id: str) -> dict:
    from scholarly import scholarly

    author: dict = scholarly.search_author_id(scholar_id)
    scholarly.fill(author, sections=["basics", "indices", "counts", "publications"])
    author["updated"] = datetime.now(timezone.utc).isoformat()
    author["publications"] = {
        publication["author_pub_id"]: publication
        for publication in author["publications"]
    }
    return author


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    scholar_id = args.scholar_id.strip()
    if not scholar_id:
        raise SystemExit(f"Missing Google Scholar author ID. Set ${SCHOLAR_ID_ENV} or pass --scholar-id.")

    output_dir = args.output_dir.expanduser()
    author = fetch_author(scholar_id)
    write_json(output_dir / "gs_data.json", author)
    write_json(
        output_dir / "gs_data_shieldsio.json",
        {
            "schemaVersion": 1,
            "label": "citations",
            "message": f"{author['citedby']}",
        },
    )
    print(json.dumps(author, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
