"""Date, time, decade and century entities.

Covers the formats listed in SPEC.md: ``05/03/2026``, ``5/3`` (in context),
``2026-03-05``, ``5 de mar.``, ``14h``, ``14h30``, ``14:30``, ``2h da manhã``,
weekday abbreviations, ``anos 90`` and ``século XXI``.
"""

from __future__ import annotations

import re
from typing import Final

from ..numbers import spell_cardinal, spell_fraction, spell_ordinal, spell_roman
from ..options import Gender, Options
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

_MONTH_NAMES: Final = "|".join(
    sorted((*[_m.lower() for _m in _MONTHS.values()], *_MONTH_ALIASES), key=len, reverse=True)
)
_WEEKDAY_NAMES: Final = "|".join(sorted(_WEEKDAYS, key=len, reverse=True))

# "3/4 de ...", "1/4 do ...", "1/4 dos ..." and "5/12 da ..." are quantity
# cues, not dates.  A following year or part of day ("de 2026", "da manhã") is
# excluded: those belong to a date phrase.
_FRACTION_PREP_RE: Final = re.compile(
    r"\s+(?:dos|das|de|do|da)\s+(?!(?:\d{4}|manhã|tarde|noite|madrugada)\b)(?=[^\W\d_])",
    re.IGNORECASE,
)

# Words that explicitly frame a d/m pair as a calendar date (review finding 4).
_DATE_CUES: Final[frozenset[str]] = frozenset(
    {
        "dia",
        "data",
        "em",
        "no",
        "na",
        "até",
        "desde",
        "seg",
        "segunda",
        "segunda-feira",
        "ter",
        "terça",
        "terça-feira",
        "qua",
        "quarta",
        "quarta-feira",
        "qui",
        "quinta",
        "quinta-feira",
        "sex",
        "sexta",
        "sexta-feira",
        "sáb",
        "sábado",
        "sab",
        "dom",
        "domingo",
    }
)

_MONTH_DAYS: Final[tuple[int, ...]] = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)

# A following four-digit year disambiguates "5/3 de 2026" as a date.
_YEAR_AFTER_RE: Final = re.compile(r"^\s+(?:de\s+)?\d{4}\b")


def _year_words(year_text: str, options: Options) -> str:
    return spell_cardinal(int(year_text), catorze_style=options.catorze_style)


def _date_words_from(day_word: str, month: int, year_text: str | None, options: Options) -> str:
    words = f"{day_word} de {_MONTHS[month]}"
    if year_text is not None:
        words += f" de {_year_words(year_text, options)}"
    return words


def _date_words(day: int, month: int, year_text: str | None, options: Options) -> str:
    day_word = spell_cardinal(day, catorze_style=options.catorze_style)
    return _date_words_from(day_word, month, year_text, options)


def _valid(day: int, month: int, year: int | None = None) -> bool:
    """Real calendar validation (a 31/02 pair is not a date).

    Without a year, 29 February is accepted because some years are leap; with
    a year, the Gregorian leap rule decides.  The previous bounds-only check
    produced impossible dates such as "trinta e um de fevereiro".
    """
    if not 1 <= month <= 12:
        return False
    limit = _MONTH_DAYS[month - 1]
    if month == 2 and (year is None or year % 400 == 0 or (year % 4 == 0 and year % 100 != 0)):
        # No year -> use the leap reference (29 Feb is a real calendar day);
        # with a year the Gregorian rule decides.  This matches the docstring.
        limit = 29
    return 1 <= day <= limit


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
    gender: Gender | None = (
        "f" if day_text.endswith("ª") else "m" if day_text.endswith("º") else None
    )
    day, month = int(re.sub(r"[ºª]", "", day_text)), int(month_text)
    year = int(year_text) if len(year_text) == 4 else None
    if not _valid(day, month, year):
        return match.group()
    if gender is not None:
        # "1º/1/2025" is an ordinal day, not a fraction numerator: read it as
        # "primeiro de janeiro de dois mil e vinte e cinco".
        return _date_words_from(spell_ordinal(day, gender=gender), month, year_text, ctx.options)
    return _date_words(day, month, year_text, ctx.options)


def _iso_date(match: re.Match[str], ctx: MatchContext) -> str:
    year_text, month_text, day_text = re.split(r"-", match.group())
    day, month = int(day_text), int(month_text)
    if not _valid(day, month, int(year_text)):
        return match.group()
    return _date_words(day, month, year_text, ctx.options)


def _short_date(match: re.Match[str], ctx: MatchContext) -> str:
    raw = match.group()
    day_text, month_text = re.split(r"/", raw)
    ordinal_gender: Gender | None = (
        "f" if day_text.endswith("ª") else "m" if day_text.endswith("º") else None
    )
    day, month = int(re.sub(r"[ºª]", "", day_text)), int(month_text)
    after = ctx.text[match.end() :]
    before_words = [word.strip('.,:;("[“') for word in ctx.text[: match.start()].lower().split()]
    date_cue = any(word in _DATE_CUES for word in before_words[-3:])
    year_cue = _YEAR_AFTER_RE.match(after) is not None
    fraction_cue = _FRACTION_PREP_RE.match(after) is not None
    valid = _valid(day, month)

    # A partitive "do/da/dos/das/de + noun" marks a quantity, not a date:
    # "1/4 do valor" -> "um quarto do valor".  A following measure noun is
    # consumed even earlier by the measure_fraction matcher.
    if fraction_cue and 2 <= month <= 12:
        return spell_fraction(day, month)

    # SPEC.md: a VALID bare d/m pair is a date by default.  No surrounding date
    # cue is required — that rule was inverted by a57e3a1, which turned every
    # valid pair into a fraction.  An ordinal day marker ("1º/9") keeps its
    # ordinal reading inside the date phrase.
    if valid:
        if ordinal_gender is not None:
            return _date_words_from(
                spell_ordinal(day, gender=ordinal_gender), month, None, ctx.options
            )
        return _date_words(day, month, None, ctx.options)

    # Impossible as a calendar date (31/02, 32/12, 31/13): never voice an
    # impossible date such as "trinta e um de fevereiro".
    if date_cue or year_cue or ordinal_gender is not None:
        # An explicit date cue means a date was intended; preserve the token
        # rather than silently turning it into a fraction.
        return raw
    if 2 <= month <= 12:
        # Bare, calendar-invalid pair: fall back to the fraction reading.
        return spell_fraction(day, month)
    return raw


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
        if minute:
            # "12h00" is simply "doze horas"; zero minutes are not spoken.
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
    Matcher("full_date", r"\b\d{1,2}[ºª]?/\d{1,2}/\d{2,4}\b", _full_numeric_date),
    Matcher("iso_date", r"\b\d{4}-\d{2}-\d{2}\b", _iso_date),
    Matcher("weekday", rf"(?i:\b(?:{_WEEKDAY_NAMES})\.)", _weekday),
    Matcher(
        "time_of_day",
        # The colon form needs two digits: "14:30" is a time, "2:1" is a score.
        r"\b\d{1,2}(?:h\d{0,2}|:\d{2})(?:min)?(?:\s*d[ae]\s*(?:madrugada|manhã|tarde|noite))?\b",
        _time,
    ),
    Matcher("short_date", r"\b\d{1,2}[ºª]?/\d{1,2}\b", _short_date),
)

_DATETIME_RE, _DATETIME_HANDLERS = compose(DATETIME_MATCHERS)


def normalize_datetime(text: str, options: Options | None = None) -> str:
    """Normalize dates, times, decades and centuries in a string."""
    if options is None:
        options = Options()
    return apply_matchers(text, _DATETIME_RE, _DATETIME_HANDLERS, options)
