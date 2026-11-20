"""Abbreviation dictionary with context rules and acronym voicing.

Abbreviations are expanded from a curated dictionary; a few entries carry
context rules (e.g. ``p.`` is "página" after a number, "por" otherwise).
Acronyms are either read as words (curated list) or spelled letter by letter
using Portuguese letter names; :attr:`falabr.Options.acronym_overrides` wins
over both the curated lists and the heuristic.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Final

from ..numbers import spell_roman
from ..options import Options
from ._common import MatchContext, Matcher, apply_matchers, compose

__all__ = [
    "ABBREVIATIONS",
    "ABBREVIATION_MATCHERS",
    "Abbreviation",
    "normalize_abbreviations",
    "spell_acronym",
]


@dataclass(frozen=True, slots=True)
class Abbreviation:
    """A written abbreviation, its default reading and optional context rules."""

    written: str
    spoken: str
    preceded_by_number: str | None = None
    followed_by_number: str | None = None


_ABBREVIATION_LIST: Final[tuple[Abbreviation, ...]] = (
    Abbreviation("Dr.", "doutor"),
    Abbreviation("Dra.", "doutora"),
    Abbreviation("Dras.", "doutoras"),
    Abbreviation("Drs.", "doutores"),
    Abbreviation("Sr.", "senhor"),
    Abbreviation("Sra.", "senhora"),
    Abbreviation("Srs.", "senhores"),
    Abbreviation("Sras.", "senhoras"),
    Abbreviation("Prof.", "professor"),
    Abbreviation("Profa.", "professora"),
    Abbreviation("Profs.", "professores"),
    Abbreviation("Av.", "avenida"),
    Abbreviation("R.", "rua"),
    Abbreviation("nº", "número"),
    Abbreviation("n°", "número"),
    Abbreviation("n.", "n.", followed_by_number="número"),
    Abbreviation("p.ex.", "por exemplo"),
    Abbreviation("p. ex.", "por exemplo"),
    Abbreviation("e.g.", "por exemplo"),
    Abbreviation("i.e.", "isto é"),
    Abbreviation("cf.", "conforme"),
    Abbreviation("etc.", "etcétera"),
    Abbreviation("obs.", "observação"),
    Abbreviation("aprox.", "aproximadamente"),
    Abbreviation("tel.", "telefone"),
    Abbreviation("ltda.", "limitada"),
    Abbreviation("S.A.", "sociedade anônima"),
    Abbreviation("s.a.", "sociedade anônima"),
    Abbreviation("pág.", "página"),
    Abbreviation("págs.", "páginas"),
    Abbreviation("p.", "por", followed_by_number="página"),
    Abbreviation("ed.", "edição"),
    Abbreviation("vol.", "volume"),
    Abbreviation("cap.", "capítulo"),
    Abbreviation("fig.", "figura"),
    Abbreviation("a.C.", "antes de Cristo"),
    Abbreviation("A.C.", "antes de Cristo"),
    Abbreviation("d.C.", "depois de Cristo"),
    Abbreviation("D.C.", "depois de Cristo"),
)

ABBREVIATIONS: Final[Mapping[str, Abbreviation]] = {
    entry.written: entry for entry in _ABBREVIATION_LIST
}

_ABBREVIATION_PATTERN: Final = "|".join(
    re.escape(entry.written)
    for entry in sorted(_ABBREVIATION_LIST, key=lambda e: len(e.written), reverse=True)
)

_LETTER_NAMES: Final[dict[str, str]] = {
    "A": "á",
    "B": "bê",
    "C": "cê",
    "D": "dê",
    "E": "e",
    "F": "efe",
    "G": "gê",
    "H": "agá",
    "I": "i",
    "J": "jota",
    "K": "cá",
    "L": "ele",
    "M": "eme",
    "N": "ene",
    "O": "ó",
    "P": "pê",
    "Q": "cê",
    "R": "erre",
    "S": "esse",
    "T": "tê",
    "U": "u",
    "V": "vê",
    "W": "dáblio",
    "X": "xis",
    "Y": "ípsilon",
    "Z": "zê",
}

_WORD_ACRONYMS: Final[frozenset[str]] = frozenset(
    {
        "PIX",
        "USP",
        "ENEM",
        "SUS",
        "FUNAI",
        "PETROBRAS",
        "IBGE",
        "DNA",
        "GPS",
        "HIV",
        "IPTU",
        "IPVA",
        "OK",
        "PIB",
        "CNH",
    }
)

_SPELL_ACRONYMS: Final[frozenset[str]] = frozenset(
    {
        "INSS",
        "CPF",
        "CNPJ",
        "RG",
        "CEP",
        "DDD",
        "FGTS",
        "IPI",
        "ICMS",
        "PIS",
        "COFINS",
    }
)

_ROMAN_RE: Final = re.compile(r"[IVXLCDM]+")


def spell_acronym(token: str, options: Options | None = None) -> str:
    """Voice a single acronym (uppercase token) in pt-BR."""
    if not isinstance(token, str):
        raise TypeError("token must be a str")
    key = token.strip().upper()
    if not key:
        raise ValueError("empty acronym")
    opts = options if options is not None else Options()
    override = opts.acronym_overrides.get(key)
    if override is not None:
        if override == "spell":
            return " ".join(_LETTER_NAMES[char] for char in key if char in _LETTER_NAMES)
        if override == "word":
            return key.lower()
        return override
    if _ROMAN_RE.fullmatch(key):
        try:
            return spell_roman(key, options=opts)
        except ValueError:
            # e.g. "DDD" is not a canonical roman numeral; it is an acronym.
            pass
    if key in _WORD_ACRONYMS:
        return key.lower()
    if key in _SPELL_ACRONYMS:
        return " ".join(_LETTER_NAMES[char] for char in key if char in _LETTER_NAMES)
    # Heuristic: unknown uppercase tokens are spelled letter by letter.
    return " ".join(_LETTER_NAMES[char] for char in key if char in _LETTER_NAMES)


def _abbreviation_handler(match: re.Match[str], ctx: MatchContext) -> str:
    raw = match.group()
    entry = ABBREVIATIONS.get(raw)
    if entry is None:
        # Case-insensitive match (e.g. "Dr" written lowercase by the user).
        entry = next(
            (
                candidate
                for candidate in ABBREVIATIONS.values()
                if candidate.written.lower() == raw.lower()
            ),
            None,
        )
    if entry is None:  # pragma: no cover - defensive
        return raw
    before = ctx.text[: match.start()].rstrip()
    after = ctx.text[match.end() :].lstrip()
    if entry.preceded_by_number is not None and before[-1:].isdigit():
        return entry.preceded_by_number
    if entry.followed_by_number is not None and after[:1].isdigit():
        return entry.followed_by_number
    return entry.spoken


def _acronym_handler(match: re.Match[str], ctx: MatchContext) -> str:
    return spell_acronym(match.group(), ctx.options)


ABBREVIATION_MATCHERS: Final[tuple[Matcher, ...]] = (
    Matcher(
        "abbreviation",
        rf"(?<!\w)(?i:{_ABBREVIATION_PATTERN})(?!\w)",
        _abbreviation_handler,
    ),
    Matcher("acronym", r"\b[A-Z]{2,8}\b", _acronym_handler),
)

_ABBREV_RE, _ABBREV_HANDLERS = compose(ABBREVIATION_MATCHERS)


def normalize_abbreviations(text: str, options: Options | None = None) -> str:
    """Normalize dictionary abbreviations and acronyms in a string."""
    if options is None:
        options = Options()
    return apply_matchers(text, _ABBREV_RE, _ABBREV_HANDLERS, options)
