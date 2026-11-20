"""Milestone 7: restore the SPEC bare ``d/m`` date rule (regression of a57e3a1).

Every expected value below is written by hand from the cited source/reasoning;
none is produced by falabr itself or copied from a generated snapshot.

Sources / reasoning for the expected values:

* SPEC.md states: "A valid bare ``dd/mm``/``d/m`` is read as a date."  A pair
  whose day fits its month is a calendar date by default; pt-BR voices the day
  as a cardinal and joins the month with ``de`` (Cunha & Cintra, *Nova Gramática
  do Português Contemporâneo*, "Numerais", and ABL/VOLP month usage):
  ``31/12`` -> "trinta e um de dezembro", ``05/03`` -> "cinco de março".
* A d/m pair is a FRACTION only when a measure/quantity noun follows it
  ("1/2 xícara" -> "meia xícara") or a partitive ``do/da/dos/das/de`` + noun
  follows it ("1/4 do valor" -> "um quarto do valor").  Cunha & Cintra,
  "Numerais fracionários"; SPEC.md fraction/measure clause.
* An impossible date is never spoken as a date: February has 28 days (29 in a
  leap year), so ``31/02`` must not become "trinta e um de fevereiro"; it falls
  back to the fraction reading (denominator 2 -> "meios").
* Emoji names come from CLDR pt-BR annotations; adjacent clusters are described
  separately with a comma pause and a regional-indicator pair names the flag.
"""

from __future__ import annotations

import pytest

from falabr import EmojiMode, Options, normalize

DESCRIBE = Options(emoji_mode=EmojiMode.DESCRIBE)


# --- THE BUG: a valid bare d/m must be read as a date -------------------------
# a57e3a1 inverted the SPEC rule and rewrote these expectations to fractions.
# Restore each one to the date reading required by SPEC.md.

BARE_DATE_CASES: tuple[tuple[str, str], ...] = (
    # December has 31 days -> valid -> date (was "... doze avos").
    ("31/12", "trinta e um de dezembro"),
    # March has 31 days -> valid -> date (was "... terços").
    ("05/03", "cinco de março"),
    ("5/3", "cinco de março"),
    # "a partir de" is ordinary text; no fraction cue follows the pair.
    ("a partir de 12/10", "a partir de doze de outubro"),
    # February has 29 days in a leap year; bare pairs use that reference.
    ("1/2", "um de fevereiro"),
    # April has 30 days.
    ("3/4", "três de abril"),
    ("12/10", "doze de outubro"),
    # 29 February is a real calendar day.  With no year the leap reference is
    # used (as _valid's docstring specifies), so it is a date, not "29 meios".
    ("29/02", "vinte e nove de fevereiro"),
)


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        # With an explicit non-leap year the Gregorian rule rejects it.
        ("29/02/2025", "29/02/2025"),
        ("29/02/2024", "vinte e nove de fevereiro de dois mil e vinte e quatro"),
    ],
)
def test_leap_day_validation_with_year(source: str, expected: str) -> None:
    assert normalize(source) == expected


@pytest.mark.parametrize(("source", "expected"), BARE_DATE_CASES)
def test_valid_bare_day_month_is_a_date(source: str, expected: str) -> None:
    assert normalize(source) == expected


# --- GUARDS: fraction contexts must stay fractions ----------------------------
# These passed before the fix and must keep passing (the date default must not
# swallow a genuine fraction).

FRACTION_CONTEXT_CASES: tuple[tuple[str, str], ...] = (
    # "do" + noun -> partitive fraction; 1/4 = "um quarto".
    ("Recebeu 1/4 do valor", "Recebeu um quarto do valor"),
    # "da" + noun -> partitive fraction; denominator 12 -> "doze avos".
    ("5/12 da pizza", "cinco doze avos da pizza"),
    # "dos"/"das" + noun are partitives too.
    ("1/4 dos lucros", "um quarto dos lucros"),
    ("2/3 das vendas", "dois terços das vendas"),
    # A following measure noun -> special fraction/noun agreement.
    ("1/2 xícara", "meia xícara"),
    ("1/3 xícara", "um terço de xícara"),
)


@pytest.mark.parametrize(("source", "expected"), FRACTION_CONTEXT_CASES)
def test_fraction_contexts_are_not_dates(source: str, expected: str) -> None:
    assert normalize(source) == expected


# --- GUARDS: impossible dates never become spoken dates -----------------------

INVALID_DATE_CASES: tuple[tuple[str, str], ...] = (
    # February has at most 29 days: 31/02 is impossible, so it falls back to a
    # fraction reading ("31 halves"), NEVER "trinta e um de fevereiro".
    ("31/02", "trinta e um meios"),
    # With an explicit date cue an impossible date is preserved verbatim.
    ("Dia 31/02", "Dia 31/02"),
    # Day 32 and month 13 are out of bounds.
    ("32/12", "trinta e dois doze avos"),
    ("31/13", "31/13"),
)


@pytest.mark.parametrize(("source", "expected"), INVALID_DATE_CASES)
def test_invalid_day_month_never_becomes_a_date(source: str, expected: str) -> None:
    assert normalize(source) == expected


# --- Held findings from a57e3a1 must survive the date-rule restoration --------

HELD_CASES: tuple[tuple[str, str], ...] = (
    ("1 filha", "uma filha"),  # gender agreement
    ("200 pessoas", "duzentas pessoas"),  # gender agreement
    ("R$ 2.000.000,50", "dois milhões de reais e cinquenta centavos"),  # money
    ("Henrique VIII", "Henrique oitavo"),  # regnal numeral
    ("0800 123 4567", "zero oitocentos, um dois três, quatro cinco seis sete"),  # phone
)


@pytest.mark.parametrize(("source", "expected"), HELD_CASES)
def test_held_findings_still_hold(source: str, expected: str) -> None:
    assert normalize(source) == expected


# --- Emoji describe mode ------------------------------------------------------

EMOJI_CASES: tuple[tuple[str, str], ...] = (
    # Each adjacent emoji is described, separated by a comma pause.
    ("😀🎉", "rosto sorridente, festa"),
    # A regional-indicator pair is a flag; pt-BR CLDR name for BR.
    ("🇧🇷", "bandeira do Brasil"),
)


@pytest.mark.parametrize(("source", "expected"), EMOJI_CASES)
def test_emoji_describe_mode(source: str, expected: str) -> None:
    assert normalize(source, options=DESCRIBE) == expected
