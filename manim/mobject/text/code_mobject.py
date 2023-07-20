"""Mobject representing highlighted source code listings."""

from __future__ import annotations

__all__ = [
    "Code",
]

from os import PathLike
from pathlib import Path

from pygments import highlight
from pygments.formatters.pangomarkup import PangoMarkupFormatter
from pygments.lexers import get_lexer_by_name, guess_lexer, guess_lexer_for_filename

from manim.constants import *
from manim.mobject.text.text_mobject import MarkupText
from manim.utils.color import WHITE


class Code(MarkupText):
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
        code_or_filepath: str,  # TODO: Make this str | PathLike
        /,
        *,
        language: str | None = None,
        file_encoding: str | None = None,
        style: str | None = None,
        font_size: float = 24,
        margin: float = 0.3,
        indentation_chars: str = "    ",
        background: str = "rectangle",  # or window
        background_stroke_width: float = 1,
        background_stroke_color: str = WHITE,
        corner_radius: float = 0.2,
        insert_line_no: bool = True,
        line_no_from: int = 1,
        line_no_buff: float = 0.4,
        **kwargs,
    ):
        # TODO: These need to go on another object to manage code with background. Are currently unused.
        self.background_stroke_color = background_stroke_color
        self.background_stroke_width = background_stroke_width
        self.margin = margin
        self.indentation_chars = indentation_chars
        self.background = background
        self.corner_radius = corner_radius
        self.insert_line_no = insert_line_no
        self.line_no_from = line_no_from
        self.line_no_buff = line_no_buff

        if not code_or_filepath:
            raise ValueError("Argument 'code_or_filepath' cannot be None")

        code_path: Path = Path(
            code_or_filepath
        ).resolve()  # doesn't need to be resolved here
        code_is_path = code_path.is_file()
        if code_is_path:
            self.code_string: str = read_code_file(
                Path(code_or_filepath),
                encoding=file_encoding,
            )
        else:
            self.code_string: str = code_or_filepath

        if code_is_path and language:
            # TODO: Handle invalid file paths *if needed*
            lexer = guess_lexer_for_filename(code_path.name, self.code_string)
        elif language:
            lexer = get_lexer_by_name(language)
        else:
            lexer = guess_lexer(self.code_string)

        style = style.lower() if style is not None else None
        formatter = PangoMarkupFormatter(style=style)
        pango_code = highlight(self.code_string, lexer, formatter)

        super().__init__(
            text=pango_code,
            font_size=font_size,
            **kwargs,
        )


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
