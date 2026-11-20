"""Emoji removal/description vectors with CLDR-derived names."""

from __future__ import annotations

import pytest

from falabr import CLDR_SOURCE, EmojiMode, Options, describe_emoji, normalize, normalize_emoji

DESCRIBE_CASES: tuple[tuple[str, str], ...] = (
    ("😀", "rosto sorridente"),
    ("😂", "rosto com lágrimas de alegria"),
    ("🥰", "rosto sorridente com corações"),
    ("😎", "rosto com óculos de sol"),
    ("🤔", "rosto pensativo"),
    ("😭", "rosto chorando alto"),
    ("👍", "polegar para cima"),
    ("👎", "polegar para baixo"),
    ("👏", "palmas"),
    ("🙏", "mãos juntas"),
    ("❤️", "coração vermelho"),
    ("💔", "coração partido"),
    ("🔥", "fogo"),
    ("🌈", "arco-íris"),
    ("💡", "lâmpada"),
    ("🍕", "pizza"),
    ("🍔", "hambúrguer"),
    ("🚀", "foguete"),
    ("🏆", "troféu"),
    ("✅", "marca de verificação"),
    ("⚠️", "aviso"),
    ("👨‍👩‍👧", "família"),
    ("👍🏽", "polegar para cima"),
    ("🦄", "emoji"),
)

DESCRIBE_OPTIONS = Options(emoji_mode=EmojiMode.DESCRIBE)

NORMALIZE_EMOJI_CASES: tuple[tuple[str, str], ...] = (
    ("Olá 😀 mundo", "Olá rosto sorridente mundo"),
    ("Comprei 🍕 e 🍔", "Comprei pizza e hambúrguer"),
    ("💡 ideia", "lâmpada ideia"),
    ("😀", "rosto sorridente"),
)

REMOVE_EMOJI_CASES: tuple[tuple[str, str], ...] = (
    ("Olá 😀 mundo", "Olá mundo"),
    ("Comprei 🍕 e 🍔", "Comprei e"),
    ("💡 ideia", "ideia"),
    ("😀", ""),
)


@pytest.mark.parametrize(("emoji", "expected"), DESCRIBE_CASES)
def test_cldr_short_names(emoji: str, expected: str) -> None:
    assert describe_emoji(emoji) == expected


@pytest.mark.parametrize(("source", "expected"), NORMALIZE_EMOJI_CASES)
def test_emoji_describe(source: str, expected: str) -> None:
    assert normalize_emoji(source, options=DESCRIBE_OPTIONS) == expected


@pytest.mark.parametrize(("source", "expected"), REMOVE_EMOJI_CASES)
def test_emoji_remove(source: str, expected: str) -> None:
    assert normalize_emoji(source) == expected


def test_cldr_source_is_cited() -> None:
    assert "cldr" in CLDR_SOURCE.lower()
    assert "pt_BR.xml" in CLDR_SOURCE


def test_emoji_in_pipeline() -> None:
    assert normalize("Parabéns 🎉!", options=DESCRIBE_OPTIONS) == "Parabéns festa!"
    assert normalize("Parabéns 🎉!") == "Parabéns!"


def test_describe_emoji_invalid_input() -> None:
    with pytest.raises(TypeError):
        describe_emoji(1)  # type: ignore[arg-type]
