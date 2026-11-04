from datetime import datetime

import pytest

from scratch_lab import cli, commands, store

NOW = datetime(2026, 11, 3, 12, 0, 0)


@pytest.fixture
def scratch(scratch_home):
    s = commands.new("rust", "parser-try", now=NOW)
    (s.path / "notes.txt").write_text("keep me\n")
    return s


def test_promote_to_new_path_drops_metadata(scratch, tmp_path):
    dest = tmp_path / "code" / "parser"
    dest.parent.mkdir()
    assert commands.promote("parser", dest) == dest
    assert not scratch.path.exists()
    assert (dest / "Cargo.toml").exists()
    assert (dest / "notes.txt").read_text() == "keep me\n"
    assert not (dest / store.META_FILE).exists()
    assert store.all_scratches() == []


def test_promote_into_existing_folder_keeps_name(scratch, tmp_path):
    code = tmp_path / "code"
    code.mkdir()
    assert commands.promote("parser", code) == code / "parser-try"
    assert (code / "parser-try" / "src" / "main.rs").exists()


def test_promote_refuses_to_overwrite(scratch, tmp_path):
    (tmp_path / "code" / "parser-try").mkdir(parents=True)
    with pytest.raises(store.StoreError, match="already exists"):
        commands.promote("parser", tmp_path / "code")
    assert scratch.path.is_dir()


def test_promote_needs_an_existing_parent(scratch, tmp_path):
    with pytest.raises(store.StoreError, match="does not exist"):
        commands.promote("parser", tmp_path / "no" / "such" / "place")
    assert scratch.path.is_dir()


def test_promote_into_itself_is_refused(scratch):
    with pytest.raises(store.StoreError, match="into itself"):
        commands.promote("parser", scratch.path / "src")
    assert store.read(scratch.path) is not None


def test_cli_promote_prints_new_path(scratch, tmp_path, capsys):
    dest = tmp_path / "parser"
    assert cli.main(["promote", "parser", str(dest)]) == 0
    assert capsys.readouterr().out.strip() == str(dest)
    assert cli.main(["promote", "parser", str(dest)]) == 1
    assert "no scratches in" in capsys.readouterr().err
