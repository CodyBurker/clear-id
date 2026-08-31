"""Command-line interface: ``python -m clear_id "some string"``."""

from __future__ import annotations

import argparse
import sys

from .digest import capacity, phrase_id, phrase_space


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="clear-id",
        description="Digest a string into a memorable adjective-adjective-noun phrase.",
    )
    parser.add_argument("text", nargs="*", help="strings to digest (default: read lines from stdin)")
    parser.add_argument("-a", "--adjectives", type=int, default=2, help="number of adjectives (default 2)")
    parser.add_argument("-s", "--separator", default="-", help="word separator (default '-')")
    parser.add_argument(
        "--stats",
        action="store_true",
        help="print the phrase-space size and 0.01%% collision capacity instead",
    )
    args = parser.parse_args(argv)

    if args.stats:
        space = phrase_space(args.adjectives)
        print(f"phrase space: {space:,}")
        print(f"capacity at 0.01% collision probability: {capacity(0.0001, adjectives=args.adjectives):,}")
        return 0

    inputs = args.text or (line.rstrip("\n") for line in sys.stdin)
    for text in inputs:
        print(phrase_id(text, adjectives=args.adjectives, separator=args.separator))
    return 0


if __name__ == "__main__":
    sys.exit(main())
