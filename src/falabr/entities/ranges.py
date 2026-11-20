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
    first_word = spell_cardinal(first, catorze_style=ctx.options.catorze_style)
    last_word = spell_cardinal(last, catorze_style=ctx.options.catorze_style)
    normalized_cue = cue.rstrip(".").lower()
    if normalized_cue == "de":
        return f"{cue} {first_word} a {last_word}"
    if normalized_cue == "entre":
        # "entre 2010-2020" -> "entre dois mil e dez e dois mil e vinte": the
        # second "e" replaces the range connector after "entre".  The cue is
        # lowercased because it is a function word, not a proper noun.
        return f"{normalized_cue} {first_word} e {last_word}"
    return f"{cue} de {first_word} a {last_word}"


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


def _bare_score_x_handler(match: re.Match[str], ctx: MatchContext) -> str:
    """Voice ``n x m``: "a" in score context, "por" for dimensions otherwise."""
    first = int(match.group("x_first"))
    last = int(match.group("x_last"))
    before = ctx.text[: match.start()].lower()[-40:]
    score_context = re.search(
        r"\b(?:placar|resultado|score|razão|razao|proporção|proporcao|jogo|partida|gols)\b",
        before,
    )
    after = ctx.text[match.end() :]
    multiplication = re.match(r"\s*(?:=|iguais|aos|são|sao|é|e\b)", after, re.IGNORECASE)
    # With no explicit cue, a trailing 0 or 1 is taken as a score (the vast
    # majority of "n x 0/1" forms are match results); otherwise the pair is a
    # dimension ("3 x 4" -> "três por quatro").  "x" before "=" or "são" is a
    # multiplication sign ("2 x 2 = 4" -> "dois vezes dois igual quatro").
    # Documented limit: a bare "4 x 3" score is read as a dimension.
    if multiplication:
        joiner = "vezes"
    else:
        score_like = last <= 1
        joiner = "a" if (score_context or score_like) else "por"
    return (
        f"{spell_cardinal(first, catorze_style=ctx.options.catorze_style)} {joiner} "
        f"{spell_cardinal(last, catorze_style=ctx.options.catorze_style)}"
    )


_X_PATTERN: Final = r"(?<![\w:])(?P<x_first>\d{1,3})\s*x\s*(?P<x_last>\d{1,3})\b"

# A bare "2-0" is a score (one side is zero); "10-20" stays a plain hyphenated
# pair unless a cue word makes it a range.
_HYPHEN_ZERO_PATTERN: Final = r"(?<![\d/-])(?:\d\s*-\s*0|0\s*-\s*\d)\b(?![\d/-])"


def _hyphen_zero_handler(match: re.Match[str], ctx: MatchContext) -> str:
    first_text, last_text = (part.strip() for part in match.group().split("-"))
    return (
        f"{spell_cardinal(int(first_text), catorze_style=ctx.options.catorze_style)} a "
        f"{spell_cardinal(int(last_text), catorze_style=ctx.options.catorze_style)}"
    )


# A bare "2:1" is a score; "14:30" is already consumed by the time matcher
# because the date/time matchers are listed first in the pipeline.
SCORE_MATCHERS: Final[tuple[Matcher, ...]] = (
    Matcher("score", _SCORE_PATTERN, _score_handler),
    Matcher("score_bare", _BARE_SCORE_PATTERN, _bare_score_handler),
    Matcher("score_hyphen_zero", _HYPHEN_ZERO_PATTERN, _hyphen_zero_handler),
    Matcher("x_ratio", _X_PATTERN, _bare_score_x_handler),
)

# Distinct group names: ``compose`` merges all matchers into one regex, so
# reusing the ``dash_*`` names from ``_DASH_BODY`` would be a duplicate group.
_ENTRE_DASH_PATTERN: Final = (
    r"(?i:\bentre\b)\s+(?<![\d/-])(?P<ed_first>\d{1,6})\s*[–—]\s*"
    r"(?P<ed_last>\d{1,6})\b(?![\d/-])"
)


def _entre_dash_handler(match: re.Match[str], ctx: MatchContext) -> str:
    first = spell_cardinal(int(match.group("ed_first")), catorze_style=ctx.options.catorze_style)
    last = spell_cardinal(int(match.group("ed_last")), catorze_style=ctx.options.catorze_style)
    return f"entre {first} e {last}"


RANGE_MATCHERS: Final[tuple[Matcher, ...]] = (
    Matcher("range", rf"{_CUE_PATTERN}\s*:?\s*{_HYPHEN_BODY}", _range_handler),
    # "entre 10-20" with an en dash uses a dedicated matcher that consumes the
    # cue so it is not doubled.
    Matcher("entre_dash", _ENTRE_DASH_PATTERN, _entre_dash_handler),
    Matcher("range_dash", rf"\b{_DASH_BODY}", _dash_handler),
)

_RANGE_RE, _RANGE_HANDLERS = compose((*SCORE_MATCHERS, *RANGE_MATCHERS))


def normalize_ranges(text: str, options: Options | None = None) -> str:
    """Normalize score and range expressions in ``text``."""
    if options is None:
        options = Options()
    return apply_matchers(text, _RANGE_RE, _RANGE_HANDLERS, options)
