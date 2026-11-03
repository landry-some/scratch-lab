"""The work behind each subcommand, separate from argument parsing."""

from datetime import datetime

from . import store, templates


def new(lang, name=None, now=None):
    """Create a scratch from the language's template and return it."""
    template = templates.find(lang)
    lang = template.name
    now = now or datetime.now().replace(microsecond=0)
    root = store.home()
    root.mkdir(parents=True, exist_ok=True)
    if name is None:
        name = store.default_name(lang, now, root)
    store.check_name(name)
    dest = root / name
    if dest.exists():
        raise store.StoreError(f"scratch '{name}' already exists: {dest}")
    dest.mkdir()
    templates.render(template, dest, name)
    scratch = store.Scratch(name=name, path=dest, lang=lang, created=now)
    store.write_meta(scratch)
    return scratch
