"""falabr — Brazilian Portuguese text normalization for text-to-speech."""

from .numbers import (
    MAX_CARDINAL as MAX_CARDINAL,
)
from .numbers import (
    RomanContext as RomanContext,
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
    Gender as Gender,
)
from .options import (
    Options as Options,
)

__all__ = [
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
]

__version__ = "0.1.0"
