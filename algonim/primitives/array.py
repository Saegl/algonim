import math

import pyglet
from pyglet import shapes

from algonim.colors import DIM, SURFACE, WHITE, Color, scale_alpha
from algonim.easing import ease_in_out_cubic, lerp
from algonim.script import (
    Anim,
    Prop,
    Script,
    frames,
    par,
    seq,
    set_to,
    tween,
    tween_color,
)

type Point = tuple[float, float]


class Array:
    def __init__(
        self,
        script: Script,
        x,
        y,
        data: list[int],
        cell_size: float = 80,
        gap: float = 12,
        font_size: float = 30,
        indexes: bool = True,
    ):
        """Row of rounded cells, (x, y) is its center. Index labels sit under
        the cells, `Pointer`s can point at cells from further below."""
        self.resolution = res = script.resolution
        self.data = list(data)
        self.cell_size = cell_size
        self.gap = gap
        self.show_indexes = indexes

        self.cells = [
            shapes.RoundedRectangle(
                0, 0, res.length(cell_size), res.length(cell_size), res.length(12)
            )
            for _ in data
        ]
        self.values = [
            pyglet.text.Label(
                str(value),
                font_size=res.length(font_size),
                bold=True,
                anchor_x="center",
                anchor_y="center",
            )
            for value in data
        ]
        self.indexes = [
            pyglet.text.Label(
                str(i),
                font_size=res.length(font_size * 0.6),
                anchor_x="center",
                anchor_y="center",
            )
            for i in range(len(data))
        ]
        # Label shown in each cell, while the script is written
        self.slot = list(range(len(data)))

        self._x = x
        self._y = y
        self._alpha = 0.0
        self._fills = [SURFACE] * len(data)
        self._positions = [(self.cell_x(i), 0.0) for i in range(len(data))]

        self.x = script.prop(x, self.set_x)
        self.y = script.prop(y, self.set_y)
        self.alpha = script.prop(0.0, self.set_alpha)
        self.fills: list[Prop[Color]] = [
            script.prop(SURFACE, self._fill_setter(i)) for i in range(len(data))
        ]
        # Value label positions relative to the array center
        self.positions: list[Prop[Point]] = [
            script.prop(self._positions[i], self._position_setter(i))
            for i in range(len(data))
        ]
        script.register(self)

    @property
    def width(self) -> float:
        n = len(self.data)
        return n * self.cell_size + (n - 1) * self.gap

    def cell_x(self, i: float) -> float:
        """Center of cell `i` relative to the array center, fractional
        indexes lie between cells"""
        return -self.width / 2 + self.cell_size / 2 + i * (self.cell_size + self.gap)

    def swap(self, a: int, b: int, duration: float = 0.6) -> Anim:
        """Values trade cells, one arcing over the row and one dipping under it"""
        label_a, label_b = self.slot[a], self.slot[b]
        self.slot[a], self.slot[b] = label_b, label_a
        self.data[a], self.data[b] = self.data[b], self.data[a]
        height = self.cell_size * 0.9
        return par(
            _arc(self.positions[label_a], self.cell_x(b), height, duration),
            _arc(self.positions[label_b], self.cell_x(a), -height / 4, duration),
        )

    def update(self, data: list[int], duration: float = 0.6) -> Anim:
        """Animate to new data, a swap of two values moves them, other changes
        are not supported yet"""
        changed = [i for i in range(len(data)) if self.data[i] != data[i]]
        if not changed:
            return seq()
        if len(changed) == 2:
            a, b = changed
            if (self.data[a], self.data[b]) == (data[b], data[a]):
                return self.swap(a, b, duration)
        raise NotImplementedError(f"Array update {self.data} -> {data}")

    def color(self, i: int, color: Color, duration: float = 0.25) -> Anim:
        if self.fills[i].value == color:
            return seq()
        return tween_color(self.fills[i], color, duration)

    def layout(self):
        res = self.resolution
        half = self.cell_size / 2
        for i, cell in enumerate(self.cells):
            cell.position = (
                res.length(self._x + self.cell_x(i) - half),
                res.length(self._y - half),
            )
        for label, (dx, dy) in zip(self.values, self._positions, strict=True):
            label.position = (res.length(self._x + dx), res.length(self._y + dy), 0)
        for i, label in enumerate(self.indexes):
            label.position = (
                res.length(self._x + self.cell_x(i)),
                res.length(self._y - half - self.cell_size * 0.28),
                0,
            )

    def update_colors(self):
        for cell, fill in zip(self.cells, self._fills, strict=True):
            cell.color = scale_alpha(fill, self._alpha)
        for label in self.values:
            label.color = scale_alpha(WHITE, self._alpha)
        for label in self.indexes:
            label.color = scale_alpha(DIM, self._alpha)

    def _fill_setter(self, i: int):
        def set_fill(color: Color):
            self._fills[i] = color
            self.update_colors()

        return set_fill

    def _position_setter(self, i: int):
        def set_position(position: Point):
            self._positions[i] = position
            self.layout()

        return set_position

    def set_x(self, x):
        self._x = x
        self.layout()

    def set_y(self, y):
        self._y = y
        self.layout()

    def set_alpha(self, alpha):
        self._alpha = alpha
        self.update_colors()

    def draw(self):
        for cell in self.cells:
            cell.draw()
        for label in self.values:
            label.draw()
        if self.show_indexes:
            for label in self.indexes:
                label.draw()


def _arc(position: Prop[Point], end_x: float, height: float, duration: float) -> Anim:
    start_x, y = position.value
    n = frames(duration)
    for i in range(1, n + 1):
        yield
        t = ease_in_out_cubic(i / n)
        position.value = (lerp(start_x, end_x, t), y + height * math.sin(math.pi * t))
    position.value = (end_x, y)


class Pointer:
    def __init__(
        self,
        script: Script,
        array: Array,
        name: str,
        row: int = 0,
        color: Color = WHITE,
        font_size: float = 24,
    ):
        """Caret with a variable name under an array's index labels, rows
        stack pointers so they never overlap"""
        self.resolution = res = script.resolution
        self.array = array
        self.color = color
        self.row_offset = row * font_size * 2.5
        self.caret = shapes.Triangle(0, 0, 0, 0, 0, 0)
        self.label = pyglet.text.Label(
            name,
            font_size=res.length(font_size),
            bold=True,
            anchor_x="center",
            anchor_y="top",
        )
        self.font_size = font_size
        self._index = 0.0
        self._alpha = 0.0
        self.index = script.prop(0.0, self.set_index)
        self.alpha = script.prop(0.0, self.set_alpha)
        script.register(self)

    def point_to(self, i: int, duration: float = 0.35) -> Anim:
        """Move to cell `i`, the first call fades the pointer in there"""
        if self.alpha.value == 0:
            return seq(set_to(self.index, float(i)), tween(self.alpha, 255, duration))
        return tween(self.index, float(i), duration, ease_in_out_cubic)

    def layout(self):
        res = self.resolution
        array = self.array
        x = array._x + array.cell_x(self._index)
        tip = array._y - array.cell_size / 2 - array.cell_size * 0.52 - self.row_offset
        size = self.font_size * 0.45
        self.caret.x, self.caret.y = res.length(x), res.length(tip)
        self.caret.x2, self.caret.y2 = res.length(x - size), res.length(tip - size)
        self.caret.x3, self.caret.y3 = res.length(x + size), res.length(tip - size)
        self.label.position = (res.length(x), res.length(tip - size * 1.3), 0)

    def set_index(self, index):
        self._index = index
        self.layout()

    def set_alpha(self, alpha):
        self._alpha = alpha
        self.caret.color = scale_alpha(self.color, alpha)
        self.label.color = scale_alpha(self.color, alpha)

    def draw(self):
        # The array may have moved since the last seek
        self.layout()
        self.caret.draw()
        self.label.draw()
