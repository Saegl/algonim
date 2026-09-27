import pytest

from algonim.primitives.text import Text
from algonim.resolution import RESOLUTIONS, Resolution
from algonim.script import Script


def test_presets_are_16_by_9():
    for name in RESOLUTIONS:
        resolution = Resolution.preset(name)
        assert resolution.width * 9 == resolution.height * 16


def test_rejects_other_aspect_ratios():
    with pytest.raises(ValueError):
        Resolution(1920, 1200)


def test_text_width_scales_with_resolution(window):
    line = "Use basic language features instead: variables and loops."
    widths = []
    for name in RESOLUTIONS:
        resolution = Resolution.preset(name)
        text = Text(Script(resolution), 800, 450, line)
        widths.append(text.label.content_width / resolution.scale)

    # Hinted glyph advances used to drift by ~2%
    assert max(widths) - min(widths) < 1.0
