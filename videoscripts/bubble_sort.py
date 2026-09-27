import pathlib

from algonim.primitives.hcode import HighlightedCode
from algonim.primitives.var import Var
from algonim.python_tracer import Snapshot, trace
from algonim.script import Script

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


def build_script(script: Script):
    program_filepath = pathlib.Path("videoprograms/bubble_sort.py")

    code = HighlightedCode(script, program_filepath.open("rt").read(), 350, 675)

    lines = trace(program_filepath, {"arr", "swapped", "i", "j"})

    variables = {
        "i": Var(script, 83, 83, "i", "null"),
        "j": Var(script, 250, 83, "j", "null"),
        "swapped": Var(script, 417, 83, "swapped", "null"),
        "arr": Var(script, 833, 83, "arr", "null"),
    }

    prev_snapshot = Snapshot({}, "", -1)
    for lineno, snapshot in lines:
        new_vars, changed = snapshot.diff(prev_snapshot)
        print(new_vars, changed)

        script.play(code.hl(lineno, snapshot.line))
        prev_snapshot = snapshot

        for varname in new_vars:
            value = snapshot.vars[varname]
            script.play(variables[varname].update_val(value))
            print(f"NEW VAR {varname} = {value}")

        for varname in changed:
            script.play(variables[varname].update_val(changed[varname].to))

        script.wait(2)
