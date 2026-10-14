"""Lightweight checks for the Scholar crawler CLI."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import main


def test_parse_args_uses_environment_defaults() -> None:
    old_id = os.environ.get(main.SCHOLAR_ID_ENV)
    old_output = os.environ.get(main.OUTPUT_DIR_ENV)
    try:
        os.environ[main.SCHOLAR_ID_ENV] = "test-author"
        os.environ[main.OUTPUT_DIR_ENV] = "tmp-scholar-output"
        args = main.parse_args([])
        assert args.scholar_id == "test-author"
        assert args.output_dir == Path("tmp-scholar-output")
    finally:
        if old_id is None:
            os.environ.pop(main.SCHOLAR_ID_ENV, None)
        else:
            os.environ[main.SCHOLAR_ID_ENV] = old_id
        if old_output is None:
            os.environ.pop(main.OUTPUT_DIR_ENV, None)
        else:
            os.environ[main.OUTPUT_DIR_ENV] = old_output


def test_missing_scholar_id_exits_before_network_import() -> None:
    old_id = os.environ.get(main.SCHOLAR_ID_ENV)
    try:
        os.environ.pop(main.SCHOLAR_ID_ENV, None)
        try:
            main.main([])
        except SystemExit as exc:
            assert "Missing Google Scholar author ID" in str(exc)
        else:
            raise AssertionError("main() should exit when no Scholar ID is configured")
    finally:
        if old_id is not None:
            os.environ[main.SCHOLAR_ID_ENV] = old_id


def test_write_json_creates_parent_directory() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "nested" / "payload.json"
        main.write_json(path, {"ok": True})
        assert path.read_text(encoding="utf-8") == '{\n  "ok": true\n}\n'


if __name__ == "__main__":
    test_parse_args_uses_environment_defaults()
    test_missing_scholar_id_exits_before_network_import()
    test_write_json_creates_parent_directory()
