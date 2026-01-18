import pyglet

from algonim.script import Script


class HighlightBox:
    def __init__(self, x, y, width, height, script: Script):
        self.x = x
        self.y = y
        self.box = pyglet.shapes.Rectangle(
            x, y, width, height, color=(255, 179, 67, 255)
        )
        script.register(self)

    def set_height(self, height):
        self.box.height = height

    def draw(self):
        self.box.draw()
