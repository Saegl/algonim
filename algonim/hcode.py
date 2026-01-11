import pyglet
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatter import Formatter
from pygments.styles import get_style_by_name
from pygments.token import Token

from algonim.primitives.arrow import Arrow
from algonim.easing import cubic_ease_in_out
from algonim.script import ActionFn, defer, move_to


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
        self.styles = {token: style for token, style in style}
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


code = """
def hello_world():
    print("Hello, world!")
"""


class HighlightedCode:
    def __init__(self, code: str, x, y, font_size: int):
        self.font_size = font_size
        formatter = PygletFormatter(style="monokai")
        lexer = PythonLexer()
        highlight(code, lexer, formatter)  # This populates formatter.output

        document = pyglet.text.document.FormattedDocument()
        for value, rgba in formatter.output:
            document.insert_text(
                len(document.text),
                value,
                {
                    "color": rgba,
                    "font_size": font_size,
                    "font_name": "FiraCode Nerd Font Mono",
                },
            )

        self.layout = pyglet.text.layout.TextLayout(
            document, multiline=True, wrap_lines=False
        )
        self.layout.x = x
        self.layout.y = y
        self.layout.width = self.layout.content_width
        self.layout.height = self.layout.content_height
        # self.cursor = pyglet.shapes.Circle(x, y, 20)
        self.cursor = Arrow(
            pyglet.graphics.Batch(), x - 150, y, x - 100, y, head_length=25, width=3
        )

        n_lines = len(self.layout._get_lines())
        numbers = pyglet.text.document.FormattedDocument()
        for i in range(1, n_lines):
            digits = str(i)
            prefix = " " if len(digits) == 1 else ""
            numbers.insert_text(
                len(numbers.text),
                prefix + str(i) + ("\n" if i < n_lines - 1 else ""),
                {
                    "color": [255, 255, 255, 255],
                    "font_size": font_size,
                    "font_name": "FiraCode Nerd Font Mono",
                },
            )
        self.numbers = pyglet.text.layout.TextLayout(
            numbers, multiline=True, wrap_lines=False
        )
        self.numbers.y = self.layout.top - self.numbers.content_height
        self.numbers.x = self.layout.x - 80
        # self.cursor.x = self.layout.x - 120
        # self.numbers.y = self.layout.y

        self.line = pyglet.shapes.Line(
            self.numbers.x + 60,
            self.numbers.y,
            self.numbers.x + 60,
            self.numbers.y + self.numbers.content_height,
            width=3,
        )

    def hl(self, lineno: int, line) -> ActionFn:
        def make():
            line_y = self.layout._get_lines()[lineno].y
            final_y = line_y + self.layout.y + self.layout.content_height + 60

            return move_to(self.cursor, self.cursor.x, final_y, 0.5, cubic_ease_in_out)

        return defer(make)

    def draw(self):
        self.layout.draw()
        self.cursor.draw()
        self.numbers.draw()
        self.line.draw()


if __name__ == "__main__":
    window = pyglet.window.Window(800, 600, "Pygments in Pyglet")
    hcode = HighlightedCode(code, 0, 0, 32)

    @window.event
    def on_draw():
        window.clear()
        hcode.draw()

    pyglet.app.run()
