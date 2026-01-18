type Color = tuple[int, int, int, int]
"""RGBA Color, each component [0..255]"""

WHITE = (255, 255, 255, 255)
TRANSPARENT = (255, 255, 255, 0)
GREY = (222, 222, 222, 255)
BLACK = (0, 0, 0, 255)


def replace_alpha(color, alpha):
    return (*color[:3], alpha)
