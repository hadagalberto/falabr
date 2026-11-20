"""Composed normalization pipeline and SSML/sentence helpers.

This is the milestone-2 entry point: every entity is a matcher in one ordered
alternation, so a single left-to-right scan produces the spoken text and the
original-to-spoken spans used for TTS alignment.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Final
from xml.sax.saxutils import escape

from ..numbers import (
    spell_fraction,
    spell_number,
    spell_ordinal,
    spell_roman,
)
from ..options import Gender, Options, RomanContext, SsmlMode
from ._common import (
    MatchContext,
    Matcher,
    compose,
    decimal_value,
    group_digits,
    spell_numeric,
)
from ._gender import following_noun
from .abbrev import ABBREVIATION_MATCHERS, ABBREVIATIONS, spell_acronym
from .datetime import DATETIME_MATCHERS
from .emoji import EMOJI_MATCHERS
from .identifiers import IDENTIFIER_MATCHERS
from .measures import MEASURE_FRACTION_MATCHER
from .money import MONEY_MATCHERS
from .ranges import RANGE_MATCHERS, SCORE_MATCHERS
from .shorthand import SHORTHAND_MATCHERS
from .symbols import SYMBOL_MATCHERS
from .units import UNIT_MATCHERS
from .web import WEB_MATCHERS

__all__ = [
    "Normalized",
    "Span",
    "normalize",
    "normalize_ssml",
    "normalize_with_spans",
    "split_sentences",
]


@dataclass(frozen=True, slots=True)
class Span:
    """One original token and its spoken replacement, in normalized offsets."""

    start: int
    end: int
    original: str
    spoken: str
    kind: str


@dataclass(frozen=True, slots=True)
class Normalized:
    """Result of :func:`normalize_with_spans`."""

    text: str
    spans: tuple[Span, ...]


_NUMBER: Final = r"-?(?:\d{1,3}(?:\.\d{3})+|\d+)(?:,\d+)?"


def _percentage(match: re.Match[str], ctx: MatchContext) -> str:
    raw = match.group()
    number_text = raw[: raw.index("%")].strip()
    return spell_numeric(number_text, ctx.options) + " por cento"


def _ordinal(match: re.Match[str], ctx: MatchContext) -> str:
    raw = match.group()
    gender: Gender = "f" if raw.rstrip().endswith("ª") else "m"
    digits = re.sub(r"[ºª]", "", raw).strip()
    return spell_ordinal(int(digits), gender=gender)


def _fraction(match: re.Match[str], ctx: MatchContext) -> str:
    left, right = re.split(r"\s*/\s*", match.group())
    return spell_fraction(int(left), int(right))


def _spell_count(raw: str, ctx: MatchContext, end: int) -> str:
    """Spell a numeral that may modify the noun immediately after it.

    The following word decides the gender ("duzentas pessoas").  An integer
    that ends exactly at a scale of 10⁶ or above also gains "de" before the
    counted noun ("um milhão de pessoas"), mirroring the money rule; "mil" is
    deliberately excluded ("mil pessoas").  The noun itself is NOT consumed,
    so alignment spans keep pointing at just the numeric token.
    """
    value = decimal_value(raw)
    after = ctx.text[end:]
    gender, noun = following_noun(after)
    spoken = spell_number(value, gender=gender or "m", options=ctx.options)
    integer = int(value)
    if (
        noun is not None
        and value == integer
        and integer >= 10**6
        and integer % 10**6 == 0
        and not re.match(r"\s+(?:de|do|da)\b", after, re.IGNORECASE)
    ):
        # Do not duplicate a "de" the author already wrote ("2.000.000 de
        # pessoas") — the following noun is not consumed by this matcher.
        spoken += " de"
    return spoken


def _plain_number(match: re.Match[str], ctx: MatchContext) -> str:
    return _spell_count(match.group(), ctx, match.end())


def _dotted_number(match: re.Match[str], ctx: MatchContext) -> str:
    raw = match.group()
    negative = raw.startswith("-")
    unsigned = raw.lstrip("-")
    sign = "-" if negative else ""
    if "," in unsigned:
        candidate = sign + unsigned.replace(".", "")
    elif re.fullmatch(r"\d{1,3}(?:\.\d{3})+", unsigned):
        candidate = raw
    else:
        candidate = sign + unsigned.replace(".", ",")
    try:
        return _spell_count(candidate, ctx, match.end())
    except ValueError:
        # Multi-group codes such as "1234.5678.9012" are not pt-BR decimals;
        # read them digit by digit instead of failing the whole normalization.
        return group_digits(raw, ctx.options.digit_group_separator)


# A regnal numeral is identified by the *name* that precedes it, not by a
# fixed handful of monarchs.  The two lists also decide grammatical gender:
# "Elizabeth II" -> "segunda", "Henrique VIII" -> "oitavo".
_FEMALE_REGNAL_NAMES: Final[frozenset[str]] = frozenset(
    {
        "elizabeth",
        "isabel",
        "maria",
        "ana",
        "joana",
        "catarina",
        "sofia",
        "beatriz",
        "helena",
        "vitória",
        "vitoria",
        "rainha",
        "imperatriz",
        "princesa",
        "duquesa",
        "santa",
        "madre",
    }
)
_MALE_REGNAL_NAMES: Final[frozenset[str]] = frozenset(
    {
        "henrique",
        "pedro",
        "joão",
        "joao",
        "pio",
        "bento",
        "carlos",
        "luís",
        "luis",
        "francisco",
        "jorge",
        "filipe",
        "felipe",
        "alberto",
        "alexandre",
        "gregório",
        "inocêncio",
        "leão",
        "leo",
        "dom",
        "papa",
        "paulo",
        "rei",
        "santo",
        "são",
        "sao",
        "imperador",
        "príncipe",
        "duque",
    }
)
_REGNAL_CUES: Final[frozenset[str]] = _MALE_REGNAL_NAMES | _FEMALE_REGNAL_NAMES


def _regnal_gender(words: list[str]) -> Gender:
    cleaned = [word.strip(".,").lower() for word in words]
    if any(word in _FEMALE_REGNAL_NAMES for word in cleaned):
        return "f"
    return "m"


def _acronym_with_context(match: re.Match[str], ctx: MatchContext) -> str:
    token = match.group()
    if re.fullmatch(r"[IVXLCDM]+", token):
        before = ctx.text[: match.start()].rstrip().lower().split()
        if any(word.strip(".,") in _REGNAL_CUES for word in before[-3:]):
            try:
                return spell_roman(
                    token,
                    context=RomanContext.REGNAL,
                    gender=_regnal_gender(before[-3:]),
                    options=ctx.options,
                )
            except ValueError:
                pass
    return spell_acronym(token, ctx.options)


# A regnal numeral is preceded by a *name* (optionally with a title), so the
# whole phrase is one alignment span.  This also covers single-letter numerals
# ("Pio X", "D. Pedro I"), which the generic acronym pattern cannot see.
_REGNAL_TITLE: Final = (
    r"(?:D\.|Dom|Papa|Rainha|rainha|Rei|rei|Santo|Santa|santo|santa|São|são|"
    r"Imperador|imperador|Príncipe|princesa)"
)
_REGNAL_NAME_WORD: Final = r"[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-zà-ÿ]+"
_REGNAL_PATTERN: Final = (
    r"(?<![\w])"
    rf"(?P<rn_title>(?:{_REGNAL_TITLE})\s+)?"
    rf"(?P<rn_name>{_REGNAL_NAME_WORD}(?:\s+{_REGNAL_NAME_WORD})?)"
    r"\s+(?P<rn_numeral>[IVXLCDM]{1,6})\b"
)


def _regnal(match: re.Match[str], ctx: MatchContext) -> str:
    name = match.group("rn_name")
    name_words = name.split()
    if not all(word.lower() in _REGNAL_CUES for word in name_words):
        # "Capítulo V", "Casa X" and similar are not regnal names.
        return match.group()
    title = (match.group("rn_title") or "").strip()
    if title == "D.":
        title = "Dom"
    gender = _regnal_gender([*name_words, title])
    try:
        numeral = spell_roman(
            match.group("rn_numeral"),
            context=RomanContext.REGNAL,
            gender=gender,
            options=ctx.options,
        )
    except ValueError:  # pragma: no cover - the pattern only admits roman letters
        return match.group()
    spoken = f"{name} {numeral}"
    return f"{title} {spoken}" if title else spoken


_NUMBER_MATCHERS: Final[tuple[Matcher, ...]] = (
    Matcher("percentage", rf"{_NUMBER}\s*%", _percentage),
    Matcher("ordinal", r"\b\d{1,6}\s*[ºª]", _ordinal),
    Matcher("fraction", r"\b\d{1,6}\s*/\s*\d{1,6}\b", _fraction),
)

_REGNAL_MATCHER: Final = Matcher("regnal_name", _REGNAL_PATTERN, _regnal)

_RAW_MATCHERS: Final[tuple[Matcher, ...]] = (
    # Shorthand expansion runs before web/symbol handling so "p/" does not
    # become "p barra" and "c/ Ana" does not become "c barra Ana".
    *SHORTHAND_MATCHERS,
    *EMOJI_MATCHERS,
    *WEB_MATCHERS,
    *MONEY_MATCHERS,
    *IDENTIFIER_MATCHERS,
    # Ranges precede the decade matcher so "anos 10-20" is one range.
    *RANGE_MATCHERS,
    # Measure fractions ("1/2 xícara", "3/4 de litro") must win over the
    # short-date matcher, otherwise they are read as dates (1 February, ...).
    MEASURE_FRACTION_MATCHER,
    *DATETIME_MATCHERS,
    # After the time matcher: "14:30" is a clock, "2:1" is a score.
    *SCORE_MATCHERS,
    _REGNAL_MATCHER,
    *_NUMBER_MATCHERS,
    *UNIT_MATCHERS,
    Matcher("dotted_decimal", r"(?<![\w])-?\d+(?:\.\d+)+(?:,\d+)?(?![\w])", _dotted_number),
    Matcher("integer", rf"(?<![\w]){_NUMBER}(?![\w])", _plain_number),
    *ABBREVIATION_MATCHERS,
    *SYMBOL_MATCHERS,
)

# Replace the generic acronym handler with the context-aware one.
_BASE_MATCHERS: Final[tuple[Matcher, ...]] = tuple(
    Matcher(m.name, m.pattern, _acronym_with_context) if m.name == "acronym" else m
    for m in _RAW_MATCHERS
)

_SAY_AS: Final[dict[str, str]] = {
    "money_symbol": "currency",
    "money_words": "currency",
    "cpf": "digits",
    "cnpj": "digits",
    "cep": "digits",
    "card": "digits",
    "phone": "digits",
    "protocol": "digits",
    "full_date": "date",
    "iso_date": "date",
    "month_date": "date",
    "short_date": "date",
    "time_of_day": "time",
    "ordinal": "ordinal",
    "integer": "cardinal",
    "decimal": "cardinal",
    "acronym": "characters",
    "url": "characters",
    "email": "characters",
}


def _lexicon_matcher(options: Options) -> Matcher | None:
    if not options.user_lexicon:
        return None
    lowered = {key.lower(): value for key, value in options.user_lexicon.items()}
    pattern = (
        r"(?i:\b(?:"
        + "|".join(re.escape(key) for key in sorted(lowered, key=len, reverse=True))
        + r")\b)"
    )

    def handler(match: re.Match[str], ctx: MatchContext) -> str:
        return lowered[match.group().lower()]

    return Matcher("user_lexicon", pattern, handler)


def _collapse_spaces(raw: str, spans: list[Span]) -> tuple[str, tuple[Span, ...]]:
    """Collapse horizontal whitespace while keeping spans aligned."""
    out: list[str] = []
    mapping = [0] * (len(raw) + 1)
    i = 0
    pos = 0
    while i < len(raw):
        if raw[i] in " \t":
            j = i
            while j < len(raw) and raw[j] in " \t":
                j += 1
            mapping[i] = pos
            out.append(" ")
            pos += 1
            for k in range(i + 1, j + 1):
                mapping[k] = pos
            i = j
        else:
            out.append(raw[i])
            mapping[i] = pos
            pos += 1
            i += 1
    mapping[len(raw)] = pos
    collapsed = "".join(out)
    leading = len(collapsed) - len(collapsed.lstrip(" \t"))
    output = collapsed.strip(" \t")
    adjusted: list[Span] = []
    for span in spans:
        start = mapping[span.start] - leading
        end = mapping[span.end] - leading
        if end <= start or end > len(output):
            continue
        adjusted.append(Span(start, end, span.original, span.spoken, span.kind))
    return output, tuple(adjusted)


def _normalize_impl(text: str, options: Options) -> Normalized:
    lexicon = _lexicon_matcher(options)
    matchers: tuple[Matcher, ...] = (lexicon, *_BASE_MATCHERS) if lexicon else _BASE_MATCHERS
    regex, handlers = compose(matchers)

    pieces: list[str] = []
    spans: list[Span] = []
    cursor = 0
    output_cursor = 0
    for match in regex.finditer(text):
        pieces.append(text[cursor : match.start()])
        output_cursor += match.start() - cursor
        name = next(n for n in handlers if match.group(n) is not None)
        spoken = handlers[name](match, MatchContext(options, text))
        spans.append(Span(output_cursor, output_cursor + len(spoken), match.group(), spoken, name))
        pieces.append(spoken)
        output_cursor += len(spoken)
        cursor = match.end()
    pieces.append(text[cursor:])
    output, adjusted = _collapse_spaces("".join(pieces), spans)
    # An abbreviation/date matcher consumes the final period of a sentence
    # ("Ltda.", "a.C.", "25 de Março.").  Keep it as a sentence boundary for
    # TTS chunking — the spoken words are unchanged.
    if text.rstrip().endswith(".") and not output.endswith((".", "!", "?")):
        output += "."
    return Normalized(output, adjusted)


def normalize_with_spans(text: str, options: Options | None = None) -> Normalized:
    """Normalize text and return the spoken text plus alignment spans."""
    if not isinstance(text, str):
        raise TypeError("text must be a str")
    return _normalize_impl(text, options if options is not None else Options())


def normalize(text: str, options: Options | None = None) -> str:
    """Turn written pt-BR into exactly what a narrator would say."""
    return normalize_with_spans(text, options).text


def normalize_ssml(text: str, options: Options | None = None) -> str:
    """Normalize text and wrap it in ``<speak>`` with structural breaks.

    Two strategies are supported (see :class:`~falabr.options.SsmlMode`):

    ``normalized`` (default)
        Emit fully normalized, already-spoken words and only ``<break>``
        structure.  Speech engines must never receive spoken words inside a
        ``<say-as>`` element: they re-interpret them (e.g. "trinta e um de
        dezembro" can be re-parsed as a fraction or a different date).

    ``say-as``
        For entities with a declared interpretation, emit the ORIGINAL token
        inside ``<say-as interpret-as=...>`` so the engine does the parsing.
        Everything else is still emitted as spoken words.
    """
    opts = options if options is not None else Options()
    result = normalize_with_spans(text, opts)
    pieces: list[str] = []
    cursor = 0
    for span in result.spans:
        pieces.append(escape(result.text[cursor : span.start]))
        tag = _SAY_AS.get(span.kind)
        if opts.ssml_mode is SsmlMode.SAY_AS and tag is not None:
            pieces.append(f'<say-as interpret-as="{tag}">{escape(span.original)}</say-as>')
        else:
            pieces.append(escape(span.spoken))
        cursor = span.end
    pieces.append(escape(result.text[cursor:]))
    body = "".join(pieces)
    if len(split_sentences(result.text)) > 1:
        body = re.sub(r"(?<=[.!?]) (?=[A-ZÀ-Ý0-9])", ' <break strength="medium"/> ', body)
    return f"<speak>{body}</speak>"


_ABBREV_PERIODS: Final = tuple(
    sorted((written for written in ABBREVIATIONS if "." in written), key=len, reverse=True)
)


def split_sentences(text: str, max_chars: int | None = None) -> list[str]:
    """Split text into TTS chunks, respecting abbreviations and decimals.

    A period inside a known abbreviation or between digits is protected before
    splitting, so ``Dr. Silva`` and ``3.14`` stay in a single chunk.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a str")
    if max_chars is not None and max_chars <= 0:
        raise ValueError("max_chars must be positive")
    protected = re.sub(r"(?<=\d)\.(?=\d)", "\x01", text)
    for written in _ABBREV_PERIODS:
        # Word boundaries keep short abbreviations such as "R." and "n." from
        # matching the final letters of ordinary words ("açúcar.", "min.").
        pattern = rf"(?<!\w){re.escape(written)}(?!\w)"
        protected = re.sub(
            pattern, lambda m: m.group().replace(".", "\x02"), protected, flags=re.IGNORECASE
        )
    chunks = re.split(r"(?<=[.!?])\s+|\n+", protected)
    restored = [chunk.replace("\x01", ".").replace("\x02", ".").strip() for chunk in chunks]
    sentences = [chunk for chunk in restored if chunk]
    if max_chars is None:
        return sentences
    result: list[str] = []
    for sentence in sentences:
        if len(sentence) <= max_chars:
            result.append(sentence)
            continue
        current: list[str] = []
        length = 0
        for word in sentence.split():
            if current and length + 1 + len(word) > max_chars:
                result.append(" ".join(current))
                current, length = [], 0
            current.append(word)
            length += len(word) + (1 if len(current) > 1 else 0)
        if current:
            result.append(" ".join(current))
    return result
