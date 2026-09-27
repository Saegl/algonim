from typing import Any

import pyglet
from pyglet.gl import Config  # pyright: ignore[reportPrivateImportUsage]
from pyglet.window import key

from algonim.resolution import Resolution


class AppWindow(pyglet.window.Window):
    def __init__(self, resolution: Resolution, visible: bool):
        super().__init__(
            width=resolution.width,
            height=resolution.height,
            resizable=False,
            fullscreen=False,
            visible=visible,
            config=Config(double_buffer=True, sample_buffers=1, samples=4),  # type: ignore[abstract]
        )
        self.resolution = resolution
        # TODO: improve typing later
        self.objects: list[Any] = []

    def on_draw(self):
        self.clear()
        for object in self.objects:
            object.draw()

    def on_key_press(self, symbol, modifiers):
        if symbol == key.Q:
            self.close()
