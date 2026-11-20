"""Grouped digit reading for CPF, CNPJ, CEP, phones and card numbers.

Separators become comma pauses; the pause token is configurable through
:attr:`falabr.Options.digit_group_separator`.  Phone numbers additionally honour
:attr:`falabr.Options.phone_style`: ``digits`` (every digit), ``pairs`` (two-digit
numbers) or ``natural`` (the default: DDD as a number and the subscriber grouped
the way Brazilians say it).
"""

from __future__ import annotations

import re
from typing import Final

from ..numbers import spell_cardinal
from ..options import Options, PhoneStyle
from ._common import MatchContext, Matcher, apply_matchers, compose, digit_word, group_digits

__all__ = ["IDENTIFIER_MATCHERS", "normalize_identifiers"]


# A labelled protocol/code (e.g. "Protocolo 2026/12345") is read digit by
# digit, like the other identifiers.  The label makes the code unambiguous,
# so it cannot steal a decimal ("1.234,56") or a date ("05/03/2026").
_PROTOCOL_LABEL: Final = (
    r"(?P<protocol_label>(?i:\b(?:protocolo|protocol|pedido|ticket|chave|código|cod|nº|n°)"
    r"\b\.?\s*:?\s*))"
)
_PROTOCOL_PATTERN: Final = (
    rf"{_PROTOCOL_LABEL}(?P<protocol_code>\d{{2,6}}(?:[./-]\d{{1,6}}){{1,4}})"
)
_PROTOCOL_SPOKEN: Final[dict[str, str]] = {
    "nº": "número",
    "n°": "número",
    "cod": "código",
    "cod.": "código",
}


def _protocol_handler(match: re.Match[str], ctx: MatchContext) -> str:
    label = match.group("protocol_label").strip()
    code = match.group("protocol_code")
    spoken_label = _PROTOCOL_SPOKEN.get(label.lower().rstrip("."), label)
    return f"{spoken_label} {group_digits(code, ctx.options.digit_group_separator)}"


def _digits_handler(match: re.Match[str], ctx: MatchContext) -> str:
    return group_digits(match.group(), ctx.options.digit_group_separator)


def _cep_handler(match: re.Match[str], ctx: MatchContext) -> str:
    raw = match.group()
    if "-" not in raw and len(raw) == 8:
        raw = raw[:5] + "-" + raw[5:]
    return group_digits(raw, ctx.options.digit_group_separator)


def _read_digits(digits: str) -> str:
    """Read a run of digits one by one, separated by spaces."""
    return " ".join(digit_word(int(char)) for char in digits)


def _read_pairs(digits: str, options: Options) -> str:
    """Read a subscriber number as two-digit cardinals, left to right."""
    spoken: list[str] = []
    for start in range(0, len(digits), 2):
        pair = digits[start : start + 2]
        if len(pair) == 2:
            spoken.append(spell_cardinal(int(pair), catorze_style=options.catorze_style))
        else:
            spoken.append(digit_word(int(pair)))
    return ", ".join(spoken)


def _read_natural(digits: str) -> str:
    """Group the subscriber the way it is spoken in Brazil.

    Mobile numbers (nine digits) are said as ``9 | XXXX | XXXX``; landlines
    (eight digits) as ``XXXX | XXXX``.  Each group is still read digit by digit.
    """
    if len(digits) == 9:
        sizes: tuple[int, ...] = (1, 4, 4)
    elif len(digits) == 8:
        sizes = (4, 4)
    else:
        # Unknown length: keep readable four-digit chunks.
        sizes = tuple(4 for _ in range(len(digits) // 4))
        if remainder := len(digits) % 4:
            sizes += (remainder,)
    groups: list[str] = []
    cursor = 0
    for size in sizes:
        groups.append(_read_digits(digits[cursor : cursor + size]))
        cursor += size
    return ", ".join(groups)


# Parse the written form rather than a flat digit string: a hyphen makes the
# local prefix/line split unambiguous, while a bare 10-digit number needs the
# optional area code to be peeled off first.
_PHONE_PARTS: Final = re.compile(r"^(?:\+55[\s.-]*)?(?:\(?(\d{2})\)?[\s.-]*)?(\d{4,5})-(\d{4})$")


def _phone_handler(match: re.Match[str], ctx: MatchContext) -> str:
    options = ctx.options
    raw = match.group()
    parsed = _PHONE_PARTS.fullmatch(raw)
    if parsed is None:  # pragma: no cover - guaranteed by the matcher
        return group_digits(raw, options.digit_group_separator)
    area, prefix, line = parsed.groups()
    country = "55" if raw.startswith("+55") else ""

    if options.phone_style is PhoneStyle.DIGITS:
        # Keep the original digit-by-digit reading, with explicit pauses even
        # where the caller wrote no separator ("1191234-5678").
        groups = [value for value in (country, area, prefix, line) if value]
        return group_digits(" ".join(groups), options.digit_group_separator)

    spoken: list[str] = [
        spell_cardinal(int(code), catorze_style=options.catorze_style)
        for code in (country, area)
        if code
    ]
    subscriber = prefix + line
    if options.phone_style is PhoneStyle.PAIRS:
        spoken.append(_read_pairs(subscriber, options))
    else:
        spoken.append(_read_natural(subscriber))
    return ", ".join(spoken)


# Toll-free/service numbers ("0800 123 4567", "0300 ...") are written with
# spaces instead of the hyphen of an ordinary phone number.  The service prefix
# is voiced "zero oitocentos"/"zero trezentos" (zero + the cardinal of the
# remaining digits); the subscriber groups are read digit by digit.
_SERVICE_PREFIXES: Final[tuple[str, ...]] = (
    "0800",
    "0300",
    "4004",
    "4007",
    "4003",
    "3003",
    "4002",
    "4020",
)


def _service_phone_handler(match: re.Match[str], ctx: MatchContext) -> str:
    prefix, middle, last = match.group("svc_prefix", "svc_mid", "svc_last")
    if prefix.startswith("0"):
        head = f"zero {spell_cardinal(int(prefix[1:]), catorze_style=ctx.options.catorze_style)}"
    else:
        # A non-zero service prefix is announced as a full cardinal
        # ("4004" -> "quatro mil e quatro").
        head = spell_cardinal(int(prefix), catorze_style=ctx.options.catorze_style)
    groups = [head]
    if middle:
        groups.append(_read_digits(middle))
    groups.append(_read_digits(last))
    return ", ".join(groups)


_SERVICE_PHONE_PATTERN: Final = (
    r"(?<!\w)(?P<svc_prefix>"
    + "|".join(_SERVICE_PREFIXES)
    + r")\s+(?:(?P<svc_mid>\d{3})\s+)?(?P<svc_last>\d{4})(?!\w)"
)


IDENTIFIER_MATCHERS: Final[tuple[Matcher, ...]] = (
    Matcher("phone_service", _SERVICE_PHONE_PATTERN, _service_phone_handler),
    Matcher("cnpj", r"(?<!\w)\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}(?!\w)", _digits_handler),
    Matcher("cpf", r"(?<!\w)\d{3}\.\d{3}\.\d{3}-\d{2}(?!\w)", _digits_handler),
    Matcher("card", r"(?<!\w)\d{4}(?:[ -]\d{4}){3}(?!\w)", _digits_handler),
    Matcher("protocol", _PROTOCOL_PATTERN, _protocol_handler),
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
