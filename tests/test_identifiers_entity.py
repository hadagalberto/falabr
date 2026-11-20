"""Grouped-digit reading vectors for CPF/CNPJ/CEP/phone/card.

Phone numbers have three configurable styles.  ``natural`` is the default and
reads the DDD as a number before grouping the subscriber the way Brazilians say
it; ``digits`` keeps the original digit-by-digit reading (useful for checking
a number) and ``pairs`` groups the subscriber into two-digit numbers.
"""

from __future__ import annotations

import pytest

from falabr import Options, PhoneStyle, normalize_identifiers

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
        "4111 1111 1111 1111",
        "quatro um um um, um um um um, um um um um, um um um um",
    ),
    (
        "4111-1111-1111-1111",
        "quatro um um um, um um um um, um um um um, um um um um",
    ),
)

# Natural style (default): DDD as a cardinal, subscriber grouped 1|4|4 (mobile)
# or 4|4 (landline), each group read digit by digit.
PHONE_NATURAL_CASES: tuple[tuple[str, str], ...] = (
    ("(11) 98765-4321", "onze, nove, oito sete seis cinco, quatro três dois um"),
    ("(11) 91234-5678", "onze, nove, um dois três quatro, cinco seis sete oito"),
    ("11 91234-5678", "onze, nove, um dois três quatro, cinco seis sete oito"),
    ("1191234-5678", "onze, nove, um dois três quatro, cinco seis sete oito"),
    (
        "+55 11 91234-5678",
        "cinquenta e cinco, onze, nove, um dois três quatro, cinco seis sete oito",
    ),
    ("(21) 3333-4444", "vinte e um, três três três três, quatro quatro quatro quatro"),
    ("91234-5678", "nove, um dois três quatro, cinco seis sete oito"),
)

# The original digit-by-digit vectors, now selected explicitly.
PHONE_DIGITS_CASES: tuple[tuple[str, str], ...] = (
    ("(11) 91234-5678", "um um, nove um dois três quatro, cinco seis sete oito"),
    ("11 91234-5678", "um um, nove um dois três quatro, cinco seis sete oito"),
    ("1191234-5678", "um um, nove um dois três quatro, cinco seis sete oito"),
    ("+55 11 91234-5678", "cinco cinco, um um, nove um dois três quatro, cinco seis sete oito"),
)

PHONE_PAIRS_CASES: tuple[tuple[str, str], ...] = (
    (
        "(11) 98765-4321",
        "onze, noventa e oito, setenta e seis, cinquenta e quatro, trinta e dois, um",
    ),
    (
        "(21) 3333-4444",
        "vinte e um, trinta e três, trinta e três, quarenta e quatro, quarenta e quatro",
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


@pytest.mark.parametrize(("source", "expected"), PHONE_NATURAL_CASES)
def test_phone_natural_is_default(source: str, expected: str) -> None:
    assert normalize_identifiers(source) == expected
    assert normalize_identifiers(source, Options(phone_style=PhoneStyle.NATURAL)) == expected


@pytest.mark.parametrize(("source", "expected"), PHONE_DIGITS_CASES)
def test_phone_digits_style(source: str, expected: str) -> None:
    options = Options(phone_style=PhoneStyle.DIGITS)
    assert normalize_identifiers(source, options=options) == expected


@pytest.mark.parametrize(("source", "expected"), PHONE_PAIRS_CASES)
def test_phone_pairs_style(source: str, expected: str) -> None:
    options = Options(phone_style=PhoneStyle.PAIRS)
    assert normalize_identifiers(source, options=options) == expected


@pytest.mark.parametrize("source", IDENTIFIER_INVALID_CASES)
def test_identifier_entity_invalid_source_is_preserved(source: str) -> None:
    assert normalize_identifiers(source) == source


def test_identifier_custom_separator() -> None:
    options = Options(digit_group_separator=";")
    assert normalize_identifiers("123.456.789-09", options=options) == (
        "um dois três; quatro cinco seis; sete oito nove; zero nove"
    )


def test_phone_digits_style_honours_custom_separator() -> None:
    options = Options(phone_style=PhoneStyle.DIGITS, digit_group_separator=";")
    assert normalize_identifiers("(11) 91234-5678", options=options) == (
        "um um; nove um dois três quatro; cinco seis sete oito"
    )


def test_phone_style_rejects_invalid_value() -> None:
    with pytest.raises(TypeError):
        Options(phone_style="natural")  # type: ignore[arg-type]
