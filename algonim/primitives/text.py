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
        self.x = script.prop(x, self.set_x)
        self.y = script.prop(y, self.set_y)
        self.alpha = script.prop(0.0, self.set_alpha)
        script.register(self)

    def set_alpha(self, alpha):
        self.label.color = replace_alpha(self.label.color, int(alpha))

    def set_x(self, x):
        self.label.x = self.resolution.length(x)

    def set_y(self, y):
        self.label.y = self.resolution.length(y)

    def draw(self):
        self.label.draw()


def ink_bounds(
    label: pyglet.text.Label, text: str | None = None
) -> tuple[float, float]:
    """Bottom and top of the glyphs of `text` (default the label's) relative
    to the baseline, in pixels. Font ascent and descent include blank space,
    so anchoring on them centers text visibly off"""
    font = label.document.get_font(0)
    glyphs = font.get_glyphs(text or label.text)
    return min(g.vertices[1] for g in glyphs), max(g.vertices[3] for g in glyphs)


def ink_middle(label: pyglet.text.Label, text: str | None = None) -> float:
    """Height of the glyphs' visual center above the baseline, in pixels"""
    bottom, top = ink_bounds(label, text)
    return (bottom + top) / 2
