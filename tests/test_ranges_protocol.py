"""Audit-gap coverage: protocol codes, ranges, scores and colon scores.

Every vector is hand-written.  The "not a range / not a score" vectors guard
against over-eager matching: ``10-20`` without a cue is not a range, and
``14:30`` is a clock rather than a score.
"""

from __future__ import annotations

import pytest

from falabr import normalize, normalize_ranges

RANGE_CASES: tuple[tuple[str, str], ...] = (
    ("de 10-20", "de dez a vinte"),
    ("páginas 10-20", "páginas de dez a vinte"),
    ("pág. 10-20", "pág. de dez a vinte"),
    ("anos 10-20", "anos de dez a vinte"),
    ("faixa 100-200", "faixa de cem a duzentos"),
    ("10–20", "de dez a vinte"),
    ("10—20", "de dez a vinte"),
)

NOT_A_RANGE_CASES: tuple[tuple[str, str], ...] = (
    ("10-20", "dez-vinte"),
    ("3/4 de xícara", "três quartos de xícara"),
    ("3,14", "três vírgula quatorze"),
    ("2026-03-05", "cinco de março de dois mil e vinte e seis"),
)

SCORE_CASES: tuple[tuple[str, str], ...] = (
    ("placar 3-1", "placar três a um"),
    ("resultado 2:1", "resultado dois a um"),
    ("razão 3:4", "razão três a quatro"),
    ("proporção 1:2", "proporção um a dois"),
    ("placar 3x1", "placar três a um"),
    ("placar 3×1", "placar três a um"),
    ("2:1", "dois a um"),
)

NOT_A_SCORE_CASES: tuple[tuple[str, str], ...] = (
    ("14:30", "quatorze horas e trinta minutos"),
    ("14:01", "quatorze horas e um minuto"),
    ("9h05", "nove horas e cinco minutos"),
)

PROTOCOL_CASES: tuple[tuple[str, str], ...] = (
    ("Protocolo 2026/12345", "Protocolo dois zero dois seis, um dois três quatro cinco"),
    ("nº 1234.5678", "número um dois três quatro, cinco seis sete oito"),
    ("cod. 12.345.678-9", "código um dois, três quatro cinco, seis sete oito, nove"),
    ("ticket 123.456", "ticket um dois três, quatro cinco seis"),
    # Bare multi-group codes used to raise ValueError; now read digit by digit.
    ("1234.5678.9012", "um dois três quatro, cinco seis sete oito, nove zero um dois"),
)

NOT_A_PROTOCOL_CASES: tuple[tuple[str, str], ...] = (
    ("1234.56", "mil duzentos e trinta e quatro vírgula cinquenta e seis"),
    ("05/03/2026", "cinco de março de dois mil e vinte e seis"),
    ("1.234,56", "mil duzentos e trinta e quatro vírgula cinquenta e seis"),
)


@pytest.mark.parametrize(("source", "expected"), RANGE_CASES)
def test_range(source: str, expected: str) -> None:
    assert normalize(source) == expected
    assert normalize_ranges(source) == expected


@pytest.mark.parametrize(("source", "expected"), NOT_A_RANGE_CASES)
def test_not_a_range(source: str, expected: str) -> None:
    assert normalize(source) == expected
    assert normalize_ranges(source) == source  # standalone helper is cue-driven


@pytest.mark.parametrize(("source", "expected"), SCORE_CASES)
def test_score(source: str, expected: str) -> None:
    assert normalize(source) == expected
    assert normalize_ranges(source) == expected


@pytest.mark.parametrize(("source", "expected"), NOT_A_SCORE_CASES)
def test_not_a_score(source: str, expected: str) -> None:
    assert normalize(source) == expected
    assert normalize_ranges(source) == source


@pytest.mark.parametrize(("source", "expected"), PROTOCOL_CASES)
def test_protocol_code(source: str, expected: str) -> None:
    assert normalize(source) == expected
