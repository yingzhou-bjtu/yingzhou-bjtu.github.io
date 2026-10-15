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


def test_index_publications_preserves_each_unique_record() -> None:
    publications = [
        {"author_pub_id": "paper-a", "title": "A"},
        {"author_pub_id": "paper-b", "title": "B"},
    ]

    indexed = main.index_publications(publications)

    assert list(indexed) == ["paper-a", "paper-b"]
    assert indexed["paper-a"]["title"] == "A"
    assert indexed["paper-a"] is not publications[0]


def test_index_publications_rejects_missing_ids_and_duplicates() -> None:
    for publications, message in (
        ([{"title": "missing"}], "missing author_pub_id"),
        (
            [
                {"author_pub_id": "duplicate", "title": "A"},
                {"author_pub_id": "duplicate", "title": "B"},
            ],
            "Duplicate Scholar author_pub_id",
        ),
        ([{"author_pub_id": ""}], "missing author_pub_id"),
        (["not-an-object"], "must be an object"),
        ({"author_pub_id": "not-a-list"}, "must be a list"),
    ):
        try:
            main.index_publications(publications)
        except ValueError as exc:
            assert message in str(exc)
        else:
            raise AssertionError(f"expected publication payload to fail: {publications!r}")


def test_crawler_config_normalizes_direct_values() -> None:
    config = main.CrawlerConfig(
        scholar_id="  abc123  ",
        output_dir="results",
        badge_label="  citations  ",
    )

    assert config.scholar_id == "abc123"
    assert config.output_dir == Path("results")
    assert config.badge_label == "citations"


def test_crawler_config_rejects_invalid_direct_values() -> None:
    for overrides, message in (
        ({"scholar_id": 1}, "must be a string"),
        ({"scholar_id": "a b"}, "must not contain whitespace"),
        ({"badge_label": 1}, "Badge label must be a string"),
        ({"badge_label": "bad\nlabel"}, "must not contain newlines"),
        ({"output_dir": 1}, "must be a filesystem path"),
    ):
        values = {
            "scholar_id": "abc123",
            "output_dir": Path("results"),
            "badge_label": "citations",
        }
        values.update(overrides)
        try:
            main.CrawlerConfig(**values)
        except ValueError as exc:
            assert message in str(exc)
        else:
            raise AssertionError(f"invalid crawler config was accepted: {overrides}")


def test_write_author_outputs_rejects_invalid_direct_badge_label() -> None:
    author = {"citedby": 7, "publications": {}}
    with tempfile.TemporaryDirectory(prefix="scholar-output-label-") as temporary:
        output_dir = Path(temporary)
        try:
            main.write_author_outputs(output_dir, author, "bad\nlabel")
        except ValueError as exc:
            assert "newlines" in str(exc)
        else:
            raise AssertionError("invalid badge label was accepted")
        assert not (output_dir / "gs_data.json").exists()
        assert not (output_dir / "gs_data_shieldsio.json").exists()


if __name__ == "__main__":
    for name, test_func in sorted(globals().items()):
        if name.startswith("test_") and callable(test_func):
            test_func()
