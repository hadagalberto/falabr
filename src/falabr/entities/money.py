"""Money entity: currency symbols/words, cents and mi/bi/mil abbreviations.

Grammatical source for the ``de`` construction after an exact scale word:
Academia Brasileira de Letras, *Vocabulário Ortográfico da Língua Portuguesa*
(VOLP), usage entries for ``real``; also Cunha & Cintra, *Nova Gramática do
Português Contemporâneo* (numerais + preposição).
"""

from __future__ import annotations

import re
from typing import Final

from ..numbers import spell_money, spell_number
from ..options import Options
from ._common import MatchContext, Matcher, apply_matchers, compose, decimal_value

__all__ = ["MONEY_MATCHERS", "normalize_money"]

_AMOUNT: Final = r"-?(?:\d{1,3}(?:\.\d{3})+|\d+)(?:,\d+)?"
_SUFFIX: Final = r"(?:mi|bi|mil|milhões|milhão|bilhões|bilhão)\b"
_CURRENCY: Final = r"(?:reais|real|dólares|dólar|euros|euro|libras|libra)"

_CURRENCY_CODES: Final[dict[str, str]] = {
    "r$": "BRL",
    "us$": "USD",
    "€": "EUR",
    "£": "GBP",
    "real": "BRL",
    "reais": "BRL",
    "dólar": "USD",
    "dólares": "USD",
    "euro": "EUR",
    "euros": "EUR",
    "libra": "GBP",
    "libras": "GBP",
}

_SCALE_WORDS: Final[dict[str, tuple[int, str, str]]] = {
    "mil": (10**3, "mil", "mil"),
    "mi": (10**6, "milhão", "milhões"),
    "milhão": (10**6, "milhão", "milhões"),
    "milhões": (10**6, "milhão", "milhões"),
    "bi": (10**9, "bilhão", "bilhões"),
    "bilhão": (10**9, "bilhão", "bilhões"),
    "bilhões": (10**9, "bilhão", "bilhões"),
}

_CURRENCY_NOUNS: Final[dict[str, tuple[str, str]]] = {
    "BRL": ("real", "reais"),
    "USD": ("dólar", "dólares"),
    "EUR": ("euro", "euros"),
    "GBP": ("libra", "libras"),
}


def _extract(text: str, options: Options, negative: bool = False) -> str:
    lowered = text.lower()
    suffix = ""
    for candidate in sorted(_SCALE_WORDS, key=len, reverse=True):
        if re.search(rf"\b{re.escape(candidate)}\b", lowered):
            suffix = candidate
            break

    amount_match = re.search(_AMOUNT, text)
    if amount_match is None:
        return text
    raw_amount = amount_match.group()
    amount = decimal_value(raw_amount)
    if negative:
        amount = -amount

    code = "BRL"
    for key, value in _CURRENCY_CODES.items():
        if key in lowered:
            code = value
            break

    if not suffix:
        return spell_money(amount, currency=code, options=options)

    factor, _, plural = _SCALE_WORDS[suffix]
    if amount != amount.to_integral_value():
        # Keep the written scale explicit: "R$ 3,5 bi" -> "três vírgula cinco
        # bilhões de reais" instead of expanding to full cardinals.
        _, currency_plural = _CURRENCY_NOUNS[code]
        return f"{spell_number(amount, options=options)} {plural} de {currency_plural}"
    return spell_money(amount * factor, currency=code, options=options)


def _money_handler(match: re.Match[str], ctx: MatchContext) -> str:
    raw = match.group()
    return _extract(raw.lstrip("- ").strip(), ctx.options, negative=raw.lstrip().startswith("-"))


MONEY_MATCHERS: Final[tuple[Matcher, ...]] = (
    Matcher(
        "money_symbol",
        # A minus sign directly before the symbol is a negative amount; a
        # separated dash ("2 kg - R$ 15,90") is a punctuation separator.
        rf"-?(?:R\$|US\$|€|£)\s*{_AMOUNT}(?:\s*{_SUFFIX})?(?:\s+de)?(?:\s+{_CURRENCY})?\b",
        _money_handler,
    ),
    Matcher(
        "money_words",
        rf"{_AMOUNT}(?:\s*{_SUFFIX})?(?:\s+de)?\s+{_CURRENCY}\b",
        _money_handler,
    ),
)

_MONEY_RE, _MONEY_HANDLERS = compose(MONEY_MATCHERS)


def normalize_money(text: str, options: Options | None = None) -> str:
    """Normalize money expressions in a string (standalone entity helper)."""
    if options is None:
        options = Options()
    return apply_matchers(text, _MONEY_RE, _MONEY_HANDLERS, options)
