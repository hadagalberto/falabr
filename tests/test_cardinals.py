"""Hand-written cardinal vectors.

Sources for the expected strings:
* Celso Cunha & Lindley Cintra, *Nova Gramática do Português Contemporâneo*, 7th
  ed., ch. "Numerais" (connector and comma rules).
* Paul Teyssier, *Manual de Língua Portuguesa* (1989), pp. 181-182.
* Academia Brasileira de Letras, *Vocabulário Ortográfico da Língua Portuguesa*
  (VOLP) — "quatorze" default; "dezesseis/dezessete" spelling.
* Câmara Municipal de Belo Horizonte, *Guia de Redação* — commas between
  bilhão/milhão/milhar.
* Brasil Escola / Norma Culta/ Dicio — "mil e cem", "mil cento e um".
"""

from __future__ import annotations

import pytest

from falabr import MAX_CARDINAL, CatorzeStyle, Options, spell_cardinal, spell_number

# 0..19 — basic lexical forms (Cunha & Cintra; VOLP).
BASICS: tuple[tuple[int, str], ...] = (
    (0, "zero"),
    (1, "um"),
    (2, "dois"),
    (3, "três"),
    (4, "quatro"),
    (5, "cinco"),
    (6, "seis"),
    (7, "sete"),
    (8, "oito"),
    (9, "nove"),
    (10, "dez"),
    (11, "onze"),
    (12, "doze"),
    (13, "treze"),
    (14, "quatorze"),
    (15, "quinze"),
    (16, "dezesseis"),
    (17, "dezessete"),
    (18, "dezoito"),
    (19, "dezenove"),
)

# Tens and tens+units — "e" is always intercalated (Cunha & Cintra, rule 1).
TENS: tuple[tuple[int, str], ...] = (
    (20, "vinte"),
    (21, "vinte e um"),
    (22, "vinte e dois"),
    (27, "vinte e sete"),
    (30, "trinta"),
    (32, "trinta e dois"),
    (40, "quarenta"),
    (43, "quarenta e três"),
    (50, "cinquenta"),
    (55, "cinquenta e cinco"),
    (60, "sessenta"),
    (68, "sessenta e oito"),
    (70, "setenta"),
    (71, "setenta e um"),
    (80, "oitenta"),
    (89, "oitenta e nove"),
    (90, "noventa"),
    (99, "noventa e nove"),
)

# 100..999 — "cem" alone, "cento" before a follower; "e" before tens/units.
HUNDREDS: tuple[tuple[int, str], ...] = (
    (100, "cem"),
    (101, "cento e um"),
    (105, "cento e cinco"),
    (110, "cento e dez"),
    (115, "cento e quinze"),
    (120, "cento e vinte"),
    (125, "cento e vinte e cinco"),
    (199, "cento e noventa e nove"),
    (200, "duzentos"),
    (201, "duzentos e um"),
    (210, "duzentos e dez"),
    (230, "duzentos e trinta"),
    (234, "duzentos e trinta e quatro"),
    (299, "duzentos e noventa e nove"),
    (300, "trezentos"),
    (333, "trezentos e trinta e três"),
    (400, "quatrocentos"),
    (404, "quatrocentos e quatro"),
    (500, "quinhentos"),
    (555, "quinhentos e cinquenta e cinco"),
    (600, "seiscentos"),
    (666, "seiscentos e sessenta e seis"),
    (700, "setecentos"),
    (777, "setecentos e setenta e sete"),
    (800, "oitocentos"),
    (888, "oitocentos e oitenta e oito"),
    (900, "novecentos"),
    (999, "novecentos e noventa e nove"),
)

# 1000..999999 — "e" after mil only before <100 or an exact hundred
# (Cunha & Cintra rule 2; Teyssier; Norma Culta; Dicio).
THOUSANDS: tuple[tuple[int, str], ...] = (
    (1000, "mil"),
    (1001, "mil e um"),
    (1005, "mil e cinco"),
    (1010, "mil e dez"),
    (1021, "mil e vinte e um"),
    (1050, "mil e cinquenta"),
    (1099, "mil e noventa e nove"),
    (1100, "mil e cem"),
    (1101, "mil cento e um"),
    (1110, "mil cento e dez"),
    (1150, "mil cento e cinquenta"),
    (1199, "mil cento e noventa e nove"),
    (1200, "mil e duzentos"),
    (1201, "mil duzentos e um"),
    (1230, "mil duzentos e trinta"),
    (1234, "mil duzentos e trinta e quatro"),
    (1500, "mil e quinhentos"),
    (1501, "mil quinhentos e um"),
    (1800, "mil e oitocentos"),
    (1892, "mil oitocentos e noventa e dois"),
    (1999, "mil novecentos e noventa e nove"),
    (2000, "dois mil"),
    (2001, "dois mil e um"),
    (2020, "dois mil e vinte"),
    (2024, "dois mil e vinte e quatro"),
    (2030, "dois mil e trinta"),
    (2100, "dois mil e cem"),
    (2101, "dois mil cento e um"),
    (2200, "dois mil e duzentos"),
    (2210, "dois mil duzentos e dez"),
    (2222, "dois mil duzentos e vinte e dois"),
    (3000, "três mil"),
    (4000, "quatro mil"),
    (5000, "cinco mil"),
    (6000, "seis mil"),
    (7000, "sete mil"),
    (8000, "oito mil"),
    (9000, "nove mil"),
    (9003, "nove mil e três"),
    (9030, "nove mil e trinta"),
    (10000, "dez mil"),
    (20000, "vinte mil"),
    (21000, "vinte e um mil"),
    (100000, "cem mil"),
    (101000, "cento e um mil"),
    (125000, "cento e vinte e cinco mil"),
    (200000, "duzentos mil"),
    (500000, "quinhentos mil"),
    (516100, "quinhentos e dezesseis mil e cem"),
    (516987, "quinhentos e dezesseis mil novecentos e oitenta e sete"),
    (735346, "setecentos e trinta e cinco mil trezentos e quarenta e seis"),
    (961637, "novecentos e sessenta e um mil seiscentos e trinta e sete"),
    (999999, "novecentos e noventa e nove mil novecentos e noventa e nove"),
)

# Milhões+ — commas between classes >= 10^6, never between mil and units
# (Cunha & Cintra rule 3; CMBH Guia de Redação; SPEC.md examples).
LARGE: tuple[tuple[int, str], ...] = (
    (1000000, "um milhão"),
    (1000001, "um milhão e um"),
    (1100000, "um milhão e cem mil"),
    (1200000, "um milhão e duzentos mil"),
    (1200005, "um milhão, duzentos mil e cinco"),
    (1234567, "um milhão, duzentos e trinta e quatro mil quinhentos e sessenta e sete"),
    (1537469, "um milhão, quinhentos e trinta e sete mil quatrocentos e sessenta e nove"),
    (2000000, "dois milhões"),
    (2500000, "dois milhões e quinhentos mil"),
    (3000000, "três milhões"),
    (3450000, "três milhões, quatrocentos e cinquenta mil"),
    (293572, "duzentos e noventa e três mil quinhentos e setenta e dois"),
    (1000000000, "um bilhão"),
    (1000000001, "um bilhão e um"),
    (1200000000, "um bilhão e duzentos milhões"),
    (
        332415741211,
        "trezentos e trinta e dois bilhões, quatrocentos e quinze milhões, "
        "setecentos e quarenta e um mil duzentos e onze",
    ),
    (10**12, "um trilhão"),
    (10**15, "um quatrilhão"),
    (
        MAX_CARDINAL,
        "novecentos e noventa e nove quatrilhões, novecentos e noventa e nove trilhões, "
        "novecentos e noventa e nove bilhões, novecentos e noventa e nove milhões, "
        "novecentos e noventa e nove mil novecentos e noventa e nove",
    ),
)

CARDINAL_CASES = BASICS + TENS + HUNDREDS + THOUSANDS + LARGE


@pytest.mark.parametrize(
    ("number", "expected"), CARDINAL_CASES, ids=[str(n) for n, _ in CARDINAL_CASES]
)
def test_cardinal_table(number: int, expected: str) -> None:
    assert spell_cardinal(number) == expected
    assert spell_number(number) == expected


# Gender agreement (Cunha & Cintra; Elon.io reference grammar).
GENDER_CASES: tuple[tuple[int, str, str], ...] = (
    (1, "um", "uma"),
    (2, "dois", "duas"),
    (21, "vinte e um", "vinte e uma"),
    (22, "vinte e dois", "vinte e duas"),
    (100, "cem", "cem"),
    (101, "cento e um", "cento e uma"),
    (200, "duzentos", "duzentas"),
    (201, "duzentos e um", "duzentas e uma"),
    (212, "duzentos e doze", "duzentas e doze"),
    (234, "duzentos e trinta e quatro", "duzentas e trinta e quatro"),
    (500, "quinhentos", "quinhentas"),
    (1000, "mil", "mil"),
    (2000, "dois mil", "duas mil"),
    (2100, "dois mil e cem", "duas mil e cem"),
    (2200, "dois mil e duzentos", "duas mil e duzentas"),
    (1234, "mil duzentos e trinta e quatro", "mil duzentas e trinta e quatro"),
    (200000, "duzentos mil", "duzentas mil"),
    (1200000, "um milhão e duzentos mil", "um milhão e duzentas mil"),
    (2000000, "dois milhões", "dois milhões"),
)


@pytest.mark.parametrize(
    ("number", "masculine", "feminine"), GENDER_CASES, ids=[str(n) for n, _, _ in GENDER_CASES]
)
def test_gender(number: int, masculine: str, feminine: str) -> None:
    assert spell_cardinal(number, gender="m") == masculine
    assert spell_cardinal(number, gender="f") == feminine
    assert spell_number(number, gender="f") == feminine


def test_catorze_option() -> None:
    assert spell_number(14) == "quatorze"
    assert spell_number(14, options=Options(catorze_style=CatorzeStyle.CATORZE)) == "catorze"
    assert spell_number(114, options=Options(catorze_style=CatorzeStyle.CATORZE)) == (
        "cento e catorze"
    )
    assert spell_number(2014, options=Options(catorze_style=CatorzeStyle.CATORZE)) == (
        "dois mil e catorze"
    )


def test_negative_numbers() -> None:
    assert spell_cardinal(-1) == "menos um"
    assert spell_cardinal(-234, gender="f") == "menos duzentas e trinta e quatro"
    assert spell_number(-1) == "menos um"
    assert spell_number(-21) == "menos vinte e um"
    assert spell_number(-1100, gender="f") == "menos mil e cem"
    assert spell_number("-1.000.000") == "menos um milhão"


def test_bad_cardinal_inputs() -> None:
    with pytest.raises(TypeError):
        spell_cardinal("12")  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        spell_cardinal(True)
    with pytest.raises(ValueError, match="at most"):
        spell_cardinal(10**18)
    with pytest.raises(ValueError, match="gender"):
        spell_cardinal(1, gender="x")  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="catorze_style"):
        spell_cardinal(1, catorze_style="catorze")  # type: ignore[arg-type]


def test_cardinal_case_count() -> None:
    assert len(CARDINAL_CASES) >= 130
