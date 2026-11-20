"""SSML output and sentence segmentation vectors."""

from __future__ import annotations

import pytest

from falabr import normalize_ssml, split_sentences

SSML_CASES: tuple[tuple[str, str], ...] = (
    ("a & b 3", '<speak>a e b <say-as interpret-as="cardinal">três</say-as></speak>'),
    ("R$ 10", '<speak><say-as interpret-as="currency">dez reais</say-as></speak>'),
    (
        "123.456.789-09",
        '<speak><say-as interpret-as="digits">'
        "um dois três, quatro cinco seis, sete oito nove, zero nove"
        "</say-as></speak>",
    ),
    (
        "05/03/2026",
        '<speak><say-as interpret-as="date">'
        "cinco de março de dois mil e vinte e seis</say-as></speak>",
    ),
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
