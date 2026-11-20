"""Decimal, negative and numeric-input vectors.

Sources: pt-BR uses a decimal comma ("dois vírgula cinco" — Cunha & Cintra,
Numerais); reading the fractional part as a cardinal or digit by digit are the
two modes required by SPEC.md.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from falabr import CatorzeStyle, DecimalMode, Options, spell_number

CARDINAL_DECIMALS: tuple[tuple[object, str], ...] = (
    ("3,14", "três vírgula quatorze"),
    ("12,5", "doze vírgula cinco"),
    ("0,5", "zero vírgula cinco"),
    ("0,05", "zero vírgula zero cinco"),
    ("0,005", "zero vírgula zero zero cinco"),
    ("1,001", "um vírgula zero zero um"),
    ("3,140", "três vírgula cento e quarenta"),
    ("100,00", "cem"),
    ("0,0", "zero"),
    ("1,1", "um vírgula um"),
    ("2,25", "dois vírgula vinte e cinco"),
    ("14,14", "quatorze vírgula quatorze"),
    ("1,234567", "um vírgula duzentos e trinta e quatro mil quinhentos e sessenta e sete"),
    ("-2,75", "menos dois vírgula setenta e cinco"),
    ("-0,5", "menos zero vírgula cinco"),
    ("1.234,56", "mil duzentos e trinta e quatro vírgula cinquenta e seis"),
    ("1.000", "mil"),
    ("1234", "mil duzentos e trinta e quatro"),
    (Decimal("12.5"), "doze vírgula cinco"),
    (12.5, "doze vírgula cinco"),
    (12, "doze"),
)


@pytest.mark.parametrize(
    ("value", "expected"), CARDINAL_DECIMALS, ids=[str(v) for v, _ in CARDINAL_DECIMALS]
)
def test_decimal_cardinal_mode(value: object, expected: str) -> None:
    assert spell_number(value) == expected  # type: ignore[arg-type]


DIGIT_DECIMALS: tuple[tuple[str, str], ...] = (
    ("3,14", "três vírgula um quatro"),
    ("0,05", "zero vírgula zero cinco"),
    ("12,50", "doze vírgula cinco zero"),
    ("-1,23", "menos um vírgula dois três"),
    ("2,0", "dois"),
    ("14,14", "quatorze vírgula um quatro"),
    ("1.234,56", "mil duzentos e trinta e quatro vírgula cinco seis"),
)


@pytest.mark.parametrize(("value", "expected"), DIGIT_DECIMALS)
def test_decimal_digit_mode(value: str, expected: str) -> None:
    options = Options(decimal_mode=DecimalMode.DIGITS)
    assert spell_number(value, options=options) == expected


def test_decimal_options_combined() -> None:
    options = Options(decimal_mode=DecimalMode.DIGITS, catorze_style=CatorzeStyle.CATORZE)
    assert spell_number("14,14", options=options) == "catorze vírgula um quatro"
    assert spell_number("2,5", gender="f") == "duas vírgula cinco"


@pytest.mark.parametrize(
    "value", ["", "abc", "1,2,3", "1.2.3", "-", "12,", "1.234,5.6", "  ", "1e5"]
)
def test_invalid_numeric_strings(value: str) -> None:
    with pytest.raises((ValueError, TypeError)):
        spell_number(value)


def test_invalid_numeric_types() -> None:
    with pytest.raises(TypeError):
        spell_number(True)
    with pytest.raises(TypeError):
        spell_number(None)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="finite"):
        spell_number(Decimal("Infinity"))
    with pytest.raises(ValueError, match="finite"):
        spell_number(Decimal("NaN"))


def test_options_validation() -> None:
    with pytest.raises(TypeError, match="catorze_style"):
        Options(catorze_style="catorze")  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="decimal_mode"):
        Options(decimal_mode="digits")  # type: ignore[arg-type]
