# Roadmap

v0.1 covers `new`, `ls`, `path`, `keep`/`unkeep`, `clean` and user templates.
Everything below is planned follow-up work. Total estimate: **27 h**.

## Features

- [x] `scratch new --open`: start `$EDITOR` (or `$VISUAL`) in the new scratch (1.5 h)
- [ ] `scratch run [query]`: run the scratch with a per-language command
      (`python main.py`, `cargo run`, `go run .`, ...) set in the template (3 h)
- [ ] `scratch promote <query> <dest>`: move a scratch out into a real project folder
      and drop its metadata (2 h)
- [ ] `scratch note <query> "text"`: one-line note per scratch, shown in `ls` (1.5 h)
- [ ] `scratch new --from <file>`: start a scratch from an existing file (1 h)
- [x] Template variables beyond `{{name}}`: `{{date}}`, `{{lang}}` (1 h)
- [ ] `scratch mv <old> <new>`: rename a scratch and update the name inside
      `Cargo.toml`, `go.mod` and `package.json` (2 h)
- [ ] Shell completion for bash and zsh, including scratch names (2.5 h)

## Bugs and edge cases

- [ ] Handle scratch folders created or renamed by hand (no metadata file) in `ls`
      and `clean` (1.5 h)
- [ ] `clean` on symlinked scratch folders and read-only files (1.5 h)
- [ ] Windows paths and `%USERPROFILE%` as the default home (2 h)

## Refactors

- [ ] Move the metadata file read/write into one small store module with a version
      field, so the format can change later (1.5 h)

## Tests

- [ ] End-to-end tests that run the installed `scratch` command in a temp home (1.5 h)
- [ ] Tests for every built-in template: files exist and `{{name}}` is filled (1 h)
- [ ] CI on GitHub Actions for Linux and macOS, Python 3.11 to 3.13 (1.5 h)

## Docs

- [ ] README section on writing your own templates, with an example (1 h)
- [ ] `--help` text examples for each subcommand (0.5 h)
- [ ] CHANGELOG.md and a tagged v0.1.0 release (0.5 h)
