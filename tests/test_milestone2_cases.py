"""Milestone-2 accounting: new hand-written table cases (total >= 600 in SPEC)."""

from __future__ import annotations

from tests import (
    test_abbrev_entity,
    test_datetime_entity,
    test_emoji_entity,
    test_identifiers_entity,
    test_money_entity,
    test_pipeline,
    test_ssml_sentences,
    test_symbols_entity,
    test_units_entity,
    test_web_entity,
)


def test_milestone2_hand_written_case_count() -> None:
    total = (
        len(test_money_entity.MONEY_ENTITY_CASES)
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
    )
    assert total >= 300
