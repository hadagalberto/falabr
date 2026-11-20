"""Configuration values shared by the falabr API.

The number-related options come from milestone 1; milestone 2 adds emoji,
acronym and lexicon options to the same frozen dataclass.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
from typing import Final, Literal

Gender = Literal["m", "f"]


class RomanContext(str, Enum):
    """How a roman numeral is voiced.

    ``REGNAL`` follows the pt-BR convention: popes/kings up to X are ordinals
    ("Bento XVI" -> "dezesseis" because 16 > 10; "Dom Pedro II" -> "segundo"),
    while ``CARDINAL`` always uses the cardinal ("século XXI" -> "vinte e um").
    """

    CARDINAL = "cardinal"
    REGNAL = "regnal"


class CatorzeStyle(str, Enum):
    """Orthographic variant of the number 14 (both are correct in pt-BR)."""

    QUATORZE = "quatorze"
    CATORZE = "catorze"


class DecimalMode(str, Enum):
    """How the fractional part of a decimal number is read aloud."""

    CARDINAL = "cardinal"
    DIGITS = "digits"


class EmojiMode(str, Enum):
    """How emoji characters are voiced by :func:`falabr.normalize`."""

    REMOVE = "remove"
    DESCRIBE = "describe"


@dataclass(frozen=True, slots=True)
class Options:
    """Immutable bundle of normalization options."""

    catorze_style: CatorzeStyle = CatorzeStyle.QUATORZE
    decimal_mode: DecimalMode = DecimalMode.CARDINAL
    emoji_mode: EmojiMode = EmojiMode.REMOVE
    acronym_overrides: Mapping[str, str] = field(default_factory=dict)
    user_lexicon: Mapping[str, str] = field(default_factory=dict)
    digit_group_separator: str = ","
    roman_context: RomanContext = RomanContext.CARDINAL

    def __post_init__(self) -> None:
        if not isinstance(self.catorze_style, CatorzeStyle):
            raise TypeError("catorze_style must be a CatorzeStyle")
        if not isinstance(self.decimal_mode, DecimalMode):
            raise TypeError("decimal_mode must be a DecimalMode")
        if not isinstance(self.emoji_mode, EmojiMode):
            raise TypeError("emoji_mode must be an EmojiMode")
        if not isinstance(self.roman_context, RomanContext):
            raise TypeError("roman_context must be a RomanContext")
        for name in ("acronym_overrides", "user_lexicon"):
            value = getattr(self, name)
            if not isinstance(value, Mapping):
                raise TypeError(f"{name} must be a mapping")
            for key, spoken in value.items():
                if not isinstance(key, str) or not isinstance(spoken, str):
                    raise TypeError(f"{name} keys and values must be strings")
        if not isinstance(self.digit_group_separator, str):
            raise TypeError("digit_group_separator must be a str")


DEFAULT_OPTIONS: Final = Options()
