import pytest

from algonim import easing
from algonim.resolution import Resolution
from algonim.script import (
    FPS,
    Script,
    delay,
    fade_in,
    move_by,
    move_down,
    move_up,
    par,
    seq,
    set_to,
    stagger,
    tween,
    wait,
)


class Dummy:
    def __init__(self, script: Script):
        self.drawn: dict[str, float] = {}
        self.x = script.prop(0.0, lambda v: self.drawn.__setitem__("x", v))
        self.y = script.prop(0.0, lambda v: self.drawn.__setitem__("y", v))
        self.alpha = script.prop(0.0, lambda v: self.drawn.__setitem__("alpha", v))


@pytest.fixture
def script():
    return Script(Resolution.preset("1080p"))


def played(script: Script, anim) -> float:
    start = script.frame
    script.play(anim)
    return (script.frame - start) / FPS


def test_durations_compose(script):
    assert played(script, seq(wait(0.2), wait(0.3))) == pytest.approx(0.5)
    assert played(script, par(wait(0.2), wait(0.5))) == pytest.approx(0.5)
    assert played(script, delay(1.0, wait(0.5))) == pytest.approx(1.5)
    anims = [wait(1.0), wait(1.0), wait(1.0)]
    assert played(script, stagger(0.2, *anims)) == pytest.approx(1.4)


def test_play_and_wait_advance_script(script):
    obj = Dummy(script)
    script.play(fade_in(obj, duration=0.5), wait(1.0))
    script.wait(0.25)
    script.play(move_by(obj, 5, 0, duration=0.5))
    assert script.duration == pytest.approx(1.75)


def test_seek_samples_any_frame(script):
    obj = Dummy(script)
    script.play(fade_in(obj, duration=1.0))
    script.seek(FPS // 2)
    assert obj.drawn["alpha"] == pytest.approx(127.5)
    script.seek(FPS)
    assert obj.drawn["alpha"] == 255
    script.seek(0)  # backwards
    assert obj.drawn["alpha"] == 0


def test_move_by_starts_from_position_at_its_start(script):
    obj = Dummy(script)
    script.play(move_up(obj, 170, duration=1.0))
    script.play(move_down(obj, 170, duration=1.0))
    assert obj.y.at(FPS) == pytest.approx(170)
    assert obj.y.at(FPS * 3 // 2) == pytest.approx(85)
    assert obj.y.at(FPS * 2) == pytest.approx(0)


def test_move_by_leaves_untouched_axis_free(script):
    obj = Dummy(script)
    script.play(move_by(obj, 0, 10), move_by(obj, 10, 0))
    assert (obj.x.at(FPS), obj.y.at(FPS)) == pytest.approx((10, 10))


def test_back_to_back_animations(script):
    obj = Dummy(script)
    script.play(seq(*[tween(obj.x, i, duration=0.1) for i in range(1, 11)]))
    assert script.frame == FPS
    assert obj.x.at(FPS) == pytest.approx(10)


def test_set_to_jumps(script):
    text = script.prop("a", lambda v: None)
    script.play(set_to(text, "b"))
    assert script.frame == 0
    assert text.at(0) == "b"


def test_prop_made_mid_script_has_initial_value_before(script):
    script.wait(1.0)
    obj = Dummy(script)
    script.play(fade_in(obj))
    assert obj.alpha.at(0) == 0
    assert obj.alpha.at(FPS * 2) == 255


@pytest.mark.parametrize(
    "fn",
    [getattr(easing, name) for name in dir(easing) if name.startswith("ease_")],
)
def test_easing_endpoints(fn):
    assert fn(0.0) == pytest.approx(0.0, abs=1e-9)
    assert fn(1.0) == pytest.approx(1.0, abs=1e-9)
