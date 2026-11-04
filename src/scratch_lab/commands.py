"""The work behind each subcommand, separate from argument parsing."""

import os
import shlex
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from . import fmt, store, templates


def new(lang, name=None, now=None):
    """Create a scratch from the language's template and return it."""
    template = templates.find(lang)
    lang = template.name
    now = now or datetime.now()
    root = store.home()
    root.mkdir(parents=True, exist_ok=True)
    if name is None:
        name = store.default_name(lang, now, root)
    store.check_name(name)
    dest = root / name
    if dest.exists():
        raise store.StoreError(f"scratch '{name}' already exists: {dest}")
    dest.mkdir()
    templates.render(template, dest, {"name": name, "lang": lang, "date": f"{now:%Y-%m-%d}"})
    scratch = store.Scratch(name=name, path=dest, lang=lang, created=now)
    store.write_meta(scratch)
    return scratch


def open_editor(path):
    """Start $VISUAL (or $EDITOR) on path from inside it and wait. Returns its exit code."""
    editor = os.environ.get("VISUAL") or os.environ.get("EDITOR")
    if not editor:
        raise store.StoreError("set $VISUAL or $EDITOR to use --open")
    cmd = shlex.split(editor) + [str(path)]
    try:
        return subprocess.run(cmd, cwd=path).returncode
    except FileNotFoundError:
        raise store.StoreError(f"editor not found: {cmd[0]}") from None


def listing(now=None):
    """The `scratch ls` table as text, or a hint if there are no scratches."""
    now = now or datetime.now()
    scratches = store.all_scratches()
    if not scratches:
        return f"no scratches in {store.home()} yet (try: scratch new python)"
    notes = any(s.note for s in scratches)
    rows = [("", "NAME", "LANG", "AGE", "SIZE") + (("NOTE",) if notes else ())]
    for s in scratches:
        row = (
            "*" if s.keep else "",
            s.name,
            s.lang,
            fmt.age((now - s.created).total_seconds()),
            fmt.size(store.size_of(s.path)),
        )
        rows.append(row + ((s.note,) if notes else ()))
    return fmt.table(rows)


def set_keep(query, keep):
    """Mark a scratch as kept (clean skips it) or not, and return it."""
    scratch = store.find(query)
    scratch.keep = keep
    store.write_meta(scratch)
    return scratch


def set_note(query, text):
    """Give a scratch a one-line note (empty text removes it) and return it."""
    scratch = store.find(query)
    scratch.note = " ".join(text.split())
    store.write_meta(scratch)
    return scratch


def promote(query, dest):
    """Move a scratch to dest (or into dest if it is a folder) and drop its metadata.

    Returns the new path. After this it is a plain folder, no longer a scratch.
    """
    scratch = store.find(query)
    dest = Path(dest).expanduser().absolute()
    if dest.is_dir():
        dest = dest / scratch.name
    if dest.exists():
        raise store.StoreError(f"{dest} already exists")
    if not dest.parent.is_dir():
        raise store.StoreError(f"folder {dest.parent} does not exist")
    if dest.is_relative_to(scratch.path.absolute()):
        raise store.StoreError(f"cannot move {scratch.name} into itself")
    shutil.move(scratch.path, dest)
    (dest / store.META_FILE).unlink(missing_ok=True)
    return dest


def stale(older, now=None):
    """Scratches that are not kept and were created more than `older` ago."""
    now = now or datetime.now()
    return [s for s in store.all_scratches() if not s.keep and now - s.created > older]


def clean(older, really, now=None):
    """Remove stale scratches if really is True. Returns the affected scratches."""
    victims = stale(older, now)
    if really:
        for s in victims:
            shutil.rmtree(s.path)
    return victims
