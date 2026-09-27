type Color = tuple[int, int, int, int]
"""RGBA Color, each component [0..255]"""

WHITE = (255, 255, 255, 255)
TRANSPARENT = (255, 255, 255, 0)
GREY = (222, 222, 222, 255)
DIM = (130, 134, 150, 255)
BLACK = (0, 0, 0, 255)

# Fills, readable behind white text on the black background
SURFACE = (44, 48, 60, 255)
CURSOR = (68, 70, 88, 255)
ACCENT = (230, 160, 60, 255)
SUCCESS = (60, 160, 100, 255)
INFO = (80, 140, 235, 255)


def replace_alpha(color, alpha):
    return (*color[:3], alpha)


def scale_alpha(color: Color, alpha: float) -> Color:
    """Color faded by `alpha` [0..255], for objects with their own opacity"""
    return (*color[:3], round(color[3] * alpha / 255))


def lerp_color(a: Color, b: Color, t: float) -> Color:
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b, strict=True))  # type: ignore[return-value]
