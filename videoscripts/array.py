from algonim.window import AppWindow
from algonim.primitives.array import Array
from algonim.script import (
    Script,
    parallel,
    animate_creation,
    move_up,
    animate_deletion,
    move_down,
)


def build_script(window: AppWindow):
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
