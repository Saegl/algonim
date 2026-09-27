import pytest

from algonim import easing
from algonim.resolution import Resolution
from algonim.script import Script, ScriptExecutor, fade_in, move_by, parallel, seq, wait


class Dummy:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.alpha = 0

    def set_x(self, x):
        self.x = x

    def set_y(self, y):
        self.y = y

    def set_alpha(self, alpha):
        self.alpha = alpha


def run(action, dt=0.1, max_frames=1000) -> int:
    for frame in range(1, max_frames + 1):
        if action(dt):
            return frame
    raise AssertionError("action never completed")


def test_wait():
    assert run(wait(1.0), dt=0.25) == 4


def test_fade_in_reaches_full_alpha():
    obj = Dummy()
    run(fade_in(obj, duration=0.5))
    assert obj.alpha == 255


def test_move_by_uses_position_at_start_time():
    obj = Dummy()
    step = move_by(obj, 10, -5, duration=0.3)
    obj.x = 100  # moved after the action was created
    run(step)
    assert (obj.x, obj.y) == pytest.approx((110, -5))


def test_parallel_runs_in_given_order():
    calls = []

    def recorder(name):
        return lambda dt: calls.append(name) or True

    run(parallel(recorder("a"), recorder("b"), recorder("c")))
    assert calls == ["a", "b", "c"]


def test_parallel_waits_for_longest():
    assert run(parallel(wait(0.2), wait(0.5)), dt=0.1) == 5


def test_seq_runs_one_after_another():
    assert run(seq(wait(0.2), wait(0.3)), dt=0.1) == 5


def test_executor_runs_all_steps():
    obj = Dummy()
    script = Script(Resolution.preset("1080p"))
    script.do(fade_in(obj, duration=0.2))
    script.do(move_by(obj, 5, 0, duration=0.2), wait(0.1))

    executor = ScriptExecutor(script)
    while not executor.is_complete():
        executor.execute_current_action(0.1)

    assert obj.alpha == 255
    assert obj.x == pytest.approx(5)


@pytest.mark.parametrize(
    "fn",
    [getattr(easing, name) for name in dir(easing) if name.startswith("ease_")],
)
def test_easing_endpoints(fn):
    assert fn(0.0) == pytest.approx(0.0, abs=1e-9)
    assert fn(1.0) == pytest.approx(1.0, abs=1e-9)
