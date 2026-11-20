"""Ordinal vectors, masculine and feminine (1..999999).

Sources: Cunha & Cintra, *Nova Gramática do Português Contemporâneo* — ordinal
series; ABL/VOLP for "sétimo", "octogésimo", "milésimo"; Brazilian usage for
the univerbated compounds (no "e" between ordinal components).
"""

from __future__ import annotations

import pytest

from falabr import spell_ordinal

ORDINAL_CASES: tuple[tuple[int, str], ...] = (
    (1, "primeiro"),
    (2, "segundo"),
    (3, "terceiro"),
    (4, "quarto"),
    (5, "quinto"),
    (6, "sexto"),
    (7, "sétimo"),
    (8, "oitavo"),
    (9, "nono"),
    (10, "décimo"),
    (11, "décimo primeiro"),
    (12, "décimo segundo"),
    (15, "décimo quinto"),
    (19, "décimo nono"),
    (20, "vigésimo"),
    (21, "vigésimo primeiro"),
    (25, "vigésimo quinto"),
    (30, "trigésimo"),
    (33, "trigésimo terceiro"),
    (40, "quadragésimo"),
    (50, "quinquagésimo"),
    (60, "sexagésimo"),
    (70, "septuagésimo"),
    (80, "octogésimo"),
    (90, "nonagésimo"),
    (99, "nonagésimo nono"),
    (100, "centésimo"),
    (101, "centésimo primeiro"),
    (110, "centésimo décimo"),
    (111, "centésimo décimo primeiro"),
    (121, "centésimo vigésimo primeiro"),
    (200, "ducentésimo"),
    (300, "trecentésimo"),
    (400, "quadringentésimo"),
    (500, "quingentésimo"),
    (600, "sexcentésimo"),
    (700, "septingentésimo"),
    (800, "octingentésimo"),
    (900, "nongentésimo"),
    (999, "nongentésimo nonagésimo nono"),
    (1000, "milésimo"),
    (1001, "milésimo primeiro"),
    (1021, "milésimo vigésimo primeiro"),
    (1100, "milésimo centésimo"),
    (1234, "milésimo ducentésimo trigésimo quarto"),
    (2000, "dois milésimo"),
    (2024, "dois milésimo vigésimo quarto"),
    (100000, "cem milésimo"),
    (999999, "novecentos e noventa e nove milésimo nongentésimo nonagésimo nono"),
)


@pytest.mark.parametrize(
    ("number", "expected"), ORDINAL_CASES, ids=[str(n) for n, _ in ORDINAL_CASES]
)
def test_ordinal_masculine(number: int, expected: str) -> None:
    assert spell_ordinal(number) == expected


FEMININE_CASES: tuple[tuple[int, str], ...] = (
    (1, "primeira"),
    (2, "segunda"),
    (3, "terceira"),
    (4, "quarta"),
    (7, "sétima"),
    (9, "nona"),
    (10, "décima"),
    (11, "décima primeira"),
    (20, "vigésima"),
    (21, "vigésima primeira"),
    (100, "centésima"),
    (101, "centésima primeira"),
    (121, "centésima vigésima primeira"),
    (200, "ducentésima"),
    (500, "quingentésima"),
    (900, "nongentésima"),
    (1000, "milésima"),
    (1001, "milésima primeira"),
    (2000, "duas milésima"),
    (2024, "duas milésima vigésima quarta"),
)


@pytest.mark.parametrize(
    ("number", "expected"), FEMININE_CASES, ids=[str(n) for n, _ in FEMININE_CASES]
)
def test_ordinal_feminine(number: int, expected: str) -> None:
    assert spell_ordinal(number, gender="f") == expected


def test_ordinal_invalid_inputs() -> None:
    with pytest.raises(ValueError, match="between"):
        spell_ordinal(0)
    with pytest.raises(ValueError, match="between"):
        spell_ordinal(1000000)
    with pytest.raises(ValueError, match="between"):
        spell_ordinal(-1)
    with pytest.raises(TypeError):
        spell_ordinal(True)
    with pytest.raises(TypeError):
        spell_ordinal("21")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="gender"):
        spell_ordinal(1, gender="x")  # type: ignore[arg-type]
