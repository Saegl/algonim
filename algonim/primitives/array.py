import pyglet
from pyglet import shapes

from algonim.colors import TRANSPARENT, WHITE, replace_alpha


class Array:
    def __init__(self, x, y, data: list[int], thickness: float = 5.0):
        self.x = x
        self.y = y
        self.time = 0

        n = len(data)
        self.data = data
        self.entry_size = 100
        self.thickness = thickness

        width = n * self.entry_size
        height = self.entry_size

        left_bottom_x = x - width / 2
        left_bottom_y = y - height / 2

        self.left_border = shapes.Line(
            x=left_bottom_x,
            y=left_bottom_y,
            x2=left_bottom_x,
            y2=left_bottom_y + self.entry_size,
            width=thickness,
            color=WHITE,
        )
        self.right_border = shapes.Line(
            x=left_bottom_x + self.entry_size * n,
            y=left_bottom_y,
            x2=left_bottom_x + self.entry_size * n,
            y2=left_bottom_y + self.entry_size,
            width=thickness,
            color=WHITE,
        )
        self.bottom_border = shapes.Line(
            x=left_bottom_x - thickness / 2,
            y=left_bottom_y,
            x2=left_bottom_x + self.entry_size * n + thickness / 2,
            y2=left_bottom_y,
            width=thickness,
            color=WHITE,
        )
        self.top_border = shapes.Line(
            x=left_bottom_x - thickness / 2,
            y=left_bottom_y + self.entry_size,
            x2=left_bottom_x + self.entry_size * n + thickness / 2,
            y2=left_bottom_y + self.entry_size,
            width=thickness,
            color=WHITE,
        )
        self.inside_lines = []
        for i in range(n - 1):
            self.inside_lines.append(
                shapes.Line(
                    x=left_bottom_x + self.entry_size * (i + 1),
                    y=left_bottom_y,
                    x2=left_bottom_x + self.entry_size * (i + 1),
                    y2=left_bottom_y + self.entry_size,
                    width=thickness,
                    color=WHITE,
                )
            )

        self.entries = []
        for i, number in enumerate(data):
            self.entries.append(
                pyglet.text.Label(
                    str(number),
                    font_size=36,
                    x=left_bottom_x + self.entry_size / 2 + self.entry_size * i,
                    y=y,
                    anchor_x="center",
                    anchor_y="center",
                )
            )
        self.set_color(TRANSPARENT)

    def draw(self):
        self.left_border.draw()
        self.right_border.draw()
        self.bottom_border.draw()
        self.top_border.draw()
        for line in self.inside_lines:
            line.draw()

        for entry in self.entries:
            entry.draw()

    def move_x(self, dx):
        self.x += dx
        self.left_border.x += dx
        self.right_border.x += dx
        self.bottom_border.x += dx
        self.top_border.x += dx
        for line in self.inside_lines:
            line.x += dx

        for entry in self.entries:
            entry.x += dx

    def move_y(self, dy):
        self.y += dy
        self.left_border.y += dy
        self.right_border.y += dy
        self.bottom_border.y += dy
        self.top_border.y += dy
        for line in self.inside_lines:
            line.y += dy

        for entry in self.entries:
            entry.y += dy

    def set_x(self, x):
        delta_x = x - self.x
        self.move_x(delta_x)

    def set_y(self, y):
        delta_y = y - self.y
        self.move_y(delta_y)

    def set_color(self, color):
        self.left_border.color = color
        self.right_border.color = color
        self.bottom_border.color = color
        self.top_border.color = color
        for line in self.inside_lines:
            line.color = color

        for entry in self.entries:
            entry.color = color

    def set_alpha(self, alpha):
        color = replace_alpha(self.left_border.color, alpha)

        self.left_border.color = color
        self.right_border.color = color
        self.bottom_border.color = color
        self.top_border.color = color
        for line in self.inside_lines:
            line.color = color

        for entry in self.entries:
            entry.color = color
