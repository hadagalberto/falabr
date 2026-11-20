"""Common pt-BR chat/e-mail shorthand expansion.

Written Portuguese often abbreviates function words in messages and e-mails:
``p/`` (para), ``c/`` (com), ``vc`` (você), ``pq`` (porque / por que), and so
on.  These must be expanded **before** the web and symbol matchers run,
otherwise ``p/`` is voiced as the letter ``p`` followed by "barra".

Expansion is deliberately conservative: a shorthand is only recognised as a
standalone token (start/whitespace/opening bracket before; whitespace,
punctuation or end after).  That keeps abbreviations inside URLs and paths
untouched — in ``www.exemplo.com/p/2026`` the ``p`` is part of the path, not a
shorthand, and is read as "p" by the URL handler.
"""

from __future__ import annotations

import re
from typing import Final

from ..options import Options
from ._common import MatchContext, Matcher, apply_matchers, compose

__all__ = ["SHORTHAND_MATCHERS", "normalize_shorthand"]

# Source: common pt-BR writing conventions (e.g. Cunha & Cintra, *Nova Gramática
# do Português Contemporâneo*, §"Abreviações"; VOLP/ABL usage notes for ``ex.``
# = "exemplo" and ``obs.`` = "observação").  Only unambiguous tokens are listed.
_SHORTHAND: Final[dict[str, str]] = {
    "p/": "para",
    "c/": "com",
    "s/": "sem",
    "q": "que",
    "q.": "que",
    "vc": "você",
    "tb": "também",
    "tbm": "também",
    "obs.": "observação",
    "ex.": "exemplo",
}

# Longest alternatives first so "q." wins over "q" and "tbm" over "tb".
_TOKENS: Final = r"p/|c/|s/|obs\.|ex\.|tbm|tb|q\.|q|vc|pq"

# The preceding character must be whitespace, an opening bracket/quote or the
# start of the string.  A slash, dot, @ or letter before the token means the
# token is inside a URL, path, e-mail or word and must not be expanded.
_START: Final = r"(?<![^\s(\[“])"
# The following character must be whitespace, sentence punctuation or end.
_END: Final = r"(?=$|[\s,;:!?.)\]”])"

_SHORTHAND_PATTERN: Final = _START + r"(?i:" + _TOKENS + r")" + _END


def _shorthand_handler(match: re.Match[str], ctx: MatchContext) -> str:
    token = match.group().lower()
    if token == "pq":
        # "por que" is the two-word form before a question mark; elsewhere the
        # causal conjunction is the single word "porque".
        following = ctx.text[match.end() :].lstrip()
        return "por que" if following.startswith("?") else "porque"
    return _SHORTHAND[token]


SHORTHAND_MATCHERS: Final[tuple[Matcher, ...]] = (
    Matcher("shorthand", _SHORTHAND_PATTERN, _shorthand_handler),
)

_SHORTHAND_RE, _SHORTHAND_HANDLERS = compose(SHORTHAND_MATCHERS)


def normalize_shorthand(text: str, options: Options | None = None) -> str:
    """Expand standalone pt-BR shorthands in ``text``."""
    if options is None:
        options = Options()
    return apply_matchers(text, _SHORTHAND_RE, _SHORTHAND_HANDLERS, options)
