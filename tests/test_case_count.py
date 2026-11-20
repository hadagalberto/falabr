"""SPEC requires at least 600 hand-written table cases across the suite.

This single assertion sums every curated table (milestones 1-4) so the number
cannot silently drift below the requirement when tables are reorganised.
"""

from __future__ import annotations

from tests import (
    test_abbrev_entity,
    test_cardinals,
    test_datetime_entity,
    test_decimals,
    test_emoji_entity,
    test_fractions_money,
    test_identifiers_entity,
    test_milestone5,
    test_money_entity,
    test_ordinals,
    test_parser,
    test_pipeline,
    test_ranges_protocol,
    test_roman,
    test_shorthand_entity,
    test_ssml_sentences,
    test_symbols_entity,
    test_units_entity,
    test_web_entity,
)


def test_hand_written_table_case_count_at_least_600() -> None:
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
        + len(test_money_entity.MONEY_ENTITY_CASES)
        + len(test_money_entity.MONEY_INVALID_CASES)
        + len(test_datetime_entity.DATE_CASES)
        + len(test_datetime_entity.TIME_CASES)
        + len(test_datetime_entity.PERIOD_CASES)
        + len(test_datetime_entity.WEEKDAY_CASES)
        + len(test_datetime_entity.DATETIME_INVALID_CASES)
        + len(test_units_entity.UNIT_CASES)
        + len(test_units_entity.UNIT_INVALID_CASES)
        + len(test_abbrev_entity.ABBREV_CASES)
        + len(test_abbrev_entity.ABBREV_INVALID_CASES)
        + len(test_abbrev_entity.ACRONYM_CASES)
        + len(test_identifiers_entity.IDENTIFIER_CASES)
        + len(test_identifiers_entity.IDENTIFIER_INVALID_CASES)
        + len(test_identifiers_entity.PHONE_NATURAL_CASES)
        + len(test_identifiers_entity.PHONE_DIGITS_CASES)
        + len(test_identifiers_entity.PHONE_PAIRS_CASES)
        + len(test_web_entity.WEB_CASES)
        + len(test_web_entity.WEB_INVALID_CASES)
        + len(test_web_entity.CAMEL_CASES)
        + len(test_emoji_entity.DESCRIBE_CASES)
        + len(test_emoji_entity.NORMALIZE_EMOJI_CASES)
        + len(test_emoji_entity.REMOVE_EMOJI_CASES)
        + len(test_symbols_entity.SYMBOL_CASES)
        + len(test_symbols_entity.SYMBOL_INVALID_CASES)
        + len(test_pipeline.PIPELINE_CASES)
        + len(test_pipeline.PIPELINE_OPTION_CASES)
        + len(test_ssml_sentences.SSML_CASES)
        + len(test_ssml_sentences.SENTENCE_CASES)
        + len(test_shorthand_entity.SHORTHAND_CASES)
        + len(test_shorthand_entity.PRESERVED_CASES)
        + len(test_shorthand_entity.PIPELINE_CASES)
        + len(test_ranges_protocol.RANGE_CASES)
        + len(test_ranges_protocol.NOT_A_RANGE_CASES)
        + len(test_ranges_protocol.SCORE_CASES)
        + len(test_ranges_protocol.NOT_A_SCORE_CASES)
        + len(test_ranges_protocol.PROTOCOL_CASES)
        + len(test_ranges_protocol.NOT_A_PROTOCOL_CASES)
        + len(test_milestone5.DATE_VS_FRACTION_CASES)
        + len(test_milestone5.MEASURE_FRACTION_CASES)
        + len(test_milestone5.GOLDEN_PARAGRAPH_CASES)
        + len(test_milestone5.SSML_MODE_CASES)
    )
    assert total >= 600, f"expected at least 600 hand-written cases, got {total}"
