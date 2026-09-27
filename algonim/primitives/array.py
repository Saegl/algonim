import pyglet
from pyglet import shapes

from algonim.colors import WHITE, replace_alpha
from algonim.script import Script


class Array:
    def __init__(
        self,
        script: Script,
        x,
        y,
        data: list[int],
        entry_size: float = 80,
        thickness: float = 4.0,
        font_size: float = 30,
    ):
        self.resolution = script.resolution
        self.data = data
        self.entry_size = entry_size
        self.thickness = thickness

        n = len(data)
        width = n * entry_size
        half = thickness / 2

        # Segments relative to the bottom left corner, horizontal borders
        # stick out to fill the corners
        self.segments = [
            (-half, 0, width + half, 0),
            (-half, entry_size, width + half, entry_size),
        ] + [(entry_size * i, 0, entry_size * i, entry_size) for i in range(n + 1)]
        self.lines = [
            shapes.Line(
                0, 0, 0, 0, width=self.resolution.length(thickness), color=WHITE
            )
            for _ in self.segments
        ]
        self.entries = [
            pyglet.text.Label(
                str(number),
                font_size=self.resolution.length(font_size),
                anchor_x="center",
                anchor_y="center",
            )
            for number in data
        ]

        self._x = x
        self._y = y
        self.x = script.prop(x, self.set_x)
        self.y = script.prop(y, self.set_y)
        self.alpha = script.prop(0.0, self.set_alpha)
        script.register(self)

    def layout(self):
        res = self.resolution
        left = self._x - len(self.data) * self.entry_size / 2
        bottom = self._y - self.entry_size / 2

        for line, (x1, y1, x2, y2) in zip(self.lines, self.segments, strict=True):
            line.position = (res.length(left + x1), res.length(bottom + y1))
            line.x2 = res.length(left + x2)
            line.y2 = res.length(bottom + y2)

        for i, entry in enumerate(self.entries):
            entry.position = (
                res.length(left + self.entry_size * (i + 0.5)),
                res.length(self._y),
                0,
            )

    def draw(self):
        for line in self.lines:
            line.draw()

        for entry in self.entries:
            entry.draw()

    def set_x(self, x):
        self._x = x
        self.layout()

    def set_y(self, y):
        self._y = y
        self.layout()

    def set_color(self, color):
        for line in self.lines:
            line.color = color

        for entry in self.entries:
            entry.color = color

    def set_alpha(self, alpha):
        self.set_color(replace_alpha(WHITE, int(alpha)))
