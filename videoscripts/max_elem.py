from algonim.window import AppWindow
from algonim.script import Script, animate_creation, fade_in, wait, move_down
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
    script.do(wait(1.0))

    arr_data = [4, 3, 1, 7, 20, 7, 5]
    arr = Array(win_center_x, win_center_y + 100, arr_data)
    window.objects.append(arr)

    script.do(animate_creation(arr))
    script.do(animate_creation(arr))

    return script
