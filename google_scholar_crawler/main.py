#!/usr/bin/env python3
"""Fetch Google Scholar metadata for the homepage badge data."""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping


DEFAULT_OUTPUT_DIR = Path("results")
SCHOLAR_ID_ENV = "GOOGLE_SCHOLAR_ID"
OUTPUT_DIR_ENV = "GOOGLE_SCHOLAR_OUTPUT_DIR"
BADGE_LABEL_ENV = "GOOGLE_SCHOLAR_BADGE_LABEL"


@dataclass(frozen=True)
class CrawlerConfig:
    scholar_id: str
    output_dir: Path
    badge_label: str


def parse_args(
    argv: list[str] | None = None,
    env: Mapping[str, str] | None = None,
) -> argparse.Namespace:
    env_values = os.environ if env is None else env
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--scholar-id",
        default=env_values.get(SCHOLAR_ID_ENV, ""),
        help=f"Google Scholar author ID. Defaults to ${SCHOLAR_ID_ENV}.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(env_values.get(OUTPUT_DIR_ENV, DEFAULT_OUTPUT_DIR)),
        help=f"Directory for generated JSON files. Defaults to ${OUTPUT_DIR_ENV} or results/.",
    )
    parser.add_argument(
        "--badge-label",
        default=env_values.get(BADGE_LABEL_ENV, "citations"),
        help=f"Shields.io badge label. Defaults to ${BADGE_LABEL_ENV} or citations.",
    )
    return parser.parse_args(argv)


def config_from_args(args: argparse.Namespace) -> CrawlerConfig:
    scholar_id = args.scholar_id.strip()
    if not scholar_id:
        raise ValueError(
            f"Missing Google Scholar author ID. Set ${SCHOLAR_ID_ENV} or pass --scholar-id."
        )
    if any(char.isspace() for char in scholar_id):
        raise ValueError("Google Scholar author ID must not contain whitespace.")

    output_dir = args.output_dir.expanduser()
    if output_dir.exists() and not output_dir.is_dir():
        raise ValueError(f"Output path is not a directory: {output_dir}")

    badge_label = args.badge_label.strip()
    if not badge_label:
        raise ValueError("Badge label must not be empty.")
    return CrawlerConfig(
        scholar_id=scholar_id,
        output_dir=output_dir,
        badge_label=badge_label,
    )


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


def shields_payload(author: Mapping[str, object], label: str) -> dict[str, object]:
    return {
        "schemaVersion": 1,
        "label": label,
        "message": f"{author['citedby']}",
    }


def write_author_outputs(output_dir: Path, author: dict, badge_label: str) -> None:
    write_json(output_dir / "gs_data.json", author)
    write_json(
        output_dir / "gs_data_shieldsio.json",
        shields_payload(author, badge_label),
    )


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        config = config_from_args(args)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    author = fetch_author(config.scholar_id)
    write_author_outputs(config.output_dir, author, config.badge_label)
    print(json.dumps(author, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
