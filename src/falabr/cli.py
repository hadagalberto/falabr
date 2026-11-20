"""Command-line interface for falabr.

The CLI goes through the very same composed pipeline as the Python API, so a
sentence spoken on the command line is byte-for-byte identical to
``falabr.normalize``.  It supports positional text, ``-f/--file``, stdin,
``--ssml``, ``--json`` spans, and the grammar options exposed by :class:`Options`.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence

from .entities import normalize, normalize_ssml, normalize_with_spans
from .options import CatorzeStyle, DecimalMode, EmojiMode, Options, RomanContext

__all__ = ["build_parser", "main"]


def build_parser() -> argparse.ArgumentParser:
    """Construct the argument parser (kept separate for testability)."""
    parser = argparse.ArgumentParser(
        prog="falabr",
        description="Normalize Brazilian Portuguese text for text-to-speech.",
    )
    parser.add_argument("text", nargs="*", help="text to normalize; omitted means stdin")
    parser.add_argument("-f", "--file", metavar="PATH", help="read text from a file")
    parser.add_argument("--json", action="store_true", help="emit original→spoken spans as JSON")
    parser.add_argument("--ssml", action="store_true", help="wrap output in SSML")
    parser.add_argument(
        "--catorze", action="store_true", help="use 'catorze' instead of 'quatorze'"
    )
    parser.add_argument(
        "--decimal-mode",
        choices=[mode.value for mode in DecimalMode],
        default=DecimalMode.CARDINAL.value,
        help="read decimals as a cardinal or digit by digit",
    )
    parser.add_argument(
        "--emoji-mode",
        choices=[mode.value for mode in EmojiMode],
        default=EmojiMode.REMOVE.value,
        help="remove emoji or describe them in Portuguese",
    )
    parser.add_argument(
        "--roman-context",
        choices=[context.value for context in RomanContext],
        default=RomanContext.CARDINAL.value,
        help="how roman numerals are voiced (regnal for kings and popes)",
    )
    return parser


def _read_text(args: argparse.Namespace) -> str:
    """Resolve the input text from a file, positional arguments, or stdin."""
    if args.file is not None:
        with open(args.file, encoding="utf-8") as handle:
            return handle.read()
    if args.text:
        return " ".join(args.text)
    return sys.stdin.read()


def _options_from_args(args: argparse.Namespace) -> Options:
    """Translate CLI flags into the immutable :class:`Options` bundle."""
    return Options(
        catorze_style=CatorzeStyle.CATORZE if args.catorze else CatorzeStyle.QUATORZE,
        decimal_mode=DecimalMode(args.decimal_mode),
        emoji_mode=EmojiMode(args.emoji_mode),
        roman_context=RomanContext(args.roman_context),
    )


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point for the ``falabr`` console script."""
    args = build_parser().parse_args(argv)
    text = _read_text(args)
    options = _options_from_args(args)

    if args.json:
        result = normalize_with_spans(text, options)
        payload = {
            "text": result.text,
            "spans": [
                {
                    "start": span.start,
                    "end": span.end,
                    "original": span.original,
                    "spoken": span.spoken,
                    "kind": span.kind,
                }
                for span in result.spans
            ],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    elif args.ssml:
        print(normalize_ssml(text, options))
    else:
        print(normalize(text, options))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
