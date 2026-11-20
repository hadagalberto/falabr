# falabr — English overview

Brazilian Portuguese text normalization for **text-to-speech**, voice assistants, audiobooks
and voice-overs. Turns written pt-BR into exactly what a narrator would say.

> `R$ 1.234,56` → "mil duzentos e trinta e quatro reais e cinquenta e seis centavos"

Zero runtime dependencies, Python ≥ 3.10, fully typed for `mypy --strict`, MIT licensed.
The project is **not** published to PyPI. The primary documentation is [README.md](README.md)
(in Portuguese); this file is a complete English mirror of the essentials.

## Install

```bash
python -m pip install -e ".[dev]"
```

## Quick start

```python
from falabr import Options, PhoneStyle, normalize, normalize_ssml

normalize("Dia 05/03, às 14h30")
# 'Dia cinco de março, às quatorze horas e trinta minutos'

normalize("(11) 98765-4321", Options(phone_style=PhoneStyle.NATURAL))
# 'onze, nove, oito sete seis cinco, quatro três dois um'

normalize_ssml("R$ 10")
# '<speak><say-as interpret-as="currency">dez reais</say-as></speak>'
```

## Before / after

All outputs below are verified by the repository's hand-written table and golden tests.

### Numbers, fractions, percentages

| Input | Output |
| --- | --- |
| `1101` | `mil cento e um` |
| `200, gender="f"` | `duzentas` |
| `1.000.000` | `um milhão` |
| `1.000.001` | `um milhão e um` |
| `-30` | `menos trinta` |
| `3,14` | `três vírgula catorze` |
| `3,14` with `decimal_mode=digits` | `três vírgula um quatro` |
| `14` with `catorze_style=catorze` | `catorze` |
| `21º` | `vigésimo primeiro` |
| `1000ª` | `milésima` |
| `3/4` | `três quartos` |
| `5/12` | `cinco doze avos` |
| `12,5%` | `doze vírgula cinco por cento` |

### Money

| Input | Output |
| --- | --- |
| `R$ 1.234,56` | `mil duzentos e trinta e quatro reais e cinquenta e seis centavos` |
| `R$ 2 mi` | `dois milhões de reais` |
| `R$ 3,5 bi` | `três vírgula cinco bilhões de reais` |
| `10 mil reais` | `dez mil reais` |
| `-R$ 10` | `menos dez reais` |

### Dates, times, centuries

| Input | Output |
| --- | --- |
| `05/03/2026` | `cinco de março de dois mil e vinte e seis` |
| `2026-03-05` | `cinco de março de dois mil e vinte e seis` |
| `5 de mar.` | `cinco de março` |
| `14h30` / `14:30` | `quatorze horas e trinta minutos` |
| `2h da manhã` | `duas horas da manhã` |
| `século XXI` | `século vinte e um` |
| `Dom Pedro II` | `Dom Pedro segundo` |
| `anos 90` | `anos noventa` |

### Units, identifiers, phone styles

| Input | Output |
| --- | --- |
| `1,5 km` | `um vírgula cinco quilômetros` |
| `80 km/h` | `oitenta quilômetros por hora` |
| `25 °C` | `vinte e cinco graus Celsius` |
| `CPF 123.456.789-09` | `cê pê efe um dois três, quatro cinco seis, sete oito nove, zero nove` |
| `Protocolo 2026/12345` | `Protocolo dois zero dois seis, um dois três quatro cinco` |
| `(11) 98765-4321` (natural) | `onze, nove, oito sete seis cinco, quatro três dois um` |
| `(11) 98765-4321` (digits) | `um um, nove oito sete seis cinco, quatro três dois um` |
| `(11) 98765-4321` (pairs) | `onze, noventa e oito, setenta e seis, cinquenta e quatro, trinta e dois, um` |

`phone_style='natural'` is the default: the area code is read as a number and the subscriber
is grouped the way Brazilians say it. `digits` reads every digit (verification), `pairs`
groups into two-digit numbers.

### Abbreviations, acronyms, shorthand, web, emoji

| Input | Output |
| --- | --- |
| `Dr. Silva` | `doutor Silva` |
| `Av. Paulista, nº 1000` | `avenida Paulista, número mil` |
| `O INSS, o PIX e a USP` | `O i ene esse esse, o pix e a usp` |
| `mande e-mail p/ ana@exemplo.com.br` | `mande e-mail para ana arroba exemplo ponto com ponto br` |
| `c/ café e s/ açúcar` | `com café e sem açúcar` |
| `Vc tb quer? Pq sim, q. fazer?` | `você também quer? porque sim, que fazer?` |
| `www.exemplo.com.br` | `w w w ponto exemplo ponto com ponto br` |
| `joao@example.com` | `joao arroba example ponto com` |
| `#BomDia @JoaoSilva 🎉` | `hashtag bom dia arroba joao silva` |
| `#BomDia 🎉` with `emoji_mode=describe` | `hashtag bom dia festa` |

Common shorthand (`p/`, `c/`, `s/`, `q`, `vc`, `tb`, `tbm`, `pq`, `obs.`, `ex.`) expands before
web/symbol handling, but only as standalone tokens — never inside URLs or paths.

### Ranges and scores

| Input | Output |
| --- | --- |
| `de 10-20` | `de dez a vinte` |
| `páginas 10-20` | `páginas de dez a vinte` |
| `10–20` | `de dez a vinte` |
| `placar 3-1` | `placar três a um` |
| `2:1` | `dois a um` |

A bare hyphen (`10-20`) is not forced into a range; `14:30` remains a clock time.

## API

- `normalize(text, options=None) -> str`
- `normalize_with_spans(text, options=None) -> Normalized` — `Span(start, end, original, spoken, kind)` offsets refer to the **normalized** text, for subtitle/TTS alignment.
- `normalize_ssml(text, options=None) -> str` — `<speak>` with `<say-as>`/`<break>` and XML escaping.
- `split_sentences(text, max_chars=None) -> list[str]`
- Spellers: `spell_cardinal`, `spell_number`, `spell_ordinal`, `spell_fraction`, `spell_percentage`, `spell_money`, `spell_roman`, `spell_acronym`.
- Parsers: `parse_spoken_number`, `roman_to_int`, `int_to_roman`.
- Entity helpers: `normalize_money`, `normalize_datetime`, `normalize_units`, `normalize_abbreviations`, `normalize_identifiers`, `normalize_web`, `normalize_symbols`, `normalize_emoji`, `normalize_shorthand`, `normalize_ranges`, `describe_emoji`, `split_camel`.

`Options` is a frozen dataclass: `catorze_style`, `decimal_mode`, `emoji_mode`, `phone_style`,
`acronym_overrides`, `user_lexicon`, `digit_group_separator`, `roman_context`.

## CLI

```bash
falabr "Dia 14, comprei 1.234,56 reais"
falabr -f texto.txt --ssml
echo "século XXI" | falabr --ssml
falabr "total: 12,5 reais" --json
falabr "(11) 98765-4321" --phone-style pairs
falabr "Um. Dois. Três." --sentences --max-chars 20
```

Flags: `-f/--file`, `--json`, `--ssml`, `--sentences`, `--max-chars`, `--catorze`,
`--decimal-mode cardinal|digits`, `--emoji-mode remove|describe`,
`--roman-context cardinal|regnal`, `--phone-style digits|pairs|natural`,
`--digit-group-separator`, `--acronym-override KEY=VALUE` (repeatable),
`--user-lexicon KEY=VALUE` (repeatable).

## Integration recipes

### Piper (local TTS)

Piper reads text from stdin. Resolve its executable through `PATH` — never through the
Python runtime path.

```python
import subprocess
from falabr import normalize


def speak_piper(text: str, model: str = "pt_BR-faber-medium.onnx", out: str = "out.wav") -> None:
    subprocess.run(
        ["piper", "--model", model, "--output_file", out],
        input=normalize(text),
        text=True,
        check=True,
    )
```

### Coqui XTTS (voice cloning)

```python
from TTS.api import TTS  # install in your app; not a falabr dependency
from falabr import normalize

tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to("cuda")
tts.tts_to_file(
    text=normalize("Dia 05/03, às 14h30"),
    speaker_wav="reference.wav",
    language="pt-br",
    file_path="out.wav",
)
```

### ElevenLabs (HTTP API)

ElevenLabs does not accept SSML; send plain `normalize()` output. Standard library only:

```python
import json
import urllib.request
from pathlib import Path
from falabr import normalize


def speak_elevenlabs(text: str, api_key: str, voice_id: str) -> None:
    body = json.dumps(
        {
            "text": normalize(text),
            "model_id": "eleven_multilingual_v2",
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
        data=body,
        headers={
            "xi-api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        },
        method="POST",
    )
    with urllib.request.urlopen(request) as response:
        Path("out.mp3").write_bytes(response.read())
```

### Azure Speech (SSML)

Keep the body of `normalize_ssml()` and swap the root node for Azure's:

```python
from falabr import normalize_ssml


def azure_ssml(text: str, voice: str = "pt-BR-FranciscaNeural") -> str:
    generated = normalize_ssml(text)
    body = generated.removeprefix("<speak>").removesuffix("</speak>")
    return (
        '<speak version="1.0" xmlns="http://www.w3.org/2001/10/Synthesis" '
        'xml:lang="pt-BR">'
        f'<voice name="{voice}">{body}</voice>'
        "</speak>"
    )
```

## Development

```bash
python -m ruff check . && python -m ruff format --check .
python -m mypy
python -m pytest
python -m coverage run -m pytest && python -m coverage report
python -m build
```

CI runs on Ubuntu, Windows and macOS with Python 3.10–3.14. `.gitattributes` forces LF for
text files (including golden fixtures) and the workflow sets `PYTHONUTF8=1`. See
`CONTRIBUTING.md` and `SPEC.md`.

## License

MIT — Hadagalberto Junior. See `LICENSE`.
