"""Command-line interface for falabr.

Milestone 1 exposes a number-focused CLI: it finds numeric tokens in the
input and spells them out, optionally emitting spans for TTS alignment.
Later milestones plug the full ``normalize`` pipeline into the same entry
point.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Sequence
from typing import cast
from xml.sax.saxutils import escape

from .numbers import RomanContext, spell_fraction, spell_number, spell_ordinal, spell_roman
from .options import CatorzeStyle, DecimalMode, Gender, Options

_TOKEN_RE = re.compile(
    r"(?P<fraction>\d+\s*/\s*\d+)"
    r"|(?P<ordinal>\d+\s*[ºª])"
    r"|(?P<decimal>\d[\d.]*,\d+)"
    r"|(?P<integer>\d{1,3}(?:\.\d{3})+|\d+)"
    r"|(?P<roman>\b[IVXLCDM]{2,8}\b)"
)


def _spoken_for(token: str, kind: str, options: Options, roman_context: RomanContext) -> str:
    if kind == "fraction":
        left, right = re.split(r"\s*/\s*", token)
        return spell_fraction(int(left), int(right))
    if kind == "ordinal":
        gender: Gender = "f" if token.strip().endswith("ª") else "m"
        return spell_ordinal(int(re.sub(r"[ºª]", "", token)), gender=gender)
    if kind == "decimal":
        return spell_number(token, options=options)
    if kind == "integer":
        return spell_number(int(token.replace(".", "")), options=options)
    return spell_roman(token, context=roman_context, options=options)


def build_parser() -> argparse.ArgumentParser:
    """Construct the argument parser (kept separate for testability)."""
    parser = argparse.ArgumentParser(
        prog="falabr",
        description="Spell Portuguese numbers in text (milestone 1 number core).",
    )
    parser.add_argument("text", nargs="*", help="text to normalize; omitted means stdin")
    parser.add_argument("-f", "--file", metavar="PATH", help="read text from a file")
    parser.add_argument("--json", action="store_true", help="emit original→spoken spans")
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
        "--roman-context",
        choices=[context.value for context in RomanContext],
        default=RomanContext.CARDINAL.value,
        help="how roman numerals are voiced",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point for the ``falabr`` console script."""
    args = build_parser().parse_args(argv)

    if args.file is not None:
        with open(args.file, encoding="utf-8") as handle:
            text = handle.read()
    elif args.text:
        text = " ".join(args.text)
    else:
        text = sys.stdin.read()

    options = Options(
        catorze_style=CatorzeStyle.CATORZE if args.catorze else CatorzeStyle.QUATORZE,
        decimal_mode=DecimalMode(args.decimal_mode),
    )
    roman_context = RomanContext(args.roman_context)

    spans: list[dict[str, object]] = []
    pieces: list[str] = []
    cursor = 0
    for match in _TOKEN_RE.finditer(text):
        # Every alternative in _TOKEN_RE is a named group.
        kind = cast(str, match.lastgroup)
        original = match.group()
        try:
            spoken = _spoken_for(original, kind, options, roman_context)
        except ValueError:
            continue
        pieces.append(text[cursor : match.start()])
        pieces.append(spoken)
        cursor = match.end()
        spans.append(
            {
                "start": match.start(),
                "end": match.end(),
                "original": original,
                "spoken": spoken,
            }
        )
    pieces.append(text[cursor:])
    output = "".join(pieces)

    if args.json:
        payload = {"text": output, "spans": spans}
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    elif args.ssml:
        print(f"<speak>{escape(output)}</speak>")
    else:
        print(output)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
