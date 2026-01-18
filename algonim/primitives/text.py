import pyglet

from algonim.colors import TRANSPARENT, Color


class Text:
    def __init__(self, x, y, text: str, font_size: int = 32):
        self.x = x
        self.y = y
        self.label = pyglet.text.Label(
            text, x, y, anchor_x="center", anchor_y="center", font_size=font_size
        )
        self.label.color = TRANSPARENT

    def set_color(self, color: Color):
        self.label.color = color

    def set_x(self, x):
        self.x = x
        self.label.x = x

    def set_y(self, y):
        self.y = y
        self.label.y = y

    def draw(self):
        self.label.draw()
