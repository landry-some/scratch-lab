"""Find language templates and copy them into a new scratch folder."""

import os
from pathlib import Path

BUILTIN_DIR = Path(__file__).parent / "templates"

ALIASES = {
    "py": "python",
    "rs": "rust",
    "golang": "go",
    "node": "js",
    "javascript": "js",
    "bash": "sh",
    "shell": "sh",
}


class TemplateError(Exception):
    pass


def canonical(lang):
    lang = lang.lower()
    return ALIASES.get(lang, lang)


def user_dir():
    """$XDG_CONFIG_HOME/scratch-lab/templates, or ~/.config/scratch-lab/templates."""
    config = os.environ.get("XDG_CONFIG_HOME")
    base = Path(config).expanduser() if config else Path.home() / ".config"
    return base / "scratch-lab" / "templates"


def template_dirs():
    """Folders that hold one subfolder per language. Earlier ones win."""
    return [user_dir(), BUILTIN_DIR]


def sources():
    """[(language, template folder)] for every usable template, sorted by language."""
    found = {}
    for base in template_dirs():
        if base.is_dir():
            for p in base.iterdir():
                if p.is_dir():
                    found.setdefault(p.name, p)
    return sorted(found.items())


def available():
    """Sorted names of every language that has a template."""
    return [name for name, _ in sources()]


def find(lang):
    """Return the template folder for a language, or raise TemplateError."""
    lang = canonical(lang)
    for base in template_dirs():
        candidate = base / lang
        if candidate.is_dir():
            return candidate
    raise TemplateError(
        f"no template for '{lang}' (available: {', '.join(available())})"
    )


def render(template, dest, name):
    """Copy a template folder into dest, filling in {{name}} in text files."""
    for src in sorted(template.rglob("*")):
        if "__pycache__" in src.parts:
            continue
        target = dest / src.relative_to(template)
        if src.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        data = src.read_bytes()
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            target.write_bytes(data)
        else:
            target.write_text(text.replace("{{name}}", name), encoding="utf-8")
        mode = src.stat().st_mode & 0o777
        if src.suffix == ".sh":
            mode |= 0o111
        target.chmod(mode)
