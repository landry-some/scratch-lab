from datetime import datetime, timedelta

import pytest

from scratch_lab import cli, commands, store

NOW = datetime(2026, 11, 3, 12, 0, 0)


@pytest.fixture
def three(scratch_home):
    commands.new("python", "regex-old", now=NOW - timedelta(days=2))
    commands.new("python", "regex", now=NOW - timedelta(days=1))
    commands.new("rust", "my-regex-rs", now=NOW)


def test_no_query_gives_newest(three):
    assert store.find().name == "my-regex-rs"


def test_exact_name_beats_newer_prefix_match(three):
    assert store.find("regex").name == "regex"


def test_prefix_beats_substring(three):
    assert store.find("rege").name == "regex"


def test_substring_match_and_case(three):
    assert store.find("REGEX-RS").name == "my-regex-rs"
    assert store.find("-old").name == "regex-old"


def test_no_match_is_an_error(three):
    with pytest.raises(store.StoreError, match="no scratch matches 'zzz'"):
        store.find("zzz")


def test_empty_home_is_an_error(scratch_home):
    with pytest.raises(store.StoreError, match="no scratches in"):
        store.find()


def test_cli_path(three, scratch_home, capsys):
    assert cli.main(["path", "old"]) == 0
    assert capsys.readouterr().out.strip() == str(scratch_home / "regex-old")
    assert cli.main(["path", "nope"]) == 1
    assert "no scratch matches 'nope'" in capsys.readouterr().err


def test_newest_is_last_made_even_within_one_second(scratch_home):
    for lang in ("rust", "python", "go"):
        commands.new(lang)
    assert store.find().lang == "go"
    assert [s.lang for s in store.all_scratches()] == ["go", "python", "rust"]
