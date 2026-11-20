# Changelog

All notable changes to this project are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- Milestone 5: `SsmlMode` (`normalized`/`say-as`) and `Options.ssml_mode`, wired through
  `normalize_ssml`, the public API and the CLI's `--ssml-mode`. Table tests pin both
  strategies, including that engines never receive spoken words inside `<say-as>`.
- Measure-fraction matcher (`1/2 xícara` → "meia xícara", `1/3 de xícara` →
  "um terço de xícara", `3/4 xícara` → "três quartos de xícara") with feminine/masculine
  agreement and exact alignment spans.
- Golden/table vectors for the ambiguous day/month cases (`1/2`, `3/4`, `12/10`, `5/3`,
  `31/12`) and for the two SSML strategies.
- Milestone 4 documentation: `README.md` (pt-BR) and `README.en.md` now contain extensive
  before/after tables, the full API/CLI reference, and integration recipes for **Piper**,
  **Coqui XTTS**, **ElevenLabs** and **Azure Speech SSML**. `CONTRIBUTING.md` documents the
  test rules and the cross-platform checklist.
- Shorthand expansion (`normalize_shorthand`, `SHORTHAND_MATCHERS`): standalone `p/`, `c/`,
  `s/`, `q`, `q.`, `vc`, `tb`, `tbm`, `pq`, `obs.` and `ex.` expand **before** web/symbol
  handling, and never inside URLs, paths, e-mails or larger words. `pq` becomes "por que"
  before a question mark and "porque" elsewhere. `ex.` and `q.` joined the abbreviation
  dictionary so sentence splitting protects them.
- Phone styles: `Options.phone_style` with `PhoneStyle.DIGITS`, `PAIRS` and `NATURAL`.
  `NATURAL` is the default and reads the DDD as a number before grouping the subscriber as
  Brazilians speak it ("onze, nove, oito sete seis cinco, quatro três dois um"). The CLI
  exposes `--phone-style`.
- Ranges and scores (`normalize_ranges`, `RANGE_MATCHERS`, `SCORE_MATCHERS`): cue-driven
  `10-20` → "de dez a vinte", en/em dash ranges, `placar 3-1`, `resultado 2:1`, `2:1`.
  Time matching now requires two digits after `:` so `14:30` is a clock, not a score.
- Protocol-code reading (`Protocolo 2026/12345`) and a digit-by-digit fallback for bare
  multi-group codes such as `1234.5678.9012`, which previously raised `ValueError`.
- Negative money with a leading symbol (`-R$ 10` → "menos dez reais"); a separated dash
  (`2 kg - R$ 15,90`) stays punctuation.
- CLI wiring for the remaining `Options` fields: `--digit-group-separator`,
  `--acronym-override KEY=VALUE` and `--user-lexicon KEY=VALUE` (repeatable), plus
  `--sentences` / `--max-chars` chunking.
- Golden paragraphs `shorthand`, `phone` and `social` (the latter mixes handles, hashtags,
  emoji, URLs, money, dates and units), with hand-written expected output.
- A single test asserts the SPEC minimum of 600 hand-written table cases across all
  milestones; CI now includes Python 3.14 and sets `PYTHONUTF8=1`.
- `.gitattributes` marks text fixtures with `eol=lf` and binary assets as `binary`.
- Milestone 3: the CLI runs the full composed pipeline (the same code as the Python API),
  including `--json` spans with entity kinds, SSML `say-as`/breaks, `--emoji-mode` and a
  functional `--roman-context` flag carried by `Options`. Golden paragraphs for news,
  receipts, recipes, sports and finance plus a throughput benchmark test (generous 20k
  words/s bound against a 100k target).
- Milestone 2 entities and the composed `normalize` pipeline: money (symbols, cents,
  mi/bi/mil abbreviations, `de` rule, all four currencies), dates/times in every listed
  format, weekdays, decades and centuries, units with gender/number agreement, an
  abbreviation dictionary with context rules, curated acronym word/spell lists plus user
  overrides, grouped digit reading for CPF/CNPJ/CEP/phone/card, URLs, e-mails, handles,
  camelCase hashtags, symbols, and CLDR-derived pt-BR emoji names with the source cited.
- `normalize_ssml` (say-as + sentence breaks), `normalize_with_spans` for TTS alignment,
  `split_sentences` (abbreviation/decimal aware, optional max chunk length), and the
  frozen `Options` fields `emoji_mode`, `acronym_overrides`, `user_lexicon` and
  `digit_group_separator`.

### Changed

- `normalize_ssml` now defaults to fully normalized spoken words with only `<break>`
  structure. Use `Options(ssml_mode=SsmlMode.SAY_AS)` (or `--ssml-mode say-as`) for the
  original-token `<say-as>` behaviour of earlier releases.
- Phone numbers now default to the `natural` reading; the previous digit-by-digit output
  remains available as `PhoneStyle.DIGITS` and is covered by the original vectors.
- `--json`, `--ssml` and `--sentences` are mutually exclusive CLI output modes.

### Fixed

- Bare `dd/mm`/`d/m` pairs are read as dates whenever valid (day 1–31, month 1–12):
  `até 31/12!` → "até trinta e um de dezembro!" instead of "trinta e um doze avos".
  Measure contexts are excluded from this rule.
- Fractions before a noun no longer produce "um meio xícara"; `1/2` uses the agreeing
  "meia"/"meio" and the other fractions take the "de" preposition.
- Phone parsing uses the written separators instead of a flat digit string, so 10-digit
  numbers like `(21) 3333-4444` keep their two-digit area code.
- `split_sentences` abbreviation protection: short entries such as `R.` and `n.` no
  longer match inside ordinary words (`açúcar.`, `min.`), preserving sentence and
  TTS-chunk boundaries.

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
