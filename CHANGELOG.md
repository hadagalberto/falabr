# Changelog

All notable changes to this project are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- Milestone 3: the CLI now runs the full composed pipeline (the same code as the
  Python API), including `--json` spans with entity kinds, SSML `say-as`/breaks,
  `--emoji-mode` and a functional `--roman-context` flag carried by `Options`.
  Golden-paragraph tests for news, receipts, recipes, sports and finance plus a
  throughput benchmark test (generous 20k words/s bound against a 100k target).
- Milestone 2 entities and the composed `normalize` pipeline: money (symbols, cents,
  mi/bi/mil abbreviations, `de` rule, all four currencies), dates/times in every listed
  format, weekdays, decades and centuries, units with gender/number agreement, an
  abbreviation dictionary with context rules, curated acronym word/spell lists plus
  user overrides, grouped digit reading for CPF/CNPJ/CEP/phone/card, URLs, e-mails,
  handles, camelCase hashtags, symbols, and CLDR-derived pt-BR emoji names with the
  source cited.
- `normalize_ssml` (say-as + sentence breaks), `normalize_with_spans` for TTS alignment,
  `split_sentences` (abbreviation/decimal aware, optional max chunk length), and the
  frozen `Options` fields `emoji_mode`, `acronym_overrides`, `user_lexicon` and
  `digit_group_separator`.
- 345 additional hand-written table cases across the new entity modules, plus pipeline,
  SSML and sentence tests.

### Fixed

- `split_sentences` abbreviation protection: short entries such as `R.` and `n.` no
  longer match inside ordinary words (`açúcar.`, `min.`), preserving sentence and
  TTS-chunk boundaries.

### Changed

- `RomanContext` now lives in `falabr.options` with the other configuration enums;
  it is still re-exported from `falabr` and accepted by `spell_roman`.

## [0.1.0] — 2026-11-20

### Added

- Project scaffold: `pyproject.toml` (hatchling, `src/` layout, `py.typed`), ruff,
  mypy strict, pytest + hypothesis + coverage (≥ 95%), `falabr` CLI entry point,
  MIT `LICENSE`, CI on Ubuntu/Windows/macOS with Python 3.10–3.13.
- Exact pt-BR cardinals from 0 to 10^18−1: `cem`/`cento`, `e` connectors, `de` before
  currency after an exact milhão/bilhão, gender agreement, negatives.
- Decimals in cardinal and digit-by-digit modes, `catorze`/`quatorze` option.
- Ordinals (1–999999, m/f), fractions, percentages, money and roman numerals with
  regnal/century conventions.
- `parse_spoken_number` with `spell_number` round-trip property test and ≥ 300
  hand-written table cases with grammar sources cited.
