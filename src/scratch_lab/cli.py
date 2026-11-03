"""Command-line entry point for `scratch`."""

import argparse
import sys

from . import __version__, commands, fmt, store, templates


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

    sub.add_parser("ls", help="list scratches, newest first (* = kept)")

    p_path = sub.add_parser("path", help="print the path of the newest or a matching scratch")
    p_path.add_argument("query", nargs="?", help="name or part of a name (default: newest)")

    for name, text in (("keep", "protect a scratch from clean"), ("unkeep", "let clean remove it again")):
        p_keep = sub.add_parser(name, help=text)
        p_keep.add_argument("query", nargs="?", help="name or part of a name (default: newest)")

    p_clean = sub.add_parser("clean", help="remove old scratches that are not kept")
    p_clean.add_argument("--older", default="14d", metavar="AGE",
                         help="only scratches older than this, e.g. 12h, 14d, 2w (default: 14d)")
    p_clean.add_argument("--yes", action="store_true",
                         help="really delete; without it the list is only printed")

    return parser


def run_clean(args):
    older = fmt.parse_duration(args.older)
    victims = commands.clean(older, really=args.yes)
    if not victims:
        print(f"nothing older than {args.older} to remove")
        return 0
    verb = "removed" if args.yes else "would remove"
    for s in victims:
        print(f"{verb}: {s.name}")
    if not args.yes:
        print(f"{len(victims)} scratch(es). Run again with --yes to delete them.")
    return 0


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        if args.command == "new":
            scratch = commands.new(args.lang, args.name)
            print(scratch.path)
        elif args.command == "ls":
            print(commands.listing())
        elif args.command == "path":
            print(store.find(args.query).path)
        elif args.command in ("keep", "unkeep"):
            scratch = commands.set_keep(args.query, args.command == "keep")
            print(f"{'kept' if scratch.keep else 'no longer kept'}: {scratch.name}")
        elif args.command == "clean":
            return run_clean(args)
    except (store.StoreError, templates.TemplateError, ValueError) as err:
        print(f"scratch: {err}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
