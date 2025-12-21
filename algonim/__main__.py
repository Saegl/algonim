import pathlib
import pyglet
from PIL import Image
from pyglet import shapes
from pyglet.window import key

from algonim.hcode import HighlightedCode
from algonim.easing import EasingTransition, cubic_ease_in_out
from algonim.primitives.var import Var

WHITE = (255, 255, 255, 255)
TRANSPARENT = (255, 255, 255, 0)
BLACK = (0, 0, 0, 255)


class Code:
    def __init__(self, x, y, codetext: str):
        self.x = x
        self.y = y

        self.label = pyglet.text.Label(
            codetext,
            font_size=36,
            x=self.x,
            y=self.y,
            anchor_x="center",
            anchor_y="center",
        )
        self.creation_time = 0.0
        self.set_color(BLACK)

    def draw(self):
        self.label.draw()

    def set_color(self, color):
        self.label.color = color

    def creation(self, delta):
        self.creation_time += delta
        alpha = min(255, int(self.creation_time * 254))
        if alpha == 255:
            return True

        new_color = (*WHITE[0:3], alpha)

        self.set_color(new_color)
        return False


class Array:
    def __init__(self, x, y, data: list[int], thickness: float = 5.0):
        self.x = x
        self.y = y
        self.time = 0

        n = len(data)
        self.data = data
        self.entry_size = 100
        self.thickness = thickness

        width = n * self.entry_size
        height = self.entry_size

        left_bottom_x = x - width / 2
        left_bottom_y = y - height / 2

        self.left_border = shapes.Line(
            x=left_bottom_x,
            y=left_bottom_y,
            x2=left_bottom_x,
            y2=left_bottom_y + self.entry_size,
            width=thickness,
            color=WHITE,
        )
        self.right_border = shapes.Line(
            x=left_bottom_x + self.entry_size * n,
            y=left_bottom_y,
            x2=left_bottom_x + self.entry_size * n,
            y2=left_bottom_y + self.entry_size,
            width=thickness,
            color=WHITE,
        )
        self.bottom_border = shapes.Line(
            x=left_bottom_x - thickness / 2,
            y=left_bottom_y,
            x2=left_bottom_x + self.entry_size * n + thickness / 2,
            y2=left_bottom_y,
            width=thickness,
            color=WHITE,
        )
        self.top_border = shapes.Line(
            x=left_bottom_x - thickness / 2,
            y=left_bottom_y + self.entry_size,
            x2=left_bottom_x + self.entry_size * n + thickness / 2,
            y2=left_bottom_y + self.entry_size,
            width=thickness,
            color=WHITE,
        )
        self.inside_lines = []
        for i in range(n - 1):
            self.inside_lines.append(
                shapes.Line(
                    x=left_bottom_x + self.entry_size * (i + 1),
                    y=left_bottom_y,
                    x2=left_bottom_x + self.entry_size * (i + 1),
                    y2=left_bottom_y + self.entry_size,
                    width=thickness,
                    color=WHITE,
                )
            )

        self.entries = []
        for i, number in enumerate(data):
            self.entries.append(
                pyglet.text.Label(
                    str(number),
                    font_size=36,
                    x=left_bottom_x + self.entry_size / 2 + self.entry_size * i,
                    y=y,
                    anchor_x="center",
                    anchor_y="center",
                )
            )

        self.creation_time = 0.0
        self.deletion_time = 0.0
        self.set_color(TRANSPARENT)

    def draw(self):
        self.left_border.draw()
        self.right_border.draw()
        self.bottom_border.draw()
        self.top_border.draw()
        for line in self.inside_lines:
            line.draw()

        for entry in self.entries:
            entry.draw()

    def move_x(self, dx):
        self.x += dx
        self.left_border.x += dx
        self.right_border.x += dx
        self.bottom_border.x += dx
        self.top_border.x += dx
        for line in self.inside_lines:
            line.x += dx

        for entry in self.entries:
            entry.x += dx

    def move_y(self, dy):
        self.y += dy
        self.left_border.y += dy
        self.right_border.y += dy
        self.bottom_border.y += dy
        self.top_border.y += dy
        for line in self.inside_lines:
            line.y += dy

        for entry in self.entries:
            entry.y += dy

    def set_x(self, x):
        delta_x = x - self.x
        self.move_x(delta_x)

    def set_y(self, y):
        delta_y = y - self.y
        self.move_y(delta_y)

    def set_color(self, color):
        self.left_border.color = color
        self.right_border.color = color
        self.bottom_border.color = color
        self.top_border.color = color
        for line in self.inside_lines:
            line.color = color

        for entry in self.entries:
            entry.color = color

    def creation(self, delta):
        self.creation_time += delta
        alpha = min(255, int(self.creation_time * 254))
        if alpha == 255:
            return True

        new_color = (*WHITE[0:3], alpha)

        self.set_color(new_color)
        return False

    def deletion(self, delta):
        self.deletion_time += delta
        alpha = max(0, 255 - int(self.deletion_time * 254))
        if alpha == 0:
            return True

        new_color = (*WHITE[0:3], alpha)

        self.set_color(new_color)
        return False


class AlgonimWindow(pyglet.window.Window):
    def __init__(self):
        super().__init__(
            width=1600,
            height=900,
            resizable=False,
            fullscreen=False,
            visible=True,
        )
        self.objects = []
        self.frames = []

    def update(self, delta: float):
        print(delta)

    def on_draw(self):
        self.clear()
        for object in self.objects:
            try:
                object.draw()
            except:
                print(object)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.Q:
            self.close()

    # def on_resize(self, width, height):
    #     self.label.width = self.width

    def capture_frame(self, delta):
        import numpy as np

        buffer = pyglet.image.get_buffer_manager().get_color_buffer()
        image_data = buffer.get_image_data()
        data = image_data.get_data("RGBA", image_data.width * 4)
        img = Image.frombytes("RGBA", (image_data.width, image_data.height), data)
        img = img.transpose(
            Image.Transpose.FLIP_TOP_BOTTOM
        )  # Flip the image (OpenGL stores it upside down)

        frame = np.array(img)
        self.frames.append(frame)


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


def array_script(window: AlgonimWindow):
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


def bubble_sort_script(window: AlgonimWindow):
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

    window = AlgonimWindow()

    # run_script(window, bubble_sort_script)
    run_script(window, array_script)

    if args.video:
        pyglet.clock.schedule(window.capture_frame)

    # pyglet.gl.glClearColor(1, 1, 1, 1)
    pyglet.app.run()

    if args.video:
        video = mpy.ImageSequenceClip(window.frames, fps=165)
        video.write_videofile("output.mp4", codec="libx264")
