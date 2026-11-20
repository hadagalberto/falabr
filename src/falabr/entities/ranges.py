"""Numeric ranges and scores.

SPEC requires ``10-20`` to be read "de dez a vinte" *in context* — a bare
hyphen between numbers may also be a score ("3-1") or a subtraction, so cue
words (``de``, ``páginas``, ``anos``, ...) make the range unambiguous.  An
en dash or em dash is unambiguous on its own.  Scores use their own cue
words (``placar``, ``resultado``, ``razão``, ...) and are read "X a Y".
"""

from __future__ import annotations

import re
from typing import Final

from ..numbers import spell_cardinal
from ..options import Options
from ._common import MatchContext, Matcher, apply_matchers, compose

__all__ = ["RANGE_MATCHERS", "SCORE_MATCHERS", "normalize_ranges"]

_RANGE_CUES: Final[tuple[str, ...]] = (
    "de",
    "entre",
    "páginas",
    "paginas",
    "pags",
    "págs",
    "pag",
    "pág",
    "anos",
    "faixa",
    "intervalo",
    "dias",
    "linhas",
    "capítulos",
    "capitulos",
    "volumes",
    "seções",
    "secoes",
    "itens",
    "pontos",
)
_SCORE_CUES: Final[tuple[str, ...]] = (
    "placar",
    "resultado",
    "score",
    "razão",
    "razao",
    "proporção",
    "proporcao",
)

# The lookarounds keep date-like chains ("2026-03-05") out of the range helper.
_HYPHEN_BODY: Final = (
    r"(?<![\d/-])(?P<range_first>\d{1,6})\s*-\s*(?P<range_last>\d{1,6})\b(?![\d/-])"
)
_DASH_BODY: Final = (
    r"(?<![\d/-])(?P<dash_first>\d{1,6})\s*[–—]\s*(?P<dash_last>\d{1,6})\b(?![\d/-])"
)

_CUE_PATTERN: Final = (
    r"(?P<range_cue>(?i:\b(?:"
    + "|".join(re.escape(cue) for cue in sorted(_RANGE_CUES, key=len, reverse=True))
    + r")\b\.?))"
)
_SCORE_PATTERN: Final = (
    r"(?P<score_cue>(?i:\b(?:"
    + "|".join(re.escape(cue) for cue in sorted(_SCORE_CUES, key=len, reverse=True))
    + r")\b))\s*:?\s*(?P<score_first>\d{1,3})\s*[-:x×]\s*(?P<score_last>\d{1,3})\b"
)


def _range_handler(match: re.Match[str], ctx: MatchContext) -> str:
    cue = match.group("range_cue")
    first = int(match.group("range_first"))
    last = int(match.group("range_last"))
    spoken = (
        f"{spell_cardinal(first, catorze_style=ctx.options.catorze_style)} a "
        f"{spell_cardinal(last, catorze_style=ctx.options.catorze_style)}"
    )
    if cue.rstrip(".").lower() != "de":
        spoken = "de " + spoken
    return f"{cue} {spoken}"


def _dash_handler(match: re.Match[str], ctx: MatchContext) -> str:
    first = int(match.group("dash_first"))
    last = int(match.group("dash_last"))
    return (
        f"de {spell_cardinal(first, catorze_style=ctx.options.catorze_style)} a "
        f"{spell_cardinal(last, catorze_style=ctx.options.catorze_style)}"
    )


def _score_handler(match: re.Match[str], ctx: MatchContext) -> str:
    cue = match.group("score_cue")
    first = int(match.group("score_first"))
    last = int(match.group("score_last"))
    return (
        f"{cue} {spell_cardinal(first, catorze_style=ctx.options.catorze_style)} a "
        f"{spell_cardinal(last, catorze_style=ctx.options.catorze_style)}"
    )


# At least one side is a single digit, which excludes clock times ("14:30").
_BARE_SCORE_PATTERN: Final = r"(?<![\d:])(?:\d:\d{1,2}|\d{1,2}:\d)\b"


def _bare_score_handler(match: re.Match[str], ctx: MatchContext) -> str:
    first_text, last_text = match.group().split(":")
    first = int(first_text)
    last = int(last_text)
    return (
        f"{spell_cardinal(first, catorze_style=ctx.options.catorze_style)} a "
        f"{spell_cardinal(last, catorze_style=ctx.options.catorze_style)}"
    )


# A bare "2:1" is a score; "14:30" is already consumed by the time matcher
# because the date/time matchers are listed first in the pipeline.
SCORE_MATCHERS: Final[tuple[Matcher, ...]] = (
    Matcher("score", _SCORE_PATTERN, _score_handler),
    Matcher("score_bare", _BARE_SCORE_PATTERN, _bare_score_handler),
)

RANGE_MATCHERS: Final[tuple[Matcher, ...]] = (
    Matcher("range", rf"{_CUE_PATTERN}\s*:?\s*{_HYPHEN_BODY}", _range_handler),
    Matcher("range_dash", rf"\b{_DASH_BODY}", _dash_handler),
)

_RANGE_RE, _RANGE_HANDLERS = compose((*SCORE_MATCHERS, *RANGE_MATCHERS))


def normalize_ranges(text: str, options: Options | None = None) -> str:
    """Normalize score and range expressions in ``text``."""
    if options is None:
        options = Options()
    return apply_matchers(text, _RANGE_RE, _RANGE_HANDLERS, options)
