"""Independent-review findings: failing-first regression vectors.

Every expected string below is written by hand from the stated rule; none is
produced by falabr itself or copied from a generated snapshot.

Grammar authorities / reasoning used for the expected values:

* Numeral-noun gender agreement: Cunha & Cintra, *Nova Gramática do Português
  Contemporâneo*, chapter "Numerais" — the cardinal agrees in gender with the
  counted noun ("uma filha", "duzentas pessoas").  ``mil`` is invariant; the
  multiplier of ``milhão``/``bilhão`` agrees with those masculine scale nouns
  ("duas mil pessoas", "dois milhões de pessoas").
* ``de`` after an exact milhão/bilhão scale: ABL/VOLP usage for ``real`` and
  Cunha & Cintra.  The preposition depends on the INTEGER part ending exactly
  at the scale, not on whether there are cents: "um milhão de reais e um
  centavo".  It does not appear after ``mil`` ("dez mil reais").
* Fractions before ``do/da/dos/das/de`` + noun are quantifiers, not dates;
  per SPEC.md a VALID bare d/m pair is a date by default.  Real calendar dates
  only (29/02 allowed via a leap reference year; 31/02 impossible).  Sources:
  Cunha & Cintra, "Numerais fracionários"; SPEC.md date/fraction clause.
* Regnal numerals: pt-BR convention — ordinal through X, cardinal after
  (SPEC.md, "Roman numerals in regnal/century contexts"); feminine ordinal for
  female names.
* CLDR pt_BR annotations for emoji short names (``CLDR_SOURCE``), regional
  indicators for flags.
* URL reading: scheme is not spoken; ``www`` is the letter name ``dáblio``.
"""

from __future__ import annotations

import pytest

from falabr import EmojiMode, Options, normalize, normalize_web

DESCRIBE = Options(emoji_mode=EmojiMode.DESCRIBE)
REMOVE = Options(emoji_mode=EmojiMode.REMOVE)


# --- HIGH: noun gender agreement in running text -----------------------------

GENDER_CASES: tuple[tuple[str, str], ...] = (
    ("1 filha", "uma filha"),  # filha is feminine
    ("200 pessoas", "duzentas pessoas"),  # centenas agree with pessoa
    ("2.000 pessoas", "duas mil pessoas"),  # mil is invariant; multiplier agrees
    ("São 22 horas", "São vinte e duas horas"),  # hora is feminine
    ("1 vez", "uma vez"),  # vez is feminine
    ("2 semanas", "duas semanas"),
    ("1 tonelada", "uma tonelada"),
    ("2 colheres", "duas colheres"),
    ("1.101 pessoas", "mil cento e uma pessoas"),  # 1101 = mil + cento e uma
    ("3 xícaras", "três xícaras"),
    # Masculine exceptions ending in -a must NOT be feminized.
    ("1 grama", "um grama"),  # VOLP: grama is masculine ("o grama")
    ("2 dias", "dois dias"),  # dia is masculine
    ("1 problema", "um problema"),  # -ema Greek loanwords are masculine
)


@pytest.mark.parametrize(("source", "expected"), GENDER_CASES)
def test_running_text_number_agrees_with_noun(source: str, expected: str) -> None:
    assert normalize(source) == expected


# --- HIGH: "de reais" must survive when cents are present --------------------

MONEY_CENTS_SCALE_CASES: tuple[tuple[str, str], ...] = (
    ("R$ 2.000.000,50", "dois milhões de reais e cinquenta centavos"),
    ("R$ 1.000.000,01", "um milhão de reais e um centavo"),
    ("R$ 2.000.000.000,12", "dois bilhões de reais e doze centavos"),
    # Not an exact scale: "de" is still absent, as the grammar requires.
    ("R$ 1.000.001,50", "um milhão e um reais e cinquenta centavos"),
)


@pytest.mark.parametrize(("source", "expected"), MONEY_CENTS_SCALE_CASES)
def test_money_de_before_currency_with_cents(source: str, expected: str) -> None:
    assert normalize(source) == expected


# --- MED: "de" after milhão/bilhão before a noun; never after mil ------------

SCALE_DE_CASES: tuple[tuple[str, str], ...] = (
    ("1.000.000 pessoas", "um milhão de pessoas"),
    ("2.000.000 horas", "dois milhões de horas"),
    ("1.000.000.000 pessoas", "um bilhão de pessoas"),
    ("100 mil pessoas", "cem mil pessoas"),  # no "de" after mil
    ("R$ 10,5 mil", "dez vírgula cinco mil reais"),  # no "de" after mil
    ("R$ 3,5 mil", "três vírgula cinco mil reais"),
    ("R$ 3,5 mi", "três vírgula cinco milhões de reais"),  # "de" after mi
)


@pytest.mark.parametrize(("source", "expected"), SCALE_DE_CASES)
def test_scale_preposition_before_noun(source: str, expected: str) -> None:
    assert normalize(source) == expected


# --- MED: date vs fraction disambiguation and calendar validation ------------

DATE_FRACTION_CASES: tuple[tuple[str, str], ...] = (
    ("Recebeu 1/4 do valor", "Recebeu um quarto do valor"),  # "do" + noun
    ("5/12 da pizza", "cinco doze avos da pizza"),  # "da" + noun
    ("3/4 da torta", "três quartos da torta"),
    ("Dia 31/02", "Dia 31/02"),  # impossible date: never say 31 de fevereiro
    # The ordinal day marker is not a fraction numerator: read the malformed
    # "1º/1/2025" as the intended ordinal date, not as "... avos".
    ("1º/1/2025", "primeiro de janeiro de dois mil e vinte e cinco"),
    ("05/03/2026", "cinco de março de dois mil e vinte e seis"),  # real date
    ("em 5/3", "em cinco de março"),  # "em" is a date cue
    ("até 31/12", "até trinta e um de dezembro"),  # "até" is a date cue
    ("segunda-feira 5/3", "segunda-feira cinco de março"),  # weekday cue
    ("5/3 de 2026", "cinco de março de dois mil e vinte e seis"),  # year cue
    # Corrected in milestone 7: a57e3a1 inverted SPEC.md's date rule and had
    # rewritten these valid bare pairs to fractions ("três quartos", "... doze
    # avos").  A valid bare d/m is a date; only partitives above are fractions.
    ("3/4", "três de abril"),
    ("31/12", "trinta e um de dezembro"),
)


@pytest.mark.parametrize(("source", "expected"), DATE_FRACTION_CASES)
def test_date_fraction_disambiguation(source: str, expected: str) -> None:
    assert normalize(source) == expected


# --- MED: regnal numerals beyond a fixed name list ---------------------------

REGNAL_CASES: tuple[tuple[str, str], ...] = (
    ("Henrique VIII", "Henrique oitavo"),  # 8 -> ordinal, name not on old list
    ("Elizabeth II", "Elizabeth segunda"),  # feminine ordinal for a female name
    ("Pio X", "Pio décimo"),  # single-letter roman numeral
    ("D. Pedro I", "Dom Pedro primeiro"),  # "D." expands to "Dom"
    ("Dom Pedro II", "Dom Pedro segundo"),
    ("Bento XVI", "Bento dezesseis"),  # > X -> cardinal per pt-BR convention
    ("João Paulo II", "João Paulo segundo"),  # two-part name
)


@pytest.mark.parametrize(("source", "expected"), REGNAL_CASES)
def test_regnal_numeral_detection(source: str, expected: str) -> None:
    assert normalize(source) == expected


# --- MED: toll-free / service phone numbers ----------------------------------

PHONE_CASES: tuple[tuple[str, str], ...] = (
    (
        "Telefone: 0800 123 4567",
        "Telefone: zero oitocentos, um dois três, quatro cinco seis sete",
    ),
    ("0300 123 4567", "zero trezentos, um dois três, quatro cinco seis sete"),
    ("4004 123 4567", "quatro mil e quatro, um dois três, quatro cinco seis sete"),
)


@pytest.mark.parametrize(("source", "expected"), PHONE_CASES)
def test_service_phone_digit_groups(source: str, expected: str) -> None:
    assert normalize(source) == expected


# --- MED: emoji grapheme clusters, flags, skin tones --------------------------

EMOJI_CASES: tuple[tuple[str, Options, str], ...] = (
    ("😀🎉", DESCRIBE, "rosto sorridente, festa"),  # two adjacent clusters
    ("🇧🇷", DESCRIBE, "bandeira do Brasil"),  # regional-indicator pair
    ("Olá 😀🎉 mundo", DESCRIBE, "Olá rosto sorridente, festa mundo"),
    ("👍🏽", DESCRIBE, "polegar para cima"),  # skin tone stays attached
    ("👨‍👩‍👧", DESCRIBE, "família"),  # ZWJ sequence stays one cluster
)


@pytest.mark.parametrize(("source", "options", "expected"), EMOJI_CASES)
def test_emoji_clusters(source: str, options: Options, expected: str) -> None:
    assert normalize(source, options=options) == expected


def test_adjacent_emoji_remove_mode() -> None:
    assert normalize("😀🎉", options=REMOVE) == ""


# --- LOW: times, scores, dimensions, codes, abbreviations --------------------

LOW_CASES: tuple[tuple[str, str], ...] = (
    ("12h00", "doze horas"),  # zero minutes are not spoken
    ("7 x 1", "sete a um"),  # score cue absent -> score reading
    ("3 x 4", "três por quatro"),  # dimensions: "por"
    ("Dimensões 3 x 4", "Dimensões três por quatro"),
    ("2-0", "dois a zero"),  # bare single-digit score
    ("Entre 2010-2020", "entre dois mil e dez e dois mil e vinte"),
    ("BR-116", "bê erre cento e dezesseis"),  # highway code
    ("km 23", "quilômetro vinte e três"),  # unit before number
    ("apto. 5", "apartamento cinco"),
    ("Sto. Antônio", "Santo Antônio"),
    # Alphanumeric codes are read as letters followed by individual digits.
    ("AZ1234", "á zê um dois três quatro"),
    # Sentence-final punctuation survives an abbreviated entity.
    ("Ltda.", "limitada."),
    ("a.C.", "antes de Cristo."),
    ("25 de Março.", "vinte e cinco de março."),
)


@pytest.mark.parametrize(("source", "expected"), LOW_CASES)
def test_low_findings(source: str, expected: str) -> None:
    assert normalize(source) == expected


# --- LOW: acronyms and URLs ---------------------------------------------------

ACRONYM_URL_CASES: tuple[tuple[str, str], ...] = (
    ("ONU", "onu"),  # read as a word
    ("OTAN", "otan"),
    ("MEC", "mec"),
    ("IPTU", "i pê tê u"),  # spelled
    ("COVID-19", "covid dezenove"),
    ("https://exemplo.com.br", "exemplo ponto com ponto br"),  # scheme dropped
    ("http://site.com/a", "site ponto com barra a"),
    ("www.exemplo.com", "dáblio dáblio dáblio ponto exemplo ponto com"),
    ("https://x.com.", "x ponto com."),
)


@pytest.mark.parametrize(("source", "expected"), ACRONYM_URL_CASES)
def test_acronym_and_url_findings(source: str, expected: str) -> None:
    assert normalize(source) == expected


def test_url_entity_drops_scheme() -> None:
    assert normalize_web("https://exemplo.com.br") == "exemplo ponto com ponto br"


# --- Curated running-text sentences combining the cases above -----------------

RUNNING_TEXT_CASES: tuple[tuple[str, str], ...] = (
    (
        "Ela comprou 2 colheres e 1 xícara.",
        "Ela comprou duas colheres e uma xícara.",
    ),
    (
        "São 22 horas e 2 semanas se passaram.",
        "São vinte e duas horas e duas semanas se passaram.",
    ),
    (
        "A empresa tem 200 pessoas e 1 tonelada de grãos.",
        "A empresa tem duzentas pessoas e uma tonelada de grãos.",
    ),
    (
        "Recebeu 1/4 do valor em 5/12 da pizza.",
        "Recebeu um quarto do valor em cinco doze avos da pizza.",
    ),
    (
        "Dia 31/02 não é data; use 3/4 da torta.",
        "Dia 31/02 não é data; use três quartos da torta.",
    ),
    (
        "Henrique VIII e Elizabeth II receberam Pio X.",
        "Henrique oitavo e Elizabeth segunda receberam Pio décimo.",
    ),
    (
        "A ONU e a OTAN pediram ao MEC o IPTU.",
        "A onu e a otan pediram ao mec o i pê tê u.",
    ),
    (
        "Acesse www.exemplo.com ou ligue 0800 123 4567.",
        "Acesse dáblio dáblio dáblio ponto exemplo ponto com ou ligue "
        "zero oitocentos, um dois três, quatro cinco seis sete.",
    ),
)


@pytest.mark.parametrize(("source", "expected"), RUNNING_TEXT_CASES)
def test_curated_running_text(source: str, expected: str) -> None:
    assert normalize(source) == expected
