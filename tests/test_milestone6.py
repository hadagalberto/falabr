"""Milestone 6: independent-review regression vectors.

Every expected value below is hand-derived from the pt-BR sources cited in
comments (Cunha & Cintra, VOLP/ABL usage, CLDR pt-BR annotations), never from
the library's own output.  Each table targets one review finding.

Finding map (see docs/REVIEW-FIXES.md for the final report):

* HIGH-1 gender agreement for numbers before a noun.
* HIGH-2 money "de reais" before an exact milhão/bilhão with cents.
* MED-3 "de" after milhão/bilhão before any noun; "mil" never takes "de".
* MED-4 d/m: partitive cues ("do/da/dos/das/de" + noun) make a fraction; a
  valid bare pair is a date (SPEC.md, restored in milestone 7), with real-calendar
  validation; ordinal day markers in dates.
* MED-5 regnal numerals after any capitalized name, feminine ordinals for
  female names, single-letter numerals (I, V, X).
* MED-6 0800/0300/4004-style service phone numbers.
* MED-7 emoji grapheme clusters: adjacency, flags, ZWJ, skin tones.
* LOW-8 "12h00" is "doze horas" (minute 00 is not "zero minutos").
* LOW-9 scores/dimensions "7 x 1"/"3 x 4"/"2-0", "entre X-Y" ranges.
* LOW-10 "BR-116", "km 23", "apto.", "Sto.", sentence-final periods.
* LOW-11 ONU/OTAN/MEC as words, IPTU spelled, "COVID-19", URL scheme/www.
"""

from __future__ import annotations

import pytest

from falabr import (
    EmojiMode,
    Options,
    describe_emoji,
    normalize,
    spell_acronym,
    spell_money,
)

DESCRIBE = Options(emoji_mode=EmojiMode.DESCRIBE)

# ---------------------------------------------------------------------------
# HIGH-1: gender agreement of running-text numbers.
#
# Cunha & Cintra, "Nova Gramática do Português Contemporâneo", cap. Numerais:
# cardinals agree in gender with the noun they quantify ("duzentas páginas",
# "duas mil pessoas").  "Grama" is masculine ("o grama", VOLP/Aurélio entry
# for the unit of mass), so "200 gramas" stays "duzentos gramas".
# ---------------------------------------------------------------------------
GENDER_TEXT_CASES: tuple[tuple[str, str], ...] = (
    ("1 filha", "uma filha"),
    ("200 pessoas", "duzentas pessoas"),
    ("2.000 pessoas", "duas mil pessoas"),
    # The verb "São" is ordinary text and is preserved (corrected from an
    # expectation that accidentally dropped it).
    ("São 22 horas", "São vinte e duas horas"),
    ("1 vez", "uma vez"),
    ("2 semanas", "duas semanas"),
    ("1 tonelada", "uma tonelada"),
    ("2 colheres", "duas colheres"),
    ("1.101 pessoas", "mil cento e uma pessoas"),
    ("21 pessoas", "vinte e uma pessoas"),
    ("1,5 horas", "uma vírgula cinco horas"),
    ("2 crianças", "duas crianças"),
    ("500 cidades", "quinhentas cidades"),
    ("1 cidade", "uma cidade"),
    ("chegou às 2 de manhã", "chegou às duas de manhã"),
    # Masculine nouns keep the masculine reading.
    ("2 meninos", "dois meninos"),
    ("201 livros", "duzentos e um livros"),
    ("200 gramas", "duzentos gramas"),
    ("1 quilograma", "um quilograma"),
    ("São 31 dias", "São trinta e um dias"),
    # Greek -ma masculines: the -a heuristic must not fire.
    ("1 problema", "um problema"),
    ("2 mapas", "dois mapas"),
    # A single letter or a preposition after the number is not a counted noun.
    ("Enviou 1 para cada setor", "Enviou um para cada setor"),
    ("Escolheu 1 de cada", "Escolheu um de cada"),
    ("Frações: 3 a 2", "Frações: três a dois"),
)

GENDER_SENTENCE_CASES: tuple[tuple[str, str], ...] = (
    (
        "A assembleia reuniu 1.101 pessoas em 3 sessões.",
        "A assembleia reuniu mil cento e uma pessoas em três sessões.",
    ),
    (
        "O município tem 32.018 pessoas e 2.500 empresas.",
        # Corrected to "duas mil" agreement: the multiplier before the
        # invariant "mil" agrees with the feminine counted noun, as in the
        # milestone's "2.000 pessoas" -> "duas mil pessoas" case.
        "O município tem trinta e duas mil e dezoito pessoas e duas mil e quinhentas empresas.",
    ),
    (
        "Restam 2 semanas e 1 tonelada de arroz.",
        "Restam duas semanas e uma tonelada de arroz.",
    ),
    ("Ele tem 1 filha e 2 filhos.", "Ele tem uma filha e dois filhos."),
    (
        "Das 200 propostas, 150 foram aceitas.",
        "Das duzentas propostas, cento e cinquenta foram aceitas.",
    ),
    (
        "São 22 horas e 30 minutos.",
        "São vinte e duas horas e trinta minutos.",
    ),
)


# ---------------------------------------------------------------------------
# HIGH-2: money — an exact milhão/bilhão takes "de" even when cents follow.
#
# ABL/VOLP usage for "real" + Cunha & Cintra (numerals): "dois milhões de
# reais"; the cents join with "e" ("... e cinquenta centavos").
# ---------------------------------------------------------------------------
MONEY_CENTS_CASES: tuple[tuple[str, str], ...] = (
    ("R$ 2.000.000,50", "dois milhões de reais e cinquenta centavos"),
    ("R$ 1.000.000,01", "um milhão de reais e um centavo"),
    ("R$ 2.000.000,00", "dois milhões de reais"),
    ("R$ 1.000.000", "um milhão de reais"),
    # Non-exact integers never take "de" (unchanged behaviour, pinned).
    ("R$ 1.000.001", "um milhão e um reais"),
    ("R$ 1.000.001,50", "um milhão e um reais e cinquenta centavos"),
)


# ---------------------------------------------------------------------------
# MED-3: "de" after milhão/bilhão before any noun; never after "mil".
#
# "um milhão de pessoas" (Cunha & Cintra: a number ending in a -ão scale word
# governs its noun with "de"); "dez mil reais" (no "de" after "mil").
# ---------------------------------------------------------------------------
SCALE_DE_CASES: tuple[tuple[str, str], ...] = (
    ("1.000.000 pessoas", "um milhão de pessoas"),
    ("2.000.000 pessoas", "dois milhões de pessoas"),
    ("2.000.000 de pessoas", "dois milhões de pessoas"),
    ("1.000.000 anos", "um milhão de anos"),
    ("3.000.000.000 estrelas", "três bilhões de estrelas"),
    # "mil" never takes "de".
    ("10 mil pessoas", "dez mil pessoas"),
    ("R$ 10,5 mil", "dez vírgula cinco mil reais"),
    # Scale suffixes in money keep their "de" (mi/bi) — pinned.
    ("R$ 3,5 bi", "três vírgula cinco bilhões de reais"),
    # Nothing follows: no "de" is inserted at a boundary.
    ("Tinha 1.000.000.", "Tinha um milhão."),
)


# ---------------------------------------------------------------------------
# MED-4: d/m disambiguation and real-calendar validation.
#
# "1/4 do valor" is a fraction: the quantifier "do + noun" attaches to the
# fraction (Cunha & Cintra, numerais fracionários).  Per SPEC.md a VALID bare
# calendar date is a date by default; only an impossible date ("Dia 31/02" —
# February never has 31 days) must not be voiced as a date.
# ---------------------------------------------------------------------------
FRACTION_VS_DATE_CASES: tuple[tuple[str, str], ...] = (
    ("Recebeu 1/4 do valor", "Recebeu um quarto do valor"),
    ("Comeu 5/12 da pizza", "Comeu cinco doze avos da pizza"),
    ("Ganhou 2/3 do prêmio", "Ganhou dois terços do prêmio"),
    ("Ficou com 3/4 da herança", "Ficou com três quartos da herança"),
    # Corrected in milestone 7: a57e3a1 had inverted SPEC.md's date rule and
    # rewritten these to fractions ("um meio", "três quartos").  A valid bare
    # pair is a date; a partitive cue above is what makes a pair a fraction.
    ("1/2", "um de fevereiro"),
    ("3/4", "três de abril"),
    ("dia 5/3", "dia cinco de março"),
    ("em 12/10", "em doze de outubro"),
    ("Válido até 31/12", "Válido até trinta e um de dezembro"),
    ("segunda 5/3", "segunda cinco de março"),
    # 29 February is a real date; without a year the leap reference applies
    # (as _valid's docstring specifies), so this is a date, not a fraction.
    ("29/02", "vinte e nove de fevereiro"),
    ("29/02/2024", "vinte e nove de fevereiro de dois mil e vinte e quatro"),
    # Impossible calendar dates.
    ("Dia 31/02", "Dia 31/02"),
    ("29/02/2025", "29/02/2025"),  # 2025 is not a leap year
    ("31/04/2026", "31/04/2026"),  # April has 30 days
    ("2026-02-31", "2026-02-31"),
    ("Dia 31/06", "Dia 31/06"),  # June has 30 days; date cue -> preserved
    # Milestone-5 fallback convention for bare calendar-invalid pairs.
    ("32/12", "trinta e dois doze avos"),
    ("31/02", "trinta e um meios"),
    # Ordinal day marker in dates (pt-BR writes "1º de janeiro").
    ("1º/1/2025", "primeiro de janeiro de dois mil e vinte e cinco"),
    ("2º/1/2025", "segundo de janeiro de dois mil e vinte e cinco"),
    ("dia 1º/9", "dia primeiro de setembro"),
)


# ---------------------------------------------------------------------------
# MED-5: regnal numerals after any capitalized name.
#
# pt-BR convention (SPEC): regnal romans are ordinals up to "décimo" and
# cardinals afterwards; female sovereigns take feminine ordinals ("Elizabeth
# segunda").  Single-letter numerals (I, V, X) are recognized after known
# regnal names.
# ---------------------------------------------------------------------------
REGNAL_NAME_CASES: tuple[tuple[str, str], ...] = (
    ("Henrique VIII", "Henrique oitavo"),
    ("Elizabeth II", "Elizabeth segunda"),
    ("Pio X", "Pio décimo"),
    ("D. Pedro I", "Dom Pedro primeiro"),
    ("rainha Elizabeth II", "rainha Elizabeth segunda"),
    ("Isabel II", "Isabel segunda"),
    ("Catarina I", "Catarina primeira"),
    ("Bento XVI", "Bento dezesseis"),
    ("Luís XV", "Luís quinze"),
    ("Dom Pedro II", "Dom Pedro segundo"),
    # Non-regnal romans keep their previous reading.
    ("Capítulo V", "Capítulo V"),
    ("Casa X", "Casa X"),
    ("século XXI", "século vinte e um"),
)


# ---------------------------------------------------------------------------
# MED-6: 0800/0300/4004-style service numbers.
#
# SAC numbers are voiced prefix + digit groups: "zero oitocentos, um dois
# três, quatro cinco seis sete".  A zero-leading prefix reads "zero" plus the
# remaining cardinal; other 4-digit service prefixes read as full cardinals
# ("4004" -> "quatro mil e quatro", as announced by Brazilian airlines).
# ---------------------------------------------------------------------------
SERVICE_PHONE_CASES: tuple[tuple[str, str], ...] = (
    ("0800 123 4567", "zero oitocentos, um dois três, quatro cinco seis sete"),
    ("0300 321 4567", "zero trezentos, três dois um, quatro cinco seis sete"),
    ("4004 1234", "quatro mil e quatro, um dois três quatro"),
    ("3003 1234", "três mil e três, um dois três quatro"),
    ("Telefone: 0800 123 4567", "Telefone: zero oitocentos, um dois três, quatro cinco seis sete"),
    (
        "Ligue 0800 123 4567 agora",
        "Ligue zero oitocentos, um dois três, quatro cinco seis sete agora",
    ),
)


# ---------------------------------------------------------------------------
# MED-7: emoji grapheme clusters.
#
# CLDR pt-BR annotations (flags: "bandeira: Brasil"); adjacent clusters are
# described separately; skin-tone modifiers are stripped before lookup; a ZWJ
# sequence not in the name table falls back to its first named element.
# ---------------------------------------------------------------------------
EMOJI_CLUSTER_CASES: tuple[tuple[str, str], ...] = (
    ("😀🎉", "rosto sorridente, festa"),
    ("🇧🇷", "bandeira do Brasil"),
    ("🇺🇸", "bandeira dos Estados Unidos"),
    ("🇵🇹", "bandeira de Portugal"),
    ("🇧🇷🇺🇸", "bandeira do Brasil, bandeira dos Estados Unidos"),
    ("👍🏽", "polegar para cima"),  # skin tone stripped before lookup
    ("👨‍👩‍👧", "família"),
    ("👩‍💻", "mulher"),  # ZWJ fallback to the first named element
    ("🦄", "emoji"),  # unknown emoji keep the generic fallback
)


# ---------------------------------------------------------------------------
# LOW-8: "12h00" is "doze horas".
#
# A :00 minute field means "on the hour"; nobody says "e zero minutos".
# ---------------------------------------------------------------------------
TIME_ZERO_MINUTE_CASES: tuple[tuple[str, str], ...] = (
    ("12h00", "doze horas"),
    ("14h00", "quatorze horas"),
    ("às 9h00", "às nove horas"),
    # Non-zero minutes are unchanged.
    ("9h05", "nove horas e cinco minutos"),
    ("14h30", "quatorze horas e trinta minutos"),
)


# ---------------------------------------------------------------------------
# LOW-9: scores, dimensions and "entre" ranges.
#
# Scores read "X a Y" (reviewer: "7 x 1" -> "sete a um"); dimensions read
# "X por Y" (reviewer: "3 x 4" -> "três por quatro"); "entre X-Y" takes the
# "entre ... e ..." construction; a bare hyphen pair containing zero is a
# score ("2-0" -> "dois a zero") because ranges never have zero endpoints.
# ---------------------------------------------------------------------------
SCORE_DIMENSION_CASES: tuple[tuple[str, str], ...] = (
    ("placar 7 x 1", "placar sete a um"),
    ("venceu por 7 x 1", "venceu por sete a um"),
    ("foto 3 x 4", "foto três por quatro"),
    ("folha 3 x 4", "folha três por quatro"),
    ("2-0", "dois a zero"),
    ("0-2", "zero a dois"),
    ("venceu por 2-0", "venceu por dois a zero"),
    ("Entre 2010-2020", "entre dois mil e dez e dois mil e vinte"),
    ("entre 10–20", "entre dez e vinte"),
    # Multiplication wins when "=" follows.
    ("2 x 2 = 4", "dois vezes dois igual quatro"),
    ("2 x 2 são 4", "dois vezes dois são quatro"),
    # Guards: bare "10-20" is not a range (existing milestone guard).
    ("10-20", "dez-vinte"),
)


# ---------------------------------------------------------------------------
# LOW-10: road codes, unit markers, new abbreviations, sentence periods.
#
# "BR-116" is voiced "bê erre cento e dezesseis" (letters + cardinal, as
# Brazilians read highway codes); "km 23" is a marker: singular unit +
# cardinal; "apto." = "apartamento" (only before a number), "Sto." = "Santo".
# A sentence-final abbreviation keeps its period ("Ltda.", "a.C.").
# ---------------------------------------------------------------------------
ROAD_UNIT_ABBREV_CASES: tuple[tuple[str, str], ...] = (
    ("BR-116", "bê erre cento e dezesseis"),
    ("SP-310", "esse pê trezentos e dez"),
    ("km 23", "quilômetro vinte e três"),
    ("km 23 da BR-116", "quilômetro vinte e três da bê erre cento e dezesseis"),
    ("apto. 32", "apartamento trinta e dois"),
    ("Apto. 201", "apartamento duzentos e um"),
    ("Sto. Antônio", "Santo Antônio"),
    ("Sta. Maria", "Santa Maria"),
    # "apto." without a following number is the adjective "apto": preserved.
    ("Ele está apto. Sim.", "Ele está apto. Sim."),
    # Sentence-final periods after abbreviations and month names.
    ("Silva & Cia. Ltda.", "Silva e Cia. limitada."),
    ("em 300 a.C.", "em trezentos antes de Cristo."),
    ("Reunião em 25 de Março.", "Reunião em vinte e cinco de março."),
    ("Reunião em 5 de mar.", "Reunião em cinco de março."),
    # Mid-sentence abbreviation periods are still dropped.
    ("Ltda. e Cia.", "limitada e Cia."),
    ("5 de mar. de 2026", "cinco de março de dois mil e vinte e seis"),
)


# ---------------------------------------------------------------------------
# LOW-11: acronyms as words, IPTU spelled, "COVID-19", URL scheme/www.
#
# ONU/OTAN/MEC are pronounced as words in Brazil ("o MEC"); IPTU is spelled
# letter by letter ("i pê tê u", as every taxpayer says it).  "COVID-19" is
# the word "covid" plus "dezenove".  URLs drop the scheme and read "www" as
# "dáblio dáblio dáblio" (the pt-BR letter name for W).
# ---------------------------------------------------------------------------
ACRONYM_URL_CASES: tuple[tuple[str, str], ...] = (
    ("ONU", "onu"),
    ("OTAN", "otan"),
    ("MEC", "mec"),
    ("IPTU", "i pê tê u"),
    ("COVID", "covid"),
    ("COVID-19", "covid dezenove"),
    ("A ONU decidiu", "A onu decidiu"),
    ("o MEC publicou", "o mec publicou"),
    ("https://exemplo.com.br", "exemplo ponto com ponto br"),
    ("http://site.com/a", "site ponto com barra a"),
    ("www.exemplo.com", "dáblio dáblio dáblio ponto exemplo ponto com"),
    ("https://www.exemplo.com.br", "dáblio dáblio dáblio ponto exemplo ponto com ponto br"),
    ("https://x.com.", "x ponto com."),
    (
        "Acesse www.exemplo.com/p/inicio",
        "Acesse dáblio dáblio dáblio ponto exemplo ponto com barra p barra inicio",
    ),
    # Mixed alphanumeric codes: letters spelled, digits by group length.
    ("AZ1234", "á zê um dois três quatro"),
    ("MP3", "eme pê três"),
)


# ---------------------------------------------------------------------------
# Helpers: direct API regressions for the same findings.
# ---------------------------------------------------------------------------
DIRECT_MONEY_CASES: tuple[tuple[str, str], ...] = (
    ("2.000.000,50", "dois milhões de reais e cinquenta centavos"),
    ("1.000.000,01", "um milhão de reais e um centavo"),
)

DIRECT_ACRONYM_CASES: tuple[tuple[str, str], ...] = (
    ("ONU", "onu"),
    ("OTAN", "otan"),
    ("MEC", "mec"),
    ("IPTU", "i pê tê u"),
    ("COVID", "covid"),
)


@pytest.mark.parametrize(("source", "expected"), GENDER_TEXT_CASES)
def test_gender_agreement_in_running_text(source: str, expected: str) -> None:
    assert normalize(source) == expected


@pytest.mark.parametrize(("source", "expected"), GENDER_SENTENCE_CASES)
def test_gender_agreement_sentences(source: str, expected: str) -> None:
    assert normalize(source) == expected


@pytest.mark.parametrize(("source", "expected"), MONEY_CENTS_CASES)
def test_money_scale_de_with_cents(source: str, expected: str) -> None:
    assert normalize(source) == expected


@pytest.mark.parametrize(("amount", "expected"), DIRECT_MONEY_CASES)
def test_spell_money_scale_de_with_cents(amount: str, expected: str) -> None:
    assert spell_money(amount) == expected


@pytest.mark.parametrize(("source", "expected"), SCALE_DE_CASES)
def test_scale_de_before_nouns(source: str, expected: str) -> None:
    assert normalize(source) == expected


@pytest.mark.parametrize(("source", "expected"), FRACTION_VS_DATE_CASES)
def test_fraction_versus_date(source: str, expected: str) -> None:
    assert normalize(source) == expected


@pytest.mark.parametrize(("source", "expected"), REGNAL_NAME_CASES)
def test_regnal_names(source: str, expected: str) -> None:
    assert normalize(source) == expected


@pytest.mark.parametrize(("source", "expected"), SERVICE_PHONE_CASES)
def test_service_phone_numbers(source: str, expected: str) -> None:
    assert normalize(source) == expected


@pytest.mark.parametrize(("source", "expected"), EMOJI_CLUSTER_CASES)
def test_emoji_clusters_describe(source: str, expected: str) -> None:
    assert normalize(source, options=DESCRIBE) == expected
    # The public helper agrees with the pipeline for single clusters.
    assert describe_emoji(source) == expected


@pytest.mark.parametrize(("source", "expected"), TIME_ZERO_MINUTE_CASES)
def test_time_zero_minutes(source: str, expected: str) -> None:
    assert normalize(source) == expected


@pytest.mark.parametrize(("source", "expected"), SCORE_DIMENSION_CASES)
def test_scores_dimensions_and_entre_ranges(source: str, expected: str) -> None:
    assert normalize(source) == expected


@pytest.mark.parametrize(("source", "expected"), ROAD_UNIT_ABBREV_CASES)
def test_roads_units_abbrevs_and_periods(source: str, expected: str) -> None:
    assert normalize(source) == expected


@pytest.mark.parametrize(("source", "expected"), ACRONYM_URL_CASES)
def test_acronyms_covid_and_urls(source: str, expected: str) -> None:
    assert normalize(source) == expected


@pytest.mark.parametrize(("token", "expected"), DIRECT_ACRONYM_CASES)
def test_spell_acronym_direct(token: str, expected: str) -> None:
    assert spell_acronym(token) == expected


def test_service_phone_span_kind() -> None:
    from falabr import normalize_with_spans

    result = normalize_with_spans("Ligue 0800 123 4567")
    assert result.text == "Ligue zero oitocentos, um dois três, quatro cinco seis sete"
    assert [span.kind for span in result.spans] == ["phone_service"]
    for span in result.spans:
        assert result.text[span.start : span.end] == span.spoken


def test_km_prefix_span_kind() -> None:
    from falabr import normalize_with_spans

    result = normalize_with_spans("km 23")
    assert result.text == "quilômetro vinte e três"
    assert [span.kind for span in result.spans] == ["unit_prefix"]


def test_regnal_span_covers_name_and_numeral() -> None:
    from falabr import normalize_with_spans

    result = normalize_with_spans("Henrique VIII reinou")
    assert result.text == "Henrique oitavo reinou"
    assert [span.kind for span in result.spans] == ["regnal_name"]
    span = result.spans[0]
    assert span.original == "Henrique VIII"
    assert span.spoken == "Henrique oitavo"
    assert result.text[span.start : span.end] == span.spoken
