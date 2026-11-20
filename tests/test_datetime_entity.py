"""Date/time/decade/century vectors, including invalid-date vectors."""

from __future__ import annotations

import pytest

from falabr import normalize, normalize_datetime

DATE_CASES: tuple[tuple[str, str], ...] = (
    ("05/03/2026", "cinco de março de dois mil e vinte e seis"),
    ("5/3/2026", "cinco de março de dois mil e vinte e seis"),
    ("05/03/26", "cinco de março de vinte e seis"),
    ("2026-03-05", "cinco de março de dois mil e vinte e seis"),
    ("5 de mar.", "cinco de março"),
    ("5 de março", "cinco de março"),
    ("5 de Março de 2026", "cinco de março de dois mil e vinte e seis"),
    ("1 de janeiro", "um de janeiro"),
    ("25 de dezembro de 2025", "vinte e cinco de dezembro de dois mil e vinte e cinco"),
    # A bare d/m pair is a FRACTION, not a date: independent review finding 4
    # corrected the milestone-5 rule that read every valid pair as a date.
    # Only a date cue ("dia", "data", "em", "até", weekday) or a following year
    # triggers the calendar reading.
    ("05/03", "cinco terços"),
    ("dia 5/3", "dia cinco de março"),
    ("data 5/3", "data cinco de março"),
    ("31/12", "trinta e um doze avos"),
    ("1/2", "um meio"),
    ("3/4", "três quartos"),
    ("12/10", "doze décimos"),
    ("5/3", "cinco terços"),
)

TIME_CASES: tuple[tuple[str, str], ...] = (
    ("14h", "quatorze horas"),
    ("14h30", "quatorze horas e trinta minutos"),
    ("14:30", "quatorze horas e trinta minutos"),
    ("14h30min", "quatorze horas e trinta minutos"),
    ("1h", "uma hora"),
    ("2h", "duas horas"),
    ("0h", "zero horas"),
    ("2h da manhã", "duas horas da manhã"),
    ("3h da madrugada", "três horas da madrugada"),
    ("18h da tarde", "dezoito horas da tarde"),
    ("20h da noite", "vinte horas da noite"),
    ("9h05", "nove horas e cinco minutos"),
    ("14:01", "quatorze horas e um minuto"),
)

PERIOD_CASES: tuple[tuple[str, str], ...] = (
    ("século XXI", "século vinte e um"),
    ("séc. XX", "século vinte"),
    ("sec. IV", "século quatro"),
    ("século 21", "século vinte e um"),
    ("anos 90", "anos noventa"),
    ("anos 2000", "anos dois mil"),
    ("década de 80", "década de oitenta"),
)

WEEKDAY_CASES: tuple[tuple[str, str], ...] = (
    ("seg.", "segunda-feira"),
    ("Seg.", "segunda-feira"),
    ("ter.", "terça-feira"),
    ("qua.", "quarta-feira"),
    ("qui.", "quinta-feira"),
    ("sex.", "sexta-feira"),
    ("sáb.", "sábado"),
    ("dom.", "domingo"),
)

DATETIME_INVALID_CASES: tuple[str, ...] = (
    "32/13/2026",
    "2026-13-40",
    "99/99/9999",
)

ALL_CASES: tuple[tuple[str, str], ...] = DATE_CASES + TIME_CASES + PERIOD_CASES + WEEKDAY_CASES


@pytest.mark.parametrize(("source", "expected"), ALL_CASES)
def test_datetime_entity(source: str, expected: str) -> None:
    assert normalize_datetime(source) == expected


@pytest.mark.parametrize("source", DATETIME_INVALID_CASES)
def test_datetime_entity_invalid_date_is_preserved(source: str) -> None:
    assert normalize_datetime(source) == source


def test_datetime_entity_in_context() -> None:
    assert normalize("Dia 05/03, às 14h30") == (
        "Dia cinco de março, às quatorze horas e trinta minutos"
    )


def test_decade_and_century_in_context() -> None:
    assert normalize("Nos anos 90, no século XX") == "Nos anos noventa, no século vinte"
