"""Mobject representing highlighted source code listings."""

from __future__ import annotations

from typing import Mapping, Self

__all__ = [
    "Code",
]

from os import PathLike
from pathlib import Path

from more_itertools import peekable
from pygments import lex
from pygments.lexer import Lexer, LexerMeta
from pygments.lexers import get_lexer_by_name, guess_lexer, guess_lexer_for_filename
from pygments.style import Style
from pygments.styles import get_style_by_name
from pygments.token import _TokenType

from manim.constants import *
from manim.mobject.text.text_mobject import Paragraph, Text, remove_invisible_chars


class Code(Paragraph):
    """A highlighted source code listing.

    A non-LaTeX text object of :class:`.Code` is a :class:`.MarkupText` that supports `PangoMarkup <https://pango.gnome.org/>`.

    - Currently does **not** support backgrounds or line numbers.

    Examples
    --------

    Normal usage::

        listing = Code(
            "helloworldcpp.cpp",
            language="cpp",
            tab_width=4,
            style="github-dark",
        )



    Args:
        MarkupText (_type_): _description_
    """

    def __init__(
        self,
        code_or_filepath: str,  # TODO: Make this str | PathLike, then rename
        /,
        *,
        language: str | None = None,
        file_encoding: str | None = None,
        style: str = "default",
        font: str = "Monospace",
        font_size: float = 24,
        disable_ligatures: bool = False,
        tab_width: int = 4,
        line_spacing: float = -1,
        # margin: float = 0.3,
        # background: str = "rectangle",  # or window
        # background_stroke_width: float = 1,
        # background_stroke_color: str = WHITE,
        # corner_radius: float = 0.2,
        # insert_line_no: bool = True,
        # line_no_from: int = 1,
        # line_no_buff: float = 0.4,
        **kwargs,  # TODO: Do we need kwargs?
    ):
        # TODO: These need to go on another object to manage code with background. Are currently unused.
        # self.margin = margin
        # self.background = background
        # self.background_stroke_width = background_stroke_width
        # self.background_stroke_color = background_stroke_color
        # self.corner_radius = corner_radius
        # self.insert_line_no = insert_line_no
        # self.line_no_from = line_no_from
        # self.line_no_buff = line_no_buff

        if not code_or_filepath:
            raise ValueError("Argument 'code_or_filepath' cannot be None")

        code_path: Path = Path(
            code_or_filepath
        ).resolve()  # doesn't need to be resolved here

        code_is_path = code_path.is_file()
        if code_is_path:
            code_string: str = read_code_file(
                Path(code_or_filepath),
                encoding=file_encoding,
            )
        else:
            code_string: str = code_or_filepath

        code_string = (
            code_string.replace("\t", " " * tab_width)
            .replace("\r\n", "\n")
            .replace("\r", "\n")
        )

        lexer: Lexer | LexerMeta
        if code_is_path and language:
            # TODO: Handle invalid file paths *if needed*
            lexer = guess_lexer_for_filename(code_path.name, code_string)
        elif language:
            lexer = get_lexer_by_name(language)
        else:
            lexer = guess_lexer(code_string)

        style_name = style.lower()
        (t2c, t2s, t2w) = lex2csw(code_string, lexer, style_name)

        super().__init__(
            code_string,
            t2c=t2c,
            t2s=t2s,
            t2w=t2w,
            font=font,
            font_size=font_size,
            tab_width=tab_width,
            line_spacing=line_spacing,
            disable_ligatures=disable_ligatures,
            **kwargs,
        )


def lex2csw(code: str, lexer: Lexer | LexerMeta, style_name: str = "default"):
    styles: Mapping[_TokenType, Mapping] = dict(get_style_by_name(style_name))
    lexed_code: tuple[_TokenType, str] = lex(code, lexer)

    t2c: dict[str, str] = {}
    t2s: dict[str, str] = {}
    t2w: dict[str, str] = {}

    slice_start = slice_end = 0
    for token, value in (p := peekable(lexed_code)):
        next_token, _ = p.peek((None, None))
        
        slice_end += len(value)
        if token == next_token:
            continue
        
        slice = f"[{slice_start}:{slice_end}]"

        style = styles[token]  # type: ignore

        if style["color"]:
            t2c.update({slice: "#" + style["color"]})

        if style["italic"]:
            t2s.update({slice: ITALIC})

        if style["bold"]:
            t2w.update({slice: BOLD})
        
        slice_start = slice_end
        
    return (t2c, t2s, t2w)


def read_code_file(
    file_path: Path,
    *,
    encoding: str | None = None,
) -> str:
    """Function to validate file."""
    if file_path is None:
        raise ValueError("Name of file cannot be None")

    file_path = file_path.resolve(strict=True)
    if not file_path.is_file():
        raise FileNotFoundError(f"The provided path '{file_path}' is not a file")

    # Note on valid encodings: https://docs.python.org/3/library/codecs.html#standard-encodings
    return file_path.read_text(encoding=encoding)
