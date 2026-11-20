"""falabr — Brazilian Portuguese text normalization for text-to-speech."""

from .entities import (
    ABBREVIATIONS as ABBREVIATIONS,
)
from .entities import (
    CLDR_SOURCE as CLDR_SOURCE,
)
from .entities import (
    Normalized as Normalized,
)
from .entities import (
    Span as Span,
)
from .entities import (
    describe_emoji as describe_emoji,
)
from .entities import (
    normalize as normalize,
)
from .entities import (
    normalize_abbreviations as normalize_abbreviations,
)
from .entities import (
    normalize_datetime as normalize_datetime,
)
from .entities import (
    normalize_emoji as normalize_emoji,
)
from .entities import (
    normalize_identifiers as normalize_identifiers,
)
from .entities import (
    normalize_money as normalize_money,
)
from .entities import (
    normalize_ranges as normalize_ranges,
)
from .entities import (
    normalize_shorthand as normalize_shorthand,
)
from .entities import (
    normalize_ssml as normalize_ssml,
)
from .entities import (
    normalize_symbols as normalize_symbols,
)
from .entities import (
    normalize_units as normalize_units,
)
from .entities import (
    normalize_web as normalize_web,
)
from .entities import (
    normalize_with_spans as normalize_with_spans,
)
from .entities import (
    spell_acronym as spell_acronym,
)
from .entities import (
    split_camel as split_camel,
)
from .entities import (
    split_sentences as split_sentences,
)
from .numbers import (
    MAX_CARDINAL as MAX_CARDINAL,
)
from .numbers import (
    int_to_roman as int_to_roman,
)
from .numbers import (
    parse_spoken_number as parse_spoken_number,
)
from .numbers import (
    roman_to_int as roman_to_int,
)
from .numbers import (
    spell_cardinal as spell_cardinal,
)
from .numbers import (
    spell_fraction as spell_fraction,
)
from .numbers import (
    spell_money as spell_money,
)
from .numbers import (
    spell_number as spell_number,
)
from .numbers import (
    spell_ordinal as spell_ordinal,
)
from .numbers import (
    spell_percentage as spell_percentage,
)
from .numbers import (
    spell_roman as spell_roman,
)
from .options import (
    CatorzeStyle as CatorzeStyle,
)
from .options import (
    DecimalMode as DecimalMode,
)
from .options import (
    EmojiMode as EmojiMode,
)
from .options import (
    Gender as Gender,
)
from .options import (
    Options as Options,
)
from .options import (
    PhoneStyle as PhoneStyle,
)
from .options import (
    RomanContext as RomanContext,
)

__all__ = [
    "ABBREVIATIONS",
    "CLDR_SOURCE",
    "MAX_CARDINAL",
    "CatorzeStyle",
    "DecimalMode",
    "EmojiMode",
    "Gender",
    "Normalized",
    "Options",
    "PhoneStyle",
    "RomanContext",
    "Span",
    "describe_emoji",
    "int_to_roman",
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
    "parse_spoken_number",
    "roman_to_int",
    "spell_acronym",
    "spell_cardinal",
    "spell_fraction",
    "spell_money",
    "spell_number",
    "spell_ordinal",
    "spell_percentage",
    "spell_roman",
    "split_camel",
    "split_sentences",
]

__version__ = "0.1.0"
