import json
from datetime import datetime, timedelta

import pytest

from scratch_lab import cli, commands, store

NOW = datetime(2026, 11, 3, 12, 0, 0)


@pytest.fixture
def two(scratch_home):
    commands.new("python", "regex-try", now=NOW - timedelta(days=1))
    commands.new("go", "chan-test", now=NOW)


def test_note_is_stored_and_read_back(two):
    commands.set_note("regex", "lookbehind  with\nnamed groups")
    s = store.find("regex-try")
    assert s.note == "lookbehind with named groups"
    assert json.loads((s.path / store.META_FILE).read_text())["note"] == s.note


def test_empty_note_removes_it(two):
    commands.set_note("regex", "temp")
    commands.set_note("regex", "")
    s = store.find("regex-try")
    assert s.note == ""
    assert "note" not in json.loads((s.path / store.META_FILE).read_text())


def test_ls_shows_note_column_only_when_needed(two):
    assert "NOTE" not in commands.listing(now=NOW)
    commands.set_note("regex", "lookbehind")
    lines = commands.listing(now=NOW).splitlines()
    assert lines[0].split() == ["NAME", "LANG", "AGE", "SIZE", "NOTE"]
    assert lines[1].split()[0] == "chan-test" and len(lines[1].split()) == 4
    assert lines[2].endswith("  lookbehind")


def test_note_keeps_keep_flag(two):
    commands.set_keep("chan", True)
    commands.set_note("chan", "buffered")
    assert store.find("chan").keep


def test_cli_note(two, capsys):
    assert cli.main(["note", "chan", "select loop"]) == 0
    assert capsys.readouterr().out.strip() == "noted: chan-test"
    assert cli.main(["note", "chan", ""]) == 0
    assert capsys.readouterr().out.strip() == "note removed: chan-test"
    assert cli.main(["note", "zzz", "x"]) == 1
    assert "no scratch matches 'zzz'" in capsys.readouterr().err
