"""Lightweight checks for the Scholar crawler CLI."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import main


def test_parse_args_uses_environment_defaults() -> None:
    old_id = os.environ.get(main.SCHOLAR_ID_ENV)
    old_output = os.environ.get(main.OUTPUT_DIR_ENV)
    old_label = os.environ.get(main.BADGE_LABEL_ENV)
    try:
        os.environ[main.SCHOLAR_ID_ENV] = "test-author"
        os.environ[main.OUTPUT_DIR_ENV] = "tmp-scholar-output"
        os.environ[main.BADGE_LABEL_ENV] = "profile citations"
        args = main.parse_args([])
        assert args.scholar_id == "test-author"
        assert args.output_dir == Path("tmp-scholar-output")
        assert args.badge_label == "profile citations"
    finally:
        if old_id is None:
            os.environ.pop(main.SCHOLAR_ID_ENV, None)
        else:
            os.environ[main.SCHOLAR_ID_ENV] = old_id
        if old_output is None:
            os.environ.pop(main.OUTPUT_DIR_ENV, None)
        else:
            os.environ[main.OUTPUT_DIR_ENV] = old_output
        if old_label is None:
            os.environ.pop(main.BADGE_LABEL_ENV, None)
        else:
            os.environ[main.BADGE_LABEL_ENV] = old_label


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


def test_config_validation_rejects_bad_values() -> None:
    args = main.parse_args(
        [
            "--scholar-id",
            "bad id",
            "--badge-label",
            "citations",
        ]
    )
    try:
        main.config_from_args(args)
    except ValueError as exc:
        assert "whitespace" in str(exc)
    else:
        raise AssertionError("expected whitespace in Scholar ID to fail")

    with tempfile.NamedTemporaryFile() as tmp:
        args = main.parse_args(
            [
                "--scholar-id",
                "author-id",
                "--output-dir",
                tmp.name,
            ]
        )
        try:
            main.config_from_args(args)
        except ValueError as exc:
            assert "not a directory" in str(exc)
        else:
            raise AssertionError("expected file output path to fail")


def test_write_author_outputs_uses_custom_badge_label() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        output_dir = Path(tmp)
        author = {"citedby": 123, "publications": {}}
        main.write_author_outputs(output_dir, author, "profile citations")
        shield = output_dir / "gs_data_shieldsio.json"
        assert '"label": "profile citations"' in shield.read_text(encoding="utf-8")


if __name__ == "__main__":
    test_parse_args_uses_environment_defaults()
    test_missing_scholar_id_exits_before_network_import()
    test_write_json_creates_parent_directory()
    test_config_validation_rejects_bad_values()
    test_write_author_outputs_uses_custom_badge_label()
