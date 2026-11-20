"""Portuguese (Brazil) number spelling and parsing.

Grammatical authorities used for the connector rules:

* Celso Cunha & Lindley Cintra, *Nova Gramática do Português Contemporâneo*,
  7th ed., chapter "Numerais": "A conjunção e é sempre intercalada entre as
  centenas, as dezenas e as unidades"; "Não se emprega a conjunção entre os
  milhares e as centenas, salvo quando o número terminar numa centena com dois
  zeros"; "Em números muito grandes, a conjunção e emprega-se entre os membros
  da mesma ordem de unidades, e omite-se quando se passa de uma ordem a outra".
* Paul Teyssier, *Manual de Língua Portuguesa* (1989), pp. 181-182: "E não
  figura entre os milhares e as centenas, excepto quando a mil se segue um
  algarismo simples" (1.030 = "mil e trinta", 1.400 = "mil e quatrocentos",
  4.226 = "quatro mil duzentos e vinte e seis").
* Câmara Municipal de Belo Horizonte, *Guia de Redação*: "incluir a vírgula
  entre o bilhão e o milhão e entre o milhão e o milhar".
* Academia Brasileira de Letras, *Vocabulário Ortográfico da Língua
  Portuguesa* (VOLP): "quatorze" / "catorze" are both correct; "quatorze"
  predominates in Brazilian written usage (the default here).
"""

from __future__ import annotations

import re
from decimal import ROUND_HALF_UP, Decimal
from enum import Enum
from typing import Final

from .options import CatorzeStyle, DecimalMode, Gender, Options

MAX_CARDINAL: Final = 10**18 - 1

_ONES_M: Final[dict[int, str]] = {
    0: "zero",
    1: "um",
    2: "dois",
    3: "três",
    4: "quatro",
    5: "cinco",
    6: "seis",
    7: "sete",
    8: "oito",
    9: "nove",
    10: "dez",
    11: "onze",
    12: "doze",
    13: "treze",
    14: "quatorze",
    15: "quinze",
    16: "dezesseis",
    17: "dezessete",
    18: "dezoito",
    19: "dezenove",
}

_ONES_F: Final[dict[int, str]] = {1: "uma", 2: "duas"}

_TENS: Final[dict[int, str]] = {
    2: "vinte",
    3: "trinta",
    4: "quarenta",
    5: "cinquenta",
    6: "sessenta",
    7: "setenta",
    8: "oitenta",
    9: "noventa",
}

_HUNDREDS_M: Final[dict[int, str]] = {
    2: "duzentos",
    3: "trezentos",
    4: "quatrocentos",
    5: "quinhentos",
    6: "seiscentos",
    7: "setecentos",
    8: "oitocentos",
    9: "novecentos",
}

_HUNDREDS_F: Final[dict[int, str]] = {
    2: "duzentas",
    3: "trezentas",
    4: "quatrocentas",
    5: "quinhentas",
    6: "seiscentas",
    7: "setecentas",
    8: "oitocentas",
    9: "novecentas",
}

_SCALE_DEFS: Final[tuple[tuple[int, str, str], ...]] = (
    (10**15, "quatrilhão", "quatrilhões"),
    (10**12, "trilhão", "trilhões"),
    (10**9, "bilhão", "bilhões"),
    (10**6, "milhão", "milhões"),
    (10**3, "mil", "mil"),
)

_ORDINAL_UNITS_M: Final[dict[int, str]] = {
    1: "primeiro",
    2: "segundo",
    3: "terceiro",
    4: "quarto",
    5: "quinto",
    6: "sexto",
    7: "sétimo",
    8: "oitavo",
    9: "nono",
}

_ORDINAL_TENS_M: Final[dict[int, str]] = {
    10: "décimo",
    20: "vigésimo",
    30: "trigésimo",
    40: "quadragésimo",
    50: "quinquagésimo",
    60: "sexagésimo",
    70: "septuagésimo",
    80: "octogésimo",
    90: "nonagésimo",
}

_ORDINAL_HUNDREDS_M: Final[dict[int, str]] = {
    100: "centésimo",
    200: "ducentésimo",
    300: "trecentésimo",
    400: "quadringentésimo",
    500: "quingentésimo",
    600: "sexcentésimo",
    700: "septingentésimo",
    800: "octingentésimo",
    900: "nongentésimo",
}

_FRACTION_DENOMINATORS_M: Final[dict[int, str]] = {
    2: "meio",
    3: "terço",
    4: "quarto",
    5: "quinto",
    6: "sexto",
    7: "sétimo",
    8: "oitavo",
    9: "nono",
    10: "décimo",
    100: "centésimo",
    1000: "milésimo",
    1000000: "milionésimo",
}

_CURRENCIES: Final[dict[str, tuple[str, str]]] = {
    "BRL": ("real", "reais"),
    "USD": ("dólar", "dólares"),
    "EUR": ("euro", "euros"),
    "GBP": ("libra", "libras"),
}

# "libra" is feminine in pt-BR; the other currency nouns here are masculine.
_CURRENCY_GENDER: Final[dict[str, Gender]] = {"GBP": "f"}

_ROMAN_VALUES: Final[dict[str, int]] = {
    "I": 1,
    "V": 5,
    "X": 10,
    "L": 50,
    "C": 100,
    "D": 500,
    "M": 1000,
}

_ROMAN_SUBTRACTIVE: Final[tuple[tuple[int, str], ...]] = (
    (1000, "M"),
    (900, "CM"),
    (500, "D"),
    (400, "CD"),
    (100, "C"),
    (90, "XC"),
    (50, "L"),
    (40, "XL"),
    (10, "X"),
    (9, "IX"),
    (5, "V"),
    (4, "IV"),
    (1, "I"),
)


class RomanContext(str, Enum):
    """How a roman numeral is voiced.

    ``REGNAL`` follows the pt-BR convention: popes/kings up to X are ordinals
    ("Bento XVI" -> "dezesseis" because 16 > 10; "Dom Pedro II" -> "segundo"),
    while ``CARDINAL`` always uses the cardinal ("século XXI" -> "vinte e um").
    """

    CARDINAL = "cardinal"
    REGNAL = "regnal"


def _ones_word(value: int, gender: Gender, style: CatorzeStyle) -> str:
    if value == 14 and style is CatorzeStyle.CATORZE:
        return "catorze"
    if gender == "f" and value in _ONES_F:
        return _ONES_F[value]
    return _ONES_M[value]


def _spell_below_1000(value: int, gender: Gender, style: CatorzeStyle) -> str:
    words: list[str] = []
    hundreds, rest = divmod(value, 100)
    if hundreds == 1:
        words.append("cem" if rest == 0 else "cento")
    elif hundreds:
        table = _HUNDREDS_F if gender == "f" else _HUNDREDS_M
        words.append(table[hundreds])
    if hundreds and rest:
        # Cunha & Cintra: "e" is always intercalated between hundreds and the
        # following tens/units ("cento e um", "duzentos e trinta e quatro").
        words.append("e")

    if rest:
        if rest < 20:
            # 11..19 are lexicalized ("onze", "doze", ...) and are not tens+unit.
            words.append(_ones_word(rest, gender, style))
        else:
            tens, unit = divmod(rest, 10)
            words.append(_TENS[tens])
            if unit:
                words.append("e")
                words.append(_ones_word(unit, gender, style))
    return " ".join(words)


def _groups(number: int) -> list[tuple[int, int]]:
    """Split a cardinal into non-zero 3-digit groups, highest scale first."""
    result: list[tuple[int, int]] = []
    remaining = number
    for scale, _, _ in _SCALE_DEFS:
        value, remaining = divmod(remaining, scale)
        if value:
            result.append((scale, value))
    if remaining:
        result.append((1, remaining))
    return result


def _render_group(scale: int, value: int, gender: Gender, style: CatorzeStyle) -> str:
    if scale == 1:
        return _spell_below_1000(value, gender, style)
    if scale == 10**3:
        if value == 1:
            return "mil"
        return f"{_spell_below_1000(value, gender, style)} mil"
    # milhão/bilhão/... are masculine nouns; the multiplier agrees with them,
    # not with the counted noun.
    words = _spell_below_1000(value, "m", style)
    for scale_value, singular, plural in _SCALE_DEFS:
        if scale_value == scale:
            return f"{words} {singular if value == 1 else plural}"
    raise AssertionError("unreachable scale")  # pragma: no cover


def _is_linkable(value: int) -> bool:
    """Values that take the connective ``e`` after a scale word.

    Cunha & Cintra's "centena com dois zeros" plus Teyssier's "algarismo
    simples": any value below 100, or an exact hundred (200, 300, ...).
    """
    return value < 100 or value % 100 == 0


def _join_groups(groups: list[tuple[int, int]], gender: Gender, style: CatorzeStyle) -> str:
    pieces = [_render_group(scale, value, gender, style) for scale, value in groups]
    result = pieces[0]
    for index in range(1, len(pieces)):
        higher_scale = groups[index - 1][0]
        if index == len(pieces) - 1 and _is_linkable(groups[index][1]):
            # "mil e cem", "dois mil e trinta", "um milhão, duzentos mil e cinco"
            connector = " e "
        elif higher_scale >= 10**6:
            # Comma between classes >= milhão (Cunha & Cintra, rule 3; CMBH
            # Guia de Redação): "um milhão, duzentos e trinta e quatro mil".
            connector = ", "
        else:
            # No comma between milhar and unidades: "... mil duzentos e onze".
            connector = " "
        result += connector + pieces[index]
    return result


def spell_cardinal(
    number: int,
    *,
    gender: Gender = "m",
    catorze_style: CatorzeStyle = CatorzeStyle.QUATORZE,
) -> str:
    """Spell an integer from 0 to 10**18 - 1 in Brazilian Portuguese."""
    if isinstance(number, bool) or not isinstance(number, int):
        raise TypeError("number must be an int")
    if gender not in ("m", "f"):
        raise ValueError("gender must be 'm' or 'f'")
    if not isinstance(catorze_style, CatorzeStyle):
        raise TypeError("catorze_style must be a CatorzeStyle")
    if number < 0:
        return "menos " + spell_cardinal(-number, gender=gender, catorze_style=catorze_style)
    if number > MAX_CARDINAL:
        raise ValueError(f"number must be at most {MAX_CARDINAL}")
    if number == 0:
        return "zero"
    return _join_groups(_groups(number), gender, catorze_style)


def _coerce_decimal(value: int | float | str | Decimal) -> Decimal:
    if isinstance(value, bool):
        raise TypeError("value must be a number or numeric string")
    if isinstance(value, int):
        return Decimal(value)
    if isinstance(value, Decimal):
        if not value.is_finite():
            raise ValueError("value must be finite")
        return value
    if isinstance(value, float):
        return Decimal(str(value))
    if isinstance(value, str):
        text = value.strip().replace(" ", "").replace("\u00a0", "")
        if not text:
            raise ValueError("empty numeric string")
        negative = text.startswith("-")
        text = text.lstrip("+-")
        if "," in text and "." in text:
            if text.rfind(",") < text.rfind("."):
                raise ValueError("invalid pt-BR numeric string")
            text = text.replace(".", "").replace(",", ".")
        elif "," in text:
            text = text.replace(",", ".")
        elif "." in text:
            parts = text.split(".")
            if 1 <= len(parts[0]) <= 3 and all(len(part) == 3 for part in parts[1:]):
                # pt-BR thousands separator: 1.234, 12.345.678
                text = text.replace(".", "")
        if not re.fullmatch(r"[0-9]+(?:\.[0-9]+)?", text):
            raise ValueError(f"invalid pt-BR numeric string: {value!r}")
        result = Decimal(text)
        return -result if negative else result
    raise TypeError("value must be a number or numeric string")


def spell_number(
    value: int | float | str | Decimal,
    *,
    gender: Gender = "m",
    options: Options | None = None,
) -> str:
    """Spell an integer or decimal, including negatives, in pt-BR.

    Decimal ``cardinal`` mode reads the fractional part as a number ("3,14"
    -> "três vírgula catorze"); ``digits`` mode reads it digit by digit
    ("três vírgula um quatro").
    """
    opts = options if options is not None else Options()
    number = _coerce_decimal(value)
    negative = number < 0
    absolute = -number if negative else number
    fixed = format(absolute, "f")
    integer_text, dot, fraction_text = fixed.partition(".")
    integer_part = int(integer_text)

    words = spell_cardinal(integer_part, gender=gender, catorze_style=opts.catorze_style)

    if dot and any(char != "0" for char in fraction_text):
        if opts.decimal_mode is DecimalMode.DIGITS:
            fraction_words = " ".join(
                _ones_word(int(char), gender, opts.catorze_style) for char in fraction_text
            )
        else:
            leading_zeros = len(fraction_text) - len(fraction_text.lstrip("0"))
            fraction_words = "zero " * leading_zeros + spell_cardinal(
                int(fraction_text), gender=gender, catorze_style=opts.catorze_style
            )
        words += " vírgula " + fraction_words

    return "menos " + words if negative else words


def _ordinal_feminine(masculine: str) -> str:
    return masculine[:-1] + "a"


def _ordinal_below_1000(number: int, gender: Gender) -> str:
    words: list[str] = []
    hundreds, rest = divmod(number, 100)
    if hundreds:
        word = _ORDINAL_HUNDREDS_M[hundreds * 100]
        words.append(_ordinal_feminine(word) if gender == "f" else word)
    if rest >= 10:
        tens, unit = divmod(rest, 10)
        tens_key = 10 if rest < 20 else tens * 10
        word = _ORDINAL_TENS_M[tens_key]
        words.append(_ordinal_feminine(word) if gender == "f" else word)
        if unit:
            unit_word = _ORDINAL_UNITS_M[unit]
            words.append(_ordinal_feminine(unit_word) if gender == "f" else unit_word)
    elif rest:
        unit_word = _ORDINAL_UNITS_M[rest]
        words.append(_ordinal_feminine(unit_word) if gender == "f" else unit_word)
    return " ".join(words)


def spell_ordinal(number: int, *, gender: Gender = "m") -> str:
    """Spell an ordinal from 1 to 999999, masculine or feminine."""
    if isinstance(number, bool) or not isinstance(number, int):
        raise TypeError("number must be an int")
    if gender not in ("m", "f"):
        raise ValueError("gender must be 'm' or 'f'")
    if not 1 <= number <= 999999:
        raise ValueError("ordinal must be between 1 and 999999")
    if number < 1000:
        return _ordinal_below_1000(number, gender)

    thousands, rest = divmod(number, 1000)
    milestone = "milésima" if gender == "f" else "milésimo"
    if thousands == 1:
        words = milestone
    else:
        words = f"{spell_cardinal(thousands, gender=gender)} {milestone}"
    if rest:
        words += " " + _ordinal_below_1000(rest, gender)
    return words


def _fraction_word(denominator: int, plural: bool, gender: Gender) -> str:
    if denominator == 2:
        word = "meia" if gender == "f" else "meio"
        return word + ("s" if plural else "")
    if denominator in _FRACTION_DENOMINATORS_M:
        word = _FRACTION_DENOMINATORS_M[denominator]
        if gender == "f":
            word = _ordinal_feminine(word)
        return word + ("s" if plural else "")
    return "avos"


def spell_fraction(numerator: int, denominator: int, *, gender: Gender = "m") -> str:
    """Spell a fraction such as 3/4 -> "três quartos" or 5/12 -> "cinco doze avos"."""
    for name, value in (("numerator", numerator), ("denominator", denominator)):
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"{name} must be an int")
    if denominator < 2:
        raise ValueError("denominator must be at least 2")
    if numerator < 0:
        return "menos " + spell_fraction(-numerator, denominator, gender=gender)

    word = _fraction_word(denominator, plural=numerator != 1, gender=gender)
    if numerator == 1:
        if denominator in _FRACTION_DENOMINATORS_M:
            return f"{spell_cardinal(1, gender=gender)} {word}"
        return f"{spell_cardinal(1, gender=gender)} {spell_cardinal(denominator)} avos"
    if denominator in _FRACTION_DENOMINATORS_M:
        return f"{spell_cardinal(numerator, gender=gender)} {word}"
    return f"{spell_cardinal(numerator, gender=gender)} {spell_cardinal(denominator)} avos"


def spell_percentage(
    value: int | float | str | Decimal,
    *,
    gender: Gender = "m",
    options: Options | None = None,
) -> str:
    """Spell a percentage: 12.5 -> "doze vírgula cinco por cento"."""
    return spell_number(value, gender=gender, options=options) + " por cento"


def spell_money(
    amount: int | float | str | Decimal,
    *,
    currency: str = "BRL",
    options: Options | None = None,
) -> str:
    """Spell a money amount, observing the "de reais" rule.

    "R$ 1.000.000,00" -> "um milhão de reais"; "R$ 1.000.001,00" ->
    "um milhão e um reais" (Cunha & Cintra, VOLP usage).
    """
    code = currency.upper()
    if code not in _CURRENCIES:
        raise ValueError(f"unsupported currency: {currency!r}")
    opts = options if options is not None else Options()
    value = _coerce_decimal(amount)
    negative = value < 0
    absolute = -value if negative else value
    rounded = absolute.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    integer = int(rounded)
    cents = int((rounded - integer) * 100)

    singular, plural = _CURRENCIES[code]
    groups = _groups(integer)
    ends_at_scale = len(groups) == 1 and groups[0][0] >= 10**6

    if integer == 0:
        core = ""
    elif ends_at_scale and cents == 0:
        core = f"{spell_cardinal(integer, catorze_style=opts.catorze_style)} de {plural}"
    else:
        noun = singular if integer == 1 else plural
        gender = _CURRENCY_GENDER.get(code, "m")
        core = f"{spell_cardinal(integer, gender=gender, catorze_style=opts.catorze_style)} {noun}"

    if cents:
        cent_noun = "centavo" if cents == 1 else "centavos"
        cents_text = f"{spell_cardinal(cents, catorze_style=opts.catorze_style)} {cent_noun}"
        core = f"{core} e {cents_text}" if core else cents_text

    if not core:
        core = f"zero {plural}"
    return "menos " + core if negative else core


def int_to_roman(number: int) -> str:
    """Convert 1..3999 to canonical uppercase roman numerals."""
    if isinstance(number, bool) or not isinstance(number, int):
        raise TypeError("number must be an int")
    if not 1 <= number <= 3999:
        raise ValueError("roman numerals are supported from 1 to 3999")
    remaining = number
    result: list[str] = []
    for value, symbol in _ROMAN_SUBTRACTIVE:
        while remaining >= value:
            result.append(symbol)
            remaining -= value
    return "".join(result)


def roman_to_int(roman: str) -> int:
    """Parse a canonical roman numeral; rejects non-canonical spellings."""
    if not isinstance(roman, str):
        raise TypeError("roman must be a str")
    text = roman.strip().upper()
    if not text or any(char not in _ROMAN_VALUES for char in text):
        raise ValueError(f"invalid roman numeral: {roman!r}")
    total = 0
    previous = 0
    for char in reversed(text):
        value = _ROMAN_VALUES[char]
        if value < previous:
            total -= value
        else:
            total += value
            previous = value
    if int_to_roman(total) != text:
        raise ValueError(f"non-canonical roman numeral: {roman!r}")
    return total


def spell_roman(
    roman: str,
    *,
    context: RomanContext | str = RomanContext.CARDINAL,
    gender: Gender = "m",
    options: Options | None = None,
) -> str:
    """Voice a roman numeral in cardinal or regnal context.

    >>> spell_roman("XXI")                       # "século XXI"
    'vinte e um'
    >>> spell_roman("II", context="regnal")      # "Dom Pedro II"
    'segundo'
    """
    if not isinstance(context, RomanContext):
        try:
            context = RomanContext(context)
        except ValueError as exc:
            raise ValueError("unknown roman context") from exc
    opts = options if options is not None else Options()
    value = roman_to_int(roman)
    if context is RomanContext.REGNAL and value <= 10:
        return spell_ordinal(value, gender=gender)
    return spell_cardinal(value, gender=gender, catorze_style=opts.catorze_style)


_WORD_VALUES: Final[dict[str, int]] = {}
for _value, _word in _ONES_M.items():
    _WORD_VALUES[_word] = _value
for _value, _word in _ONES_F.items():
    _WORD_VALUES[_word] = _value
_WORD_VALUES["catorze"] = 14
for _digit, _word in _TENS.items():
    _WORD_VALUES[_word] = _digit * 10
for _table in (_HUNDREDS_M, _HUNDREDS_F):
    for _hundreds_digit, _word in _table.items():
        _WORD_VALUES[_word] = _hundreds_digit * 100
_WORD_VALUES["cem"] = 100
_WORD_VALUES["cento"] = 100

_SCALE_VALUES: Final[dict[str, int]] = {"mil": 10**3}
for _scale, _singular, _plural in _SCALE_DEFS:
    if _scale == 10**3:
        continue
    _SCALE_VALUES[_singular] = _scale
    _SCALE_VALUES[_plural] = _scale


def parse_spoken_number(text: str) -> int:
    """Parse Portuguese spoken cardinals back to their integer value.

    Accepts the exact output of :func:`spell_cardinal` (and therefore of
    :func:`spell_number` for integers), including ``e`` connectors, scale
    words, commas, gender variants and the ``catorze`` spelling.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a str")
    cleaned = text.strip().lower()
    if not cleaned:
        raise ValueError("empty number")

    sign = 1
    if cleaned.startswith("menos "):
        sign = -1
        cleaned = cleaned[len("menos ") :].strip()

    tokens = [token.strip(",.") for token in cleaned.split()]

    total = 0
    current = 0
    last_scale: int | None = None
    saw_value = False
    for token in tokens:
        if token == "e":
            continue
        scale = _SCALE_VALUES.get(token)
        if scale is not None:
            if current:
                total += current * scale
                current = 0
            elif last_scale is not None and scale > last_scale:
                # Ascending scale chain: "mil milhões" == 1000 * 10**6.
                total *= scale
            elif total == 0:
                total = scale
            else:
                # Descending chain with an unstated multiplier:
                # "sete milhões e mil" == 7*10**6 + 10**3.
                total += scale
            last_scale = scale
            saw_value = True
            continue
        if token not in _WORD_VALUES:
            raise ValueError(f"unknown number word: {token!r}")
        current += _WORD_VALUES[token]
        last_scale = None
        saw_value = True

    if not saw_value:
        raise ValueError("no number words found")
    return sign * (total + current)
