"""Web entity: URLs, e-mails, @handles and #hashtags (camelCase splitting)."""

from __future__ import annotations

import re
from typing import Final

from ..options import Options
from ._common import MatchContext, Matcher, apply_matchers, compose

__all__ = ["WEB_MATCHERS", "normalize_web", "split_camel"]

_TRAILING: Final = ".,;:!?"

# "dáblio" is the pt-BR letter name for W (ABL/VOLP), so "www" is read as
# "dáblio dáblio dáblio" rather than the English "w w w".
_WWW_SPOKEN: Final = "dáblio dáblio dáblio"


def split_camel(token: str) -> str:
    """Split camelCase/PascalCase identifiers into lowercase words."""
    text = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", token)
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", text)
    return text.replace("_", " ").lower()


def _url_handler(match: re.Match[str], ctx: MatchContext) -> str:
    raw = match.group()
    trailing = ""
    while raw and raw[-1] in _TRAILING:
        trailing = raw[-1] + trailing
        raw = raw[:-1]
    if raw.lower().startswith(("http://", "https://")):
        # The scheme is a machine detail; a narrator reads the domain only.
        _, _, rest = raw.partition("://")
        spoken = f"{_WWW_SPOKEN} ponto {rest[4:]}" if rest.lower().startswith("www.") else rest
    else:  # raw starts with "www."
        spoken = f"{_WWW_SPOKEN} ponto {raw[4:]}"
    replacements = {
        ".": " ponto ",
        "/": " barra ",
        "-": " hífen ",
        "_": " sublinhado ",
        "?": " interrogação ",
        "=": " igual ",
        "&": " e ",
        "#": " hashtag ",
        ":": " dois pontos ",
        "%": " por cento ",
        "+": " mais ",
    }
    for char, word in replacements.items():
        spoken = spoken.replace(char, word)
    return " ".join(spoken.split()) + trailing


def _email_handler(match: re.Match[str], ctx: MatchContext) -> str:
    spoken = match.group()
    for char, word in (
        ("@", " arroba "),
        (".", " ponto "),
        ("_", " sublinhado "),
        ("-", " hífen "),
    ):
        spoken = spoken.replace(char, word)
    return " ".join(spoken.lower().split())


def _handle_handler(match: re.Match[str], ctx: MatchContext) -> str:
    return "arroba " + split_camel(match.group()[1:])


def _hashtag_handler(match: re.Match[str], ctx: MatchContext) -> str:
    return "hashtag " + split_camel(match.group()[1:])


WEB_MATCHERS: Final[tuple[Matcher, ...]] = (
    Matcher("url", r"(?:https?://|www\.)[^\s<>\"′]+", _url_handler),
    Matcher("email", r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", _email_handler),
    Matcher("hashtag", r"(?<!\w)#[A-Za-z][A-Za-z0-9_]*", _hashtag_handler),
    Matcher("handle", r"(?<!\w)@[A-Za-z][A-Za-z0-9_]*", _handle_handler),
)

_WEB_RE, _WEB_HANDLERS = compose(WEB_MATCHERS)


def normalize_web(text: str, options: Options | None = None) -> str:
    """Normalize URLs, e-mails, handles and hashtags in a string."""
    if options is None:
        options = Options()
    return apply_matchers(text, _WEB_RE, _WEB_HANDLERS, options)
