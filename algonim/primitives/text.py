import pyglet
from pyglet.customtypes import AnchorX, AnchorY

from algonim.colors import WHITE, replace_alpha
from algonim.script import Script


class Text:
    def __init__(
        self,
        script: Script,
        x,
        y,
        text: str,
        font_size: float = 27,
        bold=False,
        color=WHITE,
        anchor_x: AnchorX = "center",
        anchor_y: AnchorY = "center",
    ):
        self.resolution = script.resolution
        self.label = pyglet.text.Label(
            text,
            anchor_x=anchor_x,
            anchor_y=anchor_y,
            font_size=self.resolution.length(font_size),
            bold=bold,
        )
        self.label.color = color
        self.x = script.track(x, self.set_x)
        self.y = script.track(y, self.set_y)
        self.alpha = script.track(0.0, self.set_alpha)
        script.register(self)

    def set_alpha(self, alpha):
        self.label.color = replace_alpha(self.label.color, int(alpha))

    def set_x(self, x):
        self.label.x = self.resolution.pixel(x)

    def set_y(self, y):
        self.label.y = self.resolution.pixel(y)

    def draw(self):
        self.label.draw()
