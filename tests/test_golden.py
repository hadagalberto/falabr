"""Golden-paragraph tests for realistic pt-BR text.

Each category has a hand-written input/output pair under ``tests/golden``.
The expected side is reviewed by hand against pt-BR grammar, not generated
from the implementation, so a future change in any entity breaks the paragraph
that contains it.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from falabr import normalize, normalize_ssml, split_sentences

GOLDEN_DIR: Path = Path(__file__).parent / "golden"
CATEGORIES: tuple[str, ...] = (
    "news",
    "receipts",
    "recipes",
    "sports",
    "finance",
    "shorthand",
    "phone",
    "social",
)


def _load(category: str, suffix: str) -> str:
    return (GOLDEN_DIR / f"{category}.{suffix}.txt").read_text(encoding="utf-8").strip()


@pytest.mark.parametrize("category", CATEGORIES)
def test_golden_paragraph(category: str) -> None:
    source = _load(category, "in")
    expected = _load(category, "out")
    result = normalize(source)
    assert result == expected
    assert result, "golden output must not be empty"
    # Every numeric token in these paragraphs must have been spoken.
    assert not re.search(r"\d", result), "golden output still contains digits"


@pytest.mark.parametrize("category", CATEGORIES)
def test_golden_sentence_count_is_stable(category: str) -> None:
    """Normalization must not create or swallow sentence boundaries."""
    source = _load(category, "in")
    expected = _load(category, "out")
    assert len(split_sentences(expected)) == len(split_sentences(source))


@pytest.mark.parametrize("category", CATEGORIES)
def test_golden_ssml_is_well_formed(category: str) -> None:
    ssml = normalize_ssml(_load(category, "in"))
    assert ssml.startswith("<speak>")
    assert ssml.endswith("</speak>")
    assert ssml.count("<say-as ") == ssml.count("</say-as>")
    assert "&amp;" not in ssml  # no raw ampersand survived normalization


def test_golden_files_match_expected_categories() -> None:
    """Adding a golden pair without registering it here is a test failure."""
    inputs = {path.name.removesuffix(".in.txt") for path in GOLDEN_DIR.glob("*.in.txt")}
    outputs = {path.name.removesuffix(".out.txt") for path in GOLDEN_DIR.glob("*.out.txt")}
    assert inputs == outputs
    assert inputs == set(CATEGORIES)
