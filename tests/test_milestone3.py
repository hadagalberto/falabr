"""Milestone-3 composition guarantees: ordering, spans, SSML and chunking."""

from __future__ import annotations

import xml.etree.ElementTree as ET

import pytest

from falabr import (
    CatorzeStyle,
    DecimalMode,
    EmojiMode,
    Options,
    RomanContext,
    normalize,
    normalize_ssml,
    normalize_with_spans,
    split_sentences,
)
from falabr.entities.pipeline import Span

_MIXED: str = (
    "Paguei R$ 5 em 05/03/2026. CPF 123.456.789-09. Acesse www.exemplo.com. O INSS pagou o PIX."
)


def test_matcher_priority_specific_entities_win() -> None:
    """Money/date/identifier matchers win over the generic number matcher."""
    assert normalize("R$ 10") == "dez reais"
    assert normalize("05/03/2026") == "cinco de março de dois mil e vinte e seis"
    assert normalize("12,5%") == "doze vírgula cinco por cento"
    assert normalize_with_spans("R$ 1.234,56").spans[0].kind == "money_symbol"


def test_user_lexicon_overrides_every_entity() -> None:
    options = Options(user_lexicon={"Pix": "PIX", "INSS": "instituto", "5": "cinco"})
    assert normalize("Pix INSS 5", options=options) == "PIX instituto cinco"


def test_spans_are_ordered_non_overlapping_and_aligned() -> None:
    result = normalize_with_spans(_MIXED)
    previous_end = 0
    for span in result.spans:
        assert span.start >= previous_end, "spans must not overlap"
        assert 0 <= span.start < span.end <= len(result.text)
        assert result.text[span.start : span.end] == span.spoken
        previous_end = span.end
    assert [span.kind for span in result.spans] == [
        "money_symbol",
        "full_date",
        "acronym",
        "cpf",
        "url",
        "acronym",
        "acronym",
    ]


def test_single_scan_never_double_normalizes() -> None:
    """A replacement is never fed back through another matcher."""
    result = normalize_with_spans("R$ 1.234,56 e 05/03/2026")
    assert result.text == (
        "mil duzentos e trinta e quatro reais e cinquenta e seis centavos "
        "e cinco de março de dois mil e vinte e seis"
    )
    assert len(result.spans) == 2
    assert all(span.spoken == normalize(span.original) for span in result.spans)


def test_ssml_is_well_formed_xml() -> None:
    ssml = normalize_ssml(_MIXED)
    root = ET.fromstring(ssml)
    assert root.tag == "speak"
    assert ssml.count("<say-as ") == ssml.count("</say-as>")


def test_ssml_escapes_spoken_and_plain_text() -> None:
    options = Options(user_lexicon={"x": "a & b < c"})
    ssml = normalize_ssml("x & y", options=options)
    assert "&amp;" in ssml
    assert "&lt;" in ssml
    assert ET.fromstring(ssml).text == "a & b < c e y"


def test_options_compose_without_conflicts() -> None:
    options = Options(
        catorze_style=CatorzeStyle.CATORZE,
        decimal_mode=DecimalMode.DIGITS,
        emoji_mode=EmojiMode.DESCRIBE,
        roman_context=RomanContext.REGNAL,
    )
    assert normalize("14 3,14 IX 😀", options=options) == (
        "catorze três vírgula um quatro nono rosto sorridente"
    )


def test_options_reject_wrong_roman_context() -> None:
    with pytest.raises(TypeError, match="roman_context"):
        Options(roman_context="regnal")  # type: ignore[arg-type]


def test_tts_chunking_of_a_paragraph() -> None:
    text = normalize_with_spans(_MIXED).text
    chunks = split_sentences(text, max_chars=40)
    assert len(chunks) > 1
    assert all(len(chunk) <= 40 for chunk in chunks)
    assert " ".join(chunks) == text


@pytest.mark.parametrize(
    "span",
    [
        Span(0, 3, "abc", "abc", "test"),
        Span(1, 2, "b", "b", "test"),
    ],
)
def test_span_is_frozen_and_hashable(span: Span) -> None:
    assert hash(span) == hash(Span(*(span.start, span.end, span.original, span.spoken, span.kind)))
