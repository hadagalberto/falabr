# falabr — English overview

Brazilian Portuguese text normalization for text-to-speech, voice assistants, audiobooks and
voice-overs. Turns written pt-BR into what a narrator would actually say.

**Milestone 1** delivers the number core: exact cardinals up to 10^18−1 (connectors, `cem`
vs `cento`, gender, the `de` rule), negatives, decimals (cardinal and digit-by-digit modes),
the `catorze`/`quatorze` option, ordinals (m/f), fractions, percentages, money, roman
numerals with regnal/century conventions, and `parse_spoken_number` with a round-trip
property test. **Milestone 2** adds all text entities (money, dates/times, decades/centuries,
units, abbreviations/acronyms, identifiers, web tokens, symbols, CLDR emoji names) and the
composed `normalize` / `normalize_ssml` / `normalize_with_spans` / `split_sentences` API.
See `SPEC.md` for the full roadmap.

Zero runtime dependencies, typed for `mypy --strict`, linted with `ruff`, tested with
`pytest` + `hypothesis` and ≥ 95% branch coverage.

```python
from falabr import spell_cardinal, spell_roman, parse_spoken_number

spell_cardinal(1101)  # 'mil cento e um'
spell_roman("XVI", context="regnal")  # 'dezesseis'
parse_spoken_number("um milhão e duzentos mil")  # 1200000
```

```bash
python -m pip install -e ".[dev]"
falabr "comprei 3,14 reais" --json
```

MIT licensed. Copyright (c) 2026 Hadagalberto Junior. See `LICENSE`.
