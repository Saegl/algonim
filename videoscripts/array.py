from algonim.primitives.array import Array
from algonim.script import (
    Script,
    fade_in,
    fade_out,
    move_down,
    move_up,
    parallel,
)


def build_script(script: Script):
    arr = Array(script, 800, 450, [4, 1, 2, 5, 3, 4])
    arr2 = Array(script, 800, 450 - 170, [1, 2, 3])

    script.do(
        parallel(
            fade_in(arr),
            fade_in(arr2),
        ),
    )
    script.do(move_up(arr, amount=170, seconds=2))
    # script.do(wait(3))
    script.do(fade_out(arr2))
    script.do(move_down(arr, amount=170, seconds=2))
    script.do(fade_out(arr))
