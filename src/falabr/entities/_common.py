"""Shared machinery for the entity matchers used by the normalization pipeline.

Every entity module exposes :class:`Matcher` objects: a regex pattern plus a
handler.  :func:`compose` merges them into a single ordered alternation so the
pipeline is a single left-to-right scan; Python's regex alternation gives the
first listed alternative priority at any given position, which is how more
specific entities (money, dates, identifiers) win over plain numbers.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from decimal import Decimal
from typing import Final

from ..numbers import _coerce_decimal, spell_cardinal, spell_number
from ..options import Gender, Options

__all__ = [
    "Handler",
    "MatchContext",
    "Matcher",
    "apply_matchers",
    "compose",
    "digit_word",
    "group_digits",
    "spell_numeric",
]

_DIGIT_WORDS: Final[tuple[str, ...]] = (
    "zero",
    "um",
    "dois",
    "três",
    "quatro",
    "cinco",
    "seis",
    "sete",
    "oito",
    "nove",
)


@dataclass(frozen=True, slots=True)
class MatchContext:
    """Read-only context handed to every entity handler."""

    options: Options
    text: str


Handler = Callable[[re.Match[str], MatchContext], str]


@dataclass(frozen=True, slots=True)
class Matcher:
    """A named regex alternative and the function that voices its matches."""

    name: str
    pattern: str
    handler: Handler


def apply_matchers(
    text: str,
    regex: re.Pattern[str],
    handlers: dict[str, Handler],
    options: Options,
) -> str:
    """Apply a composed regex to ``text`` and collapse replacement spacing."""
    pieces: list[str] = []
    cursor = 0
    for match in regex.finditer(text):
        pieces.append(text[cursor : match.start()])
        name = next(n for n in handlers if match.group(n) is not None)
        pieces.append(handlers[name](match, MatchContext(options, text)))
        cursor = match.end()
    pieces.append(text[cursor:])
    return re.sub(r"[ \t]{2,}", " ", "".join(pieces)).strip()


def compose(
    matchers: tuple[Matcher, ...],
) -> tuple[re.Pattern[str], dict[str, Handler]]:
    """Build one compiled alternation and the group-name → handler map."""
    alternatives: list[str] = []
    handlers: dict[str, Handler] = {}
    for matcher in matchers:
        if matcher.name in handlers:
            raise ValueError(f"duplicate matcher name: {matcher.name}")
        group = f"(?P<{matcher.name}>{matcher.pattern})"
        alternatives.append(group)
        handlers[matcher.name] = matcher.handler
    combined = re.compile("|".join(alternatives))
    return combined, handlers


def digit_word(digit: int) -> str:
    """Spoken form of a single decimal digit (masculine)."""
    if not 0 <= digit <= 9:
        raise ValueError("digit must be between 0 and 9")
    return _DIGIT_WORDS[digit]


def group_digits(raw: str, separator: str = ",") -> str:
    """Read a code digit by digit, turning separators into pause markers.

    ``"123.456-09"`` -> ``"um dois três, quatro cinco seis, zero nove"``.
    Parentheses and plus signs are dropped; runs of separators collapse into
    one pause so ``"(11) 91234-5678"`` reads cleanly.
    """
    out: list[str] = []
    pending_separator = False
    for char in raw:
        if char.isdigit():
            if pending_separator and out:
                out[-1] = out[-1] + separator
                pending_separator = False
            out.append(digit_word(int(char)))
        elif char in "()":
            continue
        elif char.isspace() or char in ".-/+":
            if out:
                pending_separator = True
        else:
            # Unknown punctuation: treat as a pause boundary as well.
            if out:
                pending_separator = True
    return " ".join(out)


def spell_numeric(raw: str, options: Options, gender: Gender = "m") -> str:
    """Spell a pt-BR numeric substring ('1.234,56', '-3', '1,5')."""
    return spell_number(_coerce_decimal(raw), gender=gender, options=options)


def decimal_value(raw: str) -> Decimal:
    """Parse a pt-BR numeric substring into a Decimal."""
    return _coerce_decimal(raw)


def spell_count(value: Decimal, options: Options) -> str:
    """Spell the integer part of a decimal used as a count."""
    return spell_cardinal(int(value), catorze_style=options.catorze_style)
