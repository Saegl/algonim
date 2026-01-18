from algonim.colors import GREY, WHITE
from algonim.easing import ease_in_out_cubic, ease_out_cubic
from algonim.primitives.hbox import HighlightBox
from algonim.primitives.hcode import HighlightedCode
from algonim.primitives.text import Text
from algonim.script import (
    Script,
    drop_in,
    drop_out,
    fade_in,
    grow_in,
    grow_out,
    move_down,
    parallel,
    seq,
    wait,
)

# NOTE: `###` in docstrings is narration
#       `#` is a comment not shown in video


def intro_scene(script: Script):
    """
    How to find the maximum in an array
    Problem: Let's say you have an array, like this:
    [4, 3, 1, 7, 20, 7, 5]
    Here, the maximum is 20
    Write a Python function that receives an array
    and returns the maximum element
    Don't use built-in functions like `max` or `sort`
        ### That would be cheating
        ### The goal of this video is to implement the algorithm from scratch
        ### in other words we do our own version of `max`
    Use basic language features instead: variables and loops.
    ### Pause here if you want to solve it yourself
    """

    win_center_x = 1920 // 2
    win_center_y = 1080 // 2

    shift_y = 410
    title_size = 36
    desc_size = 32

    title_padding_extra = 30
    padding = 42

    text_start_x = win_center_x
    text_start_y = win_center_y + shift_y

    # Highlight max (20) in both array and text, coords are just guessed
    box1 = HighlightBox(
        x=985,
        y=shift_y + 230,
        width=60,
        height=0,
        script=script,
    )
    box2 = HighlightBox(
        x=985 + 191,
        y=shift_y + 157,
        width=60,
        height=0,
        script=script,
    )

    title = Text(
        script,
        text_start_x,
        text_start_y,
        "How to find the maximum in an array",
        font_size=title_size,
        bold=True,
        color=WHITE,
    )

    script.do(
        fade_in(title),
        move_down(title, 100, 1, ease=ease_out_cubic),
    )

    desc_intro = Text(
        script,
        text_start_x,
        text_start_y - title_padding_extra - (desc_size + padding),
        "Problem: Let's say you have an array, like this:",
        font_size=desc_size,
        color=GREY,
    )
    array_example = Text(
        script,
        text_start_x,
        text_start_y - title_padding_extra - (desc_size + padding) * 2,
        "[4, 3, 1, 7, 20, 7, 5]",
        font_size=desc_size,
        color=GREY,
    )
    answer_outro = Text(
        script,
        text_start_x,
        text_start_y - title_padding_extra - (desc_size + padding) * 3,
        "Here, the maximum is 20",
        font_size=desc_size,
        color=GREY,
    )
    task_part1 = Text(
        script,
        text_start_x,
        text_start_y - title_padding_extra - (desc_size + padding) * 4,
        "Write a Python function that receives an array",
        font_size=desc_size,
        color=GREY,
    )
    task_part2 = Text(
        script,
        text_start_x,
        text_start_y - title_padding_extra - (desc_size + padding) * 5,
        "and returns the maximum element",
        font_size=desc_size,
        color=GREY,
    )
    constraint1 = Text(
        script,
        text_start_x,
        text_start_y - title_padding_extra - (desc_size + padding) * 6,
        "Don't use built-in functions like `max` or `sort`",
        font_size=desc_size,
        color=GREY,
    )
    constraint2 = Text(
        script,
        text_start_x,
        text_start_y - title_padding_extra - (desc_size + padding) * 7,
        "Use basic language features instead: variables and loops.",
        font_size=32,
        color=GREY,
    )

    script.do(
        drop_in(desc_intro),
        seq(wait(0.2), drop_in(array_example)),
    )

    script.do(wait(0.4))
    script.do(
        drop_in(answer_outro),
    )

    script.do(
        grow_in(box1, ease=ease_in_out_cubic),
        grow_in(box2, ease=ease_in_out_cubic),
    )
    script.do(wait(1.0))
    script.do(
        grow_out(box1, ease=ease_in_out_cubic),
        grow_out(box2, ease=ease_in_out_cubic),
    )

    script.do(wait(0.2))
    script.do(
        drop_in(task_part1),
        seq(wait(0.2), drop_in(task_part2)),
    )

    script.do(wait(0.2))
    script.do(
        fade_in(constraint1),
        move_down(constraint1, 100, 1, ease=ease_out_cubic),
        seq(
            wait(0.2),
            parallel(
                fade_in(constraint2),
                move_down(constraint2, 100, 1, ease=ease_out_cubic),
            ),
        ),
    )

    script.do(wait(3.0))
    script.do(
        drop_out(title),
        drop_out(desc_intro),
        drop_out(array_example),
        drop_out(answer_outro),
        drop_out(task_part1),
        drop_out(task_part2),
        drop_out(constraint1),
        drop_out(constraint2),
    )


def explainer_scene(script: Script):
    """
    Solution:
    1. First, you need to go through every element.
        ### We don’t know where the largest element could be.
        ### visiting each element once is necessary
        ### In situations like this, a for loop is often used.
    2. As you go, remember just one value: the "local" maximum.
        ### By "local maximum", I mean the largest element seen so far.
        ### When you just started first element of the array is the local largest one
        ###
        ### Once you do one step
        ### you need to choose between local largest (which is just first now)
        ### and second element
        ### and remember new local largest between them
        ###
        ### For the next (third) step, you need to choose between "local" largest
        ### and third element. As you can see, you don’t need to remember
        ### all the elements you’ve seen before.
        ### You only need one value: the current maximum.
        ### It doesn't matter whether it came from the first element or the second.
    3. Once you've visited the entire array,
        the "local" maximum becomes the global maximum.
        it is the answer to the problem
        ### Notice how `largest` variable was storing largest element in intervals
        ### 4 was largest among first 3
        # [0:2] highlighted
        ### then 7 became larger
        # [0:3] highlighted
        ### And after we got 20, it is the largest til the end
        # entire array highlighted
        ### After we done, nothing could be larger in the array
        ### It is impossible to "miss" largest somehow


    # Below is variable and array, animated with text and narration
    largest = 4
    [4, 3, 1, 7, 20, 7, 5]

    # On third step history is shown below array
    [4, 4, 4, 7, 20, 20, 20]

    ### Pause to code this solution yourself
    """

    text_start_x = 100
    text_start_y = 1080 - 100

    title_size = 36
    desc_size = 32

    title_padding_extra = 30
    padding = 42

    solution = Text(
        script,
        text_start_x,
        text_start_y,
        "Solution:",
        font_size=title_size,
        color=WHITE,
        anchor_x="left",
        anchor_y="top",
    )
    step1 = Text(
        script,
        text_start_x,
        text_start_y - title_padding_extra - (desc_size + padding),
        "1. You have to go through each element",
        font_size=desc_size,
        color=GREY,
        anchor_x="left",
        anchor_y="top",
    )
    step2 = Text(
        script,
        text_start_x,
        text_start_y - title_padding_extra - (desc_size + padding) * 2,
        '2. Remember just one "local" largest element as you go',
        font_size=desc_size,
        color=GREY,
        anchor_x="left",
        anchor_y="top",
    )
    step3 = Text(
        script,
        text_start_x,
        text_start_y - title_padding_extra - (desc_size + padding) * 3,
        "3. Once you visit entire array",
        font_size=desc_size,
        color=GREY,
        anchor_x="left",
        anchor_y="top",
    )
    step3_part2 = Text(
        script,
        text_start_x,
        text_start_y - title_padding_extra - (desc_size + padding) * 4,
        '  "local" largest element is "global" largest',
        font_size=desc_size,
        color=GREY,
        anchor_x="left",
        anchor_y="top",
    )

    script.do(drop_in(solution))
    script.do(drop_in(step1))
    script.do(drop_in(step2))
    script.do(
        drop_in(step3),
        drop_in(step3_part2),
    )


CODE = """
array = [4, 3, 1, 7, 20, 7, 5]
largest = array[0]

for i in range(1, len(array)):
    if array[i] > largest:
        largest = array[i]

print(largest)

"""


def coding_scene(script: Script):
    """
    Coding:
    ### The array is already given
    ### I’ll use the same array from the problem statement
    ### but you can experiment with any
    ### We will start by creating largest variable
    ### it is first element of the array
    ### Next we use for loop
    ### in which we compare "local" largest with current value in the array
    ### to check whether the current value should replace our local maximum
    ### At the end, we print the result.


    # Code block is revealed with narration, line by line
    ```python
    array = [4, 3, 1, 7, 20, 7, 5]
    largest = array[0]

    for i in range(1, len(array)):
        if array[i] > largest:
            largest = array[i]

    print(largest)
    ```

    ### See it in action
    largest = 4
    i = 1
    ...
    # executing line is highlighted, variables updated
    """

    code = HighlightedCode(CODE, x=200, y=200, font_size=32)
    script.register(code)


def exercises_scene(script: Script):
    """
    Exercises:
    1. Write a program to find minimum instead of maximum
    [4, 3, 1, 7, 20, 7, 5] => should print 1
    2. Instead of printing minimum, print index at which you found it
    [4, 3, 1, 7, 20, 7, 5] => should print 2
    3. What about printing the index of the first minimum versus the last minimum?
        in case of duplicates
    [4, 3, 1, 7, 20, 1, 5] => how to print 2? how to print 5?
    """


def build_script():
    script = Script()

    intro_scene(script)
    explainer_scene(script)
    # coding_scene(script)
    # exercises_scene(script)

    return script
