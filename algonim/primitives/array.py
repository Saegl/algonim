import math

import pyglet
from pyglet import shapes

from algonim.colors import DIM, SURFACE, WHITE, Color, scale_alpha
from algonim.easing import ease_in_out_cubic, lerp
from algonim.primitives.text import ink_bounds, ink_middle
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
        self.pointers: list[Pointer] = []

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
                anchor_y="baseline",
            )
            for value in data
        ]
        self.indexes = [
            pyglet.text.Label(
                str(i),
                font_size=res.length(font_size * 0.6),
                anchor_x="center",
                anchor_y="baseline",
            )
            for i in range(len(data))
        ]
        # Digits share their ink bounds, so one offset centers every label
        self.value_middle = ink_middle(self.values[0], "0123456789") / res.scale
        index_bottom, index_top = ink_bounds(self.indexes[0], "0123456789")
        self.index_y = -cell_size / 2 - font_size * 0.75
        self.index_baseline = self.index_y - (index_bottom + index_top) / 2 / res.scale
        self.index_bottom = self.index_baseline + index_bottom / res.scale
        # Cell shown at each index, while the script is written
        self.slot = list(range(len(data)))

        self._x = x
        self._y = y
        self._alpha = 0.0
        self._fills = [SURFACE] * len(data)
        self._positions = [(self.cell_x(i), 0.0) for i in range(len(data))]

        self.x = script.prop(x, self.set_x)
        self.y = script.prop(y, self.set_y)
        self.alpha = script.prop(0.0, self.set_alpha)
        # Fills and positions belong to cells, which travel between indexes
        self.fills: list[Prop[Color]] = [
            script.prop(SURFACE, self._fill_setter(i)) for i in range(len(data))
        ]
        # Cell centers relative to the array center
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
        """Cells trade places, one arcing over the other as it slides along"""
        cell_a, cell_b = self.slot[a], self.slot[b]
        self.slot[a], self.slot[b] = cell_b, cell_a
        self.data[a], self.data[b] = self.data[b], self.data[a]
        # Clears the sliding cell, so they never overlap
        height = self.cell_size + self.gap
        return par(
            _arc(self.positions[cell_a], self.cell_x(b), height, duration),
            _arc(self.positions[cell_b], self.cell_x(a), 0, duration),
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
        """Fill the cell at index `i`"""
        fill = self.fills[self.slot[i]]
        if fill.value == color:
            return seq()
        return tween_color(fill, color, duration)

    def layout(self):
        res = self.resolution
        half = self.cell_size / 2
        for cell, label, (dx, dy) in zip(
            self.cells, self.values, self._positions, strict=True
        ):
            x, y = self._x + dx, self._y + dy
            cell.position = (res.length(x - half), res.length(y - half))
            label.position = (res.length(x), res.length(y - self.value_middle), 0)
        for i, label in enumerate(self.indexes):
            label.position = (
                res.length(self._x + self.cell_x(i)),
                res.length(self._y + self.index_baseline),
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
        if self.show_indexes:
            for label in self.indexes:
                label.draw()
        # Lifted cells pass over the others
        for i in sorted(range(len(self.cells)), key=lambda i: self._positions[i][1]):
            self.cells[i].draw()
            self.values[i].draw()


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
        color: Color = WHITE,
        font_size: float = 24,
    ):
        """Caret with a variable name under an array's index labels. Pointers
        at the same cell stack, later ones below"""
        self.resolution = res = script.resolution
        self.array = array
        self.color = color
        self.caret = shapes.Triangle(0, 0, 0, 0, 0, 0)
        self.label = pyglet.text.Label(
            name,
            font_size=res.length(font_size),
            bold=True,
            anchor_x="center",
            anchor_y="baseline",
        )
        self.caret_size = font_size * 0.4
        # From the caret base down to the baseline, and down to the next row
        _, top = ink_bounds(self.label, "ij")
        bottom, _ = ink_bounds(self.label, "gj")
        self.label_drop = font_size * 0.35 + top / res.scale
        self.row_height = (
            self.caret_size + self.label_drop - bottom / res.scale + font_size * 0.5
        )
        self._index = 0.0
        self._alpha = 0.0
        self.index = script.prop(0.0, self.set_index)
        self.alpha = script.prop(0.0, self.set_alpha)
        array.pointers.append(self)
        script.register(self)

    def point_to(self, i: int, duration: float = 0.35) -> Anim:
        """Move to cell `i`, the first call fades the pointer in there"""
        if self.alpha.value == 0:
            return seq(set_to(self.index, float(i)), tween(self.alpha, 255, duration))
        return tween(self.index, float(i), duration, ease_in_out_cubic)

    def depth(self) -> float:
        """Rows of visible pointers before this one that share its cell,
        partially while they slide past each other"""
        depth = 0.0
        for other in self.array.pointers:
            if other is self:
                break
            overlap = max(0.0, 1 - abs(other._index - self._index))
            depth += overlap * other._alpha / 255
        return depth

    def layout(self):
        res = self.resolution
        array = self.array
        x = array._x + array.cell_x(self._index)
        tip = (
            array._y
            + array.index_bottom
            - self.caret_size * 1.4
            - self.depth() * self.row_height
        )
        base = tip - self.caret_size
        self.caret.x, self.caret.y = res.length(x), res.length(tip)
        self.caret.x2, self.caret.y2 = res.length(x - self.caret_size), res.length(base)
        self.caret.x3, self.caret.y3 = res.length(x + self.caret_size), res.length(base)
        self.label.position = (res.length(x), res.length(base - self.label_drop), 0)

    def set_index(self, index):
        self._index = index
        self.layout()

    def set_alpha(self, alpha):
        self._alpha = alpha
        self.caret.color = scale_alpha(self.color, alpha)
        self.label.color = scale_alpha(self.color, alpha)

    def draw(self):
        # The array and the other pointers may have moved since the last seek
        self.layout()
        self.caret.draw()
        self.label.draw()
