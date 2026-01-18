import pyglet
from pyglet.customtypes import AnchorX, AnchorY

from algonim.colors import WHITE, Color, replace_alpha
from algonim.script import Script


class Text:
    def __init__(
        self,
        script: Script,
        x,
        y,
        text: str,
        font_size: int = 32,
        bold=False,
        color=WHITE,
        anchor_x: AnchorX = "center",
        anchor_y: AnchorY = "center",
    ):
        self.x = x
        self.y = y
        self.label = pyglet.text.Label(
            text,
            x,
            y,
            anchor_x=anchor_x,
            anchor_y=anchor_y,
            font_size=font_size,
            bold=bold,
        )
        self.label.color = color
        self.set_alpha(0)
        script.register(self)

    def set_color(self, color: Color):
        self.label.color = color

    def set_alpha(self, alpha):
        self.label.color = replace_alpha(self.label.color, alpha)

    def set_x(self, x):
        self.x = x
        self.label.x = x

    def set_y(self, y):
        self.y = y
        self.label.y = y

    def draw(self):
        self.label.draw()
