from collections.abc import Callable

import pyglet

from algonim.easing import ease_in_out_cubic, ease_linear, ease_out_cubic, lerp
from algonim.time_utils import Timer

type ActionFn = Callable[[float], bool]
"""Represents an animated action

Args:
    value (float): Delta time (in seconds) since the last call

Returns:
    bool: True if the animation is completed, False otherwise
"""


class Script:
    def __init__(self) -> None:
        self.steps: list[ActionFn] = []
        # TODO: typing
        self.actors = []  # type: ignore

    def do(self, *actions: ActionFn):
        if len(actions) == 1:
            self.steps.append(actions[0])
        else:
            self.steps.append(parallel(*actions))

    def register(self, actor):
        self.actors.append(actor)


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
        is_action_complete = action(delta)
        if is_action_complete:
            self.index += 1


def write_script(window, script_writer) -> ScriptExecutor:
    with Timer("script_writer"):
        script = script_writer()

    window.objects.extend(script.actors)
    script_exec = ScriptExecutor(script)
    return script_exec


def fade_in(obj, duration=1.0, ease=ease_linear) -> ActionFn:
    elapsed = 0.0

    def action(dt):
        nonlocal elapsed
        elapsed += dt
        u = min(1.0, elapsed / duration)
        a = int(255 * ease(u))
        obj.set_alpha(a)
        return u >= 1.0

    return action


def grow_in(obj, duration=0.5, ease=ease_linear) -> ActionFn:
    elapsed = 0.0

    def action(dt):
        nonlocal elapsed
        elapsed += dt
        u = min(1.0, elapsed / duration)
        a = int(60 * ease(u))
        obj.set_height(a)
        return u >= 1.0

    return action


def grow_out(obj, duration=0.5, ease=ease_linear) -> ActionFn:
    elapsed = 0.0

    def action(dt):
        nonlocal elapsed
        elapsed += dt
        u = min(1.0, elapsed / duration)
        a = int(60 * (1.0 - ease(u)))
        obj.set_height(a)
        return u >= 1.0

    return action


def drop_in(obj) -> ActionFn:
    return parallel(
        fade_in(obj),
        move_down(obj, 100, 1, ease=ease_out_cubic),
    )


def drop_out(obj) -> ActionFn:
    return parallel(
        fade_out(obj, ease=ease_out_cubic),
        move_down(obj, 100, 1, ease=ease_out_cubic),
    )


def fade_out(obj, duration=1.0, ease=ease_linear) -> ActionFn:
    elapsed = 0.0

    def action(dt):
        nonlocal elapsed
        elapsed += dt
        u = min(1.0, elapsed / duration)
        a = int(255 * (1.0 - ease(u)))
        obj.set_alpha(a)
        return u >= 1.0

    return action


def tween_xy(
    obj, start_x, start_y, end_x, end_y, duration, ease=ease_linear
) -> ActionFn:
    t = 0.0

    def action(dt):
        nonlocal t
        t += dt
        u = min(1.0, t / duration)
        e = ease(u)

        obj.set_x(lerp(start_x, end_x, e))
        obj.set_y(lerp(start_y, end_y, e))

        return u >= 1.0

    return action


def move_to(obj, x, y, duration, ease=ease_linear) -> ActionFn:
    start_x = obj.x
    start_y = obj.y
    return tween_xy(obj, start_x, start_y, x, y, duration, ease)


def move_by(obj, dx, dy, duration, ease=ease_linear) -> ActionFn:
    return defer(lambda: move_to(obj, obj.x + dx, obj.y + dy, duration, ease))


def move_up(obj, amount, seconds, ease=ease_in_out_cubic) -> ActionFn:
    return move_by(obj, 0, amount, seconds, ease)


def move_down(obj, amount, seconds, ease=ease_in_out_cubic) -> ActionFn:
    return move_by(obj, 0, -amount, seconds, ease)


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
    remaining = set(actions)

    def combined_action(delta: float):
        for action in list(remaining):
            if action(delta):
                remaining.remove(action)

        return len(remaining) == 0

    return combined_action


def seq(*actions: ActionFn) -> ActionFn:
    index = 0

    def combined_action(dt: float):
        nonlocal index

        current_action = actions[index]
        is_complete = current_action(dt)
        if is_complete:
            index += 1

        return index >= len(actions)

    return combined_action


def wait(duration: float) -> ActionFn:
    elapsed_time = 0.0

    def action(dt: float):
        nonlocal elapsed_time
        elapsed_time += dt
        return elapsed_time >= duration

    return action
