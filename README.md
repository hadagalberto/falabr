# falabr

Normalização de texto em português brasileiro para **text-to-speech** (assistentes de voz,
audiolivros, narração de reels). O objetivo: transformar o texto escrito em exatamente o que
um locutor falaria.

> `"R$ 1.234,56"` → "mil duzentos e trinta e quatro reais e cinquenta e seis centavos"

Este é o **Marco 1**: números por extenso (cardinais, ordinais, frações, porcentagens,
decimais, dinheiro e numerais romanos) e o analisador reverso `parse_spoken_number`.
As entidades de texto completo (datas, moedas em contexto, URLs, SSML etc.) vêm nos marcos
seguintes — veja `SPEC.md`.

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
