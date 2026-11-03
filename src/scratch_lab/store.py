"""Where scratches live and what we remember about each one."""

import json
import os
import re
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
        "created": scratch.created.isoformat(timespec="seconds"),
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
