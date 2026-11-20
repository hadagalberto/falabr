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
    "👩": "mulher",  # ZWJ fallback for professions, e.g. "👩‍💻"
}

_SKIN_TONES: Final = frozenset("\U0001f3fb\U0001f3fc\U0001f3fd\U0001f3fe\U0001f3ff")
_ZWJ: Final = "\u200d"
_VS16: Final = "\ufe0f"
_KEYCAP: Final = "\u20e3"
_RI_START: Final = 0x1F1E6
_RI_END: Final = 0x1F1FF

# CLDR pt_BR names for the flags most often written in Brazilian social text.
# A regional-indicator pair is decoded to its ISO code and looked up here.
_FLAG_NAMES: Final[dict[str, str]] = {
    "BR": "bandeira do Brasil",
    "US": "bandeira dos Estados Unidos",
    "PT": "bandeira de Portugal",
    "AR": "bandeira da Argentina",
    "GB": "bandeira do Reino Unido",
    "FR": "bandeira da França",
    "DE": "bandeira da Alemanha",
    "IT": "bandeira da Itália",
    "ES": "bandeira da Espanha",
    "JP": "bandeira do Japão",
    "CN": "bandeira da China",
    "CA": "bandeira do Canadá",
    "MX": "bandeira do México",
}

# Match whole grapheme clusters, longest first: a regional-indicator flag, a
# keycap sequence, a ZWJ sequence (family/profession emoji), then a single base
# emoji with an optional variation selector and skin-tone modifier.  Adjacent
# emoji are separate clusters, so "😀🎉" is described as two emoji instead of
# collapsing into one unknown run.
_EMOJI_BASE: Final = "\U0001f000-\U0001faff\u2600-\u27bf\u2b00-\u2bff\u00a9\u00ae\u2122"
_SKIN_CLASS: Final = "[" + "".join(sorted(_SKIN_TONES)) + "]"
_SINGLE: Final = rf"[{_EMOJI_BASE}](?:{_VS16})?(?:{_SKIN_CLASS})?"
_FLAG: Final = r"[\U0001f1e6-\U0001f1ff][\U0001f1e6-\U0001f1ff]"
_KEYCAP_SEQUENCE: Final = rf"\d{_VS16}?{_KEYCAP}"
_ZWJ_SEQUENCE: Final = rf"{_SINGLE}(?:{_ZWJ}{_SINGLE})+"
_EMOJI_PATTERN: Final = rf"(?:{_FLAG}|{_KEYCAP_SEQUENCE}|{_ZWJ_SEQUENCE}|{_SINGLE})"
_EMOJI_CHAR_RE: Final = re.compile(f"[{_EMOJI_BASE}]")


def _flag_name(emoji: str) -> str | None:
    """Decode a pair of regional indicators into its pt-BR flag name."""
    if len(emoji) != 2 or not all(_RI_START <= ord(char) <= _RI_END for char in emoji):
        return None
    code = "".join(chr(ord(char) - _RI_START + ord("A")) for char in emoji)
    return _FLAG_NAMES.get(code, "bandeira")


def describe_emoji(emoji: str) -> str:
    """Return the CLDR-derived pt-BR short name for an emoji cluster."""
    if not isinstance(emoji, str):
        raise TypeError("emoji must be a str")
    # Adjacent clusters are described one by one, joined with a comma pause.
    clusters = [match.group() for match in re.finditer(_EMOJI_PATTERN, emoji)]
    if len(clusters) > 1:
        return ", ".join(describe_emoji(cluster) for cluster in clusters)
    if emoji in _EMOJI_NAMES:
        return _EMOJI_NAMES[emoji]
    flag = _flag_name(emoji)
    if flag is not None:
        return flag
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
    adjacent_after = bool(after) and _EMOJI_CHAR_RE.match(after[0]) is not None
    adjacent_before = bool(before) and _EMOJI_CHAR_RE.match(before[-1]) is not None
    plain_right = "" if not after or after[0].isspace() or after[0] in "!?,;:.)]”" else " "
    if ctx.options.emoji_mode is EmojiMode.REMOVE:
        if had_leading_space:
            return "" if adjacent_after else plain_right
        left = "" if not before or before[-1].isspace() or before[-1] in "([“" else " "
        return left + ("" if adjacent_after else plain_right)
    if had_leading_space:
        left = " "
    elif adjacent_before:
        # The previous cluster already emitted the comma separator.
        left = ""
    elif not before or before[-1].isspace() or before[-1] in "([“":
        left = ""
    else:
        left = " "
    if not after or after[0].isspace() or after[0] in "!?,;:.)]”":
        right = ""
    elif adjacent_after:
        # Adjacent emoji ("😀🎉") are described separately with a comma pause.
        right = ", "
    else:
        right = " "
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
