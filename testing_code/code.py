from typing import Mapping

from pygments import lex
from pygments.lexer import Lexer, LexerMeta
from pygments.styles import get_style_by_name
from pygments.token import _TokenType

from manim.constants import BOLD, ITALIC


def lex2csw(code: str, lexer: Lexer | LexerMeta, style_name: str = "default"):
    styles: Mapping[_TokenType, Mapping] = dict(get_style_by_name(style_name))
    lexed_code: tuple[_TokenType, str] = lex(code, lexer)

    t2c: dict[str, str] = {}
    t2s: dict[str, str] = {}
    t2w: dict[str, str] = {}

    idx = 0
    for token, value in lexed_code:
        length = len(value)
        slice = f"[{idx}:{idx + length}]"

        style = styles[token]  # type: ignore

        if style["color"]:
            t2c.update({slice: "#" + style["color"]})

        if style["italic"]:
            t2s.update({slice: ITALIC})

        if style["bold"]:
            t2w.update({slice: BOLD})

        idx += length

    return (t2c, t2s, t2w)