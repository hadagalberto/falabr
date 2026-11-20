"""Noun-gender detection for number/noun agreement in running text.

A number spoken before a noun agrees with that noun in Portuguese
("uma filha", "duzentas pessoas").  The pipeline's generic number matchers used
to always spell masculine, which produced "um filha" and "duzentos pessoas".

The lexicon below is deliberately curated (common nouns, units and frequent
measure words drawn from the same families already used by ``units`` and
``measures``); a documented morphological heuristic handles unseen nouns.
Sources: Cunha & Cintra, *Nova Gramática do Português Contemporâneo*, chapter
"Numerais"; ABL/VOLP for the masculine ``-a`` exceptions (``grama``, ``dia``,
``problema``, ``programa``, ``sistema``, ``mapa``, ``tema``, ``clima``).
"""

from __future__ import annotations

import re
from typing import Final

from ..options import Gender

__all__ = ["agreement_gender", "following_noun", "noun_gender"]

# Nouns whose grammatical gender cannot be inferred reliably from their ending.
_FEMININE: Final[frozenset[str]] = frozenset(
    {
        # people / kinship
        "filha",
        "filhas",
        "pessoa",
        "pessoas",
        "mulher",
        "mulheres",
        "mãe",
        "mães",
        "irmã",
        "irmãs",
        "tia",
        "tias",
        "avó",
        "avós",
        "neta",
        "netas",
        "sobrinha",
        "sobrinhas",
        "prima",
        "primas",
        "amiga",
        "amigas",
        "colega",
        "colegas",
        "menina",
        "meninas",
        "moça",
        "moças",
        "senhora",
        "senhoras",
        "doutora",
        "doutoras",
        "professora",
        "professoras",
        "rainha",
        "rainhas",
        "princesa",
        "princesas",
        "elizabeth",
        "maria",
        "ana",
        "isabel",
        "catarina",
        "joana",
        "sofia",
        "beatriz",
        "clara",
        "rita",
        "teresa",
        "cristina",
        "helena",
        "luíza",
        # time / units / measures (feminine)
        "hora",
        "horas",
        "semana",
        "semanas",
        "vez",
        "vezes",
        "tonelada",
        "toneladas",
        "colher",
        "colheres",
        "xícara",
        "xícaras",
        "pitada",
        "pitadas",
        "gota",
        "gotas",
        "manhã",
        "tarde",
        "noite",
        "noites",
        "madrugada",
        "libra",
        "libras",
        # places / abstract nouns
        "cidade",
        "cidades",
        "casa",
        "casas",
        "rua",
        "ruas",
        "avenida",
        "avenidas",
        "praça",
        "praças",
        "escola",
        "escolas",
        "universidade",
        "universidades",
        "empresa",
        "empresas",
        "organização",
        "organizações",
        "instituição",
        "instituições",
        "associação",
        "associações",
        "situação",
        "situações",
        "informação",
        "informações",
        "pergunta",
        "perguntas",
        "resposta",
        "respostas",
        "solução",
        "soluções",
        "questão",
        "questões",
        "razão",
        "razões",
        "versão",
        "versões",
        "decisão",
        "decisões",
        "opinião",
        "opiniões",
        "ideia",
        "ideias",
        "notícia",
        "notícias",
        "história",
        "histórias",
        "memória",
        "memórias",
        "linguagem",
        "mensagem",
        "mensagens",
        "imagem",
        "imagens",
        "viagem",
        "viagens",
        "chave",
        "chaves",
        "ponte",
        "pontes",
        "frente",
        "classes",
        "classe",
        "base",
        "fase",
        "crise",
        "análise",
        "taxa",
        "moeda",
        "medida",
        "medidas",
        "altura",
        "largura",
        "profundidade",
        "distância",
        "velocidade",
        "temperatura",
        "pressão",
        "energia",
        "força",
        "potência",
        "corrente",
        "tensão",
        "resistência",
        "sessão",
        "sessões",
        "seção",
        "seções",
        "coleção",
        "coleções",
        "direção",
        "direções",
        "produção",
        "produções",
        "construção",
        "construções",
    }
)

_MASCULINE: Final[frozenset[str]] = frozenset(
    {
        # -a endings that are masculine (VOLP)
        "grama",
        "gramas",
        "dia",
        "dias",
        "problema",
        "problemas",
        "programa",
        "programas",
        "sistema",
        "sistemas",
        "mapa",
        "mapas",
        "tema",
        "temas",
        "clima",
        "climas",
        "cinema",
        "cinemas",
        "documento",
        "documentos",
        "monumento",
        "monumentos",
        "instrumento",
        "instrumentos",
        "movimento",
        "movimentos",
        "sentimento",
        "sentimentos",
        "conhecimento",
        "conhecimentos",
        "desenvolvimento",
        "desenvolvimentos",
        "pizza",
        "sushi",
        "dólar",
        "dólares",
        "real",
        "reais",
        "euro",
        "euros",
        "rico",
        "amigo",
        "amigos",
        # feminine-looking -e nouns that are masculine
        "leite",
        "gelo",
        "gelos",
        "rio",
        "rios",
        "livro",
        "livros",
        "carro",
        "carros",
        "minuto",
        "minutos",
        "segundo",
        "segundos",
        "litro",
        "litros",
        "quilômetro",
        "quilômetros",
        "quilograma",
        "quilogramas",
        "metro",
        "metros",
        "quilowatt",
        "watts",
        "watt",
        "volts",
        "volt",
        "ampere",
        "amperes",
        "gigabyte",
        "gigabytes",
        "megabyte",
        "megabytes",
        "grau",
        "graus",
        "hectare",
        "hectares",
        "hertz",
    }
)

# Function words are skipped when looking for the counted noun.
_SKIP_WORDS: Final[frozenset[str]] = frozenset(
    {
        "de",
        "do",
        "da",
        "dos",
        "das",
        "e",
        "em",
        "no",
        "na",
        "nos",
        "nas",
        "um",
        "uma",
        "uns",
        "umas",
        "o",
        "a",
        "os",
        "as",
        "que",
        "com",
        "por",
        "para",
        "mais",
        "menos",
        "muito",
        "muitos",
        "muitas",
        "pouco",
        "poucos",
        "poucas",
        "cada",
        "todo",
        "toda",
        "todos",
        "todas",
        "outro",
        "outra",
        "outros",
        "outras",
        "novo",
        "nova",
        "novos",
        "novas",
        "primeiro",
        "primeira",
        "último",
        "última",
        "aproximadamente",
        "cerca",
        "sobre",
        "num",
        "numa",
        "pelo",
        "pela",
    }
)

_WORD_RE: Final = re.compile(r"^\s+([^\W\d_]+)", re.UNICODE)


def following_noun(after: str) -> tuple[Gender | None, str | None]:
    """Return ``(gender, noun)`` for the token following a number.

    Function words such as ``de``/``do``/``da`` are skipped so that
    ``" de pessoas"`` still yields ``("f", "pessoas")``.  ``(None, None)`` is
    returned when no noun follows (end of text, punctuation, another number).
    """
    rest = after
    for _ in range(4):
        match = _WORD_RE.match(rest)
        if match is None:
            return None, None
        word = match.group(1).lower()
        if word in _SKIP_WORDS:
            rest = rest[match.end() :]
            continue
        return noun_gender(word), word
    return None, None


def noun_gender(word: str | None) -> Gender | None:
    """Best-effort grammatical gender of a lowercase noun token.

    ``None`` means "no opinion" (no noun or unknown token); callers then keep
    the masculine default.  The morphological fallback is documented and
    intentionally conservative:

    * ``-a`` -> feminine, except the curated masculine exceptions;
    * ``-o``, ``-e``, other endings -> masculine, except curated feminine -e
      nouns such as ``noite``/``chave``;
    * loanwords ending in a consonant or in ``-i``/``-u`` default to masculine.
    """
    if not word:
        return None
    token = word.lower()
    for candidate in (token, token[:-1] if token.endswith("s") else token):
        if candidate in _FEMININE:
            return "f"
        if candidate in _MASCULINE:
            return "m"
    # A regular plural is classified by its singular ("crianças" -> "criança").
    stem = token[:-1] if token.endswith("s") else token
    if stem.endswith("a"):
        return "f"
    return "m"


def agreement_gender(after: str) -> Gender:
    """Gender to use for a number, derived from the noun that follows it."""
    gender, _noun = following_noun(after)
    return gender or "m"
