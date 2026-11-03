from datetime import datetime

from scratch_lab import cli, commands, templates

NOW = datetime(2026, 11, 3, 12, 0, 0)


def make_user_template(lang, files):
    root = templates.user_dir() / lang
    root.mkdir(parents=True, exist_ok=True)
    for rel, text in files.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text)
    return root


def test_user_dir_follows_xdg(scratch_home, tmp_path):
    assert templates.user_dir() == tmp_path / "config" / "scratch-lab" / "templates"


def test_user_dir_defaults_to_dot_config(monkeypatch, tmp_path):
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))
    assert templates.user_dir() == tmp_path / ".config" / "scratch-lab" / "templates"


def test_user_template_adds_a_language(scratch_home):
    make_user_template("ts", {"index.ts": "console.log('{{name}}')\n", "lib/util.ts": "// {{name}}\n"})
    scratch = commands.new("ts", "typed", now=NOW)
    assert scratch.lang == "ts"
    assert (scratch.path / "index.ts").read_text() == "console.log('typed')\n"
    assert (scratch.path / "lib" / "util.ts").read_text() == "// typed\n"
    assert "ts" in templates.available()


def test_user_template_overrides_builtin(scratch_home):
    make_user_template("python", {"play.py": "# {{name}}\n"})
    scratch = commands.new("py", "mine", now=NOW)
    assert (scratch.path / "play.py").exists()
    assert not (scratch.path / "main.py").exists()


def test_binary_files_are_copied_as_is(scratch_home):
    root = make_user_template("blob", {})
    (root / "data.bin").write_bytes(b"\xff\xfe{{name}}\x00")
    scratch = commands.new("blob", "b", now=NOW)
    assert (scratch.path / "data.bin").read_bytes() == b"\xff\xfe{{name}}\x00"


def test_cli_templates_shows_sources(scratch_home, capsys):
    root = make_user_template("python", {"main.py": ""})
    assert cli.main(["templates"]) == 0
    out = capsys.readouterr().out
    assert f"python  {root}" in out
    assert "rust    built-in" in out
    assert str(templates.user_dir()) in out
