import pyglet

from algonim.script import Script


class HighlightBox:
    def __init__(self, script: Script, x, y, width, height):
        self.resolution = script.resolution
        self.x = x
        self.y = y
        self.box = pyglet.shapes.Rectangle(
            self.resolution.length(x),
            self.resolution.length(y),
            self.resolution.length(width),
            self.resolution.length(height),
            color=(255, 179, 67, 255),
        )
        self.height = script.track(height, self.set_height)
        script.register(self)

    def set_height(self, height):
        self.box.height = self.resolution.length(height)

    def draw(self):
        self.box.draw()
