import math

import pyglet

from algonim.resolution import Resolution


class Arrow:
    def __init__(
        self,
        resolution: Resolution,
        start_x,
        start_y,
        end_x,
        end_y,
        head_length=20,
        head_angle=30,
        color=(255, 255, 255),
        width=2,
    ):
        """
        Represents an arrow composed of three lines: the shaft and two head lines.

        Args:
            resolution (Resolution): Maps the virtual coordinates below to pixels.
            start_x, start_y (float): Starting coordinates of the arrow.
            end_x, end_y (float): Ending coordinates of the arrow (shaft end).
            head_length (float): Length of the arrowhead lines.
            head_angle (float): Angle between the shaft and arrowhead lines (degrees).
            color (tuple): RGB color of the arrow lines.
            width (float): Width of the arrow lines.
        """
        self.resolution = resolution
        self.batch = pyglet.graphics.Batch()
        self.x = start_x
        self.y = start_y

        # Segments relative to the start point
        dx = end_x - start_x
        dy = end_y - start_y
        angle = math.atan2(dy, dx)
        self.segments = [(0, 0, dx, dy)]
        for side in (1, -1):
            head_angle_rad = angle + side * math.radians(180 - head_angle)
            self.segments.append(
                (
                    dx,
                    dy,
                    dx + head_length * math.cos(head_angle_rad),
                    dy + head_length * math.sin(head_angle_rad),
                )
            )

        self.lines = [
            pyglet.shapes.Line(
                0,
                0,
                0,
                0,
                width=resolution.length(width),
                color=color,
                batch=self.batch,
            )
            for _ in self.segments
        ]
        self.layout()

    def layout(self):
        res = self.resolution
        for line, (x1, y1, x2, y2) in zip(self.lines, self.segments, strict=True):
            line.position = (res.length(self.x + x1), res.length(self.y + y1))
            line.x2 = res.length(self.x + x2)
            line.y2 = res.length(self.y + y2)

    def draw(self):
        self.batch.draw()

    def set_x(self, x):
        self.x = x
        self.layout()

    def set_y(self, y):
        self.y = y
        self.layout()
