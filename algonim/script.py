from collections.abc import Callable, Iterator
from typing import Any

import pyglet

from algonim.easing import ease_in_out_cubic, ease_linear, ease_out_cubic, lerp
from algonim.resolution import Resolution
from algonim.time_utils import Timer

FPS = 60

type Easing = Callable[[float], float]

type Anim = Iterator[None]
"""Generator that animates props while the script is written. Each `yield`
moves to the next frame, the code after it sets the props for that frame"""


def frames(seconds: float) -> int:
    return round(seconds * FPS)


class Prop[T]:
    """Animatable property: `value` is its value in the frame being written,
    `apply` pushes a value to the drawn object when playback seeks"""

    def __init__(self, value: T, apply: Callable[[T], None], frame: int):
        self.value = value
        self.apply = apply
        # Values of the frames before the one being written, a prop made
        # mid-script has its initial value in the frames before it
        self.history: list[T] = [value] * frame
        self.applied: Any = _UNSET

    def at(self, frame: int) -> T:
        return self.history[frame] if frame < len(self.history) else self.value

    def seek(self, frame: int):
        value = self.at(frame)
        if value != self.applied:
            self.apply(value)
            self.applied = value


_UNSET = object()


class Script:
    def __init__(self, resolution: Resolution) -> None:
        self.resolution = resolution
        # TODO: typing
        self.actors: list[Any] = []
        self.props: list[Prop[Any]] = []
        # Frame being written, after writing it is the last frame
        self.frame = 0

    @property
    def duration(self) -> float:
        return self.frame / FPS

    def register(self, actor):
        self.actors.append(actor)

    def prop[T](self, value: T, apply: Callable[[T], None]) -> Prop[T]:
        prop = Prop(value, apply, self.frame)
        self.props.append(prop)
        return prop

    def play(self, *anims: Anim):
        for _ in par(*anims):
            for prop in self.props:
                prop.history.append(prop.value)
            self.frame += 1

    def wait(self, seconds: float):
        self.play(wait(seconds))

    def seek(self, frame: int):
        for prop in self.props:
            prop.seek(frame)


class Player:
    """Plays a script one frame per tick, slow drawing slows it down instead
    of skipping frames"""

    def __init__(self, script: Script):
        self.script = script
        self.frame = 0
        self.paused = False

    @property
    def finished(self) -> bool:
        return self.frame >= self.script.frame

    def start(self):
        pyglet.clock.schedule_interval(self.tick, 1 / FPS)

    def stop(self):
        pyglet.clock.unschedule(self.tick)

    def toggle_pause(self):
        if self.finished:
            self.seek(0)
            self.paused = False
        else:
            self.paused = not self.paused

    def seek(self, frame: int):
        self.frame = min(max(frame, 0), self.script.frame)
        self.script.seek(self.frame)

    def tick(self, dt: float):
        if self.paused or self.finished:
            return
        self.seek(self.frame + 1)
        if self.finished:
            print("Script complete")


def write_script(window, script_writer) -> Script:
    script = Script(window.resolution)
    with Timer("script_writer"):
        script_writer(script)

    script.seek(0)
    window.objects.extend(script.actors)
    return script


def tween(prop: Prop[float], end: float, duration: float, ease=ease_linear) -> Anim:
    start = prop.value
    n = frames(duration)
    for i in range(1, n + 1):
        yield
        prop.value = lerp(start, end, ease(i / n))
    # Exact end value, and the jump for zero duration
    prop.value = end


def tween_by(prop: Prop[float], delta: float, duration: float, ease=ease_linear):
    yield from tween(prop, prop.value + delta, duration, ease)


def set_to[T](prop: Prop[T], value: T) -> Anim:
    prop.value = value
    yield from ()


def wait(seconds: float) -> Anim:
    for _ in range(frames(seconds)):
        yield


def seq(*anims: Anim) -> Anim:
    for anim in anims:
        yield from anim


def par(*anims: Anim) -> Anim:
    running = list(anims)
    while running := [anim for anim in running if next(anim, _DONE) is not _DONE]:
        yield


_DONE = object()


def delay(seconds: float, anim: Anim) -> Anim:
    return seq(wait(seconds), anim)


def stagger(seconds: float, *anims: Anim) -> Anim:
    """Start each animation `seconds` after the previous one started"""
    return par(*(delay(i * seconds, anim) for i, anim in enumerate(anims)))


def fade_in(obj, duration=1.0, ease=ease_linear) -> Anim:
    return tween(obj.alpha, 255, duration, ease)


def fade_out(obj, duration=1.0, ease=ease_linear) -> Anim:
    return tween(obj.alpha, 0, duration, ease)


def grow_in(obj, height=50, duration=0.5, ease=ease_linear) -> Anim:
    return tween(obj.height, height, duration, ease)


def grow_out(obj, duration=0.5, ease=ease_linear) -> Anim:
    return tween(obj.height, 0, duration, ease)


def move_to(obj, x, y, duration=1.0, ease=ease_linear) -> Anim:
    return par(tween(obj.x, x, duration, ease), tween(obj.y, y, duration, ease))


def move_by(obj, dx, dy, duration=1.0, ease=ease_linear) -> Anim:
    # Untouched axes stay free for other animations
    return par(
        wait(duration),
        *([tween_by(obj.x, dx, duration, ease)] if dx else []),
        *([tween_by(obj.y, dy, duration, ease)] if dy else []),
    )


def move_up(obj, amount, duration=1.0, ease=ease_in_out_cubic) -> Anim:
    return move_by(obj, 0, amount, duration, ease)


def move_down(obj, amount, duration=1.0, ease=ease_in_out_cubic) -> Anim:
    return move_by(obj, 0, -amount, duration, ease)


def drop_in(obj) -> Anim:
    return par(fade_in(obj), move_down(obj, 80, 1, ease=ease_out_cubic))


def drop_out(obj) -> Anim:
    return par(
        fade_out(obj, ease=ease_out_cubic),
        move_down(obj, 80, 1, ease=ease_out_cubic),
    )
