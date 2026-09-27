import pyglet
from pygments import highlight
from pygments.formatter import Formatter
from pygments.lexers import PythonLexer
from pygments.styles import get_style_by_name
from pygments.token import Token

from algonim.colors import CURSOR, Color, scale_alpha
from algonim.easing import ease_in_out_cubic
from algonim.resolution import Resolution
from algonim.script import Anim, Script, par, seq, set_to, tween

# First installed font wins
FONT_NAME = ("FiraCode Nerd Font Mono", "Fira Code", "DejaVu Sans Mono")


def hex_to_rgba(hex_color: str) -> tuple[int, int, int, int]:
    if hex_color.startswith("#"):
        hex_color = hex_color[1:]
    r = int(hex_color[:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return (r, g, b, 255)


class PygletFormatter(Formatter):
    def __init__(self, **options):
        super().__init__(**options)
        style = get_style_by_name(options.get("style", "monokai"))
        self.styles = dict(style)
        self.default_style = self.styles.get(Token.Text, {"color": "#000000"})

    def format(self, tokensource, outfile):
        self.output = []
        for token_type, value in tokensource:
            # Get color and convert to RGBA
            style = self.styles.get(token_type, self.default_style)
            color = style.get("color", "#000000")
            assert color
            rgba = hex_to_rgba(color)
            self.output.append((value, rgba))  # Store token and its RGBA color


def split_lines(tokens: list[tuple[str, tuple]]) -> list[list[tuple[str, tuple]]]:
    lines: list[list[tuple[str, tuple]]] = [[]]
    for value, rgba in tokens:
        for i, part in enumerate(value.split("\n")):
            if i > 0:
                lines.append([])
            if part:
                lines[-1].append((part, rgba))
    # Pygments always ends the code with a newline
    if not lines[-1]:
        lines.pop()
    return lines


def text_width(res: Resolution, text: str, font_size: float) -> float:
    """Virtual width of `text` in the code font"""
    label = pyglet.text.Label(
        text,
        font_name=FONT_NAME,  # type: ignore[arg-type]
        font_size=res.length(font_size),
    )
    return label.content_width / res.scale


class HighlightedCode:
    def __init__(
        self,
        script: Script,
        code: str,
        x: float,
        y: float,
        font_size: float = 23,
        line_height: float | None = None,
    ):
        """Syntax highlighted code block, (x, y) is its top left corner.

        A rounded cursor behind the executing line shows progress, `goto`
        moves it and trims it to the line's text, ignoring indentation.
        """
        self.resolution = res = script.resolution
        self.x = x
        self.y = y
        self.line_height = line_height or font_size * 1.65
        self.batch = pyglet.graphics.Batch()

        formatter = PygletFormatter(style="monokai")
        highlight(code, PythonLexer(), formatter)  # This populates formatter.output
        lines = split_lines(formatter.output)
        self.bounds = [self._text_bounds(line, font_size) for line in code.split("\n")]

        # Lines are separate layouts: multiline layouts snap line height to
        # whole pixels, so lower lines drift between resolutions
        style = {"font_size": res.length(font_size), "font_name": FONT_NAME}
        self.layouts = []
        # Colored ranges of each document, faded together by `alpha`
        self.token_ranges: list[
            tuple[pyglet.text.document.FormattedDocument, int, int, Color]
        ] = []
        for i, tokens in enumerate(lines):
            document = pyglet.text.document.FormattedDocument()
            for value, rgba in tokens:
                start = len(document.text)
                document.insert_text(start, value, {**style, "color": rgba})
                self.token_ranges.append((document, start, start + len(value), rgba))
            self.layouts.append(
                pyglet.text.layout.TextLayout(
                    document,
                    x=res.length(x),
                    y=res.length(self.line_center(i + 1)),
                    anchor_y="center",
                    batch=self.batch,
                )
            )

        self.pad_x = font_size * 0.45
        self.cursor = pyglet.shapes.RoundedRectangle(
            0, 0, 0, res.length(self.line_height * 0.92), res.length(font_size * 0.35)
        )
        self.cursor_x = script.prop(x, self.set_cursor_x)
        self.cursor_y = script.prop(self.line_center(1), self.set_cursor_y)
        self.cursor_width = script.prop(0.0, self.set_cursor_width)
        self.cursor_alpha = script.prop(0.0, self.set_cursor_alpha)
        self.alpha = script.prop(0.0, self.set_alpha)
        script.register(self)

    def _text_bounds(self, line: str, font_size: float) -> tuple[float, float]:
        """Left offset and width of the line's text without indentation"""
        text = line.strip()
        if not text:
            return 0, 0
        res = self.resolution
        width = text_width(res, text, font_size)
        indent = text_width(res, line.rstrip(), font_size) - width
        return indent, width

    def line_center(self, lineno: int) -> float:
        return self.y - (lineno - 0.5) * self.line_height

    def goto(self, lineno: int, duration: float = 0.35) -> Anim:
        """Move the cursor to the line, the first call fades it in there"""
        indent, width = self.bounds[lineno - 1]
        x = self.x + indent - self.pad_x
        y = self.line_center(lineno)
        width += 2 * self.pad_x

        if self.cursor_alpha.value == 0:
            return seq(
                set_to(self.cursor_x, x),
                set_to(self.cursor_y, y),
                set_to(self.cursor_width, width),
                tween(self.cursor_alpha, 255, duration),
            )
        return par(
            tween(self.cursor_x, x, duration, ease_in_out_cubic),
            tween(self.cursor_y, y, duration, ease_in_out_cubic),
            tween(self.cursor_width, width, duration, ease_in_out_cubic),
        )

    def set_cursor_x(self, x):
        self.cursor.x = self.resolution.length(x)

    def set_cursor_y(self, y):
        self.cursor.y = self.resolution.length(y - self.line_height * 0.46)

    def set_cursor_width(self, width):
        self.cursor.width = self.resolution.length(width)

    def set_cursor_alpha(self, alpha):
        self.cursor.color = scale_alpha(CURSOR, alpha)

    def set_alpha(self, alpha):
        for document, start, end, rgba in self.token_ranges:
            document.set_style(start, end, {"color": scale_alpha(rgba, alpha)})

    def draw(self):
        self.cursor.draw()
        self.batch.draw()
