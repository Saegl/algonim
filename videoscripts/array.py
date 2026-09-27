from algonim.primitives.array import Array
from algonim.script import Script, fade_in, fade_out, move_down, move_up


def build_script(script: Script):
    arr = Array(script, 800, 450, [4, 1, 2, 5, 3, 4])
    arr2 = Array(script, 800, 450 - 170, [1, 2, 3])

    script.play(fade_in(arr), fade_in(arr2))
    script.play(move_up(arr, amount=170, duration=2))
    script.play(fade_out(arr2))
    script.play(move_down(arr, amount=170, duration=2))
    script.play(fade_out(arr))
