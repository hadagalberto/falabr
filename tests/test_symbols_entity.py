"""Symbol-entity vectors (standalone normalization)."""

from __future__ import annotations

import pytest

from falabr import normalize_symbols

SYMBOL_CASES: tuple[tuple[str, str], ...] = (
    ("a & b", "a e b"),
    ("a+b", "a mais b"),
    ("a=b", "a igual b"),
    ("3 × 4", "3 vezes 4"),
    ("8 ÷ 2", "8 dividido por 2"),
    ("a / b", "a barra b"),
    ("a < b", "a menor que b"),
    ("a > b", "a maior que b"),
    ("a ≤ b", "a menor ou igual a b"),
    ("a ≥ b", "a maior ou igual a b"),
    ("x ≠ y", "x diferente de y"),
    ("x ≈ y", "x aproximadamente igual a y"),
    ("± 2", "mais ou menos 2"),
    ("50%", "50 por cento"),
    ("∞", "infinito"),
    ("a · b", "a vezes b"),
)

SYMBOL_INVALID_CASES: tuple[str, ...] = (
    "a b c",
    "a#b",
    "somente palavras",
)


@pytest.mark.parametrize(("source", "expected"), SYMBOL_CASES)
def test_symbol_entity(source: str, expected: str) -> None:
    assert normalize_symbols(source) == expected


@pytest.mark.parametrize("source", SYMBOL_INVALID_CASES)
def test_symbol_entity_invalid_source_is_preserved(source: str) -> None:
    assert normalize_symbols(source) == source
