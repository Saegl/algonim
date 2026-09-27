from dataclasses import dataclass

import pyglet

VIRTUAL_WIDTH = 1600
VIRTUAL_HEIGHT = 900

RESOLUTIONS = {
    "720p": (1280, 720),
    "900p": (1600, 900),
    "1080p": (1920, 1080),
    "1440p": (2560, 1440),
    "4k": (3840, 2160),
}


@dataclass(frozen=True)
class Resolution:
    """Maps the virtual 1600x900 canvas that scripts use onto a 16:9 render size"""

    width: int
    height: int

    @classmethod
    def preset(cls, name: str) -> "Resolution":
        return cls(*RESOLUTIONS[name])

    def __post_init__(self):
        if self.width * VIRTUAL_HEIGHT != self.height * VIRTUAL_WIDTH:
            raise ValueError(f"{self.width}x{self.height} is not 16:9")

    @property
    def scale(self) -> float:
        return self.width / VIRTUAL_WIDTH

    def length(self, value: float) -> float:
        """Virtual coordinate or size (line width, font size) to pixels"""
        return value * self.scale


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
