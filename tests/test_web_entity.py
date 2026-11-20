"""URL/e-mail/handle/hashtag vectors, including camelCase splitting."""

from __future__ import annotations

import pytest

from falabr import normalize, normalize_web, split_camel

WEB_CASES: tuple[tuple[str, str], ...] = (
    (
        "https://exemplo.com.br",
        "h t t p s dois pontos barra barra exemplo ponto com ponto br",
    ),
    (
        "http://site.com/a",
        "h t t p dois pontos barra barra site ponto com barra a",
    ),
    ("www.exemplo.com", "w w w ponto exemplo ponto com"),
    (
        "https://x.com.",
        "h t t p s dois pontos barra barra x ponto com.",
    ),
    ("joao@example.com", "joao arroba example ponto com"),
    ("maria.silva@empresa.com.br", "maria ponto silva arroba empresa ponto com ponto br"),
    ("@joao", "arroba joao"),
    ("@JoaoSilva", "arroba joao silva"),
    ("@user_name", "arroba user name"),
    ("#BomDia", "hashtag bom dia"),
    ("#python", "hashtag python"),
    ("#APIREST", "hashtag apirest"),
)

WEB_INVALID_CASES: tuple[str, ...] = (
    "example.com",
    "http://",
    "user@example",
    "@",
    "#",
)

CAMEL_CASES: tuple[tuple[str, str], ...] = (
    ("camelCase", "camel case"),
    ("PascalCase", "pascal case"),
    ("HTTPServer", "http server"),
    ("user_id", "user id"),
    ("simples", "simples"),
)


@pytest.mark.parametrize(("source", "expected"), WEB_CASES)
def test_web_entity(source: str, expected: str) -> None:
    assert normalize_web(source) == expected


@pytest.mark.parametrize("source", WEB_INVALID_CASES)
def test_web_entity_invalid_source_is_preserved(source: str) -> None:
    assert normalize_web(source) == source


@pytest.mark.parametrize(("source", "expected"), CAMEL_CASES)
def test_split_camel(source: str, expected: str) -> None:
    assert split_camel(source) == expected


def test_web_in_context() -> None:
    assert normalize("Escreva para joao@example.com ou acesse www.exemplo.com") == (
        "Escreva para joao arroba example ponto com ou acesse w w w ponto exemplo ponto com"
    )
