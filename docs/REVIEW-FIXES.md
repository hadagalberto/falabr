# Independent review — fix report (milestone 6)

All findings from the attached review were reproduced with failing tests first
(hand-derived expected values, sources/reasoning in test comments), then fixed
at the root cause.  No existing assertion was deleted, skipped or loosened:
assertions that encoded a listed bug were corrected in place with a comment
citing the finding, and the two golden snapshots that locked in the old URL
reading were regenerated and read back and confirmed correct.

## Findings → regressions → fixes

| Item | Regression test(s) | Fix summary | Status |
| --- | --- | --- | --- |
| HIGH — numbers in running text always masculine | `test_running_text_number_agrees_with_noun`, `test_gender_agreement_in_running_text`, `test_gender_agreement_sentences`, `test_curated_running_text` | New curated feminine-noun lexicon + documented `-a`/plural heuristics in `entities/_gender.py`; pipeline count matchers spell the cardinal with the following noun's gender. Masculine exceptions (`grama`, `dia`, `problema`, `mapa`) stay masculine. | Fixed |
| HIGH — `de` dropped before currency when cents exist | `test_money_de_before_currency_with_cents`, `test_money_scale_de_with_cents`, `test_spell_money_scale_de_with_cents` | `spell_money` now uses `ends_at_major_scale(integer)`; the `and cents == 0` guard (which removed `de`) is gone. `R$ 2.000.000,50` → "dois milhões de reais e cinquenta centavos". | Fixed |
| MED — `de` after milhão/bilhão before a noun; no `de` after `mil` | `test_scale_preposition_before_noun`, `test_scale_de_before_nouns` | Count handler appends `de` only for exact 10⁶+ scales and not when the author already wrote `de`; money suffix handling emits `de` for `mi`/`bi` but never for `mil`. | Fixed |
| MED — any valid d/m read as a date | `test_date_fraction_disambiguation`, `test_fraction_versus_date` | `_short_date` decides from context: `do/da/de` + noun → fraction; `dia`/`data`/`em`/`até`/weekday/following year → date; bare pair → fraction. Real-calendar validation rejects 31/02; ordinal day markers (`1º/9`, `1º/1/2025`) read as ordinal dates. | Fixed |
| MED — regnal detection used a fixed name list | `test_regnal_numeral_detection`, `test_regnal_names`, `test_regnal_span_covers_name_and_numeral` | One `regnal_name` matcher consumes title + capitalized name(s) + roman numeral (including single letters). Curated male/female name lists + `-a` heuristic choose the ordinal gender; `D.` expands to `Dom`; >X uses the cardinal. | Fixed |
| MED — 0800/0300/4004 phone numbers | `test_service_phone_digit_groups`, `test_service_phone_numbers`, `test_service_phone_span_kind` | New `phone_service` matcher for 4-digit service prefixes (3+4 and 4+4 groupings); zero-leading prefixes read "zero + cardinal", others read the full cardinal, subscribers digit by digit with comma pauses. | Fixed |
| MED — emoji clusters become "emoji" | `test_emoji_clusters`, `test_adjacent_emoji_remove_mode`, `test_emoji_clusters_describe` | Grapheme-cluster regex (flags, keycaps, ZWJ, skin tones); adjacent clusters described separately with a comma pause; regional indicators map to pt-BR flag names; ZWJ falls back to the first named element; unknown emoji keep "emoji". | Fixed |
| LOW — 12h00, x-scores/dimensions, 2-0, entre ranges | `test_low_findings`, `test_scores_dimensions_and_entre_ranges`, `test_time_zero_minutes` | Zero minutes not spoken; `x` uses "a" with score cues/trailing 0–1, "por" for dimensions, "vezes" before `=`/`são`; bare one-digit hyphen with zero is a score; `entre` consumes its cue and uses "e". | Fixed |
| LOW — BR-116, km 23, apto./Sto., AZ1234, final periods | `test_low_findings`, `test_roads_units_abbrevs_and_periods` | Road-code, unit-prefix and alphanumeric-code matchers; `apto.` expands only before a number; `Sto.`/`Sta.` preserve capitalization; sentence-final period after an abbreviated entity is restored. | Fixed |
| LOW — acronyms and URLs | `test_acronym_and_url_findings`, `test_url_entity_drops_scheme`, `test_acronyms_covid_and_urls`, `test_spell_acronym_direct` | ONU/OTAN/MEC/COVID read as words, IPTU spelled; `COVID-19` handled as a compound; URL scheme dropped, `www` → "dáblio dáblio dáblio", domain read naturally. | Fixed |
| Tests — large curated running-text set | `tests/test_review_fixes.py` + `tests/test_milestone6.py` (≈200 hand-written vectors) | Added curated tables for feminine nouns, fractions vs dates, regnal names, phones, emoji clusters, scores/dimensions, codes, acronyms and URLs, plus combined running-text paragraphs. | Fixed |

## Verification

- `python -m pytest -q` → **1243 passed**
- `python -m ruff check .` → clean
- `python -m ruff format --check .` → 53 files formatted
- `python -m mypy` → clean (48 files)
- `python -m coverage report` → **97 %** (fail_under = 95)
- `python -m build` → sdist + wheel built cleanly

No push, publish, `gh`, `twine` or remote operation was performed.
