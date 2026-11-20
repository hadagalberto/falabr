"""Fraction-before-noun agreement for recipe and measure expressions.

In pt-BR a fraction used as a quantifier before a noun follows two rules:

* ``1/2`` becomes the agreeing adjective ``meia``/``meio`` with no preposition
  (``1/2 xícara`` -> "meia xícara", ``1/2 litro`` -> "meio litro");
* every other fraction keeps its cardinal numerator and gains the preposition
  ``de`` (``1/3 xícara`` -> "um terço de xícara", ``3/4 de xícara`` ->
  "três quartos de xícara").

This matcher runs before the date matcher so a measure expression such as
``1/2 xícara`` is never mistaken for the date 1 February.  The whole phrase is
consumed so the alignment spans stay exact.
"""

from __future__ import annotations

import re
from typing import Final

from ..numbers import spell_fraction
from ..options import Gender
from ._common import MatchContext, Matcher

__all__ = ["MEASURE_FRACTION_MATCHER"]

# Nouns that mark a fraction as a quantity rather than a dd/mm date.
# "meia" agrees with feminine nouns; "meio" with masculine ones.
_MEASURE_GENDER: Final[dict[str, Gender]] = {
    "xícara": "f",
    "xícaras": "f",
    "colher": "f",
    "colheres": "f",
    "pitada": "f",
    "pitadas": "f",
    "gota": "f",
    "gotas": "f",
    "unidade": "f",
    "unidades": "f",
    "hora": "f",
    "horas": "f",
    "litro": "m",
    "litros": "m",
    "copo": "m",
    "copos": "m",
    "prato": "m",
    "pratos": "m",
    "pacote": "m",
    "pacotes": "m",
    "quilograma": "m",
    "quilogramas": "m",
    "grama": "m",
    "gramas": "m",
    "mililitro": "m",
    "mililitros": "m",
    "minuto": "m",
    "minutos": "m",
    "kg": "m",
    "g": "m",
    "ml": "m",
    "l": "m",
}

# A fraction quantifies one measure, so plural written forms are voiced in the
# singular ("1/2 xícaras" -> "meia xícara").  Unit symbols stay unchanged.
_SINGULAR: Final[dict[str, str]] = {
    "xícaras": "xícara",
    "colheres": "colher",
    "pitadas": "pitada",
    "gotas": "gota",
    "unidades": "unidade",
    "horas": "hora",
    "litros": "litro",
    "copos": "copo",
    "pratos": "prato",
    "pacotes": "pacote",
    "quilogramas": "quilograma",
    "gramas": "grama",
    "mililitros": "mililitro",
    "minutos": "minuto",
}

_NOUNS: Final = "|".join(re.escape(noun) for noun in sorted(_MEASURE_GENDER, key=len, reverse=True))

_PATTERN: Final = (
    rf"\b(?P<mf_num>\d{{1,6}})\s*/\s*(?P<mf_den>\d{{1,6}})\s+(?:de\s+)?"
    rf"(?P<mf_noun>(?i:{_NOUNS}))\b"
)


def _measure_fraction(match: re.Match[str], _ctx: MatchContext) -> str:
    numerator = int(match.group("mf_num"))
    denominator = int(match.group("mf_den"))
    noun = match.group("mf_noun")
    if denominator < 2:
        # Not a fraction (e.g. "1/1"); leave the expression untouched.
        return match.group()
    key = noun.lower()
    gender = _MEASURE_GENDER.get(key, "m")
    noun = _SINGULAR.get(key, key)
    if numerator == 1 and denominator == 2:
        half = "meia" if gender == "f" else "meio"
        return f"{half} {noun}"
    return f"{spell_fraction(numerator, denominator)} de {noun}"


MEASURE_FRACTION_MATCHER: Final = Matcher("measure_fraction", _PATTERN, _measure_fraction)
