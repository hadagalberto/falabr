"""Milestone 5 maintainer-fix regressions.

Three fixes are pinned here with hand-written table/golden vectors:

* a ``dd/mm`` / ``d/m`` pair is a date only with date context (later review
  corrected the earlier "always a date when valid" rule);
* SSML never wraps already-spoken words in ``<say-as>`` (two explicit modes);
* a fraction before a measure noun takes agreement/preposition rules.

Grammar: Cunha & Cintra (numerais fracionários) and the pt-BR convention that
``meio``/``meia`` precede the noun directly while other fractions take ``de``.
"""

from __future__ import annotations

import pytest

from falabr import (
    Options,
    SsmlMode,
    normalize,
    normalize_ssml,
    normalize_with_spans,
)

# --- Finding 4: day/month is a date only in date context ---------------------
# Independent review corrected the original rule: a bare valid d/m pair is a
# fraction ("3/4" -> "três quartos").  "até", "dia", "data" and a following year
# keep the calendar reading.  The five bare expectations below are corrected
# here (they used to encode the bug) per the review-fix hard rules.

DATE_VS_FRACTION_CASES: tuple[tuple[str, str], ...] = (
    ("até 31/12!", "até trinta e um de dezembro!"),
    ("31/12", "trinta e um doze avos"),
    ("1/2", "um meio"),
    ("3/4", "três quartos"),
    ("12/10", "doze décimos"),
    ("5/3", "cinco terços"),
    ("05/03", "cinco terços"),
    ("dia 5/3", "dia cinco de março"),
    ("data 12/10", "data doze de outubro"),
    ("32/12", "trinta e dois doze avos"),  # invalid day -> fraction
    ("31/13", "31/13"),  # invalid day and month -> preserved
    ("05/03/2026", "cinco de março de dois mil e vinte e seis"),
    ("dia 5/3 de 2026", "dia cinco de março de dois mil e vinte e seis"),
)

# --- Finding 6: fraction + noun agreement / preposition ----------------------

MEASURE_FRACTION_CASES: tuple[tuple[str, str], ...] = (
    ("1/2 xícara", "meia xícara"),
    ("1/2 de xícara", "meia xícara"),
    ("1/2 litro", "meio litro"),
    ("1/2 kg", "meio kg"),
    ("1/2 colher", "meia colher"),
    ("1/2 hora", "meia hora"),
    ("1/2 xícaras", "meia xícara"),
    ("3/4 colheres", "três quartos de colher"),
    ("1/3 xícara", "um terço de xícara"),
    ("1/4 xícara", "um quarto de xícara"),
    ("3/4 xícara", "três quartos de xícara"),
    ("3/4 de xícara", "três quartos de xícara"),
    ("2/3 xícara", "dois terços de xícara"),
    ("3/4 de leite", "três quartos de leite"),
    ("use 1/2 xícara de leite", "use meia xícara de leite"),
    ("3/4 de xícara de açúcar", "três quartos de xícara de açúcar"),
)

GOLDEN_PARAGRAPH_CASES: tuple[tuple[str, str], ...] = (
    (
        "Até 31/12, use 1/2 xícara de leite e 3/4 de açúcar. "
        "O pedido foi feito em 05/03/2026. Chegou. Saiu.",
        "Até trinta e um de dezembro, use meia xícara de leite e três quartos de açúcar. "
        "O pedido foi feito em cinco de março de dois mil e vinte e seis. Chegou. Saiu.",
    ),
)

# --- Finding 5: the two SSML strategies -------------------------------------

SSML_MODE_CASES: tuple[tuple[str, SsmlMode, str], ...] = (
    ("R$ 10", SsmlMode.NORMALIZED, "<speak>dez reais</speak>"),
    (
        "R$ 10",
        SsmlMode.SAY_AS,
        '<speak><say-as interpret-as="currency">R$ 10</say-as></speak>',
    ),
    ("05/03/2026", SsmlMode.NORMALIZED, "<speak>cinco de março de dois mil e vinte e seis</speak>"),
    (
        "05/03/2026",
        SsmlMode.SAY_AS,
        '<speak><say-as interpret-as="date">05/03/2026</say-as></speak>',
    ),
    (
        "123.456.789-09",
        SsmlMode.NORMALIZED,
        "<speak>um dois três, quatro cinco seis, sete oito nove, zero nove</speak>",
    ),
    (
        "123.456.789-09",
        SsmlMode.SAY_AS,
        '<speak><say-as interpret-as="digits">123.456.789-09</say-as></speak>',
    ),
    ("a & b 3", SsmlMode.NORMALIZED, "<speak>a e b três</speak>"),
    (
        "a & b 3",
        SsmlMode.SAY_AS,
        '<speak>a e b <say-as interpret-as="cardinal">3</say-as></speak>',
    ),
    (
        "Chegou. Saiu.",
        SsmlMode.NORMALIZED,
        '<speak>Chegou. <break strength="medium"/> Saiu.</speak>',
    ),
    ("Chegou. Saiu.", SsmlMode.SAY_AS, '<speak>Chegou. <break strength="medium"/> Saiu.</speak>'),
)


@pytest.mark.parametrize(("source", "expected"), DATE_VS_FRACTION_CASES)
def test_valid_day_month_is_a_date(source: str, expected: str) -> None:
    assert normalize(source) == expected


@pytest.mark.parametrize(("source", "expected"), MEASURE_FRACTION_CASES)
def test_fraction_before_noun_agrees(source: str, expected: str) -> None:
    assert normalize(source) == expected


@pytest.mark.parametrize(("source", "expected"), GOLDEN_PARAGRAPH_CASES)
def test_golden_paragraph(source: str, expected: str) -> None:
    assert normalize(source) == expected


@pytest.mark.parametrize(("source", "mode", "expected"), SSML_MODE_CASES)
def test_ssml_mode(source: str, mode: SsmlMode, expected: str) -> None:
    assert normalize_ssml(source, Options(ssml_mode=mode)) == expected


def test_ssml_defaults_to_normalized() -> None:
    assert normalize_ssml("R$ 10") == normalize_ssml(
        "R$ 10", Options(ssml_mode=SsmlMode.NORMALIZED)
    )


def test_ssml_never_reinterprets_spoken_words() -> None:
    text = "até 31/12, R$ 10 e 3º lugar"
    normalized = normalize_ssml(text)
    assert "<say-as" not in normalized
    assert "trinta e um de dezembro" in normalized
    say_as = normalize_ssml(text, Options(ssml_mode=SsmlMode.SAY_AS))
    assert "<say-as" in say_as
    assert "31/12" in say_as
    assert "trinta e um de dezembro" not in say_as


def test_non_fraction_measure_expression_is_preserved() -> None:
    assert normalize("1/1 xícara") == "1/1 xícara"


def test_measure_fraction_span_is_exact() -> None:
    result = normalize_with_spans("Use 1/2 xícara de leite")
    assert result.text == "Use meia xícara de leite"
    span = result.spans[0]
    assert span.original == "1/2 xícara"
    assert span.spoken == "meia xícara"
    assert span.kind == "measure_fraction"
    assert result.text[span.start : span.end] == span.spoken


def test_ssml_mode_rejects_strings() -> None:
    with pytest.raises(TypeError, match="ssml_mode"):
        Options(ssml_mode="say-as")  # type: ignore[arg-type]
