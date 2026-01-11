from typing import Callable
import pyglet
from algonim.colors import WHITE
from algonim.primitives.array import Array

from algonim.easing import EasingTransition, cubic_ease_in_out
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


def fade_in(primitive, duration: float = 1.0) -> ActionFn:
    elapsed_time = 0.0

    def action(dt: float) -> bool:
        nonlocal elapsed_time

        elapsed_time += dt

        alpha = min(255, int(elapsed_time / duration * 254))
        new_color = (*WHITE[0:3], alpha)
        primitive.set_color(new_color)

        return elapsed_time >= duration

    return action


def animate_creation(obj: Array):
    return obj.creation


def animate_deletion(obj: Array):
    return obj.deletion


def move_up(obj: Array, amount: int, seconds: int):
    return EasingTransition(seconds, amount, obj, cubic_ease_in_out, (0.0, 1.0)).step


def move_down(obj: Array, amount: int, seconds: int):
    return EasingTransition(seconds, amount, obj, cubic_ease_in_out, (0.0, -1.0)).step


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
