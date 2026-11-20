# falabr

Normalização de texto em português brasileiro para **text-to-speech**, assistentes de voz,
audiolivros e narração de reels. O objetivo: transformar o texto escrito em exatamente o que
um locutor falaria.

> `R$ 1.234,56` → "mil duzentos e trinta e quatro reais e cinquenta e seis centavos"

**Zero dependências em runtime**, Python ≥ 3.10, totalmente tipado (`mypy --strict`),
licença MIT. O projeto **não** publica no PyPI.

## Instalação

```bash
python -m pip install -e ".[dev]"
```

Para usar apenas a biblioteca (sem as ferramentas de desenvolvimento):

```bash
python -m pip install .
```

## Uso rápido

```python
from falabr import Options, PhoneStyle, normalize, normalize_ssml

normalize("R$ 1.234,56")
# 'mil duzentos e trinta e quatro reais e cinquenta e seis centavos'

normalize("Dia 05/03, às 14h30")
# 'Dia cinco de março, às quatorze horas e trinta minutos'

normalize("(11) 98765-4321", Options(phone_style=PhoneStyle.NATURAL))
# 'onze, nove, oito sete seis cinco, quatro três dois um'

normalize_ssml("R$ 10")
# '<speak><say-as interpret-as="currency">dez reais</say-as></speak>'
```

## Antes / depois — exemplos por categoria

Cada linha foi verificada com os testes golden/table-driven do repositório.

### Números, frações e porcentagens

| Entrada | Saída |
| --- | --- |
| `1101` | `mil cento e um` |
| `200, gender="f"` | `duzentas` |
| `1.000.000` | `um milhão` |
| `1.000.001` | `um milhão e um` |
| `-30` | `menos trinta` |
| `3,14` | `três vírgula catorze` |
| `3,14` com `decimal_mode=digits` | `três vírgula um quatro` |
| `14` com `catorze_style=catorze` | `catorze` |
| `21º` | `vigésimo primeiro` |
| `1000ª` | `milésima` |
| `3/4` | `três quartos` |
| `1/3` | `um terço` |
| `5/12` | `cinco doze avos` |
| `12,5%` | `doze vírgula cinco por cento` |

```python
from falabr import (
    CatorzeStyle,
    DecimalMode,
    Options,
    parse_spoken_number,
    spell_cardinal,
    spell_fraction,
    spell_money,
    spell_number,
    spell_ordinal,
    spell_percentage,
    spell_roman,
)

spell_cardinal(1234)  # 'mil duzentos e trinta e quatro'
spell_cardinal(200, gender="f")  # 'duzentas'
spell_number("3,14", options=Options(decimal_mode=DecimalMode.DIGITS))
# 'três vírgula um quatro'
spell_number(14, options=Options(catorze_style=CatorzeStyle.CATORZE))  # 'catorze'
spell_ordinal(21)  # 'vigésimo primeiro'
spell_ordinal(1000, gender="f")  # 'milésima'
spell_fraction(3, 4)  # 'três quartos'
spell_fraction(5, 12)  # 'cinco doze avos'
spell_percentage(12.5)  # 'doze vírgula cinco por cento'
spell_money("1000000")  # 'um milhão de reais'
spell_money("1000001")  # 'um milhão e um reais'
spell_roman("XXI")  # 'vinte e um'  (século XXI)
spell_roman("II", context="regnal")  # 'segundo'  (Dom Pedro II)
parse_spoken_number("dois mil e trinta")  # 2030
```

As regras de conectores seguem Celso Cunha & Lindley Cintra, Paul Teyssier e o guia de
redação da Câmara Municipal de Belo Horizonte; `catorze` segue VOLP/ABL. As referências
estão no cabeçalho de `src/falabr/numbers.py`.

### Dinheiro

| Entrada | Saída |
| --- | --- |
| `R$ 1.234,56` | `mil duzentos e trinta e quatro reais e cinquenta e seis centavos` |
| `R$ 2 mi` | `dois milhões de reais` |
| `R$ 3,5 bi` | `três vírgula cinco bilhões de reais` |
| `10 mil reais` | `dez mil reais` |
| `US$ 20,50 e € 15` | `vinte dólares e cinquenta centavos e quinze euros` |
| `-R$ 10` | `menos dez reais` |

### Datas, horas, séculos e décadas

| Entrada | Saída |
| --- | --- |
| `05/03/2026` | `cinco de março de dois mil e vinte e seis` |
| `2026-03-05` | `cinco de março de dois mil e vinte e seis` |
| `5 de mar.` | `cinco de março` |
| `14h30` | `quatorze horas e trinta minutos` |
| `14:30` | `quatorze horas e trinta minutos` |
| `2h da manhã` | `duas horas da manhã` |
| `seg. às 2h da manhã` | `segunda-feira às duas horas da manhã` |
| `século XXI` | `século vinte e um` |
| `Dom Pedro II` | `Dom Pedro segundo` |
| `anos 90` | `anos noventa` |

### Unidades

| Entrada | Saída |
| --- | --- |
| `1 km` | `um quilômetro` |
| `1,5 km` | `um vírgula cinco quilômetros` |
| `80 km/h` | `oitenta quilômetros por hora` |
| `25 °C` | `vinte e cinco graus Celsius` |
| `2 GB a 100 Mbps` | `dois gigabytes a cem megabits por segundo` |
| `3 kWh` | `três quilowatt-horas` |

### Códigos e telefones

| Entrada | Saída |
| --- | --- |
| `CPF 123.456.789-09` | `cê pê efe um dois três, quatro cinco seis, sete oito nove, zero nove` |
| `CNPJ 12.345.678/0001-95` | `cê ene pê jota um dois, três quatro cinco, seis sete oito, zero zero zero um, nove cinco` |
| `CEP 01310-100` | `cê e pê zero um três um zero, um zero zero` |
| `cartão 4111 1111 1111 1111` | `cartão quatro um um um, um um um um, um um um um, um um um um` |
| `Protocolo 2026/12345` | `Protocolo dois zero dois seis, um dois três quatro cinco` |

**Estilos de telefone.** O padrão é `natural`: o DDD é lido como número e o assinante é
agrupado como os brasileiros falam — número móvel (9 dígitos) em `9 | XXXX | XXXX`,
fixo (8 dígitos) em `XXXX | XXXX`, cada grupo digitado com pausas:

```python
from falabr import Options, PhoneStyle, normalize

numero = "(11) 98765-4321"
normalize(numero)  # 'onze, nove, oito sete seis cinco, quatro três dois um'

normalize(numero, Options(phone_style=PhoneStyle.DIGITS))
# 'um um, nove oito sete seis cinco, quatro três dois um'

normalize(numero, Options(phone_style=PhoneStyle.PAIRS))
# 'onze, noventa e oito, setenta e seis, cinquenta e quatro, trinta e dois, um'
```

`DIGITS` lê todos os dígitos (útil para conferência), `PAIRS` agrupa em números de dois
dígitos e `NATURAL` é o padrão documentado acima. Código do país `+55` é dito como número
("cinquenta e cinco"). Use `--digit-group-separator` (ou `Options.digit_group_separator`)
para trocar a vírgula das pausas.

### Abreviações, siglas e shorthand

| Entrada | Saída |
| --- | --- |
| `Dr. Silva e a Profa. Maria` | `doutor Silva e a professora Maria` |
| `Av. Paulista, nº 1000` | `avenida Paulista, número mil` |
| `O INSS, o PIX e a USP` | `O i ene esse esse, o pix e a usp` |
| `mande e-mail p/ ana@exemplo.com.br` | `mande e-mail para ana arroba exemplo ponto com ponto br` |
| `c/ café e s/ açúcar` | `com café e sem açúcar` |
| `Vc tb quer? Pq sim, q. fazer?` | `você também quer? porque sim, que fazer?` |
| `Obs. importante. Ex. de uso.` | `observação importante. exemplo de uso.` |

Shorthand comuns (`p/`, `c/`, `s/`, `q`, `q.`, `vc`, `tb`, `tbm`, `pq`, `obs.`, `ex.`) são
expandidos **antes** do tratamento de URLs/símbolos, mas só como tokens isolados — nunca
dentro de URLs ou caminhos: em `www.exemplo.com/p/inicio` o `p` continua sendo "p".

```python
normalize("O INSS", Options(acronym_overrides={"INSS": "word"}))  # 'O inss'
normalize("Pix", Options(user_lexicon={"Pix": "PIX"}))  # 'PIX'
```

### Web, emojis e símbolos

| Entrada | Saída |
| --- | --- |
| `www.exemplo.com.br` | `w w w ponto exemplo ponto com ponto br` |
| `joao@example.com` | `joao arroba example ponto com` |
| `#BomDia @JoaoSilva 🎉` | `hashtag bom dia arroba joao silva` (emoji removido) |
| `#BomDia 🎉` com `emoji_mode=describe` | `hashtag bom dia festa` |
| `A & B = C / 3 × 4` | `A e B igual C barra três vezes quatro` |

Nomes curtos de emojis vêm da tabela CLDR pt-BR (fonte em `falabr.CLDR_SOURCE`).

### Intervalos e placares

| Entrada | Saída |
| --- | --- |
| `de 10-20` | `de dez a vinte` |
| `páginas 10-20` | `páginas de dez a vinte` |
| `10–20` (travessão) | `de dez a vinte` |
| `placar 3-1` | `placar três a um` |
| `resultado 2:1` | `resultado dois a um` |
| `2:1` | `dois a um` |

Um hífen sem contexto (`10-20`) **não** é forçado a intervalo; `14:30` continua sendo hora.

### Parágrafo completo (teste golden)

```python
normalize(
    "🎉 #Lançamento: R$ 1.234,56 em 05/03 às 14h30! Acesse https://exemplo.com.br "
    "ou fale @JoaoSilva. São 1,5 km a 80 km/h e 25 °C. Detalhes p/ ana@exemplo.com.br 👍"
)
# 'hashtag lançamento: mil duzentos e trinta e quatro reais e cinquenta e seis centavos
#  em cinco de março às quatorze horas e trinta minutos! Acesse h t t p s dois pontos
#  barra barra exemplo ponto com ponto br ou fale arroba joao silva. São um vírgula cinco
#  quilômetros a oitenta quilômetros por hora e vinte e cinco graus Celsius. Detalhes
#  para ana arroba exemplo ponto com ponto br'
```

## API

| Função | Uso |
| --- | --- |
| `normalize(text, options=None)` | texto normalizado (pipeline completa) |
| `normalize_with_spans(text, options=None)` | `Normalized(text, spans)` com `Span(start, end, original, spoken, kind)` para alinhamento |
| `normalize_ssml(text, options=None)` | `<speak>` com `<say-as>` e `<break>`; escapa XML |
| `split_sentences(text, max_chars=None)` | chunks para TTS, respeitando abreviações e decimais |
| `spell_cardinal`, `spell_number`, `spell_ordinal`, `spell_fraction`, `spell_percentage`, `spell_money`, `spell_roman`, `spell_acronym` | soletração isolada |
| `parse_spoken_number`, `roman_to_int`, `int_to_roman` | analisadores reversos |
| `normalize_money`, `normalize_datetime`, `normalize_units`, `normalize_abbreviations`, `normalize_identifiers`, `normalize_web`, `normalize_symbols`, `normalize_emoji`, `normalize_shorthand`, `normalize_ranges`, `describe_emoji`, `split_camel` | helpers por entidade |

`Options` (frozen dataclass): `catorze_style`, `decimal_mode`, `emoji_mode`, `phone_style`,
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

Opções: `-f/--file`, `--json` (spans com `start`/`end` **no texto normalizado**, `original`,
`spoken`, `kind`), `--ssml`, `--sentences`, `--max-chars`, `--catorze`,
`--decimal-mode cardinal|digits`, `--emoji-mode remove|describe`,
`--roman-context cardinal|regnal`, `--phone-style digits|pairs|natural`,
`--digit-group-separator`, `--acronym-override KEY=VALUE` (repetível),
`--user-lexicon KEY=VALUE` (repetível).

## Integrações

### Piper (TTS local)

O Piper lê texto da stdin; alimente-o já normalizado. O executável é resolvido pelo `PATH`
— nunca via `sys.executable` ou caminho do runtime Python.

```python
import subprocess
from falabr import normalize


def falar_piper(
    texto: str, modelo: str = "pt_BR-faber-medium.onnx", saida: str = "saida.wav"
) -> None:
    subprocess.run(
        ["piper", "--model", modelo, "--output_file", saida],
        input=normalize(texto),
        text=True,
        check=True,
    )
```

### Coqui XTTS (clonagem de voz)

```python
from TTS.api import TTS  # pip install TTS  (dependência da sua aplicação, não do falabr)
from falabr import normalize

tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to("cuda")
tts.tts_to_file(
    text=normalize("Dia 05/03, às 14h30"),
    speaker_wav="referencia.wav",
    language="pt-br",
    file_path="saida.wav",
)
```

### ElevenLabs (API HTTP)

A ElevenLabs não aceita SSML; envie `normalize()` puro. Exemplo com `urllib` da stdlib:

```python
import json
import urllib.request
from pathlib import Path
from falabr import normalize


def falar_elevenlabs(texto: str, api_key: str, voice_id: str) -> None:
    corpo = json.dumps(
        {
            "text": normalize(texto),
            "model_id": "eleven_multilingual_v2",
        }
    ).encode("utf-8")
    requisicao = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
        data=corpo,
        headers={
            "xi-api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        },
        method="POST",
    )
    with urllib.request.urlopen(requisicao) as resposta:
        Path("saida.mp3").write_bytes(resposta.read())
```

### Azure Speech (SSML)

`normalize_ssml` devolve um `<speak>` com `<say-as>` e `<break>`; basta trocar o nó raiz
pelo formato do Azure e manter o corpo.

```python
from falabr import normalize_ssml


def ssml_azure(texto: str, voz: str = "pt-BR-FranciscaNeural") -> str:
    gerado = normalize_ssml(texto)
    corpo = gerado.removeprefix("<speak>").removesuffix("</speak>")
    return (
        '<speak version="1.0" xmlns="http://www.w3.org/2001/10/Synthesis" '
        'xml:lang="pt-BR">'
        f'<voice name="{voz}">{corpo}</voice>'
        "</speak>"
    )


# ssml_azure("Paguei R$ 10 em 05/03")
# '<speak ... xml:lang="pt-BR"><voice name="pt-BR-FranciscaNeural">
#  Paguei <say-as interpret-as="currency">dez reais</say-as> em
#  <say-as interpret-as="date">cinco de março</say-as></voice></speak>'
```

## Desenvolvimento

```bash
python -m ruff check . && python -m ruff format --check .
python -m mypy
python -m pytest
python -m coverage run -m pytest && python -m coverage report  # fail_under = 95
python -m build
```

CI: Ubuntu, Windows e macOS × Python 3.10–3.14. `.gitattributes` força LF em arquivos de
texto (inclusive os golden), e o workflow define `PYTHONUTF8=1` para que pt-BR funcione em
qualquer sistema operacional. Veja `CONTRIBUTING.md` e `SPEC.md`.

## Licença

MIT — Hadagalberto Junior. Ver `LICENSE`.
