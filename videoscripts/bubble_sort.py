from pathlib import Path

from algonim.colors import ACCENT, INFO, SUCCESS, SURFACE, WHITE
from algonim.primitives.array import Array, Pointer
from algonim.primitives.flag import Flag
from algonim.primitives.hcode import HighlightedCode
from algonim.python_tracer import Snapshot, trace
from algonim.script import Anim, Script, fade_in, par, stagger

PROGRAM = Path(__file__).parent / "assets" / "bubble_sort.py"

# Lines comparing or swapping arr[j] and arr[j + 1]
COMPARE_LINES = {7, 8, 9}
STEP = 0.35


def cell_colors(snapshot: Snapshot, lineno: int, size: int) -> list:
    """Sorted tail is green, the pair being compared is highlighted"""
    i = snapshot.vars.get("i")
    j = snapshot.vars.get("j")
    colors = [SURFACE] * size
    if i is not None:
        for k in range(i + 1, size):
            colors[k] = SUCCESS
    if lineno in COMPARE_LINES and j is not None:
        colors[j] = colors[j + 1] = ACCENT
    return colors


def build_script(script: Script):
    steps = trace(PROGRAM, {"arr", "swapped", "i", "j"})
    initial = steps[1][1].vars["arr"]

    array = Array(script, 800, 735, initial, cell_size=84)
    pointers = {
        "j": Pointer(script, array, "j", row=0, color=ACCENT),
        "i": Pointer(script, array, "i", row=1, color=WHITE),
    }
    swapped = Flag(script, 800 + array.width / 2 + 150, 735, "swapped", on_color=INFO)
    code = HighlightedCode(script, PROGRAM.read_text(), 330, 520)

    def recolor(snapshot: Snapshot, lineno: int) -> Anim:
        colors = cell_colors(snapshot, lineno, len(initial))
        return par(*(array.color(k, c) for k, c in enumerate(colors)))

    def effect(before: Snapshot, after: Snapshot) -> Anim:
        """What executing a line did to the watched variables"""
        anims = []
        if "arr" in before.vars and after.vars["arr"] != before.vars["arr"]:
            anims.append(array.update(after.vars["arr"]))
        for name, pointer in pointers.items():
            value = after.vars.get(name)
            if value is not None and value != before.vars.get(name):
                anims.append(pointer.point_to(value))
        value = after.vars.get("swapped")
        if value is not None and value != before.vars.get("swapped"):
            anims.append(swapped.set(value))
        return par(*anims)

    script.play(stagger(0.3, fade_in(array, 0.8), fade_in(code, 0.8)))
    script.wait(0.5)

    for (lineno, snapshot), (_, after) in zip(
        steps, steps[1:] + steps[-1:], strict=True
    ):
        script.play(code.goto(lineno), recolor(snapshot, lineno))
        script.wait(STEP)
        changes = effect(snapshot, after)
        script.play(changes, recolor(after, lineno))
        script.wait(STEP / 2)

    script.play(*(array.color(k, SUCCESS) for k in range(len(initial))))
    script.wait(2)
