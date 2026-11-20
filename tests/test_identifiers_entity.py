"""Grouped-digit reading vectors for CPF/CNPJ/CEP/phone/card."""

from __future__ import annotations

import pytest

from falabr import Options, normalize_identifiers

IDENTIFIER_CASES: tuple[tuple[str, str], ...] = (
    (
        "123.456.789-09",
        "um dois três, quatro cinco seis, sete oito nove, zero nove",
    ),
    (
        "111.444.777-35",
        "um um um, quatro quatro quatro, sete sete sete, três cinco",
    ),
    (
        "12.345.678/0001-95",
        "um dois, três quatro cinco, seis sete oito, zero zero zero um, nove cinco",
    ),
    ("01310-100", "zero um três um zero, um zero zero"),
    ("01310100", "zero um três um zero, um zero zero"),
    (
        "(11) 91234-5678",
        "um um, nove um dois três quatro, cinco seis sete oito",
    ),
    (
        "11 91234-5678",
        "um um, nove um dois três quatro, cinco seis sete oito",
    ),
    (
        "1191234-5678",
        "um um, nove um dois três quatro, cinco seis sete oito",
    ),
    (
        "+55 11 91234-5678",
        "cinco cinco, um um, nove um dois três quatro, cinco seis sete oito",
    ),
    (
        "4111 1111 1111 1111",
        "quatro um um um, um um um um, um um um um, um um um um",
    ),
    (
        "4111-1111-1111-1111",
        "quatro um um um, um um um um, um um um um, um um um um",
    ),
)

IDENTIFIER_INVALID_CASES: tuple[str, ...] = (
    "12345",
    "1234-567",
    "abc.def",
    "12.345",
)


@pytest.mark.parametrize(("source", "expected"), IDENTIFIER_CASES)
def test_identifier_entity(source: str, expected: str) -> None:
    assert normalize_identifiers(source) == expected


@pytest.mark.parametrize("source", IDENTIFIER_INVALID_CASES)
def test_identifier_entity_invalid_source_is_preserved(source: str) -> None:
    assert normalize_identifiers(source) == source


def test_identifier_custom_separator() -> None:
    options = Options(digit_group_separator=";")
    assert normalize_identifiers("123.456.789-09", options=options) == (
        "um dois três; quatro cinco seis; sete oito nove; zero nove"
    )
