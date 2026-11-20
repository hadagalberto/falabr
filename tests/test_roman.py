"""Roman numeral vectors and regnal/century conventions.

Sources: pt-BR convention for popes/regents — ordinal through "décimo",
cardinal afterwards ("Dom Pedro II" -> segundo, "Bento XVI" -> dezesseis);
centuries always cardinal ("século XXI" -> vinte e um). Canonical subtractive
forms only (IV, IX, XL, XC, CD, CM).
"""

from __future__ import annotations

import pytest

from falabr import (
    CatorzeStyle,
    Options,
    RomanContext,
    int_to_roman,
    roman_to_int,
    spell_roman,
)

ROMAN_CONVERSIONS: tuple[tuple[int, str], ...] = (
    (1, "I"),
    (2, "II"),
    (3, "III"),
    (4, "IV"),
    (5, "V"),
    (9, "IX"),
    (10, "X"),
    (14, "XIV"),
    (40, "XL"),
    (44, "XLIV"),
    (50, "L"),
    (90, "XC"),
    (94, "XCIV"),
    (99, "XCIX"),
    (100, "C"),
    (144, "CXLIV"),
    (400, "CD"),
    (499, "CDXCIX"),
    (500, "D"),
    (900, "CM"),
    (999, "CMXCIX"),
    (1000, "M"),
    (1492, "MCDXCII"),
    (1999, "MCMXCIX"),
    (2024, "MMXXIV"),
    (3999, "MMMCMXCIX"),
)


@pytest.mark.parametrize(
    ("number", "roman"), ROMAN_CONVERSIONS, ids=[str(n) for n, _ in ROMAN_CONVERSIONS]
)
def test_int_to_roman(number: int, roman: str) -> None:
    assert int_to_roman(number) == roman


@pytest.mark.parametrize(
    ("number", "roman"), ROMAN_CONVERSIONS, ids=[str(n) for n, _ in ROMAN_CONVERSIONS]
)
def test_roman_to_int(number: int, roman: str) -> None:
    assert roman_to_int(roman) == number
    assert roman_to_int(roman.lower()) == number


@pytest.mark.parametrize("roman", ["", "IIII", "VX", "IC", "XM", "ABC", "MMMM", "IIV", "IL"])
def test_non_canonical_roman_rejected(roman: str) -> None:
    with pytest.raises(ValueError, match="roman numeral"):
        roman_to_int(roman)


def test_roman_conversion_bad_types() -> None:
    with pytest.raises(TypeError):
        int_to_roman("1")  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        int_to_roman(True)
    with pytest.raises(ValueError, match="roman numerals"):
        int_to_roman(0)
    with pytest.raises(ValueError, match="roman numerals"):
        int_to_roman(4000)
    with pytest.raises(TypeError):
        roman_to_int(7)  # type: ignore[arg-type]


CARDINAL_ROMAN_CASES: tuple[tuple[str, str], ...] = (
    ("I", "um"),
    ("II", "dois"),
    ("IV", "quatro"),
    ("IX", "nove"),
    ("X", "dez"),
    ("XI", "onze"),
    ("XV", "quinze"),
    ("XXI", "vinte e um"),
    ("XL", "quarenta"),
    ("MCMXCIX", "mil novecentos e noventa e nove"),
    ("MMXXIV", "dois mil e vinte e quatro"),
)


@pytest.mark.parametrize(("roman", "expected"), CARDINAL_ROMAN_CASES)
def test_roman_cardinal_context(roman: str, expected: str) -> None:
    assert spell_roman(roman) == expected
    assert spell_roman(roman, context=RomanContext.CARDINAL) == expected


REGNAL_ROMAN_CASES: tuple[tuple[str, str], ...] = (
    ("I", "primeiro"),
    ("II", "segundo"),
    ("III", "terceiro"),
    ("IV", "quarto"),
    ("V", "quinto"),
    ("VIII", "oitavo"),
    ("IX", "nono"),
    ("X", "décimo"),
    ("XI", "onze"),
    ("XIII", "treze"),
    ("XVI", "dezesseis"),
    ("XXI", "vinte e um"),
)


@pytest.mark.parametrize(("roman", "expected"), REGNAL_ROMAN_CASES)
def test_roman_regnal_context(roman: str, expected: str) -> None:
    assert spell_roman(roman, context="regnal") == expected


def test_roman_gender_and_options() -> None:
    assert spell_roman("II", context="regnal", gender="f") == "segunda"
    options = Options(catorze_style=CatorzeStyle.CATORZE)
    assert spell_roman("XIV", options=options) == "catorze"


def test_roman_invalid_context() -> None:
    with pytest.raises(ValueError, match="context"):
        spell_roman("II", context="papal")
