"""Emoji entity: remove or describe emoji using pt-BR short names.

The short-name table below is derived from the Unicode CLDR annotation data
for Brazilian Portuguese:

    Unicode CLDR, ``common/annotations/pt_BR.xml``
    https://github.com/unicode-org/cldr/blob/main/common/annotations/pt_BR.xml

Names are the CLDR ``<name>`` values, lightly normalised to lowercase.  Unknown
emoji fall back to the generic word "emoji" (or are removed, per options).
"""

from __future__ import annotations

import re
from typing import Final

from ..options import EmojiMode, Options
from ._common import MatchContext, Matcher, apply_matchers, compose

__all__ = ["CLDR_SOURCE", "EMOJI_MATCHERS", "describe_emoji", "normalize_emoji"]

CLDR_SOURCE: Final = (
    "Unicode CLDR annotations, pt_BR.xml — "
    "https://github.com/unicode-org/cldr/blob/main/common/annotations/pt_BR.xml"
)

# CLDR-derived pt-BR short names (see CLDR_SOURCE above).
_EMOJI_NAMES: Final[dict[str, str]] = {
    "😀": "rosto sorridente",
    "😃": "rosto sorridente com olhos grandes",
    "😄": "rosto sorridente com olhos semicerrados",
    "😁": "rosto com olhos semicerrados",
    "😆": "rosto com olhos semicerrados e boca aberta",
    "😂": "rosto com lágrimas de alegria",
    "🤣": "rosto rolando no chão de rir",
    "😊": "rosto sorridente com olhos corados",
    "😍": "rosto com olhos de coração",
    "🥰": "rosto sorridente com corações",
    "😘": "rosto mandando um beijo",
    "😋": "rosto comendo algo delicioso",
    "😎": "rosto com óculos de sol",
    "🤓": "rosto com óculos de nerd",
    "🧐": "rosto com monocelo",
    "🤔": "rosto pensativo",
    "🤨": "rosto com uma sobrancelha erguida",
    "😐": "rosto neutro",
    "😑": "rosto sem expressão",
    "🙄": "rosto revirando os olhos",
    "😏": "rosto com sorriso de deboche",
    "😒": "rosto sem entusiasmo",
    "😢": "rosto triste",
    "😭": "rosto chorando alto",
    "😤": "rosto com raiva contida",
    "😡": "rosto com raiva",
    "🤬": "rosto com raiva e palavrões",
    "😱": "rosto com grito de terror",
    "😨": "rosto assustado",
    "😴": "rosto dormindo",
    "🤯": "rosto com cabeça explodindo",
    "🥳": "rosto comemorando",
    "🤗": "rosto com mãos abertas",
    "🤭": "rosto com a mão sobre a boca",
    "🤫": "rosto pedindo silêncio",
    "😇": "rosto com auréola",
    "🤠": "rosto de cowboy",
    "🥺": "rosto implorando",
    "👍": "polegar para cima",
    "👎": "polegar para baixo",
    "👏": "palmas",
    "🙌": "mãos erguidas",
    "🤝": "aperto de mão",
    "🙏": "mãos juntas",
    "💪": "bíceps",
    "✌️": "sinal de vitória",
    "🤞": "dedos cruzados",
    "🤟": "sinal de eu te amo",
    "👋": "mão acenando",
    "✋": "mão aberta",
    "🤚": "costas da mão erguidas",
    "👌": "sinal de ok",
    "🤌": "dedos apertados",
    "❤️": "coração vermelho",
    "🧡": "coração laranja",
    "💛": "coração amarelo",
    "💚": "coração verde",
    "💙": "coração azul",
    "💜": "coração roxo",
    "🖤": "coração preto",
    "💔": "coração partido",
    "❣️": "coração com exclamação",
    "💕": "dois corações",
    "💖": "coração cintilante",
    "✨": "brilhos",
    "⭐": "estrela",
    "🌟": "estrela brilhante",
    "💫": "estrela com tontura",
    "🔥": "fogo",
    "🌈": "arco-íris",
    "☀️": "sol",
    "🌙": "lua crescente",
    "🌊": "onda",
    "🌱": "muda",
    "🌻": "girassol",
    "🌹": "rosa",
    "🍀": "trevo de quatro folhas",
    "🌍": "globo terrestre",
    "🌐": "globo com meridianos",
    "🎉": "festa",
    "🎊": "confete",
    "🎁": "presente",
    "🎂": "bolo de aniversário",
    "🎈": "balão",
    "☕": "café",
    "🍕": "pizza",
    "🍔": "hambúrguer",
    "🍣": "sushi",
    "🍎": "maçã vermelha",
    "🍌": "banana",
    "🍇": "uvas",
    "🥇": "medalha de ouro",
    "🥈": "medalha de prata",
    "🥉": "medalha de bronze",
    "⚽": "bola de futebol",
    "🏀": "bola de basquete",
    "🏆": "troféu",
    "🚀": "foguete",
    "🚗": "carro",
    "✈️": "avião",
    "🏠": "casa",
    "🏢": "prédio de escritórios",
    "💰": "saco de dinheiro",
    "💵": "nota de dinheiro",
    "💡": "lâmpada",
    "📌": "alfinete",
    "📎": "clipe de papel",
    "📚": "livros",
    "📝": "memorando",
    "📱": "telefone celular",
    "💻": "computador",
    "⌨️": "teclado",
    "🖨️": "impressora",
    "🔒": "cadeado fechado",
    "🔑": "chave",
    "🔔": "sino",
    "🎵": "nota musical",
    "🎶": "notas musicais",
    "✅": "marca de verificação",
    "❌": "x vermelho",
    "⚠️": "aviso",
    "⏰": "relógio de alarme",
    "🕐": "relógio uma hora",
    "♻️": "símbolo de reciclagem",
    "🔗": "link",
    "🧠": "cérebro",
    "👀": "olhos",
    "👶": "bebê",
    "🐶": "cachorro",
    "🐱": "gato",
    "🐦": "pássaro",
    "🐝": "abelha",
    "👨‍👩‍👧": "família",
}

_SKIN_TONES: Final = frozenset("\U0001f3fb\U0001f3fc\U0001f3fd\U0001f3fe\U0001f3ff")
_ZWJ: Final = "\u200d"
_VS16: Final = "\ufe0f"

_EMOJI_CHARS: Final = (
    "\U0001f000-\U0001faff\u2600-\u27bf\u2b00-\u2bff\u20e3\ufe0f\u200d\u00a9\u00ae\u2122"
)
_EMOJI_PATTERN: Final = rf"(?:(?:\d\ufe0f?\u20e3)|(?:[{_EMOJI_CHARS}]+))"


def describe_emoji(emoji: str) -> str:
    """Return the CLDR-derived pt-BR short name for an emoji cluster."""
    if not isinstance(emoji, str):
        raise TypeError("emoji must be a str")
    if emoji in _EMOJI_NAMES:
        return _EMOJI_NAMES[emoji]
    without_skin = "".join(char for char in emoji if char not in _SKIN_TONES)
    if without_skin in _EMOJI_NAMES:
        return _EMOJI_NAMES[without_skin]
    first = emoji.split(_ZWJ)[0]
    for candidate in (first, first + _VS16):
        if candidate in _EMOJI_NAMES:
            return _EMOJI_NAMES[candidate]
    return "emoji"


def _emoji_handler(match: re.Match[str], ctx: MatchContext) -> str:
    raw = match.group()
    had_leading_space = raw.startswith((" ", "\t"))
    emoji = raw[1:] if had_leading_space else raw
    before = ctx.text[: match.start()]
    after = ctx.text[match.end() :]
    right = "" if not after or after[0].isspace() or after[0] in "!?,;:.)]”" else " "
    if ctx.options.emoji_mode is EmojiMode.REMOVE:
        if had_leading_space:
            return right
        left = "" if not before or before[-1].isspace() or before[-1] in "([“" else " "
        return left + right
    left = (
        " "
        if had_leading_space
        else ("" if not before or before[-1].isspace() or before[-1] in "([“" else " ")
    )
    return left + describe_emoji(emoji) + right


EMOJI_MATCHERS: Final[tuple[Matcher, ...]] = (
    Matcher("emoji", rf"[ \t]?{_EMOJI_PATTERN}", _emoji_handler),
)

_EMOJI_RE, _EMOJI_HANDLERS = compose(EMOJI_MATCHERS)


def normalize_emoji(text: str, options: Options | None = None) -> str:
    """Remove or describe emoji in a string, per ``options.emoji_mode``."""
    if options is None:
        options = Options()
    return apply_matchers(text, _EMOJI_RE, _EMOJI_HANDLERS, options)
