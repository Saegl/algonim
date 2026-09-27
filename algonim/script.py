import math
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import pyglet

from algonim.easing import ease_in_out_cubic, ease_linear, ease_out_cubic, lerp
from algonim.resolution import Resolution
from algonim.time_utils import Timer

type Easing = Callable[[float], float]
type Lerp[T] = Callable[[T, T, float], T]

# Tolerance for float sums of durations, so back to back animations don't
# count as overlapping
EPSILON = 1e-9


@dataclass(frozen=True)
class Segment[T]:
    t0: float
    t1: float
    start: T
    end: T
    ease: Easing


class Track[T]:
    """Property value as a function of time: the initial value, then
    non-overlapping segments that ease from one value to another.

    `apply` pushes the value to the drawn object, it runs on seek only.
    Tracks without `lerp` (like text) can only jump between values.
    """

    def __init__(
        self, initial: T, apply: Callable[[T], None], lerp: Lerp[T] | None = None
    ):
        self.initial = initial
        self.apply = apply
        self.lerp = lerp
        self.segments: list[Segment[T]] = []
        self.applied: Any = _UNSET

    @property
    def end_time(self) -> float:
        return self.segments[-1].t1 if self.segments else 0.0

    def at(self, t: float) -> T:
        value = self.initial
        for seg in self.segments:
            if t < seg.t0:
                break
            if t < seg.t1:
                assert self.lerp is not None
                u = (t - seg.t0) / (seg.t1 - seg.t0)
                return self.lerp(seg.start, seg.end, seg.ease(u))
            value = seg.end
        return value

    def tween(self, t0: float, duration: float, end: T, ease: Easing = ease_linear):
        if t0 < self.end_time - EPSILON:
            raise ValueError(
                f"Animation at {t0:.3f}s overlaps the previous one on this track,"
                f" which ends at {self.end_time:.3f}s"
            )
        if duration > 0 and self.lerp is None:
            raise ValueError("Track can't interpolate, use set_to()")
        self.segments.append(Segment(t0, t0 + duration, self.at(t0), end, ease))

    def seek(self, t: float):
        value = self.at(t)
        if value != self.applied:
            self.apply(value)
            self.applied = value


_UNSET = object()


@dataclass(frozen=True)
class Anim:
    """Animation description: `place(t0)` writes it to tracks starting at t0"""

    duration: float
    place: Callable[[float], None]


class Script:
    def __init__(self, resolution: Resolution) -> None:
        self.resolution = resolution
        # TODO: typing
        self.actors: list[Any] = []
        self.tracks: list[Track[Any]] = []
        # Grows as the script is written, it is where the next play() starts
        self.duration = 0.0

    def register(self, actor):
        self.actors.append(actor)

    def track[T](
        self, initial: T, apply: Callable[[T], None], lerp: Lerp[Any] | None = lerp
    ) -> Track[T]:
        track = Track(initial, apply, lerp)
        self.tracks.append(track)
        return track

    def play(self, *anims: Anim):
        anim = par(*anims)
        anim.place(self.duration)
        self.duration += anim.duration

    def wait(self, seconds: float):
        self.duration += seconds

    def seek(self, t: float):
        for track in self.tracks:
            track.seek(t)


class Player:
    """Plays a script in real time on the pyglet clock"""

    def __init__(self, script: Script):
        self.script = script
        self.t = 0.0
        self.paused = False

    @property
    def finished(self) -> bool:
        return self.t >= self.script.duration

    def start(self):
        pyglet.clock.schedule(self.tick)

    def stop(self):
        pyglet.clock.unschedule(self.tick)

    def toggle_pause(self):
        if self.finished:
            self.seek(0.0)
            self.paused = False
        else:
            self.paused = not self.paused

    def seek(self, t: float):
        self.t = min(max(t, 0.0), self.script.duration)
        self.script.seek(self.t)

    def tick(self, dt: float):
        if self.paused or self.finished:
            return
        self.seek(self.t + dt)
        if self.finished:
            print("Script complete")


def frame_count(duration: float, fps: int) -> int:
    """Frames at 0, 1/fps, ..., the last one at or after the end"""
    return math.ceil(duration * fps - EPSILON) + 1


def write_script(window, script_writer) -> Script:
    script = Script(window.resolution)
    with Timer("script_writer"):
        script_writer(script)

    script.seek(0)
    window.objects.extend(script.actors)
    return script


def tween[T](track: Track[T], end: T, duration: float, ease=ease_linear) -> Anim:
    return Anim(duration, lambda t0: track.tween(t0, duration, end, ease))


def tween_by(track: Track[float], delta: float, duration: float, ease=ease_linear):
    """Tween relative to the value the track has when the animation starts"""
    return Anim(
        duration, lambda t0: track.tween(t0, duration, track.at(t0) + delta, ease)
    )


def set_to[T](track: Track[T], value: T) -> Anim:
    return Anim(0.0, lambda t0: track.tween(t0, 0.0, value))


def wait(duration: float) -> Anim:
    return Anim(duration, lambda t0: None)


def seq(*anims: Anim) -> Anim:
    def place(t0: float):
        for anim in anims:
            anim.place(t0)
            t0 += anim.duration

    return Anim(sum(anim.duration for anim in anims), place)


def par(*anims: Anim) -> Anim:
    def place(t0: float):
        for anim in anims:
            anim.place(t0)

    return Anim(max((anim.duration for anim in anims), default=0.0), place)


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
