import pyglet
from algonim.primitives.array import Array

from algonim.hcode import HighlightedCode
from algonim.easing import EasingTransition, cubic_ease_in_out
from algonim.primitives.var import Var
from algonim.primitives.array import Array
from algonim.time_utils import Timer


class Script:
    def __init__(self):
        self.steps = []

    def do(self, action):
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


def animate_creation(obj: Array):
    return obj.creation


def animate_deletion(obj: Array):
    return obj.deletion


def move_up(obj: Array, amount: int, seconds: int):
    return EasingTransition(seconds, amount, obj, cubic_ease_in_out, (0.0, 1.0)).step


def move_down(obj: Array, amount: int, seconds: int):
    return EasingTransition(seconds, amount, obj, cubic_ease_in_out, (0.0, -1.0)).step


def parallel(*actions):
    actions = set(actions)

    def combined_action(delta: float):
        for action in list(actions):
            if action(delta):
                actions.remove(action)

        return len(actions) == 0

    return combined_action


def wait(seconds: float):
    elapsed_time = 0.0

    def waiter(delta: float):
        nonlocal elapsed_time
        elapsed_time += delta
        return elapsed_time >= seconds

    return waiter
