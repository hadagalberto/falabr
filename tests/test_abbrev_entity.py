"""Abbreviation dictionary/context rules and acronym voicing vectors."""

from __future__ import annotations

import pytest

from falabr import Options, normalize_abbreviations, spell_acronym

ABBREV_CASES: tuple[tuple[str, str], ...] = (
    ("Dr. Silva", "doutor Silva"),
    ("dr. Silva", "doutor Silva"),
    ("Dra. Silva", "doutora Silva"),
    ("Drs. Silva", "doutores Silva"),
    ("Sr. João", "senhor João"),
    ("Sra. Maria", "senhora Maria"),
    ("Prof. Alves", "professor Alves"),
    ("Profa. Alves", "professora Alves"),
    ("Av. Brasil", "avenida Brasil"),
    ("R. das Flores", "rua das Flores"),
    ("nº 5", "número 5"),
    ("n° 5", "número 5"),
    ("n. 5", "número 5"),
    ("p.ex. isso", "por exemplo isso"),
    ("p. ex. isso", "por exemplo isso"),
    ("e.g. isso", "por exemplo isso"),
    ("i.e. isso", "isto é isso"),
    ("cf. a norma", "conforme a norma"),
    ("etc.", "etcétera"),
    ("obs. importante", "observação importante"),
    ("aprox. 10", "aproximadamente 10"),
    ("tel. 1234", "telefone 1234"),
    ("ltda.", "limitada"),
    ("S.A.", "sociedade anônima"),
    ("s.a.", "sociedade anônima"),
    ("pág. 12", "página 12"),
    ("págs. 12", "páginas 12"),
    ("p. 5", "página 5"),
    ("p. foi", "por foi"),
    ("ed. 2", "edição 2"),
    ("vol. 3", "volume 3"),
    ("cap. 4", "capítulo 4"),
    ("fig. 5", "figura 5"),
    ("a.C.", "antes de Cristo"),
    ("A.C.", "antes de Cristo"),
    ("d.C.", "depois de Cristo"),
    ("D.C.", "depois de Cristo"),
)

ABBREV_INVALID_CASES: tuple[str, ...] = (
    "doctor Silva",
    "xyz. Silva",
    "palavra.",
)

ACRONYM_CASES: tuple[tuple[str, str], ...] = (
    ("INSS", "i ene esse esse"),
    ("CPF", "cê pê efe"),
    ("CNPJ", "cê ene pê jota"),
    ("RG", "erre gê"),
    ("CEP", "cê e pê"),
    ("DDD", "dê dê dê"),
    ("FGTS", "efe gê tê esse"),
    ("PIX", "pix"),
    ("USP", "usp"),
    ("ENEM", "enem"),
    ("SUS", "sus"),
    ("FUNAI", "funai"),
    ("PETROBRAS", "petrobras"),
    ("IBGE", "ibge"),
    ("DNA", "dna"),
    ("GPS", "gps"),
    ("HIV", "hiv"),
    # Acronym finding: IPTU is spelled, not read as a word (corrected here).
    ("IPTU", "i pê tê u"),
    ("IPVA", "ipva"),
    ("OK", "ok"),
    ("PIB", "pib"),
    ("XXI", "vinte e um"),
    ("II", "dois"),
    ("W", "dáblio"),
)


@pytest.mark.parametrize(("source", "expected"), ABBREV_CASES)
def test_abbreviation_entity(source: str, expected: str) -> None:
    assert normalize_abbreviations(source) == expected


@pytest.mark.parametrize("source", ABBREV_INVALID_CASES)
def test_abbreviation_entity_invalid_source_is_preserved(source: str) -> None:
    assert normalize_abbreviations(source) == source


@pytest.mark.parametrize(("token", "expected"), ACRONYM_CASES)
def test_acronym_spelling(token: str, expected: str) -> None:
    assert spell_acronym(token) == expected


def test_acronym_user_overrides() -> None:
    assert spell_acronym("INSS", Options(acronym_overrides={"INSS": "word"})) == "inss"
    assert spell_acronym("INSS", Options(acronym_overrides={"INSS": "i ene"})) == "i ene"
    assert spell_acronym("XYZ", Options(acronym_overrides={"XYZ": "spell"})) == "xis ípsilon zê"


def test_acronym_invalid_inputs() -> None:
    with pytest.raises(ValueError, match="empty"):
        spell_acronym("")
    with pytest.raises(TypeError):
        spell_acronym(123)  # type: ignore[arg-type]


def test_abbreviations_in_context() -> None:
    assert normalize_abbreviations("O INSS pagou o PIX") == ("O i ene esse esse pagou o pix")
