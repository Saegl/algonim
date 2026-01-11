from algonim.window import AppWindow
from algonim.script import (
    Script,
    fade_in,
    fade_out,
    move_up,
    wait,
    move_down,
)
from algonim.primitives.array import Array
from algonim.primitives.text import Text


def build_script(window: AppWindow):
    script = Script()

    win_center_x = 1600 // 2
    win_center_y = 900 // 2

    text = Text(
        win_center_x, win_center_y, "How to find max number in array?", font_size=32
    )
    window.objects.append(text)

    script.do(fade_in(text))
    script.do(move_down(text, 100, 1))
    script.do(wait(0.5))

    arr_data = [4, 3, 1, 7, 20, 7, 5]
    arr = Array(win_center_x, win_center_y + 100, arr_data)
    window.objects.append(arr)

    script.do(fade_in(arr))
    script.do(fade_out(arr))

    script.do(move_up(text, 100, 1.0))
    script.do(fade_out(text))

    return script
