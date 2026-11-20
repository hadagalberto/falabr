"""Table-driven vectors for pt-BR shorthand expansion (maintainer finding 1).

Known-valid tokens must expand; known-invalid contexts (inside URLs, paths,
e-mails or larger words) must survive verbatim.  The full pipeline assertions
guard the ordering requirement: expansion happens before web/symbol handling.
"""

from __future__ import annotations

import pytest

from falabr import normalize, normalize_shorthand

SHORTHAND_CASES: tuple[tuple[str, str], ...] = (
    ("p/ Ana", "para Ana"),
    ("c/ você", "com você"),
    ("s/ açúcar", "sem açúcar"),
    ("q", "que"),
    ("q.", "que"),
    ("vc", "você"),
    ("VC", "você"),
    ("Vc", "você"),
    ("tb", "também"),
    ("TB", "também"),
    ("tbm", "também"),
    ("pq", "porque"),
    ("Pq", "porque"),
    ("pq?", "por que?"),
    ("Pq ?", "por que ?"),
    ("obs.", "observação"),
    ("Obs.", "observação"),
    ("ex.", "exemplo"),
    ("Ex.", "exemplo"),
    ("(p/ Ana)", "(para Ana)"),
    ("Olá, p/ você!", "Olá, para você!"),
    ("q. fazer?", "que fazer?"),
    ("Mande p/ ana@exemplo.com.br", "Mande para ana@exemplo.com.br"),
)

# These tokens are not standalone shorthands: no expansion is allowed.
PRESERVED_CASES: tuple[str, ...] = (
    "rep/",
    "p/x",
    "a.p/",
    "vc@exemplo.com",
    "http://x.com/p/a",
    "www.exemplo.com/p/2026",
    "/caminho/s/arquivo",
    "p/ana@exemplo.com",
)

# Full-pipeline expectations: shorthand before web/symbol handling.
PIPELINE_CASES: tuple[tuple[str, str], ...] = (
    (
        "mande e-mail p/ ana@exemplo.com.br",
        "mande e-mail para ana arroba exemplo ponto com ponto br",
    ),
    (
        "mande c/ João, s/ açúcar e p/ Ana",
        "mande com João, sem açúcar e para Ana",
    ),
    (
        "vc tb quer? pq sim, q. fazer?",
        "você também quer? porque sim, que fazer?",
    ),
    (
        "acesse www.exemplo.com/p/inicio",
        # Corrected from "w w w" per the URL finding ("dáblio").
        "acesse dáblio dáblio dáblio ponto exemplo ponto com barra p barra inicio",
    ),
)


@pytest.mark.parametrize(("source", "expected"), SHORTHAND_CASES)
def test_shorthand_expand(source: str, expected: str) -> None:
    assert normalize_shorthand(source) == expected


@pytest.mark.parametrize("source", PRESERVED_CASES)
def test_shorthand_not_expanded_inside_tokens(source: str) -> None:
    assert normalize_shorthand(source) == source


@pytest.mark.parametrize(("source", "expected"), PIPELINE_CASES)
def test_shorthand_runs_before_web_and_symbols(source: str, expected: str) -> None:
    assert normalize(source) == expected
