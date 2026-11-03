from datetime import datetime, timedelta

import pytest

from scratch_lab import cli, commands, fmt, store

NOW = datetime(2026, 11, 3, 12, 0, 0)


def test_parse_duration():
    assert fmt.parse_duration("30m") == timedelta(minutes=30)
    assert fmt.parse_duration("12H") == timedelta(hours=12)
    assert fmt.parse_duration("14d") == timedelta(days=14)
    assert fmt.parse_duration("2w") == timedelta(weeks=2)
    for bad in ("", "14", "d", "1.5d", "-2d", "3y"):
        with pytest.raises(ValueError):
            fmt.parse_duration(bad)


@pytest.fixture
def mixed(scratch_home):
    commands.new("python", "ancient", now=NOW - timedelta(days=30))
    commands.new("python", "precious", now=NOW - timedelta(days=40))
    commands.new("go", "fresh", now=NOW - timedelta(days=1))
    commands.set_keep("precious", True)
    return scratch_home


def test_keep_and_unkeep_toggle_metadata(mixed):
    assert store.find("precious").keep
    commands.set_keep("precious", False)
    assert not store.find("precious").keep


def test_stale_skips_kept_and_recent(mixed):
    assert [s.name for s in commands.stale(timedelta(days=14), now=NOW)] == ["ancient"]


def test_clean_without_really_deletes_nothing(mixed):
    victims = commands.clean(timedelta(days=14), really=False, now=NOW)
    assert [s.name for s in victims] == ["ancient"]
    assert (mixed / "ancient").is_dir()


def test_clean_really_deletes_only_stale(mixed):
    commands.clean(timedelta(days=14), really=True, now=NOW)
    assert sorted(p.name for p in mixed.iterdir()) == ["fresh", "precious"]


def test_clean_leaves_folders_without_metadata(mixed):
    (mixed / "made-by-hand").mkdir()
    commands.clean(timedelta(0), really=True, now=NOW)
    assert sorted(p.name for p in mixed.iterdir()) == ["made-by-hand", "precious"]


def test_cli_clean_dry_run_then_yes(scratch_home, capsys):
    s = commands.new("c", "old-c", now=datetime.now() - timedelta(days=20))
    assert cli.main(["clean"]) == 0
    out = capsys.readouterr().out
    assert "would remove: old-c" in out and "--yes" in out
    assert s.path.exists()
    assert cli.main(["clean", "--yes"]) == 0
    assert "removed: old-c" in capsys.readouterr().out
    assert not s.path.exists()


def test_cli_clean_bad_duration(scratch_home, capsys):
    assert cli.main(["clean", "--older", "soon"]) == 1
    assert "bad duration 'soon'" in capsys.readouterr().err


def test_cli_keep_prints_name(mixed, capsys):
    assert cli.main(["keep", "anc"]) == 0
    assert capsys.readouterr().out.strip() == "kept: ancient"
    assert cli.main(["unkeep", "anc"]) == 0
    assert capsys.readouterr().out.strip() == "no longer kept: ancient"
