"""Lightweight checks for the Scholar crawler CLI."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import main


def test_parse_args_uses_environment_defaults() -> None:
    args = main.parse_args(
        [],
        env={
            main.SCHOLAR_ID_ENV: "test-author",
            main.OUTPUT_DIR_ENV: "tmp-scholar-output",
            main.BADGE_LABEL_ENV: "profile citations",
        },
    )
    assert args.scholar_id == "test-author"
    assert args.output_dir == Path("tmp-scholar-output")
    assert args.badge_label == "profile citations"


def test_parse_args_treats_empty_optional_env_as_default() -> None:
    args = main.parse_args(
        [],
        env={
            main.SCHOLAR_ID_ENV: "test-author",
            main.OUTPUT_DIR_ENV: "",
            main.BADGE_LABEL_ENV: "",
        },
    )
    assert args.output_dir == main.DEFAULT_OUTPUT_DIR
    assert args.badge_label == "citations"


def test_missing_scholar_id_exits_before_network_import() -> None:
    try:
        args = main.parse_args([], env={})
        main.config_from_args(args)
    except ValueError as exc:
        assert "Missing Google Scholar author ID" in str(exc)
    else:
        raise AssertionError("config_from_args() should fail without a Scholar ID")


def test_write_json_creates_parent_directory() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "nested" / "payload.json"
        main.write_json(path, {"ok": True})
        assert path.read_text(encoding="utf-8") == '{\n  "ok": true\n}\n'
        assert not list(path.parent.glob(".payload.json.*.tmp"))


def test_write_json_preserves_existing_file_when_payload_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "payload.json"
        path.write_text('{"old": true}\n', encoding="utf-8")
        try:
            main.write_json(path, {"bad": object()})
        except TypeError:
            pass
        else:
            raise AssertionError("expected non-JSON payload to fail")

        assert path.read_text(encoding="utf-8") == '{"old": true}\n'
        assert not list(path.parent.glob(".payload.json.*.tmp"))


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


def test_resolve_output_dir_accepts_expected_repository_dirs() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        assert main.resolve_output_dir(Path("results"), root) == (
            root / "results"
        ).resolve()
        assert main.resolve_output_dir(Path("google-scholar-stats"), root) == (
            root / "google-scholar-stats"
        ).resolve()


def test_resolve_output_dir_anchors_relative_paths_to_project_root() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "repo"
        root.mkdir()
        nested_cwd = Path(tmp) / "nested"
        nested_cwd.mkdir()
        old_cwd = Path.cwd()
        try:
            os.chdir(nested_cwd)
            assert main.resolve_output_dir(Path("results"), root) == (
                root / "results"
            ).resolve()
        finally:
            os.chdir(old_cwd)


def test_resolve_output_dir_accepts_external_dir() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "repo"
        output_dir = Path(tmp) / "external-scholar-output"

        assert main.resolve_output_dir(output_dir, root) == output_dir


def test_resolve_output_dir_rejects_untracked_repository_dir() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        try:
            main.resolve_output_dir(root / "tmp-scholar-output", root)
        except ValueError as exc:
            assert "results/" in str(exc)
            assert "google-scholar-stats/" in str(exc)
        else:
            raise AssertionError("expected untracked repository output dir to fail")


def test_write_author_outputs_uses_custom_badge_label() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        output_dir = Path(tmp)
        author = {"citedby": 123, "publications": {}}
        main.write_author_outputs(output_dir, author, "profile citations")
        shield = output_dir / "gs_data_shieldsio.json"
        assert '"label": "profile citations"' in shield.read_text(encoding="utf-8")


def test_write_author_outputs_rejects_malformed_author_payload() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        output_dir = Path(tmp)
        try:
            main.write_author_outputs(output_dir, {"publications": {}}, "citations")
        except ValueError as exc:
            assert "citedby" in str(exc)
        else:
            raise AssertionError("expected missing citedby to fail")

        try:
            main.write_author_outputs(
                output_dir,
                {"citedby": 123, "publications": []},
                "citations",
            )
        except ValueError as exc:
            assert "publications mapping" in str(exc)
        else:
            raise AssertionError("expected non-mapping publications to fail")

        assert not (output_dir / "gs_data.json").exists()
        assert not (output_dir / "gs_data_shieldsio.json").exists()


if __name__ == "__main__":
    for name, test_func in sorted(globals().items()):
        if name.startswith("test_") and callable(test_func):
            test_func()
