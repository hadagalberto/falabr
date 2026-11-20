# Contributing

Obrigado por contribuir com o falabr. O projeto é pequeno, mas as regras gramaticais são
exatas: mudanças precisam de testes com vetores escritos à mão, não de expectativas geradas
pela implementação.

## Setup

1. Fork/clone e crie um branch. **Nunca** faça `git push`, use `gh`, `twine`, `uv publish` ou
   qualquer comando de publicação — o projeto não publica no PyPI.
2. Instale os extras de desenvolvimento:

   ```bash
   python -m pip install -e ".[dev]"
   ```

3. Rode a suíte completa antes de começar para garantir que seu ambiente está limpo.

## Regras para mudanças

- Sem stubs, TODOs, `NotImplementedException`, testes pulados ou placeholders.
- Todo comportamento público precisa de asserções com vetores **válidos e inválidos**
  conhecidos. Em particular: se você adiciona uma entidade, inclua casos em que ela **não**
  deve disparar (por exemplo, `p/` dentro de uma URL não é shorthand).
- Novas regras gramaticais devem citar a fonte em comentários (ABL/VOLP, Cunha & Cintra,
  Teyssier, CLDR etc.).
- Regras de número: atualize os casos em `tests/test_cardinals.py`, `test_ordinals.py`,
  `test_fractions_money.py` etc. e o cabeçalho de `src/falabr/numbers.py`.
- Golden paragraphs: crie o par `tests/golden/<categoria>.in.txt` e
  `tests/golden/<categoria>.out.txt` (UTF-8, LF), registre a categoria em
  `tests/test_golden.py::CATEGORIES` e escreva a saída esperada à mão. O teste falha se um
  par de arquivos não estiver registrado.
- Se uma API pública for adicionada/renomeada, atualize `falabr.__all__`,
  `tests/test_api.py::test_public_exports`, `README.md`, `README.en.md` e o `CHANGELOG.md`.

## Checklist antes do commit

Tudo precisa passar, sem exceções e sem enfraquecer testes:

```bash
python -m ruff check .
python -m ruff format --check .
python -m mypy
python -m pytest
python -m coverage run -m pytest
python -m coverage report          # fail_under = 95
python -m build
```

Se algo falhar, corrija a causa raiz. Nunca delete ou enfraqueça um teste para fazê-lo
passar.

## Checklist multiplataforma (CI)

O CI roda em Ubuntu, Windows e macOS com Python 3.10–3.14. Respeite estes pontos:

- `.gitattributes` força `eol=lf` para texto e marca assets binários com `binary`. Não
  commite arquivos de texto com CRLF; o formatador (`ruff format --check`) espera LF.
- Não dependa de comportamento específico de OS/ICU/locale: sem `locale`, `strftime`,
  `datetime.now()`, fuso horário, separador de caminho codificado ou `TextDecoder` com
  rótulos locais. Use `pathlib`, `encoding="utf-8"` e normalização explícita.
- Não localize executáveis externos através do caminho do runtime (por exemplo,
  `sys.executable` para achar `npm`/`dotnet`/`cargo`/`piper`). Receitas de integração
  resolvem binários pelo `PATH`.
- Nenhum teste deve depender de um artefato já construído. A CLI é testada chamando
  `falabr.cli.main()` diretamente; o workflow constrói o pacote (`python -m build`) no job
  de qualidade.
- O workflow usa `PYTHONUTF8=1` para que pt-BR funcione no console do Windows. Ao adicionar
  um passo, verifique linha por linha que ele funciona nos três sistemas operacionais.

## Commits

Use Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `ci:`). Exemplo:

```
feat: expand pt-BR shorthand before web entity handling
```

Referências gramaticais para números estão no topo de `src/falabr/numbers.py`.
