from typing import Any

import pyglet
from pyglet.gl import Config  # pyright: ignore[reportPrivateImportUsage]
from pyglet.window import key, mouse

from algonim.dev import Timeline
from algonim.resolution import Resolution
from algonim.script import Player


def _use_unhinted_advances():
    """FreeType hints glyph advances to whole pixels, so text width drifts by a
    few percent between resolutions. Unhinted advances scale exactly, and
    pyglet still rounds every glyph quad to the pixel grid, keeping it crisp.
    """
    if not pyglet.compat_platform.startswith("linux"):
        return

    from pyglet.font.freetype import FreeTypeGlyphRenderer

    get_glyph_metrics = FreeTypeGlyphRenderer._get_glyph_metrics

    def get_unhinted_glyph_metrics(self):
        get_glyph_metrics(self)
        self._advance_x = self._glyph_slot.linearHoriAdvance / 65536

    FreeTypeGlyphRenderer._get_glyph_metrics = get_unhinted_glyph_metrics  # type: ignore[method-assign]


_use_unhinted_advances()


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
        # Set in preview only, so video rendering ignores playback controls
        self.player: Player | None = None
        self.timeline: Timeline | None = None
        self.dev_mode = False
        self.scrubbing = False

    def attach_player(self, player: Player):
        self.player = player
        self.timeline = Timeline(player, self.resolution)

    def on_draw(self):
        self.clear()
        for object in self.objects:
            object.draw()
        if self.dev_mode and self.timeline:
            self.timeline.draw()

    def on_key_press(self, symbol, modifiers):
        if symbol == key.Q:
            self.close()
        elif symbol == key.F3 and self.player:
            self.dev_mode = not self.dev_mode
        elif symbol == key.SPACE and self.player:
            self.player.toggle_pause()

    def on_mouse_press(self, x, y, button, modifiers):
        if button == mouse.LEFT and self.dev_mode and self.timeline:
            self.scrubbing = self.timeline.hit(y)
            if self.scrubbing:
                self.timeline.seek_to(x)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.scrubbing and self.timeline:
            self.timeline.seek_to(x)

    def on_mouse_release(self, x, y, button, modifiers):
        if button == mouse.LEFT:
            self.scrubbing = False
