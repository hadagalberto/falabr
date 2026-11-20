"""Milestone-2 entities for Brazilian Portuguese TTS normalization."""

from .abbrev import (
    ABBREVIATION_MATCHERS,
    ABBREVIATIONS,
    Abbreviation,
    normalize_abbreviations,
    spell_acronym,
)
from .datetime import DATETIME_MATCHERS, normalize_datetime
from .emoji import CLDR_SOURCE, EMOJI_MATCHERS, describe_emoji, normalize_emoji
from .identifiers import IDENTIFIER_MATCHERS, normalize_identifiers
from .money import MONEY_MATCHERS, normalize_money
from .pipeline import (
    Normalized,
    Span,
    normalize,
    normalize_ssml,
    normalize_with_spans,
    split_sentences,
)
from .ranges import RANGE_MATCHERS, SCORE_MATCHERS, normalize_ranges
from .shorthand import SHORTHAND_MATCHERS, normalize_shorthand
from .symbols import SYMBOL_MATCHERS, normalize_symbols
from .units import UNIT_MATCHERS, normalize_units
from .web import WEB_MATCHERS, normalize_web, split_camel

__all__ = [
    "ABBREVIATIONS",
    "ABBREVIATION_MATCHERS",
    "CLDR_SOURCE",
    "DATETIME_MATCHERS",
    "EMOJI_MATCHERS",
    "IDENTIFIER_MATCHERS",
    "MONEY_MATCHERS",
    "RANGE_MATCHERS",
    "SCORE_MATCHERS",
    "SHORTHAND_MATCHERS",
    "SYMBOL_MATCHERS",
    "UNIT_MATCHERS",
    "WEB_MATCHERS",
    "Abbreviation",
    "Normalized",
    "Span",
    "describe_emoji",
    "normalize",
    "normalize_abbreviations",
    "normalize_datetime",
    "normalize_emoji",
    "normalize_identifiers",
    "normalize_money",
    "normalize_ranges",
    "normalize_shorthand",
    "normalize_ssml",
    "normalize_symbols",
    "normalize_units",
    "normalize_web",
    "normalize_with_spans",
    "spell_acronym",
    "split_camel",
    "split_sentences",
]
