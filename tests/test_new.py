import json
import os
from datetime import datetime

import pytest

from scratch_lab import cli, commands, store, templates

NOW = datetime(2026, 11, 3, 14, 5, 9)


def test_new_uses_lang_and_time_as_default_name(scratch_home):
    scratch = commands.new("rust", now=NOW)
    assert scratch.name == "rust-20261103-140509"
    assert scratch.path == scratch_home / scratch.name
    assert (scratch.path / "Cargo.toml").read_text().count('name = "rust-20261103-140509"') == 1
    assert "hello from rust-20261103-140509" in (scratch.path / "src" / "main.rs").read_text()


def test_new_writes_metadata(scratch_home):
    scratch = commands.new("python", "regex-try", now=NOW)
    meta = json.loads((scratch.path / store.META_FILE).read_text())
    assert meta == {"lang": "python", "created": "2026-11-03T14:05:09", "keep": False}
    assert store.read(scratch.path) == scratch


def test_alias_maps_to_template_name(scratch_home):
    assert commands.new("py", now=NOW).lang == "python"
    assert commands.new("bash", now=NOW).lang == "sh"


def test_same_second_gets_a_suffix(scratch_home):
    first = commands.new("go", now=NOW)
    second = commands.new("go", now=NOW)
    assert second.name == first.name + "-2"


def test_shell_template_is_executable(scratch_home):
    scratch = commands.new("sh", now=NOW)
    assert os.access(scratch.path / "main.sh", os.X_OK)


def test_existing_name_is_refused(scratch_home):
    commands.new("c", "probe", now=NOW)
    with pytest.raises(store.StoreError, match="already exists"):
        commands.new("c", "probe", now=NOW)


@pytest.mark.parametrize("name", ["../escape", "a/b", ".hidden", ""])
def test_bad_names_are_refused(scratch_home, name):
    with pytest.raises(store.StoreError, match="bad scratch name"):
        commands.new("python", name, now=NOW)


def test_unknown_language_lists_available(scratch_home):
    with pytest.raises(templates.TemplateError, match="available: c, go, js, python, rust, sh"):
        commands.new("cobol")


@pytest.mark.parametrize("lang", templates.available())
def test_every_builtin_template_fills_the_name(scratch_home, lang):
    scratch = commands.new(lang, "demo", now=NOW)
    files = [p for p in scratch.path.rglob("*") if p.is_file() and p.name != store.META_FILE]
    assert files
    for f in files:
        assert "{{name}}" not in f.read_text()


def test_cli_new_prints_path(scratch_home, capsys):
    assert cli.main(["new", "js", "fetch-test"]) == 0
    assert capsys.readouterr().out.strip() == str(scratch_home / "fetch-test")


def test_cli_new_error_goes_to_stderr(scratch_home, capsys):
    assert cli.main(["new", "cobol"]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err.startswith("scratch: no template for 'cobol'")
