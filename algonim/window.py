from typing import Any

import pyglet
from pyglet.gl import Config  # pyright: ignore[reportPrivateImportUsage]
from pyglet.window import key


class AppWindow(pyglet.window.Window):
    def __init__(self, visible: bool, double_buffer: bool):
        super().__init__(
            width=1600,
            height=900,
            resizable=False,
            fullscreen=False,
            visible=visible,
            config=Config(double_buffer=double_buffer),  # type: ignore[abstract]
        )
        # TODO: improve typing later
        self.objects: list[Any] = []

    def update(self, delta: float):
        print(delta)

    def on_draw(self):
        self.clear()
        for object in self.objects:
            object.draw()

    def on_key_press(self, symbol, modifiers):
        if symbol == key.Q:
            self.close()
