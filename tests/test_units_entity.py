"""Unit-entity vectors. Source: SPEC.md (SI + common units, agreement)."""

from __future__ import annotations

import pytest

from falabr import normalize, normalize_units

UNIT_CASES: tuple[tuple[str, str], ...] = (
    ("1 km", "um quilômetro"),
    ("2 km", "dois quilômetros"),
    ("0 km", "zero quilômetros"),
    ("1,5 km", "um vírgula cinco quilômetros"),
    ("10,25 km", "dez vírgula vinte e cinco quilômetros"),
    ("1 km/h", "um quilômetro por hora"),
    ("100 km/h", "cem quilômetros por hora"),
    ("80,5 km/h", "oitenta vírgula cinco quilômetros por hora"),
    ("1 m", "um metro"),
    ("3 m", "três metros"),
    ("1 m²", "um metro quadrado"),
    ("5 m²", "cinco metros quadrados"),
    ("2 m³", "dois metros cúbicos"),
    ("3 cm", "três centímetros"),
    ("1 mm", "um milímetro"),
    ("1 kg", "um quilograma"),
    ("2 kg", "dois quilogramas"),
    ("2 g", "dois gramas"),
    ("1 mg", "um miligrama"),
    ("500 ml", "quinhentos mililitros"),
    ("1 l", "um litro"),
    ("2 l", "dois litros"),
    ("32 °C", "trinta e dois graus Celsius"),
    ("1 °C", "um grau Celsius"),
    ("-5 °C", "menos cinco graus Celsius"),
    ("70 °F", "setenta graus Fahrenheit"),
    ("10 GB", "dez gigabytes"),
    ("1 GB", "um gigabyte"),
    ("1 MB", "um megabyte"),
    ("2 TB", "dois terabytes"),
    ("1 KB", "um quilobyte"),
    ("5 Mbps", "cinco megabits por segundo"),
    ("1 Mbps", "um megabit por segundo"),
    ("2 kbps", "dois quilobits por segundo"),
    ("10 kWh", "dez quilowatt-horas"),
    ("1 kWh", "um quilowatt-hora"),
    ("1 kW", "um quilowatt"),
    ("100 W", "cem watts"),
    ("12 V", "doze volts"),
    ("5 A", "cinco amperes"),
    ("1 A", "um ampere"),
    ("60 Hz", "sessenta hertz"),
    ("1 Ah", "um ampere-hora"),
    ("2 ha", "dois hectares"),
    ("3 m/s", "três metros por segundo"),
    ("1 mg/dL", "um miligrama por decilitro"),
    ("70 mg/dL", "setenta miligramas por decilitro"),
    ("2 min", "dois minutos"),
    ("1 h", "uma hora"),
    ("2 h", "duas horas"),
    ("10 s", "dez segundos"),
)

UNIT_INVALID_CASES: tuple[str, ...] = (
    "10 bananas",
    "km sozinho",
    "5 xyz",
    "kg e mais kg",
)


@pytest.mark.parametrize(("source", "expected"), UNIT_CASES)
def test_unit_entity(source: str, expected: str) -> None:
    assert normalize_units(source) == expected


@pytest.mark.parametrize("source", UNIT_INVALID_CASES)
def test_unit_entity_invalid_source_is_preserved(source: str) -> None:
    assert normalize_units(source) == source


def test_unit_in_context() -> None:
    assert normalize("São 1,5 km até lá") == "São um vírgula cinco quilômetros até lá"
