from typing import Callable
import pyglet
from algonim.colors import WHITE
from algonim.primitives.array import Array

from algonim.easing import cubic_ease_in_out, linear_ease
from algonim.time_utils import Timer

type ActionFn = Callable[[float], bool]
"""Represents an animated action

Args:
    value (float): Delta time (in seconds) since the last call

Returns:
    bool: True if the animation is completed, False otherwise
"""


class Script:
    def __init__(self):
        self.steps: list[ActionFn] = []

    def do(self, action: ActionFn):
        self.steps.append(action)


class ScriptExecutor:
    def __init__(self, script: Script):
        self.script = script
        self.index = 0

    def start(self):
        pyglet.clock.schedule(self.execute_current_action)

    def stop(self):
        pyglet.clock.unschedule(self.execute_current_action)

    def is_complete(self):
        return self.index >= len(self.script.steps)

    def execute_current_action(self, delta: float):
        if self.is_complete():
            self.stop()
            print("Script complete")
            return

        action = self.script.steps[self.index]
        is_action_compelete = action(delta)
        if is_action_compelete:
            self.index += 1


def run_script(window, script_writer):
    with Timer("script_writer"):
        script = script_writer(window)

    script_exec = ScriptExecutor(script)
    script_exec.start()


def fade_in(obj, duration=1.0, ease=linear_ease) -> ActionFn:
    elapsed = 0.0

    def action(dt):
        nonlocal elapsed
        elapsed += dt
        u = min(1.0, elapsed / duration)
        a = int(255 * ease(u))
        obj.set_color((*WHITE[:3], a))
        return u >= 1.0

    return action


def fade_out(obj, duration=1.0, ease=linear_ease) -> ActionFn:
    elapsed = 0.0

    def action(dt):
        nonlocal elapsed
        elapsed += dt
        u = min(1.0, elapsed / duration)
        a = int(255 * (1.0 - ease(u)))
        obj.set_color((*WHITE[:3], a))
        return u >= 1.0

    return action


def tween_xy(
    obj, start_x, start_y, end_x, end_y, duration, ease=linear_ease
) -> ActionFn:
    t = 0.0
    dx = end_x - start_x
    dy = end_y - start_y

    def action(dt):
        nonlocal t
        t += dt
        u = min(1.0, t / duration)
        e = ease(u)
        obj.set_x(start_x + dx * e)
        obj.set_y(start_y + dy * e)
        return u >= 1.0

    return action


def move_to(obj, x, y, duration, ease=linear_ease) -> ActionFn:
    start_x = obj.x
    start_y = obj.y
    return tween_xy(obj, start_x, start_y, x, y, duration, ease)


def move_by(obj, dx, dy, duration, ease=linear_ease) -> ActionFn:
    return defer(lambda: move_to(obj, obj.x + dx, obj.y + dy, duration, ease))


def move_up(obj, amount, seconds) -> ActionFn:
    return move_by(obj, 0, amount, seconds, cubic_ease_in_out)


def move_down(obj, amount, seconds) -> ActionFn:
    return move_by(obj, 0, -amount, seconds, cubic_ease_in_out)


def defer(factory) -> ActionFn:
    "Late binding"

    action = None

    def run(dt):
        nonlocal action
        if action is None:
            action = factory()
        return action(dt)

    return run


def parallel(*actions: ActionFn) -> ActionFn:
    actions = set(actions)

    def combined_action(delta: float):
        for action in list(actions):
            if action(delta):
                actions.remove(action)

        return len(actions) == 0

    return combined_action


def wait(duration: float) -> ActionFn:
    elapsed_time = 0.0

    def action(dt: float):
        nonlocal elapsed_time
        elapsed_time += dt
        return elapsed_time >= duration

    return action
