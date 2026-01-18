"""
Easing functions from https://easings.net/
"""

import math


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


# LINEAR
def ease_linear(t: float) -> float:
    return t


# SINE
def ease_in_sine(t: float) -> float:
    return 1 - math.cos((t * math.pi) / 2)


def ease_out_sine(t: float) -> float:
    return math.sin((t * math.pi) / 2)


def ease_in_out_sine(t: float) -> float:
    return -(math.cos(math.pi * t) - 1) / 2


# QUADRATIC
def ease_in_quad(t: float) -> float:
    return t * t


def ease_out_quad(t: float) -> float:
    return 1 - (1 - t) * (1 - t)


def ease_in_out_quad(t: float) -> float:
    if t < 0.5:
        return 2 * t * t
    return 1 - (-2 * t + 2) ** 2 / 2


# CUBIC
def ease_in_cubic(t: float) -> float:
    return t * t * t


def ease_out_cubic(t: float) -> float:
    return 1 - (1 - t) ** 3


def ease_in_out_cubic(t: float) -> float:
    if t < 0.5:
        return 4 * t**3
    return 1 - (-2 * t + 2) ** 3 / 2


# QUARTIC
def ease_in_quart(t: float) -> float:
    return t**4


def ease_out_quart(t: float) -> float:
    return 1 - (1 - t) ** 4


def ease_in_out_quart(t: float) -> float:
    if t < 0.5:
        return 8 * t**4
    return 1 - (-2 * t + 2) ** 4 / 2


# QUINTIC
def ease_in_quint(t: float) -> float:
    return t**5


def ease_out_quint(t: float) -> float:
    return 1 - (1 - t) ** 5


def ease_in_out_quint(t: float) -> float:
    if t < 0.5:
        return 16 * t**5
    return 1 - (-2 * t + 2) ** 5 / 2


# EXPONENTIAL
def ease_in_expo(t: float) -> float:
    return 0 if t == 0 else 2 ** (10 * t - 10)


def ease_out_expo(t: float) -> float:
    return 1 if t == 1 else 1 - 2 ** (-10 * t)


def ease_in_out_expo(t: float) -> float:
    if t == 0:
        return 0
    if t == 1:
        return 1
    if t < 0.5:
        return 2 ** (20 * t - 10) / 2
    return (2 - 2 ** (-20 * t + 10)) / 2


# CIRCULAR
def ease_in_circ(t: float) -> float:
    return 1 - math.sqrt(1 - t**2)


def ease_out_circ(t: float) -> float:
    return math.sqrt(1 - (t - 1) ** 2)


def ease_in_out_circ(t: float) -> float:
    if t < 0.5:
        return (1 - math.sqrt(1 - (2 * t) ** 2)) / 2
    return (math.sqrt(1 - (-2 * t + 2) ** 2) + 1) / 2


# BACK
def ease_in_back(t: float, c1: float = 1.70158) -> float:
    return t**2 * ((c1 + 1) * t - c1)


def ease_out_back(t: float, c1: float = 1.70158) -> float:
    return 1 + (t - 1) ** 2 * ((c1 + 1) * (t - 1) + c1)


def ease_in_out_back(t: float, c1: float = 1.70158) -> float:
    c2 = c1 * 1.525
    if t < 0.5:
        return ((2 * t) ** 2 * ((c2 + 1) * 2 * t - c2)) / 2
    return ((2 * t - 2) ** 2 * ((c2 + 1) * (2 * t - 2) + c2) + 2) / 2


# ELASTIC
def ease_in_elastic(t: float, c4: float = (2 * math.pi) / 3) -> float:
    if t == 0 or t == 1:
        return t
    return -(2 ** (10 * t - 10)) * math.sin((t * 10 - 10.75) * c4)


def ease_out_elastic(t: float, c4: float = (2 * math.pi) / 3) -> float:
    if t == 0 or t == 1:
        return t
    return 2 ** (-10 * t) * math.sin((t * 10 - 0.75) * c4) + 1


def ease_in_out_elastic(t: float, c5: float = (2 * math.pi) / 4.5) -> float:
    if t == 0 or t == 1:
        return t
    if t < 0.5:
        return -(2 ** (20 * t - 10) * math.sin((20 * t - 11.125) * c5)) / 2
    return (2 ** (-20 * t + 10) * math.sin((20 * t - 11.125) * c5)) / 2 + 1


# BOUNCE
def ease_out_bounce(t: float) -> float:
    n1 = 7.5625
    d1 = 2.75
    if t < 1 / d1:
        return n1 * t * t
    if t < 2 / d1:
        t -= 1.5 / d1
        return n1 * t * t + 0.75
    if t < 2.5 / d1:
        t -= 2.25 / d1
        return n1 * t * t + 0.9375
    t -= 2.625 / d1
    return n1 * t * t + 0.984375


def ease_in_bounce(t: float) -> float:
    return 1 - ease_out_bounce(1 - t)


def ease_in_out_bounce(t: float) -> float:
    if t < 0.5:
        return (1 - ease_out_bounce(1 - 2 * t)) / 2
    return (1 + ease_out_bounce(2 * t - 1)) / 2
