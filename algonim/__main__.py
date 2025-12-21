import pathlib
import pyglet

from algonim.hcode import HighlightedCode
from algonim.easing import EasingTransition, cubic_ease_in_out
from algonim.primitives.var import Var
from algonim.primitives.array import Array
from algonim.window import AppWindow


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


def array_script(window: AppWindow):
    script = Script()

    arr = Array(window.width // 2, window.height // 2, [4, 1, 2, 5, 3, 4])
    window.objects.append(arr)

    arr2 = Array(window.width // 2, window.height // 2 - 200, [1, 2, 3])
    window.objects.append(arr2)

    script.do(
        parallel(
            animate_creation(arr),
            animate_creation(arr2),
        ),
    )
    script.do(move_up(arr, amount=200, seconds=2))
    # script.do(wait(3))
    script.do(animate_deletion(arr2))
    script.do(move_down(arr, amount=200, seconds=2))
    script.do(animate_deletion(arr))

    return script


bubble_sort_code = """\
arr = [3, 1, 3, 4, 6, 9, 5]
n = len(arr)

for i in reversed(range(n)):
    swapped = False
    for j in range(i):
        if arr[j] > arr[j + 1]:
            swapped = True
            arr[j], arr[j + 1] = arr[j + 1], arr[j]
    if not swapped:
        break
"""

from algonim.python_tracer import Snapshot, trace


def bubble_sort_script(window: AppWindow):
    script = Script()

    win_center_x = window.width // 2
    win_center_y = window.height // 2

    # arr = Array(win_center_x, win_center_y + 300, [4, 1, 2, 5, 3, 4])
    # window.objects.append(arr)

    # script.do(animate_creation(arr))
    # script.do(move_up(arr, amount=300, seconds=2))

    program_filepath = pathlib.Path("videoprograms/bubble_sort.py")

    code = HighlightedCode(program_filepath.open("rt").read(), 420, 250, 28)
    print(code.layout.content_width, code.layout.content_height)
    window.objects.append(code)

    lines = trace(program_filepath, {"arr", "swapped", "i", "j"})

    variables = {
        "i": Var(100, 100, "i", "null"),
        "j": Var(300, 100, "j", "null"),
        "swapped": Var(500, 100, "swapped", "null"),
        "arr": Var(1000, 100, "arr", "null"),
    }

    for var in variables.values():
        window.objects.append(var)

    prev_snapshot = Snapshot({}, "", -1)
    for lineno, snapshot in lines:
        new_vars, changed = snapshot.diff(prev_snapshot)
        # print(prev_snapshot, snapshot)
        print(new_vars, changed)
        # print(snapshot)

        script.do(code.hl(lineno, snapshot.line))
        prev_snapshot = snapshot

        for varname in new_vars:
            value = snapshot.vars[varname]
            script.do(variables[varname].update_val(value))
            print(f"NEW VAR {varname} = {value}")

        for varname in changed:
            script.do(variables[varname].update_val(changed[varname].to))

        script.do(wait(2))

    return script


if __name__ == "__main__":
    from argparse import ArgumentParser

    import moviepy.editor as mpy

    parser = ArgumentParser("algonim")
    parser.add_argument("--video", action="store_true")

    args = parser.parse_args()

    window = AppWindow()

    # run_script(window, bubble_sort_script)
    run_script(window, array_script)

    if args.video:
        pyglet.clock.schedule(window.capture_frame)

    # pyglet.gl.glClearColor(1, 1, 1, 1)
    pyglet.app.run()

    if args.video:
        video = mpy.ImageSequenceClip(window.frames, fps=165)
        video.write_videofile("output.mp4", codec="libx264")
