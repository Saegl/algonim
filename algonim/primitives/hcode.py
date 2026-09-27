import pyglet
from pygments import highlight
from pygments.formatter import Formatter
from pygments.lexers import PythonLexer
from pygments.styles import get_style_by_name
from pygments.token import Token

from algonim.easing import ease_in_out_cubic
from algonim.primitives.arrow import Arrow
from algonim.script import Anim, Script, tween

FONT_NAME = "FiraCode Nerd Font Mono"


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
        """Code block with line numbers, (x, y) is its top left corner"""
        res = script.resolution
        self.x = x
        self.y = y
        self.line_height = line_height or font_size * 1.65
        self.batch = pyglet.graphics.Batch()

        formatter = PygletFormatter(style="monokai")
        highlight(code, PythonLexer(), formatter)  # This populates formatter.output
        lines = split_lines(formatter.output)

        # Lines are separate layouts: multiline layouts snap line height to
        # whole pixels, so lower lines drift between resolutions
        style = {"font_size": res.length(font_size), "font_name": FONT_NAME}
        self.layouts = []
        for i, tokens in enumerate(lines):
            document = pyglet.text.document.FormattedDocument()
            for value, rgba in tokens:
                document.insert_text(
                    len(document.text), value, {**style, "color": rgba}
                )

            number = pyglet.text.document.FormattedDocument()
            number.insert_text(0, str(i + 1), {**style, "color": (255, 255, 255, 255)})

            center_y = res.length(self.line_center(i + 1))
            self.layouts += [
                pyglet.text.layout.TextLayout(
                    document,
                    x=res.length(x),
                    y=center_y,
                    anchor_y="center",
                    batch=self.batch,
                ),
                pyglet.text.layout.TextLayout(
                    number,
                    x=res.length(x - 25),
                    y=center_y,
                    anchor_x="right",
                    anchor_y="center",
                    batch=self.batch,
                ),
            ]

        self.line = pyglet.shapes.Line(
            res.length(x - 15),
            res.length(y),
            res.length(x - 15),
            res.length(y - len(lines) * self.line_height),
            width=res.length(2.5),
            batch=self.batch,
        )
        cursor_y = self.line_center(1)
        self.cursor = Arrow(
            res, x - 125, cursor_y, x - 85, cursor_y, head_length=20, width=2.5
        )
        self.cursor_y = script.prop(cursor_y, self.cursor.set_y)
        script.register(self)

    def line_center(self, lineno: int) -> float:
        return self.y - (lineno - 0.5) * self.line_height

    def hl(self, lineno: int, line) -> Anim:
        return tween(self.cursor_y, self.line_center(lineno), 0.5, ease_in_out_cubic)

    def draw(self):
        self.batch.draw()
        self.cursor.draw()
