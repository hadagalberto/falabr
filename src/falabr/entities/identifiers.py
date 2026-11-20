"""Grouped digit reading for CPF, CNPJ, CEP, phones and card numbers.

Separators become comma pauses; the pause token is configurable through
:attr:`falabr.Options.digit_group_separator`.
"""

from __future__ import annotations

import re
from typing import Final

from ..options import Options
from ._common import MatchContext, Matcher, apply_matchers, compose, group_digits

__all__ = ["IDENTIFIER_MATCHERS", "normalize_identifiers"]


def _digits_handler(match: re.Match[str], ctx: MatchContext) -> str:
    return group_digits(match.group(), ctx.options.digit_group_separator)


def _cep_handler(match: re.Match[str], ctx: MatchContext) -> str:
    raw = match.group()
    if "-" not in raw and len(raw) == 8:
        raw = raw[:5] + "-" + raw[5:]
    return group_digits(raw, ctx.options.digit_group_separator)


def _phone_handler(match: re.Match[str], ctx: MatchContext) -> str:
    # Normalize the prefix (+55 country code, 2-digit area code, local number)
    # so grouped reading has explicit boundaries even when none were written.
    digits = re.sub(r"\D", "", match.group())
    local = re.search(r"(\d{4,5})(\d{4})$", digits)
    if local is None:  # pragma: no cover - guaranteed by the matcher
        return group_digits(match.group(), ctx.options.digit_group_separator)
    rest = digits[: local.start()]
    parts: list[str] = []
    if rest.startswith("55") and len(rest) > 2:
        parts.append("55")
        rest = rest[2:]
    if rest:
        parts.append(rest)
    parts.extend((local.group(1), local.group(2)))
    return group_digits(" ".join(parts), ctx.options.digit_group_separator)


IDENTIFIER_MATCHERS: Final[tuple[Matcher, ...]] = (
    Matcher("cnpj", r"(?<!\w)\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}(?!\w)", _digits_handler),
    Matcher("cpf", r"(?<!\w)\d{3}\.\d{3}\.\d{3}-\d{2}(?!\w)", _digits_handler),
    Matcher("card", r"(?<!\w)\d{4}(?:[ -]\d{4}){3}(?!\w)", _digits_handler),
    Matcher("cep", r"(?<!\w)\d{5}-?\d{3}(?!\w)", _cep_handler),
    Matcher(
        "phone",
        r"(?<!\w)(?:\+55[\s.-]*)?(?:\(?\d{2}\)?[\s.-]*)?\d{4,5}-\d{4}(?!\w)",
        _phone_handler,
    ),
)

_IDENTIFIERS_RE, _IDENTIFIERS_HANDLERS = compose(IDENTIFIER_MATCHERS)


def normalize_identifiers(text: str, options: Options | None = None) -> str:
    """Normalize identifier codes in a string into grouped digit reading."""
    if options is None:
        options = Options()
    return apply_matchers(text, _IDENTIFIERS_RE, _IDENTIFIERS_HANDLERS, options)
