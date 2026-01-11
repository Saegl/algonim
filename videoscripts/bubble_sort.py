import pathlib

from algonim.python_tracer import Snapshot, trace
from algonim.window import AppWindow
from algonim.script import Script, wait
from algonim.hcode import HighlightedCode
from algonim.primitives.var import Var


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


def build_script(window: AppWindow):
    script = Script()

    win_center_x = window.width // 2
    win_center_y = window.height // 2

    # arr = Array(win_center_x, win_center_y + 300, [4, 1, 2, 5, 3, 4])
    # window.objects.append(arr)

    # script.do(fade_in(arr))
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
