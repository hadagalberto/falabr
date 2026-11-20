"""Command-line interface for falabr.

The CLI goes through the very same composed pipeline as the Python API, so a
sentence spoken on the command line is byte-for-byte identical to
``falabr.normalize``.  It supports positional text, ``-f/--file``, stdin,
``--ssml``, ``--json`` spans, sentence chunking, and the grammar options
exposed by :class:`Options`.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence

from .entities import normalize, normalize_ssml, normalize_with_spans, split_sentences
from .options import CatorzeStyle, DecimalMode, EmojiMode, Options, PhoneStyle, RomanContext

__all__ = ["build_parser", "main"]


def build_parser() -> argparse.ArgumentParser:
    """Construct the argument parser (kept separate for testability)."""
    parser = argparse.ArgumentParser(
        prog="falabr",
        description="Normalize Brazilian Portuguese text for text-to-speech.",
    )
    parser.add_argument("text", nargs="*", help="text to normalize; omitted means stdin")
    parser.add_argument("-f", "--file", metavar="PATH", help="read text from a file")

    output = parser.add_mutually_exclusive_group()
    output.add_argument("--json", action="store_true", help="emit original→spoken spans as JSON")
    output.add_argument("--ssml", action="store_true", help="wrap output in SSML")
    output.add_argument("--sentences", action="store_true", help="print one TTS chunk per line")

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
    parser.add_argument(
        "--phone-style",
        choices=[style.value for style in PhoneStyle],
        default=PhoneStyle.NATURAL.value,
        help="how phone numbers are voiced (digits, pairs or natural)",
    )
    parser.add_argument(
        "--digit-group-separator",
        metavar="TEXT",
        default=",",
        help="pause marker between digit groups (default: comma)",
    )
    parser.add_argument(
        "--acronym-override",
        metavar="KEY=VALUE",
        action="append",
        default=[],
        help="acronym reading override; repeatable (VALUE may be spell or word)",
    )
    parser.add_argument(
        "--user-lexicon",
        metavar="KEY=VALUE",
        action="append",
        default=[],
        help="user dictionary entry; repeatable",
    )
    parser.add_argument(
        "--max-chars",
        type=int,
        metavar="N",
        default=None,
        help="maximum characters per chunk with --sentences",
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


def _parse_pairs(items: list[str], flag: str) -> dict[str, str]:
    """Parse repeatable ``KEY=VALUE`` flags."""
    result: dict[str, str] = {}
    for item in items:
        key, separator, value = item.partition("=")
        if not separator or not key:
            raise ValueError(f"{flag} expects KEY=VALUE, got {item!r}")
        result[key] = value
    return result


def _options_from_args(args: argparse.Namespace) -> Options:
    """Translate CLI flags into the immutable :class:`Options` bundle."""
    return Options(
        catorze_style=CatorzeStyle.CATORZE if args.catorze else CatorzeStyle.QUATORZE,
        decimal_mode=DecimalMode(args.decimal_mode),
        emoji_mode=EmojiMode(args.emoji_mode),
        roman_context=RomanContext(args.roman_context),
        phone_style=PhoneStyle(args.phone_style),
        digit_group_separator=args.digit_group_separator,
        acronym_overrides=_parse_pairs(args.acronym_override, "--acronym-override"),
        user_lexicon=_parse_pairs(args.user_lexicon, "--user-lexicon"),
    )


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point for the ``falabr`` console script."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        options = _options_from_args(args)
    except ValueError as exc:
        parser.error(str(exc))
    text = _read_text(args)

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
    elif args.sentences:
        spoken = normalize(text, options)
        for chunk in split_sentences(spoken, args.max_chars):
            print(chunk)
    else:
        print(normalize(text, options))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
