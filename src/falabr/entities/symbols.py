"""Symbol entity: mathematical and typographic signs voiced in pt-BR."""

from __future__ import annotations

import re
from typing import Final

from ..options import Options
from ._common import MatchContext, Matcher, apply_matchers, compose

__all__ = ["SYMBOL_MATCHERS", "normalize_symbols"]

_SYMBOL_WORDS: Final[dict[str, str]] = {
    "&": "e",
    "+": "mais",
    "=": "igual",
    "%": "por cento",
    "/": "barra",
    "×": "vezes",
    "÷": "dividido por",
    "<": "menor que",
    ">": "maior que",
    "≤": "menor ou igual a",
    "≥": "maior ou igual a",
    "≠": "diferente de",
    "≈": "aproximadamente igual a",
    "±": "mais ou menos",
    "∞": "infinito",
    "·": "vezes",
}

_SYMBOL_PATTERN: Final = "[" + "".join(re.escape(char) for char in _SYMBOL_WORDS) + "]"


def _symbol_handler(match: re.Match[str], ctx: MatchContext) -> str:
    before = ctx.text[: match.start()]
    after = ctx.text[match.end() :]
    left = "" if not before or before[-1].isspace() else " "
    right = "" if not after or after[0].isspace() else " "
    return left + _SYMBOL_WORDS[match.group()] + right


SYMBOL_MATCHERS: Final[tuple[Matcher, ...]] = (Matcher("symbol", _SYMBOL_PATTERN, _symbol_handler),)

_SYMBOL_RE, _SYMBOL_HANDLERS = compose(SYMBOL_MATCHERS)


def normalize_symbols(text: str, options: Options | None = None) -> str:
    """Normalize standalone symbols in a string."""
    if options is None:
        options = Options()
    return apply_matchers(text, _SYMBOL_RE, _SYMBOL_HANDLERS, options)
