"""Command-line entry point for `scratch`."""

import argparse
import sys

from . import __version__, commands, store, templates


def build_parser():
    parser = argparse.ArgumentParser(
        prog="scratch",
        description="Make throwaway code playgrounds and clean them up later.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p_new = sub.add_parser("new", help="make a scratch from a template, print its path")
    p_new.add_argument("lang", help="template language, e.g. python, rust, go, js, sh, c")
    p_new.add_argument("name", nargs="?", help="folder name (default: <lang>-<date-time>)")

    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        if args.command == "new":
            scratch = commands.new(args.lang, args.name)
            print(scratch.path)
    except (store.StoreError, templates.TemplateError) as err:
        print(f"scratch: {err}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
