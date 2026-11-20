"""SSML output and sentence segmentation vectors."""

from __future__ import annotations

import pytest

from falabr import normalize_ssml, split_sentences
from falabr.options import Options, SsmlMode

# Default (normalized): fully spoken words, only <break> structure.  No
# <say-as> may wrap an already-interpreted word (milestone 5).
SSML_CASES: tuple[tuple[str, str], ...] = (
    ("a & b 3", "<speak>a e b três</speak>"),
    ("R$ 10", "<speak>dez reais</speak>"),
    (
        "123.456.789-09",
        "<speak>um dois três, quatro cinco seis, sete oito nove, zero nove</speak>",
    ),
    ("05/03/2026", "<speak>cinco de março de dois mil e vinte e seis</speak>"),
    ("palavras", "<speak>palavras</speak>"),
    ("Chegou. Saiu.", '<speak>Chegou. <break strength="medium"/> Saiu.</speak>'),
)

# Explicit say-as mode: ORIGINAL token inside the tag, never the spoken words.
SSML_SAY_AS_CASES: tuple[tuple[str, str], ...] = (
    ("a & b 3", '<speak>a e b <say-as interpret-as="cardinal">3</say-as></speak>'),
    ("R$ 10", '<speak><say-as interpret-as="currency">R$ 10</say-as></speak>'),
    (
        "123.456.789-09",
        '<speak><say-as interpret-as="digits">123.456.789-09</say-as></speak>',
    ),
    ("05/03/2026", '<speak><say-as interpret-as="date">05/03/2026</say-as></speak>'),
    ("3º lugar", '<speak><say-as interpret-as="ordinal">3º</say-as> lugar</speak>'),
    ("palavras", "<speak>palavras</speak>"),
    ("Chegou. Saiu.", '<speak>Chegou. <break strength="medium"/> Saiu.</speak>'),
)

SENTENCE_CASES: tuple[tuple[str, list[str]], ...] = (
    ("", []),
    ("Uma frase", ["Uma frase"]),
    ("Chegou. Saiu.", ["Chegou.", "Saiu."]),
    ("Oh! Tudo bem? Sim.", ["Oh!", "Tudo bem?", "Sim."]),
    ("Dr. Silva chegou. Sra. Maria saiu.", ["Dr. Silva chegou.", "Sra. Maria saiu."]),
    ("3.14 é pi. Certo.", ["3.14 é pi.", "Certo."]),
    ("Primeira\nSegunda", ["Primeira", "Segunda"]),
    ("R$ 1.234,56. Total ok.", ["R$ 1.234,56.", "Total ok."]),
)


@pytest.mark.parametrize(("source", "expected"), SSML_CASES)
def test_ssml(source: str, expected: str) -> None:
    assert normalize_ssml(source) == expected


@pytest.mark.parametrize(("source", "expected"), SSML_SAY_AS_CASES)
def test_ssml_say_as_mode(source: str, expected: str) -> None:
    options = Options(ssml_mode=SsmlMode.SAY_AS)
    assert normalize_ssml(source, options) == expected


def test_ssml_modes_are_explicit_and_different() -> None:
    text = "até 31/12, R$ 10 e 3º lugar"
    normalized = normalize_ssml(text)
    say_as = normalize_ssml(text, Options(ssml_mode=SsmlMode.SAY_AS))
    assert "<say-as" not in normalized
    assert "trinta e um de dezembro" in normalized
    assert "<say-as" in say_as
    assert "31/12" in say_as
    assert "trinta e um de dezembro" not in say_as


def test_ssml_escapes_special_characters() -> None:
    output = normalize_ssml("2 < 3 & 4 > 1")
    assert "&amp;" not in output  # symbols are spoken, not emitted raw
    assert "<" in output
    assert output.startswith("<speak>")
    assert "menor que" in output
    assert "maior que" in output


@pytest.mark.parametrize(("source", "expected"), SENTENCE_CASES)
def test_split_sentences(source: str, expected: list[str]) -> None:
    assert split_sentences(source) == expected


def test_split_sentences_max_chars() -> None:
    text = "uma duas três quatro cinco seis sete oito nove dez"
    chunks = split_sentences(text, max_chars=12)
    assert all(len(chunk) <= 12 for chunk in chunks)
    assert " ".join(chunks) == text


def test_split_sentences_invalid_max_chars() -> None:
    with pytest.raises(ValueError, match="max_chars"):
        split_sentences("texto", max_chars=0)
