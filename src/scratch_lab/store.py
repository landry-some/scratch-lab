"""Where scratches live and what we remember about each one."""

import json
import os
import re
import stat
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

META_FILE = ".scratch.json"
NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


class StoreError(Exception):
    pass


@dataclass
class Scratch:
    name: str
    path: Path
    lang: str
    created: datetime
    keep: bool = False


def home():
    """The folder all scratches go in: $SCRATCH_HOME or ~/scratch."""
    env = os.environ.get("SCRATCH_HOME")
    return Path(env).expanduser() if env else Path.home() / "scratch"


def check_name(name):
    if not NAME_RE.match(name):
        raise StoreError(
            f"bad scratch name '{name}': use letters, digits, '.', '_' and '-' "
            "and start with a letter or digit"
        )


def default_name(lang, now, root):
    """<lang>-<YYYYMMDD-HHMMSS>, with -2, -3, ... if that folder exists."""
    base = f"{lang}-{now:%Y%m%d-%H%M%S}"
    name, n = base, 2
    while (root / name).exists():
        name, n = f"{base}-{n}", n + 1
    return name


def write_meta(scratch):
    data = {
        "lang": scratch.lang,
        "created": scratch.created.isoformat(
            timespec="microseconds" if scratch.created.microsecond else "seconds"
        ),
        "keep": scratch.keep,
    }
    (scratch.path / META_FILE).write_text(json.dumps(data, indent=2) + "\n")


def read(path):
    """Load the Scratch stored in a folder, or None if it has no metadata."""
    try:
        data = json.loads((path / META_FILE).read_text())
        return Scratch(
            name=path.name,
            path=path,
            lang=data["lang"],
            created=datetime.fromisoformat(data["created"]),
            keep=bool(data.get("keep", False)),
        )
    except (OSError, ValueError, KeyError, TypeError):
        return None


def all_scratches():
    """Every scratch under home(), newest first. Folders without metadata are skipped."""
    root = home()
    if not root.is_dir():
        return []
    found = []
    for path in root.iterdir():
        if path.is_dir() and not path.is_symlink():
            scratch = read(path)
            if scratch is not None:
                found.append(scratch)
    found.sort(key=lambda s: (s.created, s.name), reverse=True)
    return found


def size_of(path):
    """Total bytes of the regular files below path, not following symlinks."""
    total = 0
    for dirpath, _dirs, files in os.walk(path):
        for f in files:
            try:
                st = os.lstat(os.path.join(dirpath, f))
            except OSError:
                continue
            if stat.S_ISREG(st.st_mode):
                total += st.st_size
    return total


def find(query=None):
    """Pick one scratch: the newest, or the newest whose name matches query.

    An exact name wins, then names starting with query, then names containing it.
    """
    scratches = all_scratches()
    if not scratches:
        raise StoreError(f"no scratches in {home()}")
    if not query:
        return scratches[0]
    q = query.lower()
    for test in (
        lambda n: n == q,
        lambda n: n.startswith(q),
        lambda n: q in n,
    ):
        hits = [s for s in scratches if test(s.name.lower())]
        if hits:
            return hits[0]
    raise StoreError(f"no scratch matches '{query}'")
