"""Table-driven money-entity vectors (including known-invalid inputs).

Sources: SPEC.md ("R$ 2 mi", "R$ 3,5 bi", "de" rule); ABL/VOLP for ``real``.
"""

from __future__ import annotations

import pytest

from falabr import CatorzeStyle, Options, normalize, normalize_money

MONEY_ENTITY_CASES: tuple[tuple[str, str], ...] = (
    ("R$ 1", "um real"),
    ("R$ 2", "dois reais"),
    ("R$ 0", "zero reais"),
    ("R$ 0,50", "cinquenta centavos"),
    ("R$ 0,01", "um centavo"),
    ("R$ 1,01", "um real e um centavo"),
    ("R$ 1,25", "um real e vinte e cinco centavos"),
    ("R$ 1.234,56", "mil duzentos e trinta e quatro reais e cinquenta e seis centavos"),
    ("R$ 200", "duzentos reais"),
    ("R$ 1.000", "mil reais"),
    ("R$ 1.001", "mil e um reais"),
    ("R$ 1.000.000", "um milhão de reais"),
    ("R$ 1.000.001", "um milhão e um reais"),
    ("R$ 2 mi", "dois milhões de reais"),
    ("R$ 3,5 bi", "três vírgula cinco bilhões de reais"),
    ("R$ 1 mi", "um milhão de reais"),
    ("R$ 1 bi", "um bilhão de reais"),
    ("R$ 100 mil", "cem mil reais"),
    ("10 mil reais", "dez mil reais"),
    ("2 mi reais", "dois milhões de reais"),
    ("1 milhão de reais", "um milhão de reais"),
    ("R$ -5", "menos cinco reais"),
    ("R$ -1,25", "menos um real e vinte e cinco centavos"),
    ("US$ 10", "dez dólares"),
    ("US$ 1", "um dólar"),
    ("US$ 1,5", "um dólar e cinquenta centavos"),
    ("€ 2", "dois euros"),
    ("£ 2", "duas libras"),
    ("£ 1", "uma libra"),
    ("2 euros", "dois euros"),
    ("5 dólares", "cinco dólares"),
)

MONEY_INVALID_CASES: tuple[str, ...] = (
    "R$ abc",
    "10 milhões de bananas",
    "$$ 10",
    "R$",
    "preço em reais",
)


@pytest.mark.parametrize(("source", "expected"), MONEY_ENTITY_CASES)
def test_money_entity(source: str, expected: str) -> None:
    assert normalize_money(source) == expected


@pytest.mark.parametrize("source", MONEY_INVALID_CASES)
def test_money_entity_invalid_source_is_preserved(source: str) -> None:
    assert normalize_money(source) == source


def test_money_entity_in_context() -> None:
    assert normalize("Paguei R$ 1.234,56 ontem") == (
        "Paguei mil duzentos e trinta e quatro reais e cinquenta e seis centavos ontem"
    )


def test_money_entity_options() -> None:
    options = Options(catorze_style=CatorzeStyle.CATORZE)
    assert normalize_money("R$ 14", options=options) == "catorze reais"
