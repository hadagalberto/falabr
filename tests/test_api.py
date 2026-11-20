"""Public API surface and table-case accounting."""

from __future__ import annotations

import falabr
from falabr import (
    MAX_CARDINAL,
    CatorzeStyle,
    DecimalMode,
    Options,
    RomanContext,
    spell_cardinal,
)


def test_public_exports() -> None:
    expected = {
        "MAX_CARDINAL",
        "CatorzeStyle",
        "DecimalMode",
        "Gender",
        "Options",
        "RomanContext",
        "int_to_roman",
        "parse_spoken_number",
        "roman_to_int",
        "spell_cardinal",
        "spell_fraction",
        "spell_money",
        "spell_number",
        "spell_ordinal",
        "spell_percentage",
        "spell_roman",
    }
    assert set(falabr.__all__) == expected
    for name in expected:
        assert hasattr(falabr, name)


def test_defaults() -> None:
    options = Options()
    assert options.catorze_style is CatorzeStyle.QUATORZE
    assert options.decimal_mode is DecimalMode.CARDINAL
    assert CatorzeStyle("catorze") is CatorzeStyle.CATORZE
    assert DecimalMode("digits") is DecimalMode.DIGITS
    assert RomanContext("regnal") is RomanContext.REGNAL


def test_constants() -> None:
    assert MAX_CARDINAL == 999999999999999999
    assert falabr.__version__ == "0.1.0"
    assert spell_cardinal(MAX_CARDINAL).startswith("novecentos e noventa e nove quatrilhões")


def test_hand_written_table_case_count() -> None:
    """SPEC asks for at least 300 hand-written table cases."""
    from tests import (
        test_cardinals,
        test_decimals,
        test_fractions_money,
        test_ordinals,
        test_parser,
        test_roman,
    )

    total = (
        len(test_cardinals.CARDINAL_CASES)
        + len(test_cardinals.GENDER_CASES)
        + len(test_ordinals.ORDINAL_CASES)
        + len(test_ordinals.FEMININE_CASES)
        + len(test_fractions_money.FRACTION_CASES)
        + len(test_fractions_money.PERCENTAGE_CASES)
        + len(test_fractions_money.MONEY_CASES)
        + len(test_roman.ROMAN_CONVERSIONS)
        + len(test_roman.CARDINAL_ROMAN_CASES)
        + len(test_roman.REGNAL_ROMAN_CASES)
        + len(test_parser.PARSE_CASES)
        + len(test_decimals.CARDINAL_DECIMALS)
        + len(test_decimals.DIGIT_DECIMALS)
    )
    assert total >= 300
