"""Mobject representing highlighted source code listings."""

from __future__ import annotations

__all__ = [
    "Code",
]

import html
import re
from os import PathLike
from pathlib import Path

import numpy as np
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import get_lexer_by_name, guess_lexer_for_filename
from pygments.styles import get_all_styles

from manim import logger
from manim.constants import *
from manim.mobject.geometry.arc import Dot
from manim.mobject.geometry.polygram import RoundedRectangle
from manim.mobject.geometry.shape_matchers import SurroundingRectangle
from manim.mobject.text.text_mobject import Paragraph
from manim.mobject.types.vectorized_mobject import VGroup
from manim.utils.color import WHITE


class Code(VGroup):
    """A highlighted source code listing.

    An object ``listing`` of :class:`.Code` is a :class:`.VGroup` consisting
    of three objects:

    - The background, ``listing.background_mobject``. This is either
      a :class:`.Rectangle` (if the listing has been initialized with
      ``background="rectangle"``, the default option) or a :class:`.VGroup`
      resembling a window (if ``background="window"`` has been passed).

    - The line numbers, ``listing.line_numbers`` (a :class:`.Paragraph`
      object).

    - The highlighted code itself, ``listing.code`` (a :class:`.Paragraph`
      object).

    .. WARNING::

        Using a :class:`.Transform` on text with leading whitespace (and in
        this particular case: code) can look
        `weird <https://github.com/3b1b/manim/issues/1067>`_. Consider using
        :meth:`remove_invisible_chars` to resolve this issue.

    Examples
    --------

    Normal usage::

        listing = Code(
            "helloworldcpp.cpp",
            tab_width=4,
            background_stroke_width=1,
            background_stroke_color=WHITE,
            insert_line_no=True,
            style=Code.styles_list[15],
            background="window",
            language="cpp",
        )

    We can also render code passed as a string (but note that
    the language has to be specified in this case):

    .. manim:: CodeFromString
        :save_last_frame:

        class CodeFromString(Scene):
            def construct(self):
                code = '''from manim import Scene, Square

        class FadeInSquare(Scene):
            def construct(self):
                s = Square()
                self.play(FadeIn(s))
                self.play(s.animate.scale(2))
                self.wait()
        '''
                rendered_code = Code(code=code, tab_width=4, background="window",
                                    language="Python", font="Monospace")
                self.add(rendered_code)

    Parameters
    ----------
    file_name
        Name of the code file to display.
    code
        If ``file_name`` is not specified, a code string can be
        passed directly.
    tab_width
        Number of space characters corresponding to a tab character. Defaults to 3.
    line_spacing
        Amount of space between lines in relation to font size. Defaults to 0.3, which means 30% of font size.
    font_size
        A number which scales displayed code. Defaults to 24.
    font
        The name of the text font to be used. Defaults to ``"Monospace"``.
        This is either a system font or one loaded with `text.register_font()`. Note
        that font family names may be different across operating systems.
    stroke_width
        Stroke width for text. 0 is recommended, and the default.
    margin
        Inner margin of text from the background. Defaults to 0.3.
    indentation_chars
        "Indentation chars" refers to the spaces/tabs at the beginning of a given code line. Defaults to ``"    "`` (spaces).
    background
        Defines the background's type. Currently supports only ``"rectangle"`` (default) and ``"window"``.
    background_stroke_width
        Defines the stroke width of the background. Defaults to 1.
    background_stroke_color
        Defines the stroke color for the background. Defaults to ``WHITE``.
    corner_radius
        Defines the corner radius for the background. Defaults to 0.2.
    insert_line_no
        Defines whether line numbers should be inserted in displayed code. Defaults to ``True``.
    line_no_from
        Defines the first line's number in the line count. Defaults to 1.
    line_no_buff
        Defines the spacing between line numbers and displayed code. Defaults to 0.4.
    style
        Defines the style type of displayed code. You can see possible names of styles in with :attr:`styles_list`. Defaults to ``"vim"``.
    language
        Specifies the programming language the given code was written in. If ``None``
        (the default), the language will be automatically detected. For the list of
        possible options, visit https://pygments.org/docs/lexers/ and look for
        'aliases or short names'.
    generate_html_file
        Defines whether to generate highlighted html code to the folder `assets/codes/generated_html_files`. Defaults to `False`.
    warn_missing_font
        If True (default), Manim will issue a warning if the font does not exist in the
        (case-sensitive) list of fonts returned from `manimpango.list_fonts()`.

    Attributes
    ----------
    background_mobject : :class:`~.VGroup`
        The background of the code listing.
    line_numbers : :class:`~.Paragraph`
        The line numbers for the code listing. Empty, if
        ``insert_line_no=False`` has been specified.
    code : :class:`~.Paragraph`
        The highlighted code.

    """

    # tuples in the form (name, aliases, filetypes, mimetypes)
    # 'language' is aliases or short names
    # For more information about pygments.lexers visit https://pygments.org/docs/lexers/
    # from pygments.lexers import get_all_lexers
    # all_lexers = get_all_lexers()
    styles_list = list(get_all_styles())
    # For more information about pygments.styles visit https://pygments.org/docs/styles/

    def __init__(
        self,
        code: str | None = None,
        code_file_path: str | PathLike | None = None,
        *,
        language: str | None = None,
        file_encoding: str | None = None,
        tab_width: int = 3,
        line_spacing: float = 0.3,
        font_size: float = 24,
        font: str = "Monospace",  # This should be in the font list on all platforms.
        stroke_width: float = 0,
        margin: float = 0.3,
        indentation_chars: str = "    ",  # TODO: Should this instead be tabsize?
        background: str = "rectangle",  # or window
        background_stroke_width: float = 1,
        background_stroke_color: str = WHITE,
        corner_radius: float = 0.2,
        insert_line_no: bool = True,
        line_no_from: int = 1,
        line_no_buff: float = 0.4,
        style: str = "vim",
        generate_html_file: bool = False,
        warn_missing_font: bool = True,
        **kwargs,
    ):
        super().__init__(
            stroke_width=stroke_width,
            **kwargs,
        )
        self.background_stroke_color = background_stroke_color
        self.background_stroke_width = background_stroke_width
        self.tab_width = tab_width
        self.line_spacing = line_spacing
        self.warn_missing_font = warn_missing_font
        self.font = font
        self.font_size = font_size
        self.margin = margin
        self.indentation_chars = indentation_chars
        self.background = background
        self.corner_radius = corner_radius
        self.insert_line_no = insert_line_no
        self.line_no_from = line_no_from
        self.line_no_buff = line_no_buff
        self.style = style.lower() if style else None
        self.language = language
        self.generate_html_file = generate_html_file

        if code and code_file_path:
            # TODO: Is this the right kind of error?
            raise ValueError("Both 'code' and 'code_file_path' arguments cannot be set")

        if code:
            self.code_string = code
        elif code_file_path:
            self.code_string = self._read_code_file(code_file_path, encoding="utf-8")
        else:
            raise ValueError("Either 'code' or 'code_file_path' arguments must be set")

        """ self._gen_html_string()
        strati = self.html_string.find("background:")
        self.background_color = self.html_string[strati + 12 : strati + 19]
        self._gen_code_json()

        self.code = self._gen_colored_lines()
        if self.insert_line_no:
            self.line_numbers = self._gen_line_numbers()
            self.line_numbers.next_to(self.code, direction=LEFT, buff=self.line_no_buff)
        if self.background == "rectangle":
            if self.insert_line_no:
                foreground = VGroup(self.code, self.line_numbers)
            else:
                foreground = self.code
            rect = SurroundingRectangle(
                foreground,
                buff=self.margin,
                color=self.background_color,
                fill_color=self.background_color,
                stroke_width=self.background_stroke_width,
                stroke_color=self.background_stroke_color,
                fill_opacity=1,
            )
            rect.round_corners(self.corner_radius)
            self.background_mobject = rect
        else:
            if self.insert_line_no:
                foreground = VGroup(self.code, self.line_numbers)
            else:
                foreground = self.code
            height = foreground.height + 0.1 * 3 + 2 * self.margin
            width = foreground.width + 0.1 * 3 + 2 * self.margin

            rect = RoundedRectangle(
                corner_radius=self.corner_radius,
                height=height,
                width=width,
                stroke_width=self.background_stroke_width,
                stroke_color=self.background_stroke_color,
                color=self.background_color,
                fill_opacity=1,
            )
            red_button = Dot(radius=0.1, stroke_width=0, color="#ff5f56")
            red_button.shift(LEFT * 0.1 * 3)
            yellow_button = Dot(radius=0.1, stroke_width=0, color="#ffbd2e")
            green_button = Dot(radius=0.1, stroke_width=0, color="#27c93f")
            green_button.shift(RIGHT * 0.1 * 3)
            buttons = VGroup(red_button, yellow_button, green_button)
            buttons.shift(
                UP * (height / 2 - 0.1 * 2 - 0.05)
                + LEFT * (width / 2 - 0.1 * 5 - self.corner_radius / 2 - 0.05),
            )

            self.background_mobject = VGroup(rect, buttons)
            x = (height - foreground.height) / 2 - 0.1 * 3
            self.background_mobject.shift(foreground.get_center())
            self.background_mobject.shift(UP * x)
        if self.insert_line_no:
            super().__init__(
                self.background_mobject, self.line_numbers, self.code, **kwargs
            )
        else:
            super().__init__(
                self.background_mobject,
                Dot(fill_opacity=0, stroke_opacity=0),
                self.code,
                **kwargs,
            )
        self.move_to(np.array([0, 0, 0])) """

    def _read_code_file(
        self,
        file_path: str | PathLike,
        *,
        encoding: str | None = None,
    ) -> str:
        """Function to validate file."""
        if file_path is None:
            raise ValueError("Name of file cannot be None")

        file_path = Path(file_path).resolve(strict=True)
        if not file_path.is_file():
            raise IsADirectoryError(f"The provided path '{file_path}' is not a file")

        # Note on valid encodings: https://docs.python.org/3/library/codecs.html#standard-encodings
        return file_path.read_text(encoding=encoding)

    """ def _gen_line_numbers(self):
        \"""Function to generate line_numbers.

        Returns
        -------
        :class:`~.Paragraph`
            The generated line_numbers according to parameters.
        \"""
        line_numbers_array = []
        for line_no in range(0, self.code_json.__len__()):
            number = str(self.line_no_from + line_no)
            line_numbers_array.append(number)
        line_numbers = Paragraph(
            *list(line_numbers_array),
            line_spacing=self.line_spacing,
            alignment="right",
            font_size=self.font_size,
            font=self.font,
            disable_ligatures=True,
            stroke_width=self.stroke_width,
            warn_missing_font=self.warn_missing_font,
        )
        for i in line_numbers:
            i.set_color(self.default_color)
        return line_numbers """
