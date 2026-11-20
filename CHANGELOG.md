# Changelog

All notable changes to this project are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

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
