import math

import pyglet


class Arrow:
    def __init__(
        self,
        batch,
        start_x,
        start_y,
        end_x,
        end_y,
        head_length=30,
        head_angle=30,
        color=(255, 255, 255),
        width=2,
    ):
        """
        Represents an arrow composed of three lines: the shaft and two head lines.

        Args:
            batch (pyglet.graphics.Batch): The batch to draw the arrow into.
            start_x, start_y (float): Starting coordinates of the arrow.
            end_x, end_y (float): Ending coordinates of the arrow (shaft end).
            head_length (float): Length of the arrowhead lines.
            head_angle (float): Angle between the shaft and arrowhead lines (degrees).
            color (tuple): RGB color of the arrow lines.
            width (float): Width of the arrow lines.
        """
        self.batch = batch
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.head_length = head_length
        self.head_angle = head_angle
        self.color = color
        self.width = width

        # Compute the arrowhead coordinates
        self.left_head_x, self.left_head_y, self.right_head_x, self.right_head_y = (
            self.calculate_arrowhead()
        )

        # Create the lines
        self.shaft = pyglet.shapes.Line(
            start_x, start_y, end_x, end_y, width=width, color=color, batch=batch
        )
        self.left_head = pyglet.shapes.Line(
            end_x,
            end_y,
            self.left_head_x,
            self.left_head_y,
            width=width,
            color=color,
            batch=batch,
        )
        self.right_head = pyglet.shapes.Line(
            end_x,
            end_y,
            self.right_head_x,
            self.right_head_y,
            width=width,
            color=color,
            batch=batch,
        )

        self.x = -1

    @property
    def y(self):
        return self.shaft.y

    def calculate_arrowhead(self):
        """Calculate the coordinates of the two arrowhead lines."""
        angle_rad = math.atan2(self.end_y - self.start_y, self.end_x - self.start_x)
        left_head_angle = angle_rad + math.radians(180 - self.head_angle)
        right_head_angle = angle_rad - math.radians(180 - self.head_angle)

        left_head_x = self.end_x + self.head_length * math.cos(left_head_angle)
        left_head_y = self.end_y + self.head_length * math.sin(left_head_angle)
        right_head_x = self.end_x + self.head_length * math.cos(right_head_angle)
        right_head_y = self.end_y + self.head_length * math.sin(right_head_angle)

        return left_head_x, left_head_y, right_head_x, right_head_y

    def draw(self):
        self.batch.draw()

    def set_y(self, y):
        self.shaft.y = y
        self.right_head.y = y
        self.left_head.y = y

    def set_x(self, x):
        pass


class ArrowExample(pyglet.window.Window):
    def __init__(self):
        super().__init__(width=400, height=400, caption="Arrow Example")
        self.set_location(100, 100)

        # Create a batch to manage all lines
        self.batch = pyglet.graphics.Batch()

        # Create multiple arrows
        self.arrows = [
            Arrow(
                self.batch,
                100,
                200,
                300,
                200,
                head_length=30,
                head_angle=30,
                color=(255, 0, 0),
                width=3,
            ),
            Arrow(
                self.batch,
                150,
                250,
                350,
                300,
                head_length=40,
                head_angle=45,
                color=(0, 255, 0),
                width=2,
            ),
            Arrow(
                self.batch,
                50,
                50,
                200,
                100,
                head_length=25,
                head_angle=25,
                color=(0, 0, 255),
                width=4,
            ),
        ]

    def on_draw(self):
        self.clear()
        self.batch.draw()


if __name__ == "__main__":
    window = ArrowExample()
    pyglet.app.run()
