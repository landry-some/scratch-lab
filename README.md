# scratch-lab

`scratch` is a command-line tool for throwaway code playgrounds. `scratch new rust`
makes a fresh folder from a template in one place (`~/scratch`), so test files no
longer pile up in your home folder and real projects, and old ones can be cleaned out
later in one go.

It's for people who often try out a snippet, a library or a language feature in
a terminal and want an empty, runnable starting point for it.

Built with Python 3.11+ and the standard library only. Tests use pytest.

Work in progress: see [ROADMAP.md](ROADMAP.md).

## Install

```bash
git clone https://github.com/landry-some/scratch-lab.git
cd scratch-lab
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
```

## Usage

```bash
scratch new rust                 # ~/scratch/rust-20261103-140509, path printed
scratch new py regex-try         # pick the folder name yourself
cd "$(scratch new go)"           # make one and jump into it
scratch ls                       # all scratches, newest first
scratch path                     # path of the newest scratch
cd "$(scratch path regex)"       # path of the best name match
scratch keep regex-try           # protect it from clean
scratch unkeep regex-try
scratch clean                    # list unkept scratches older than 14 days
scratch clean --older 3d --yes   # really delete those older than 3 days
scratch templates                # which templates exist and where they come from
```

Example `scratch ls` output (`*` marks kept scratches):

```
   NAME                  LANG    AGE  SIZE
   go-20261103-140212    go      2m   190B
*  regex-try             python  3d   1.2K
   rust-20261021-091500  rust    13d  48.3M
```

### Where things live

- Scratches go in `$SCRATCH_HOME`, or `~/scratch` if it isn't set. Each one is a
  plain folder with a small `.scratch.json` file holding its language, creation time
  and kept flag. `ls`, `path` and `clean` ignore folders without that file, so
  nothing you put there by hand is ever deleted.
- `clean` only prints what it would delete unless you pass `--yes`. `--older` takes
  a number with `m`, `h`, `d` or `w` (minutes, hours, days, weeks).
- `path`, `keep` and `unkeep` take part of a name. An exact name wins, then names
  that start with it, then names that contain it, newest first. With no name they
  use the newest scratch.

### Templates

Built in: `python` (`py`), `rust` (`rs`), `go`, `js` (`node`), `sh` (`bash`) and `c`.
Each is a minimal "hello" program, and `{{name}}` in any text file is replaced with
the scratch's name (used for the package name in `Cargo.toml`, `go.mod` and
`package.json`).

To add a language or replace a built-in one, make a folder
`~/.config/scratch-lab/templates/<lang>/` (or under `$XDG_CONFIG_HOME`) with the
files you want copied. A user template with the same name as a built-in one wins.

## Test

```bash
pip install -e '.[test]'
pytest
```

## License

MIT, see [LICENSE](LICENSE).
