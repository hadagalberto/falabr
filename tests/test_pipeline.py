"""End-to-end pipeline vectors combining multiple entities."""

from __future__ import annotations

import pytest

from falabr import DecimalMode, EmojiMode, Options, normalize, normalize_with_spans

PIPELINE_CASES: tuple[tuple[str, str], ...] = (
    ("palavra comum", "palavra comum"),
    ("3,14", "três vírgula quatorze"),
    ("1.234", "mil duzentos e trinta e quatro"),
    ("3.14", "três vírgula quatorze"),
    ("12,5%", "doze vírgula cinco por cento"),
    ("3º lugar", "terceiro lugar"),
    ("1ª colocada", "primeira colocada"),
    ("R$ 10 e 3/4", "dez reais e três quartos"),
    ("Dr. Silva: 14h30", "doutor Silva: quatorze horas e trinta minutos"),
    ("CPF 123.456.789-09", "cê pê efe um dois três, quatro cinco seis, sete oito nove, zero nove"),
    ("O INSS pagou o PIX", "O i ene esse esse pagou o pix"),
    ("Dom Pedro II", "Dom Pedro segundo"),
    ("Nos anos 90, no século XX", "Nos anos noventa, no século vinte"),
    ("Escreva para joao@example.com", "Escreva para joao arroba example ponto com"),
    ("Acesse www.exemplo.com", "Acesse w w w ponto exemplo ponto com"),
    ("#BomDia pessoal", "hashtag bom dia pessoal"),
    ("São 1,5 km até lá", "São um vírgula cinco quilômetros até lá"),
    ("a & b + c", "a e b mais c"),
    ("Olá 😀 mundo", "Olá mundo"),
)

PIPELINE_OPTION_CASES: tuple[tuple[str, Options, str], ...] = (
    ("3,14", Options(decimal_mode=DecimalMode.DIGITS), "três vírgula um quatro"),
    ("Olá 😀", Options(emoji_mode=EmojiMode.DESCRIBE), "Olá rosto sorridente"),
    ("O INSS", Options(acronym_overrides={"INSS": "word"}), "O inss"),
    ("Pix", Options(user_lexicon={"Pix": "PIX"}), "PIX"),
    ("INSS", Options(user_lexicon={"INSS": "instituto"}), "instituto"),
)


@pytest.mark.parametrize(("source", "expected"), PIPELINE_CASES)
def test_pipeline(source: str, expected: str) -> None:
    assert normalize(source) == expected


@pytest.mark.parametrize(("source", "options", "expected"), PIPELINE_OPTION_CASES)
def test_pipeline_options(source: str, options: Options, expected: str) -> None:
    assert normalize(source, options=options) == expected


def test_pipeline_spans() -> None:
    result = normalize_with_spans("total: 12,5 unidades")
    assert result.text == "total: doze vírgula cinco unidades"
    assert len(result.spans) == 1
    span = result.spans[0]
    assert span.original == "12,5"
    assert span.spoken == "doze vírgula cinco"
    assert result.text[span.start : span.end] == span.spoken


def test_pipeline_spans_multiple_entities() -> None:
    result = normalize_with_spans("Paguei R$ 5 em 05/03/2026")
    assert result.text == "Paguei cinco reais em cinco de março de dois mil e vinte e seis"
    assert [span.kind for span in result.spans] == ["money_symbol", "full_date"]
    for span in result.spans:
        assert result.text[span.start : span.end] == span.spoken


def test_pipeline_invalid_input() -> None:
    with pytest.raises(TypeError):
        normalize(123)  # type: ignore[arg-type]
