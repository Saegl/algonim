import pyglet
from pyglet import shapes

from algonim.colors import ACCENT, DIM, SURFACE, WHITE, Color, lerp_color, scale_alpha
from algonim.script import Anim, Script, seq, set_to, tween

OFF_TEXT = DIM
ON_TEXT = WHITE


class Flag:
    def __init__(
        self,
        script: Script,
        x,
        y,
        name: str,
        font_size: float = 24,
        on_color: Color = ACCENT,
    ):
        """Pill for a boolean variable, (x, y) is its center: dim when false,
        filled with `on_color` when true"""
        self.resolution = res = script.resolution
        self.on_color = on_color
        self.label = pyglet.text.Label(
            name,
            font_size=res.length(font_size),
            bold=True,
            anchor_x="center",
            anchor_y="center",
            x=res.length(x),
            y=res.length(y),
        )
        width = self.label.content_width / res.scale + font_size * 1.6
        height = font_size * 2
        self.pill = shapes.RoundedRectangle(
            res.length(x - width / 2),
            res.length(y - height / 2),
            res.length(width),
            res.length(height),
            res.length(height / 2),
        )
        self._on = 0.0
        self._alpha = 0.0
        self.on = script.prop(0.0, self.set_on)
        self.alpha = script.prop(0.0, self.set_alpha)
        script.register(self)

    def set(self, value: bool, duration: float = 0.3) -> Anim:
        """Switch to the value, the first call fades the flag in with it"""
        target = 1.0 if value else 0.0
        if self.alpha.value == 0:
            return seq(set_to(self.on, target), tween(self.alpha, 255, duration))
        return tween(self.on, target, duration)

    def update_colors(self):
        fill = lerp_color(SURFACE, self.on_color, self._on)
        text = lerp_color(OFF_TEXT, ON_TEXT, self._on)
        self.pill.color = scale_alpha(fill, self._alpha)
        self.label.color = scale_alpha(text, self._alpha)

    def set_on(self, on):
        self._on = on
        self.update_colors()

    def set_alpha(self, alpha):
        self._alpha = alpha
        self.update_colors()

    def draw(self):
        self.pill.draw()
        self.label.draw()
