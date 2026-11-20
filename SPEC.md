# falabr — SPEC

**falabr**: Brazilian Portuguese text normalization for **text-to-speech** (and voice assistants, audiobooks, reels voice-overs).
Turns written pt-BR into exactly what a narrator would say: `"R$ 1.234,56"` → "mil duzentos e trinta e quatro reais e cinquenta e seis centavos",
`"Dia 05/03, às 14h30"` → "dia cinco de março, às quatorze horas e trinta minutos", `"3º lugar"` → "terceiro lugar", `"CPF 123.456.789-09"` → read digit groups,
`"Dr. Silva"` → "doutor Silva", `"km/h"` → "quilômetros por hora", URLs, e-mails, emojis, roman numerals in names ("Dom Pedro II" → "Dom Pedro segundo"), etc.
Open source, MIT, "Hadagalberto Junior". NOT a toy: no stubs, no TODO, no skipped or placeholder tests.

## Stack
Python ≥ 3.10, zero runtime dependencies, fully typed (mypy --strict clean), `ruff` lint+format, `pytest` + `hypothesis`, coverage ≥ 95%.
Packaging with `pyproject.toml` (hatchling), CLI entry point `falabr`. GitHub Actions CI (ubuntu/windows/macos, Python 3.10–3.13 + latest available).
README.md (pt-BR primary) + README.en.md, CHANGELOG, CONTRIBUTING, LICENSE. Do not publish to PyPI.

## Grammar of numbers (core — must be exact)
- Cardinals 0 to 10^18−1 with correct pt-BR rules: "cem" vs "cento e …", "e" connectors ("mil e cem", "mil cento e um", "dois mil e trinta", "um milhão e duzentos mil", "um milhão, duzentos mil e cinco"),
  "um milhão de reais" vs "um milhão e um reais" (preposição "de" before currency when the number ends in milhão/bilhão… exactly), gender agreement ("duzentas pessoas", "uma", "duas" — API `gender='m'|'f'`).
  Negative numbers ("menos …"), decimals ("três vírgula catorze"; option to read decimals digit by digit), "catorze/quatorze" option (default "quatorze").
- Ordinals 1º–999.999º masculine/feminine ("vigésimo primeiro", "milésima").
- Fractions (1/2 meio, 1/3 um terço, 3/4 três quartos, 5/12 cinco doze avos), percentages ("12,5%" → "doze vírgula cinco por cento"), ranges ("10-20" → "de dez a vinte" in context), scores/ratios.
- Roman numerals in regnal/century contexts ("século XXI" → "século vinte e um", "Dom Pedro II" → "Dom Pedro segundo", "Bento XVI" → "Bento dezesseis" per pt-BR convention: ordinal up to décimo, cardinal after).
- Phone numbers, CEP, CPF/CNPJ, card numbers, protocol codes → grouped digit reading with natural pauses (commas), configurable.

## Entities
- Money: R$, US$, €, £, "reais/dólares/euros", cents, abbreviations "R$ 2 mi", "R$ 3,5 bi", "10 mil reais", negative values.
- Dates and times in all common formats (05/03/2026, 5/3, 2026-03-05, "5 de mar.", "14h", "14h30", "14:30", "2h da manhã"), weekdays abbreviations, centuries, decades ("anos 90").
- Units (SI + common: km, km/h, m², kg, ml, °C, GB, Mbps, kWh, mg/dL…) with singular/plural agreement ("1 km" "um quilômetro"; "1,5 km" "um vírgula cinco quilômetros").
- Abbreviations dictionary (Dr., Dra., Sr., Sra., Prof., Av., R., nº, p.ex., etc., pág., tel., ltda., S.A.) with context rules; acronyms spelled vs read as words (INSS → "i ene esse esse", PIX → "pix", USP read as word) via curated lists + heuristics; user dictionary overrides.
- URLs, e-mails, @handles, #hashtags (split camelCase), emojis (configurable: remove or describe in pt-BR using a CLDR-derived short-name table with source cited), symbols (&, +, =, %, /, ×).
- Sentence segmentation for TTS chunks (respect abbreviations and decimals; max chunk length option) and SSML output option (`<say-as>`, `<break>`) with proper escaping.

## API
`normalize(text, *, options) -> str`, `normalize_ssml(text, options) -> str`, `spell_number(n, gender, ...)`, `spell_ordinal`, `spell_money`, `split_sentences`;
`Options` dataclass (catorze_style, decimal_mode, emoji_mode, acronym overrides, user lexicon). Deterministic and fast (100k words/s target, benchmark test with generous bound).
CLI: `falabr "texto"`, `falabr -f arquivo.txt --ssml`, stdin support, `--json` with spans showing original → spoken mapping (for subtitle/TTS alignment).

## Tests
- ≥ 600 table-driven cases curated by category with expected outputs written by hand (pt-BR grammar sources cited in comments, e.g. Academia Brasileira de Letras / VOLP for numerals).
- Property tests: spell_number never contains digits, round-trip parser (`parse_spoken_number(spell_number(n)) == n`) for 0..10^12 random samples — implement the parser too.
- Golden file tests for realistic paragraphs (news, receipts, recipes, sports, finance) in tests/golden/.

## Hard constraints
- Never run `git push`, `gh`, `twine`, `uv publish`, or publish anything. Commit locally after each milestone. Stay inside this repository.
