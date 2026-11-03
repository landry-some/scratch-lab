"""Find language templates and copy them into a new scratch folder."""

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


def template_dirs():
    """Folders that hold one subfolder per language."""
    return [BUILTIN_DIR]


def available():
    """Sorted names of every language that has a template."""
    names = set()
    for base in template_dirs():
        if base.is_dir():
            names.update(p.name for p in base.iterdir() if p.is_dir())
    return sorted(names)


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
