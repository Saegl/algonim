from algonim.primitives.array import Array
from algonim.script import (
    Script,
    fade_in,
    fade_out,
    move_down,
    move_up,
    parallel,
)


def build_script():
    script = Script()

    arr = Array(1920 // 2, 1080 // 2, [4, 1, 2, 5, 3, 4])
    script.register(arr)

    arr2 = Array(1920 // 2, 1080 // 2 - 200, [1, 2, 3])
    script.register(arr)

    script.do(
        parallel(
            fade_in(arr),
            fade_in(arr2),
        ),
    )
    script.do(move_up(arr, amount=200, seconds=2))
    # script.do(wait(3))
    script.do(fade_out(arr2))
    script.do(move_down(arr, amount=200, seconds=2))
    script.do(fade_out(arr))

    return script
