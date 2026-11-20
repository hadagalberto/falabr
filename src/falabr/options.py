"""Configuration values shared by the falabr API.

Only the number-related options exist in this milestone; later milestones add
emoji, lexicon and acronym options to the same frozen dataclass.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Literal

Gender = Literal["m", "f"]


class CatorzeStyle(str, Enum):
    """Orthographic variant of the number 14 (both are correct in pt-BR)."""

    QUATORZE = "quatorze"
    CATORZE = "catorze"


class DecimalMode(str, Enum):
    """How the fractional part of a decimal number is read aloud."""

    CARDINAL = "cardinal"
    DIGITS = "digits"


@dataclass(frozen=True, slots=True)
class Options:
    """Immutable bundle of normalization options."""

    catorze_style: CatorzeStyle = CatorzeStyle.QUATORZE
    decimal_mode: DecimalMode = DecimalMode.CARDINAL

    def __post_init__(self) -> None:
        if not isinstance(self.catorze_style, CatorzeStyle):
            raise TypeError("catorze_style must be a CatorzeStyle")
        if not isinstance(self.decimal_mode, DecimalMode):
            raise TypeError("decimal_mode must be a DecimalMode")


DEFAULT_OPTIONS = Options()
