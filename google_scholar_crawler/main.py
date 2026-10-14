#!/usr/bin/env python3
"""Fetch Google Scholar metadata for the homepage badge data."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping


DEFAULT_OUTPUT_DIR = Path("results")
SCHOLAR_ID_ENV = "GOOGLE_SCHOLAR_ID"
OUTPUT_DIR_ENV = "GOOGLE_SCHOLAR_OUTPUT_DIR"
BADGE_LABEL_ENV = "GOOGLE_SCHOLAR_BADGE_LABEL"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_OUTPUT_DIRS = ("results", "google-scholar-stats")


@dataclass(frozen=True)
class CrawlerConfig:
    scholar_id: str
    output_dir: Path
    badge_label: str


def path_is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def resolve_output_dir(output_dir: Path, project_root: Path = PROJECT_ROOT) -> Path:
    expanded = output_dir.expanduser()
    resolved_project_root = project_root.expanduser().resolve(strict=False)
    if not expanded.is_absolute():
        expanded = resolved_project_root / expanded

    if expanded.exists() and not expanded.is_dir():
        raise ValueError(f"Output path is not a directory: {output_dir}")

    resolved = expanded.resolve(strict=False)
    if path_is_relative_to(resolved, resolved_project_root):
        allowed_dirs = [
            (resolved_project_root / dirname).resolve(strict=False)
            for dirname in REPOSITORY_OUTPUT_DIRS
        ]
        if not any(path_is_relative_to(resolved, directory) for directory in allowed_dirs):
            allowed = ", ".join(f"{dirname}/" for dirname in REPOSITORY_OUTPUT_DIRS)
            raise ValueError(f"Output directory inside the repository must be under {allowed}")

    return resolved


def parse_args(
    argv: list[str] | None = None,
    env: Mapping[str, str] | None = None,
) -> argparse.Namespace:
    env_values = os.environ if env is None else env
    output_dir_default = env_values.get(OUTPUT_DIR_ENV) or DEFAULT_OUTPUT_DIR
    badge_label_default = env_values.get(BADGE_LABEL_ENV) or "citations"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--scholar-id",
        default=env_values.get(SCHOLAR_ID_ENV, ""),
        help=f"Google Scholar author ID. Defaults to ${SCHOLAR_ID_ENV}.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(output_dir_default),
        help=f"Directory for generated JSON files. Defaults to ${OUTPUT_DIR_ENV} or results/.",
    )
    parser.add_argument(
        "--badge-label",
        default=badge_label_default,
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

    output_dir = resolve_output_dir(args.output_dir)

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
    encoded = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as tmp_file:
            tmp_path = Path(tmp_file.name)
            tmp_file.write(encoded)
            tmp_file.flush()
            os.fsync(tmp_file.fileno())
        tmp_path.replace(path)
    finally:
        if tmp_path is not None and tmp_path.exists():
            tmp_path.unlink()


def shields_payload(author: Mapping[str, object], label: str) -> dict[str, object]:
    return {
        "schemaVersion": 1,
        "label": label,
        "message": f"{author['citedby']}",
    }


def validate_author_payload(author: Mapping[str, object]) -> None:
    citedby = author.get("citedby")
    if not isinstance(citedby, int) or isinstance(citedby, bool) or citedby < 0:
        raise ValueError(
            "Scholar author payload must include non-negative integer citedby."
        )

    publications = author.get("publications")
    if not isinstance(publications, Mapping):
        raise ValueError("Scholar author payload must include publications mapping.")


def write_author_outputs(output_dir: Path, author: dict, badge_label: str) -> None:
    validate_author_payload(author)
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
