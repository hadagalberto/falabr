"""Date, time, decade and century entities.

Covers the formats listed in SPEC.md: ``05/03/2026``, ``5/3`` (in context),
``2026-03-05``, ``5 de mar.``, ``14h``, ``14h30``, ``14:30``, ``2h da manhã``,
weekday abbreviations, ``anos 90`` and ``século XXI``.
"""

from __future__ import annotations

import re
from typing import Final

from ..numbers import spell_cardinal, spell_fraction, spell_roman
from ..options import Options
from ._common import MatchContext, Matcher, apply_matchers, compose

__all__ = ["DATETIME_MATCHERS", "normalize_datetime"]

_MONTHS: Final[dict[int, str]] = {
    1: "janeiro",
    2: "fevereiro",
    3: "março",
    4: "abril",
    5: "maio",
    6: "junho",
    7: "julho",
    8: "agosto",
    9: "setembro",
    10: "outubro",
    11: "novembro",
    12: "dezembro",
}

_MONTH_ALIASES: Final[dict[str, str]] = {
    "jan": "janeiro",
    "fev": "fevereiro",
    "mar": "março",
    "abr": "abril",
    "mai": "maio",
    "jun": "junho",
    "jul": "julho",
    "ago": "agosto",
    "set": "setembro",
    "out": "outubro",
    "nov": "novembro",
    "dez": "dezembro",
}

_MONTH_BY_NAME: Final[dict[str, int]] = {name: number for number, name in _MONTHS.items()}

_WEEKDAYS: Final[dict[str, str]] = {
    "seg": "segunda-feira",
    "ter": "terça-feira",
    "qua": "quarta-feira",
    "qui": "quinta-feira",
    "sex": "sexta-feira",
    "sáb": "sábado",
    "sab": "sábado",
    "dom": "domingo",
}

_DATE_WORDS: Final[tuple[str, ...]] = ("dia", "data", "em", "no", "na")

_MONTH_NAMES: Final = "|".join(
    sorted((*[_m.lower() for _m in _MONTHS.values()], *_MONTH_ALIASES), key=len, reverse=True)
)
_WEEKDAY_NAMES: Final = "|".join(sorted(_WEEKDAYS, key=len, reverse=True))


def _year_words(year_text: str, options: Options) -> str:
    return spell_cardinal(int(year_text), catorze_style=options.catorze_style)


def _date_words(day: int, month: int, year_text: str | None, options: Options) -> str:
    words = f"{spell_cardinal(day, catorze_style=options.catorze_style)} de {_MONTHS[month]}"
    if year_text is not None:
        words += f" de {_year_words(year_text, options)}"
    return words


def _valid(day: int, month: int) -> bool:
    return 1 <= day <= 31 and 1 <= month <= 12


def _century(match: re.Match[str], ctx: MatchContext) -> str:
    raw = match.group()
    pieces = raw.split()
    value_text = pieces[-1]
    if value_text.isdigit():
        spoken = spell_cardinal(int(value_text), catorze_style=ctx.options.catorze_style)
    else:
        spoken = spell_roman(value_text, options=ctx.options)
    return f"século {spoken}"


def _decade(match: re.Match[str], ctx: MatchContext) -> str:
    raw = match.group()
    prefix, value_text = raw.rsplit(" ", 1)
    spoken = spell_cardinal(int(value_text), catorze_style=ctx.options.catorze_style)
    return f"{prefix} {spoken}"


def _month_date(match: re.Match[str], ctx: MatchContext) -> str:
    raw = match.group()
    day_text = re.match(r"\d{1,2}", raw)
    assert day_text is not None
    day = int(day_text.group())
    month_token = re.search(rf"(?:{_MONTH_NAMES})\.?", raw.lower())
    assert month_token is not None
    key = month_token.group().rstrip(".")
    alias = _MONTH_ALIASES.get(key, key)
    month = _MONTH_BY_NAME[alias]
    year_match = re.search(r"\d{4}\s*$", raw)
    year_text = year_match.group().strip() if year_match else None
    return _date_words(day, month, year_text, ctx.options)


def _full_numeric_date(match: re.Match[str], ctx: MatchContext) -> str:
    day_text, month_text, year_text = re.split(r"/", match.group())
    day, month = int(day_text), int(month_text)
    if not _valid(day, month):
        return match.group()
    return _date_words(day, month, year_text, ctx.options)


def _iso_date(match: re.Match[str], ctx: MatchContext) -> str:
    year_text, month_text, day_text = re.split(r"-", match.group())
    day, month = int(day_text), int(month_text)
    if not _valid(day, month):
        return match.group()
    return _date_words(day, month, year_text, ctx.options)


def _short_date(match: re.Match[str], ctx: MatchContext) -> str:
    raw = match.group()
    day_text, month_text = re.split(r"/", raw)
    day, month = int(day_text), int(month_text)
    before = ctx.text[: match.start()].rstrip().lower()
    padded = len(day_text) == 2 and day_text.startswith("0")
    is_date = padded or any(before.endswith(word) for word in _DATE_WORDS)
    if not is_date:
        if 1 <= month <= 12:
            return spell_fraction(day, month)
        return raw
    if not _valid(day, month):
        return raw
    return _date_words(day, month, None, ctx.options)


def _time(match: re.Match[str], ctx: MatchContext) -> str:
    raw = match.group()
    period = ""
    for label in ("da madrugada", "da manhã", "da tarde", "da noite"):
        if re.search(rf"\b{re.escape(label)}\b", raw.lower()):
            period = " " + label
            break
    clock = re.search(r"(\d{1,2})(?:h|:)(\d{2})?", raw)
    assert clock is not None
    hour = int(clock.group(1))
    minute_text = clock.group(2)
    hour_word = spell_cardinal(hour, gender="f", catorze_style=ctx.options.catorze_style)
    words = f"{hour_word} hora{'s' if hour != 1 else ''}"
    if minute_text is not None:
        minute = int(minute_text)
        minute_word = spell_cardinal(minute, catorze_style=ctx.options.catorze_style)
        unit = "minuto" if minute == 1 else "minutos"
        words += f" e {minute_word} {unit}"
    return words + period


def _weekday(match: re.Match[str], ctx: MatchContext) -> str:
    key = match.group().lower().rstrip(".")
    return _WEEKDAYS[key]


DATETIME_MATCHERS: Final[tuple[Matcher, ...]] = (
    Matcher("century", r"\b(?:século|séc\.?|sec\.?)\s+(?:[IVXLCDM]{1,6}|\d{1,3})\b", _century),
    Matcher("decade", r"\b(?:anos?|década de)\s+\d{2,4}\b", _decade),
    Matcher(
        "month_date",
        rf"\b\d{{1,2}}\s+de\s+(?i:{_MONTH_NAMES})\.?(?:\s+de\s+\d{{4}})?",
        _month_date,
    ),
    Matcher("full_date", r"\b\d{1,2}/\d{1,2}/\d{2,4}\b", _full_numeric_date),
    Matcher("iso_date", r"\b\d{4}-\d{2}-\d{2}\b", _iso_date),
    Matcher("weekday", rf"(?i:\b(?:{_WEEKDAY_NAMES})\.)", _weekday),
    Matcher(
        "time_of_day",
        r"\b\d{1,2}(?:h|:)\d{0,2}(?:min)?(?:\s*d[ae]\s*(?:madrugada|manhã|tarde|noite))?\b",
        _time,
    ),
    Matcher("short_date", r"\b\d{1,2}/\d{1,2}\b", _short_date),
)

_DATETIME_RE, _DATETIME_HANDLERS = compose(DATETIME_MATCHERS)


def normalize_datetime(text: str, options: Options | None = None) -> str:
    """Normalize dates, times, decades and centuries in a string."""
    if options is None:
        options = Options()
    return apply_matchers(text, _DATETIME_RE, _DATETIME_HANDLERS, options)
