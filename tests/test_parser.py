"""Spoken-number parser vectors + round-trip properties.

SPEC.md requires parse_spoken_number(spell_number(n)) == n for random samples
in 0..10^12; the property below covers the whole supported range 0..10^18-1.
"""

from __future__ import annotations

import pytest
from hypothesis import example, given, settings
from hypothesis import strategies as st

from falabr import (
    MAX_CARDINAL,
    parse_spoken_number,
    spell_cardinal,
    spell_number,
)

PARSE_CASES: tuple[tuple[str, int], ...] = (
    ("zero", 0),
    ("um", 1),
    ("uma", 1),
    ("dois", 2),
    ("duas", 2),
    ("três", 3),
    ("quatorze", 14),
    ("catorze", 14),
    ("dezesseis", 16),
    ("vinte e um", 21),
    ("noventa e nove", 99),
    ("cem", 100),
    ("cento e um", 101),
    ("duzentos e trinta e quatro", 234),
    ("duzentas e trinta e quatro", 234),
    ("mil", 1000),
    ("mil e cem", 1100),
    ("mil cento e um", 1101),
    ("dois mil e trinta", 2030),
    ("mil duzentos e trinta e quatro", 1234),
    ("cem mil", 100000),
    ("cento e um mil", 101000),
    ("um milhão", 1000000),
    ("um milhão e um", 1000001),
    ("um milhão e duzentos mil", 1200000),
    ("um milhão, duzentos mil e cinco", 1200005),
    (
        "um milhão, duzentos e trinta e quatro mil quinhentos e sessenta e sete",
        1234567,
    ),
    ("dois milhões", 2000000),
    ("dois milhões e quinhentos mil", 2500000),
    ("um bilhão", 10**9),
    ("um bilhão e duzentos milhões", 1200000000),
    ("mil milhões", 10**9),
    ("sete milhões e mil", 7001000),
    ("menos um", -1),
    ("menos dois mil e trinta", -2030),
    ("MENOS DOIS MIL E TRINTA", -2030),
)


@pytest.mark.parametrize(("text", "expected"), PARSE_CASES, ids=[t for t, _ in PARSE_CASES])
def test_parse_spoken_number(text: str, expected: int) -> None:
    assert parse_spoken_number(text) == expected


@pytest.mark.parametrize(
    "text",
    ["", "   ", "menos", "e", "menos e", "foo", "vinte e foo", "123", "dois gatos", "—"],
)
def test_parse_rejects_invalid_text(text: str) -> None:
    with pytest.raises(ValueError, match="number"):
        parse_spoken_number(text)


def test_parse_bad_type() -> None:
    with pytest.raises(TypeError):
        parse_spoken_number(123)  # type: ignore[arg-type]


@settings(max_examples=200, deadline=None)
@given(st.integers(min_value=0, max_value=MAX_CARDINAL))
@example(0)
@example(1)
@example(14)
@example(100)
@example(101)
@example(1000)
@example(1100)
@example(1101)
@example(1200)
@example(10**6)
@example(10**9)
@example(10**12)
@example(7001000)  # "sete milhões e mil": descending scale chain, not multiplication
@example(MAX_CARDINAL)
def test_roundtrip_full_range(number: int) -> None:
    assert parse_spoken_number(spell_cardinal(number)) == number
    assert parse_spoken_number(spell_number(number)) == number


@settings(max_examples=100, deadline=None)
@given(st.integers(min_value=0, max_value=10**12))
def test_roundtrip_feminine(number: int) -> None:
    assert parse_spoken_number(spell_cardinal(number, gender="f")) == number


@settings(max_examples=200, deadline=None)
@given(st.integers(min_value=-MAX_CARDINAL, max_value=MAX_CARDINAL))
def test_spelling_has_no_digits(number: int) -> None:
    spoken = spell_number(number)
    assert not any(char.isdigit() for char in spoken)
    if number < 0:
        assert spoken.startswith("menos ")


@settings(max_examples=100, deadline=None)
@given(st.integers(min_value=0, max_value=10**12))
def test_string_input_matches_int_input(number: int) -> None:
    assert spell_number(str(number)) == spell_cardinal(number)
