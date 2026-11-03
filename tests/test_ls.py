from datetime import datetime, timedelta

from scratch_lab import cli, commands, fmt, store

NOW = datetime(2026, 11, 3, 12, 0, 0)


def test_age_units():
    assert fmt.age(5) == "5s"
    assert fmt.age(60 * 12) == "12m"
    assert fmt.age(3600 * 3 + 59) == "3h"
    assert fmt.age(86400 * 5) == "5d"
    assert fmt.age(-3) == "0s"


def test_size_units():
    assert fmt.size(812) == "812B"
    assert fmt.size(4096) == "4.0K"
    assert fmt.size(int(1.5 * 1024**2)) == "1.5M"


def test_listing_is_newest_first_and_marks_kept(scratch_home):
    old = commands.new("python", "old-one", now=NOW - timedelta(days=3))
    commands.new("rust", "new-one", now=NOW - timedelta(minutes=10))
    old.keep = True
    store.write_meta(old)

    lines = commands.listing(now=NOW).splitlines()
    assert lines[0].split() == ["NAME", "LANG", "AGE", "SIZE"]
    assert lines[1].split()[:3] == ["new-one", "rust", "10m"]
    assert lines[2].split()[:4] == ["*", "old-one", "python", "3d"]


def test_listing_skips_folders_without_metadata(scratch_home):
    commands.new("go", "real", now=NOW)
    (scratch_home / "made-by-hand").mkdir()
    assert [s.name for s in store.all_scratches()] == ["real"]


def test_size_counts_files(scratch_home):
    s = commands.new("python", "sized", now=NOW)
    before = store.size_of(s.path)
    (s.path / "data.bin").write_bytes(b"x" * 2000)
    assert store.size_of(s.path) == before + 2000


def test_empty_listing_gives_a_hint(scratch_home, capsys):
    assert cli.main(["ls"]) == 0
    assert "no scratches in" in capsys.readouterr().out
