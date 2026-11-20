# falabr

Normalização de texto em português brasileiro para **text-to-speech** (assistentes de voz,
audiolivros, narração de reels). O objetivo: transformar o texto escrito em exatamente o que
um locutor falaria.

> `"R$ 1.234,56"` → "mil duzentos e trinta e quatro reais e cinquenta e seis centavos"

O **Marco 1** implementa números por extenso (cardinais, ordinais, frações, porcentagens,
decimais, dinheiro e numerais romanos) e o analisador reverso `parse_spoken_number`.
O **Marco 2** adiciona as entidades de texto completo e o pipeline `normalize`: moedas,
datas/horas, décadas/séculos, unidades, abreviações e siglas, códigos (CPF/CNPJ/CEP/
telefone/cartão), URLs/e-mails/@handles/#hashtags, símbolos e emojis. Veja `SPEC.md`.

## Instalação

```bash
python -m pip install -e ".[dev]"
```

Requer Python 3.10 ou superior. **Zero dependências em runtime.**

## Uso da API

```python
from falabr import (
    CatorzeStyle,
    DecimalMode,
    Options,
    spell_cardinal,
    spell_number,
    spell_ordinal,
    spell_fraction,
    spell_percentage,
    spell_money,
    spell_roman,
    parse_spoken_number,
)

spell_cardinal(1234)  # 'mil duzentos e trinta e quatro'
spell_cardinal(200, gender="f")  # 'duzentas'
spell_number("3,14")  # 'três vírgula catorze'
spell_number("3,14", options=Options(decimal_mode=DecimalMode.DIGITS))
# 'três vírgula um quatro'
spell_number(14, options=Options(catorze_style=CatorzeStyle.CATORZE))
# 'catorze'
spell_ordinal(21)  # 'vigésimo primeiro'
spell_ordinal(1000, gender="f")  # 'milésima'
spell_fraction(3, 4)  # 'três quartos'
spell_fraction(5, 12)  # 'cinco doze avos'
spell_percentage(12.5)  # 'doze vírgula cinco por cento'
spell_money("1000000")  # 'um milhão de reais'
spell_roman("XXI")  # 'vinte e um'  (século XXI)
spell_roman("II", context="regnal")  # 'segundo'     (Dom Pedro II)
parse_spoken_number("dois mil e trinta")  # 2030
```

### Pipeline de entidades (Marco 2)

```python
from falabr import EmojiMode, Options, normalize, normalize_ssml, split_sentences

normalize("R$ 1.234,56")  # 'mil duzentos e trinta e quatro reais e cinquenta e seis centavos'
normalize("Dia 05/03, às 14h30")  # 'Dia cinco de março, às quatorze horas e trinta minutos'
normalize("Dr. Silva: 14h30")  # 'doutor Silva: quatorze horas e trinta minutos'
normalize("CPF 123.456.789-09")  # 'cê pê efe um dois três, quatro cinco seis, ...'
normalize("São 1,5 km")  # 'São um vírgula cinco quilômetros'
normalize("#BomDia @JoaoSilva")  # 'hashtag bom dia arroba joao silva'
normalize("Parabéns 🎉", Options(emoji_mode=EmojiMode.DESCRIBE))  # 'Parabéns festa'
normalize("O INSS", Options(acronym_overrides={"INSS": "word"}))  # 'O inss'
normalize("Pix", Options(user_lexicon={"Pix": "PIX"}))  # 'PIX'
normalize_ssml("R$ 10")  # '<speak><say-as interpret-as="currency">dez reais</say-as></speak>'
split_sentences("Dr. Silva chegou. Sra. Maria saiu.")
# ['Dr. Silva chegou.', 'Sra. Maria saiu.']
```

Helpers por entidade: `normalize_money`, `normalize_datetime`, `normalize_units`,
`normalize_abbreviations`, `spell_acronym`, `normalize_identifiers`, `normalize_web`,
`normalize_symbols`, `normalize_emoji`, `describe_emoji`, `normalize_with_spans` e
`split_camel`. Os nomes curtos de emojis vêm da tabela CLDR pt-BR (fonte em `CLDR_SOURCE`).

### Regras gramaticais

As regras de conectores seguem Celso Cunha & Lindley Cintra (*Nova Gramática do Português
Contemporâneo*), Paul Teyssier (*Manual de Língua Portuguesa*) e o guia de redação da Câmara
Municipal de Belo Horizonte; a variante `catorze` segue o VOLP/ABL. As referências completas
estão no cabeçalho de `src/falabr/numbers.py` e nos comentários dos testes.

## CLI

```bash
falabr "Dia 14, comprei 1.234,56 reais"
falabr -f texto.txt --json
echo "século XXI" | falabr --ssml
```

Opções: `--file/-f`, `--json` (spans original→falado), `--ssml`, `--catorze`,
`--decimal-mode cardinal|digits` e `--roman-context cardinal|regnal`.

## Desenvolvimento

```bash
python -m ruff check . && python -m ruff format --check .
python -m mypy
python -m pytest
python -m coverage run -m pytest && python -m coverage report
python -m build
```

CI: Ubuntu, Windows e macOS × Python 3.10–3.13 (GitHub Actions).

## Licença

MIT — Hadagalberto Junior. Ver `LICENSE`.
