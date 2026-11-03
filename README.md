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

## Test

```bash
pip install -e '.[test]'
pytest
```

## License

MIT, see [LICENSE](LICENSE).
