"""Unit entity: SI and common pt-BR units with singular/plural agreement.

A value other than exactly one takes the plural form: ``1 km`` ->
"um quilômetro", ``1,5 km`` -> "um vírgula cinco quilômetros".
"""

from __future__ import annotations

import re
from typing import Final

from ..options import Gender, Options
from ._common import MatchContext, Matcher, apply_matchers, compose, decimal_value, spell_numeric

__all__ = ["UNIT_MATCHERS", "normalize_units"]

# symbol -> (singular, plural)
_UNITS: Final[dict[str, tuple[str, str]]] = {
    "km/h": ("quilômetro por hora", "quilômetros por hora"),
    "km²": ("quilômetro quadrado", "quilômetros quadrados"),
    "km³": ("quilômetro cúbico", "quilômetros cúbicos"),
    "m/s": ("metro por segundo", "metros por segundo"),
    "mg/dL": ("miligrama por decilitro", "miligramas por decilitro"),
    "m²": ("metro quadrado", "metros quadrados"),
    "m³": ("metro cúbico", "metros cúbicos"),
    "Mbps": ("megabit por segundo", "megabits por segundo"),
    "kbps": ("quilobit por segundo", "quilobits por segundo"),
    "GB": ("gigabyte", "gigabytes"),
    "MB": ("megabyte", "megabytes"),
    "KB": ("quilobyte", "quilobytes"),
    "TB": ("terabyte", "terabytes"),
    "kWh": ("quilowatt-hora", "quilowatt-horas"),
    "kW": ("quilowatt", "quilowatts"),
    "km": ("quilômetro", "quilômetros"),
    "cm": ("centímetro", "centímetros"),
    "mm": ("milímetro", "milímetros"),
    "kg": ("quilograma", "quilogramas"),
    "mg": ("miligrama", "miligramas"),
    "ml": ("mililitro", "mililitros"),
    "min": ("minuto", "minutos"),
    "°C": ("grau Celsius", "graus Celsius"),
    "°F": ("grau Fahrenheit", "graus Fahrenheit"),
    "Ah": ("ampere-hora", "ampere-horas"),
    "Hz": ("hertz", "hertz"),
    "ha": ("hectare", "hectares"),
    "m": ("metro", "metros"),
    "g": ("grama", "gramas"),
    "l": ("litro", "litros"),
    "W": ("watt", "watts"),
    "V": ("volt", "volts"),
    "A": ("ampere", "amperes"),
    "h": ("hora", "horas"),
    "s": ("segundo", "segundos"),
}

_UNIT_PATTERN: Final = "|".join(
    re.escape(symbol) for symbol in sorted(_UNITS, key=len, reverse=True)
)
_NUMBER: Final = r"-?(?:\d{1,3}(?:\.\d{3})+|\d+)(?:,\d+)?"
_UNIT_RE_BODY: Final = rf"(?<![\w])({_NUMBER})\s*({_UNIT_PATTERN})\b"


def _unit_handler(match: re.Match[str], ctx: MatchContext) -> str:
    raw = match.group()
    number_match = re.match(_NUMBER, raw)
    assert number_match is not None
    number_text = number_match.group()
    symbol = raw[len(number_text) :].strip()
    singular, plural = _UNITS[symbol]
    value = decimal_value(number_text)
    noun = singular if value == 1 else plural
    # "hora" is feminine; all other unit nouns in the table are masculine.
    gender: Gender = "f" if symbol == "h" else "m"
    return f"{spell_numeric(number_text, ctx.options, gender=gender)} {noun}"


UNIT_MATCHERS: Final[tuple[Matcher, ...]] = (Matcher("unit", _UNIT_RE_BODY, _unit_handler),)

_UNITS_RE, _UNITS_HANDLERS = compose(UNIT_MATCHERS)


def normalize_units(text: str, options: Options | None = None) -> str:
    """Normalize number+unit expressions in a string."""
    if options is None:
        options = Options()
    return apply_matchers(text, _UNITS_RE, _UNITS_HANDLERS, options)
