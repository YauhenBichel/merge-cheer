#!/usr/bin/env python3
"""Drawn loops for the everyday groups: ship, fix, celebration.

Same approach as scripts/seasonal_art.py (every position is a function
of loop time, so the loop has no seam), added next to the pulsing
stills rather than replacing them.
"""

from __future__ import annotations

import math
import random

from PIL import Image

from seasonal_art import (
    BLUE,
    GOLD,
    INK,
    ORANGE,
    PINK,
    RED,
    SNOW,
    TAU,
    TEAL,
    VIOLET,
    _Canvas,
    _falling,
    _mix,
    _sparkle,
)

STEEL = (176, 190, 214)
DARK_STEEL = (120, 134, 164)


def ship_rocket(t: float, size: int) -> Image.Image:
    bg = (16, 18, 46)
    canvas = _Canvas(size, bg, (44, 34, 92))
    # Stars streak down past the rocket: it is the rocket that moves.
    rng = random.Random(9)
    for _ in range(16):
        x, y0 = rng.random(), rng.random()
        laps = rng.choice((1, 2, 2))
        length = 0.03 * laps
        y = (y0 + laps * t) % 1.0 * 1.2 - 0.1
        canvas.line(x, y, x, y + length, _mix(bg, SNOW, 0.35 + 0.2 * laps), 0.006)
    shake = 0.006 * math.sin(TAU * 5 * t)
    cx = 0.5 + shake
    cy = 0.44 + 0.012 * math.sin(TAU * t)
    burn = 0.5 + 0.5 * math.sin(TAU * 4 * t)
    for width, length, color in ((0.085, 0.24, ORANGE), (0.055, 0.17, GOLD), (0.028, 0.1, (255, 250, 220))):
        reach = length * (0.8 + 0.2 * burn)
        canvas.poly(
            [(cx - width, cy + 0.2), (cx + width, cy + 0.2), (cx + 0.01 * math.sin(TAU * 3 * t), cy + 0.2 + reach)],
            color,
        )
    for side in (-1, 1):
        canvas.poly(
            [(cx + side * 0.1, cy + 0.06), (cx + side * 0.22, cy + 0.24), (cx + side * 0.1, cy + 0.21)],
            RED,
        )
    canvas.draw.ellipse(
        [canvas.p(cx - 0.13), canvas.p(cy - 0.3), canvas.p(cx + 0.13), canvas.p(cy + 0.24)],
        fill=(244, 246, 255),
    )
    canvas.draw.pieslice(
        [canvas.p(cx - 0.13), canvas.p(cy - 0.3), canvas.p(cx + 0.13), canvas.p(cy + 0.24)],
        start=225,
        end=315,
        fill=RED,
    )
    canvas.rect(cx - 0.105, cy + 0.15, cx + 0.105, cy + 0.19, BLUE, r=0.01)
    canvas.face(cx, cy - 0.03, 0.055, blink=0.55 < t < 0.62)
    for index, (sx, sy) in enumerate(((0.14, 0.24), (0.86, 0.3), (0.84, 0.74))):
        pulse = 0.5 + 0.5 * math.sin(TAU * (t * 2 + index / 3))
        _sparkle(canvas, sx, sy, 0.045 * pulse, GOLD)
    return canvas.done(size)


def fix_wrench(t: float, size: int) -> Image.Image:
    canvas = _Canvas(size, (216, 244, 236), (176, 226, 214))
    cx, cy = 0.44, 0.56
    # Tighten, ease back, tighten: one swing per loop.
    turn = 0.38 * math.sin(TAU * t)
    angle = -0.75 + turn
    hx, hy = cx + 0.46 * math.cos(angle), cy + 0.46 * math.sin(angle)
    canvas.draw.ellipse([canvas.p(0.2), canvas.p(0.86), canvas.p(0.68), canvas.p(0.91)], fill=(150, 204, 190))
    # Open jaws: a thick arc with its gap on the side away from the handle.
    box = [canvas.p(cx - 0.27), canvas.p(cy - 0.27), canvas.p(cx + 0.27), canvas.p(cy + 0.27)]
    start = math.degrees(angle) + 180 + 42
    canvas.line(cx + 0.2 * math.cos(angle), cy + 0.2 * math.sin(angle), hx, hy, DARK_STEEL, 0.11)
    canvas.circle(hx, hy, 0.055, DARK_STEEL)
    canvas.draw.arc(box, start=start, end=start + 276, fill=DARK_STEEL, width=round(canvas.p(0.1)))
    canvas.line(cx + 0.2 * math.cos(angle), cy + 0.2 * math.sin(angle), hx, hy, STEEL, 0.075)
    canvas.circle(hx, hy, 0.037, STEEL)
    inner = [canvas.p(cx - 0.255), canvas.p(cy - 0.255), canvas.p(cx + 0.255), canvas.p(cy + 0.255)]
    canvas.draw.arc(inner, start=start + 2, end=start + 274, fill=STEEL, width=round(canvas.p(0.07)))
    canvas.circle(hx, hy, 0.018, (200, 236, 226))
    nut = [
        (cx + 0.175 * math.cos(turn + index * TAU / 6), cy + 0.175 * math.sin(turn + index * TAU / 6))
        for index in range(6)
    ]
    canvas.poly(nut, (255, 214, 120))
    canvas.circle(cx, cy, 0.125, (255, 232, 170))
    canvas.face(cx, cy - 0.015, 0.05, blink=0.45 < t < 0.52)
    # Sparks when the wrench reaches the tight end of the swing.
    tight = max(0.0, math.sin(TAU * t)) ** 4
    for index, (sx, sy) in enumerate(((0.78, 0.62), (0.16, 0.26), (0.72, 0.84), (0.14, 0.7))):
        _sparkle(canvas, sx, sy, 0.02 + 0.05 * tight * (1 - 0.15 * index), (255, 255, 255))
    for index, (sx, sy) in enumerate(((0.86, 0.2), (0.24, 0.12))):
        pulse = 0.5 + 0.5 * math.sin(TAU * (t * 2 + index / 2))
        _sparkle(canvas, sx, sy, 0.04 * pulse, GOLD)
    return canvas.done(size)


def celebration_trophy(t: float, size: int) -> Image.Image:
    bg = (26, 22, 56)
    canvas = _Canvas(size, bg, (66, 40, 110))
    _falling(canvas, t, 51, 28, (GOLD, PINK, BLUE, TEAL, VIOLET), flake=False)
    bob = 0.012 * math.sin(TAU * t)
    cx, top = 0.5, 0.3 + bob
    deep = (224, 160, 50)
    shine = 0.5 + 0.5 * math.sin(TAU * 2 * t)
    canvas.circle(cx, top + 0.14, 0.33, _mix(bg, GOLD, 0.1 + 0.08 * shine))
    for side in (-1, 1):
        canvas.draw.arc(
            [canvas.p(cx + side * 0.2 - 0.11), canvas.p(top + 0.02), canvas.p(cx + side * 0.2 + 0.11), canvas.p(top + 0.24)],
            start=0,
            end=360,
            fill=deep,
            width=round(canvas.p(0.032)),
        )
    canvas.rect(cx - 0.21, top, cx + 0.21, top + 0.14, GOLD, r=0.02)
    canvas.draw.pieslice(
        [canvas.p(cx - 0.21), canvas.p(top - 0.1), canvas.p(cx + 0.21), canvas.p(top + 0.36)],
        start=0,
        end=180,
        fill=GOLD,
    )
    canvas.rect(cx - 0.035, top + 0.34, cx + 0.035, top + 0.46, deep)
    canvas.rect(cx - 0.15, top + 0.45, cx + 0.15, top + 0.52, GOLD, r=0.02)
    canvas.rect(cx - 0.19, top + 0.51, cx + 0.19, top + 0.58, deep, r=0.02)
    canvas.poly(
        [(cx - 0.17, top + 0.03), (cx - 0.12, top + 0.03), (cx - 0.1, top + 0.24), (cx - 0.14, top + 0.2)],
        _mix(GOLD, (255, 255, 255), 0.35 + 0.35 * shine),
    )
    canvas.face(cx, top + 0.13, 0.06, blink=0.25 < t < 0.32)
    canvas.star(cx, top - 0.13, 0.07 + 0.012 * shine, (255, 244, 190), turn=0.25 * math.sin(TAU * t))
    for index, (sx, sy) in enumerate(((0.13, 0.3), (0.87, 0.36), (0.14, 0.8), (0.86, 0.78))):
        pulse = 0.5 + 0.5 * math.sin(TAU * (t * 2 + index / 4))
        _sparkle(canvas, sx, sy, 0.05 * pulse, GOLD)
    return canvas.done(size)


# group, output stem, scene
SCENES = (
    ("ship", "rocket", ship_rocket),
    ("fix", "wrench", fix_wrench),
    ("celebration", "trophy", celebration_trophy),
)
