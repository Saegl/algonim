import pytest

from algonim import easing
from algonim.resolution import Resolution
from algonim.script import (
    Script,
    delay,
    fade_in,
    frame_count,
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
        self.x = script.track(0.0, lambda v: self.drawn.__setitem__("x", v))
        self.y = script.track(0.0, lambda v: self.drawn.__setitem__("y", v))
        self.alpha = script.track(0.0, lambda v: self.drawn.__setitem__("alpha", v))


@pytest.fixture
def script():
    return Script(Resolution.preset("1080p"))


def test_durations_compose(script):
    assert seq(wait(0.2), wait(0.3)).duration == pytest.approx(0.5)
    assert par(wait(0.2), wait(0.5)).duration == pytest.approx(0.5)
    assert delay(1.0, wait(0.5)).duration == pytest.approx(1.5)
    assert stagger(0.2, wait(1.0), wait(1.0), wait(1.0)).duration == pytest.approx(1.4)


def test_play_and_wait_advance_script(script):
    obj = Dummy(script)
    script.play(fade_in(obj, duration=0.5), wait(1.0))
    script.wait(0.25)
    script.play(move_by(obj, 5, 0, duration=0.5))
    assert script.duration == pytest.approx(1.75)


def test_seek_samples_any_time(script):
    obj = Dummy(script)
    script.play(fade_in(obj, duration=1.0))
    script.seek(0.5)
    assert obj.drawn["alpha"] == pytest.approx(127.5)
    script.seek(2.0)
    assert obj.drawn["alpha"] == 255
    script.seek(0.0)  # backwards
    assert obj.drawn["alpha"] == 0


def test_move_by_starts_from_position_at_its_start_time(script):
    obj = Dummy(script)
    script.play(move_up(obj, 170, duration=1.0))
    script.play(move_down(obj, 170, duration=1.0))
    assert obj.y.at(1.0) == pytest.approx(170)
    assert obj.y.at(1.5) == pytest.approx(85)
    assert obj.y.at(2.0) == pytest.approx(0)


def test_move_by_leaves_untouched_axis_free(script):
    obj = Dummy(script)
    script.play(move_by(obj, 0, 10), move_by(obj, 10, 0))
    assert (obj.x.at(1.0), obj.y.at(1.0)) == pytest.approx((10, 10))


def test_overlapping_animations_on_one_track_fail(script):
    obj = Dummy(script)
    with pytest.raises(ValueError, match="overlaps"):
        script.play(fade_in(obj, duration=1.0), delay(0.5, fade_in(obj)))


def test_back_to_back_animations_dont_overlap(script):
    obj = Dummy(script)
    script.play(seq(*[tween(obj.x, i, duration=0.1) for i in range(1, 11)]))
    assert obj.x.at(1.0) == pytest.approx(10)


def test_set_to_jumps_without_interpolation(script):
    text = script.track("a", lambda v: None, lerp=None)
    script.play(set_to(text, "b"))
    assert text.at(0.0) == "b"
    with pytest.raises(ValueError, match="interpolate"):
        script.play(tween(text, "c", duration=1.0))


def test_frame_count_covers_whole_duration():
    assert frame_count(1.0, 60) == 61
    assert frame_count(10 * 0.25, 60) == 151
    assert frame_count(0.0, 60) == 1


@pytest.mark.parametrize(
    "fn",
    [getattr(easing, name) for name in dir(easing) if name.startswith("ease_")],
)
def test_easing_endpoints(fn):
    assert fn(0.0) == pytest.approx(0.0, abs=1e-9)
    assert fn(1.0) == pytest.approx(1.0, abs=1e-9)
