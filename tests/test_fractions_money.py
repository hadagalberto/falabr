"""Fraction, percentage and money vectors.

Sources: Cunha & Cintra (Numerais fracionários), SPEC.md ("1/2 meio",
"1/3 um terço", "3/4 três quartos", "5/12 cinco doze avos"), ABL/VOLP for the
"de reais" construction after an exact milhão/bilhão.
"""

from __future__ import annotations

import pytest

from falabr import (
    CatorzeStyle,
    DecimalMode,
    Options,
    spell_fraction,
    spell_money,
    spell_percentage,
)

FRACTION_CASES: tuple[tuple[int, int, str], ...] = (
    (1, 2, "um meio"),
    (3, 2, "três meios"),
    (1, 3, "um terço"),
    (2, 3, "dois terços"),
    (1, 4, "um quarto"),
    (3, 4, "três quartos"),
    (1, 5, "um quinto"),
    (2, 5, "dois quintos"),
    (5, 6, "cinco sextos"),
    (1, 7, "um sétimo"),
    (7, 8, "sete oitavos"),
    (1, 9, "um nono"),
    (1, 10, "um décimo"),
    (9, 10, "nove décimos"),
    (1, 100, "um centésimo"),
    (3, 1000, "três milésimos"),
    (1, 1000000, "um milionésimo"),
    (1, 12, "um doze avos"),
    (5, 12, "cinco doze avos"),
    (2, 11, "dois onze avos"),
    (1, 11, "um onze avos"),
    (0, 3, "zero terços"),
    (-3, 4, "menos três quartos"),
)


@pytest.mark.parametrize(
    ("numerator", "denominator", "expected"),
    FRACTION_CASES,
    ids=[f"{n}/{d}" for n, d, _ in FRACTION_CASES],
)
def test_fractions(numerator: int, denominator: int, expected: str) -> None:
    assert spell_fraction(numerator, denominator) == expected


def test_fraction_gender() -> None:
    assert spell_fraction(1, 2, gender="f") == "uma meia"
    assert spell_fraction(3, 2, gender="f") == "três meias"
    assert spell_fraction(1, 3, gender="f") == "uma terça"


def test_fraction_invalid_inputs() -> None:
    with pytest.raises(ValueError, match="denominator"):
        spell_fraction(1, 1)
    with pytest.raises(ValueError, match="denominator"):
        spell_fraction(1, 0)
    with pytest.raises(TypeError):
        spell_fraction(1.5, 2)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        spell_fraction(1, "2")  # type: ignore[arg-type]


PERCENTAGE_CASES: tuple[tuple[object, str], ...] = (
    (12.5, "doze vírgula cinco por cento"),
    ("12,5", "doze vírgula cinco por cento"),
    (0, "zero por cento"),
    (100, "cem por cento"),
    (5, "cinco por cento"),
    ("-3,5", "menos três vírgula cinco por cento"),
    (1, "um por cento"),
    ("0,1", "zero vírgula um por cento"),
)


@pytest.mark.parametrize(
    ("value", "expected"), PERCENTAGE_CASES, ids=[str(v) for v, _ in PERCENTAGE_CASES]
)
def test_percentages(value: object, expected: str) -> None:
    assert spell_percentage(value) == expected  # type: ignore[arg-type]


def test_percentage_options() -> None:
    options = Options(decimal_mode=DecimalMode.DIGITS)
    assert spell_percentage("3,14", options=options) == ("três vírgula um quatro por cento")


MONEY_CASES: tuple[tuple[object, str, str], ...] = (
    (1, "BRL", "um real"),
    (2, "BRL", "dois reais"),
    (0, "BRL", "zero reais"),
    ("0,50", "BRL", "cinquenta centavos"),
    ("1,01", "BRL", "um real e um centavo"),
    ("1,05", "BRL", "um real e cinco centavos"),
    ("1.234,56", "BRL", "mil duzentos e trinta e quatro reais e cinquenta e seis centavos"),
    (200, "BRL", "duzentos reais"),
    (1000000, "BRL", "um milhão de reais"),
    (1000001, "BRL", "um milhão e um reais"),
    (1200000, "BRL", "um milhão e duzentos mil reais"),
    (2500000, "BRL", "dois milhões e quinhentos mil reais"),
    (10**9, "BRL", "um bilhão de reais"),
    (-5, "BRL", "menos cinco reais"),
    ("-1,25", "BRL", "menos um real e vinte e cinco centavos"),
    (1, "USD", "um dólar"),
    (2, "USD", "dois dólares"),
    ("1,5", "USD", "um dólar e cinquenta centavos"),
    (2, "EUR", "dois euros"),
)


@pytest.mark.parametrize(
    ("amount", "currency", "expected"),
    MONEY_CASES,
    ids=[f"{v}/{c}" for v, c, _ in MONEY_CASES],
)
def test_money(amount: object, currency: str, expected: str) -> None:
    assert spell_money(amount, currency=currency) == expected  # type: ignore[arg-type]


def test_money_rounding_and_options() -> None:
    assert spell_money("1,999") == "dois reais"
    options = Options(catorze_style=CatorzeStyle.CATORZE)
    assert spell_money(14, options=options) == "catorze reais"


def test_money_invalid_inputs() -> None:
    with pytest.raises(ValueError, match="currency"):
        spell_money(1, currency="XYZ")
    with pytest.raises(ValueError, match="numeric string"):
        spell_money("abc")
