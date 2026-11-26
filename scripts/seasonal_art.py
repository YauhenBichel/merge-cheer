#!/usr/bin/env python3
"""Seasonal GIFs drawn in code: christmas and newyear.

Unlike the stills in stills/, these have real motion: snow falls, lights
twinkle, fireworks open. Every position is a function of t in [0, 1), so
the last frame meets the first and the loop has no seam. No text and no
year in the picture, so they do not go stale.

Used by scripts/make_gifs.py. Each scene is `scene(t, size) -> Image`.
"""

from __future__ import annotations

import math
import random

from PIL import Image, ImageDraw

SCALE = 3  # draw large, shrink once: cheap anti-aliasing
TAU = 2 * math.pi
BANDS = 14

NIGHT = (18, 22, 44)
SNOW = (240, 246, 255)
PINK = (255, 143, 171)
GOLD = (255, 209, 102)
RED = (239, 71, 111)
GREEN = (46, 160, 108)
DEEP_GREEN = (30, 122, 86)
TEAL = (6, 214, 160)
BLUE = (76, 201, 240)
VIOLET = (177, 133, 255)
INK = (34, 34, 48)
LIGHTS = (RED, GOLD, BLUE, PINK, TEAL)


def _mix(a: tuple, b: tuple, k: float) -> tuple:
    k = max(0.0, min(1.0, k))
    return tuple(round(x + (y - x) * k) for x, y in zip(a, b))


class _Canvas:
    """Coordinates are 0..1 of the picture; drawing happens at SCALE×."""

    def __init__(self, size: int, top: tuple, bottom: tuple) -> None:
        self.px = size * SCALE
        self.image = Image.new("RGB", (self.px, self.px), top)
        self.draw = ImageDraw.Draw(self.image)
        # A few flat bands, not a smooth ramp: a ramp would eat the GIF
        # palette and leave nothing for the lights.
        for band in range(BANDS):
            self.draw.rectangle(
                [0, self.px * band // BANDS, self.px, self.px * (band + 1) // BANDS],
                fill=_mix(top, bottom, band / (BANDS - 1)),
            )

    def p(self, v: float) -> float:
        return v * self.px

    def circle(self, x: float, y: float, r: float, fill: tuple) -> None:
        self.draw.ellipse(
            [self.p(x - r), self.p(y - r), self.p(x + r), self.p(y + r)], fill=fill
        )

    def poly(self, points: list, fill: tuple) -> None:
        self.draw.polygon([(self.p(x), self.p(y)) for x, y in points], fill=fill)

    def rect(self, x0: float, y0: float, x1: float, y1: float, fill: tuple, r: float = 0) -> None:
        self.draw.rounded_rectangle(
            [self.p(x0), self.p(y0), self.p(x1), self.p(y1)], radius=self.p(r), fill=fill
        )

    def line(self, x0: float, y0: float, x1: float, y1: float, fill: tuple, w: float) -> None:
        self.draw.line(
            [self.p(x0), self.p(y0), self.p(x1), self.p(y1)],
            fill=fill,
            width=max(1, round(self.p(w))),
        )

    def star(self, x: float, y: float, r: float, fill: tuple, turn: float = 0.0) -> None:
        points = []
        for i in range(10):
            radius = r if i % 2 == 0 else r * 0.45
            angle = turn - math.pi / 2 + i * math.pi / 5
            points.append((x + radius * math.cos(angle), y + radius * math.sin(angle)))
        self.poly(points, fill)

    def face(self, x: float, y: float, s: float, blink: bool = False) -> None:
        """Two eyes, cheeks and a smile. `s` is the eye spacing."""
        for side in (-1, 1):
            ex = x + side * s
            if blink:
                self.line(ex - s * 0.3, y, ex + s * 0.3, y, INK, s * 0.16)
            else:
                self.circle(ex, y, s * 0.3, INK)
                self.circle(ex + s * 0.09, y - s * 0.11, s * 0.1, (255, 255, 255))
            self.circle(ex + side * s * 0.45, y + s * 0.55, s * 0.26, PINK)
        self.draw.arc(
            [self.p(x - s * 0.42), self.p(y + s * 0.05), self.p(x + s * 0.42), self.p(y + s * 0.8)],
            start=20,
            end=160,
            fill=INK,
            width=max(1, round(self.p(s * 0.14))),
        )

    def done(self, size: int) -> Image.Image:
        return self.image.resize((size, size), Image.Resampling.LANCZOS)


def _falling(canvas: _Canvas, t: float, seed: int, count: int, colors: tuple, flake: bool) -> None:
    """Snow or confetti. Each piece falls a whole number of screens per loop."""
    rng = random.Random(seed)
    for _ in range(count):
        x0, y0 = rng.random(), rng.random()
        laps = rng.choice((1, 1, 2))
        sway = rng.uniform(0.01, 0.035)
        phase = rng.random()
        size = rng.uniform(0.006, 0.014)
        color = rng.choice(colors)
        y = (y0 + laps * t) % 1.0 * 1.1 - 0.05
        x = x0 + sway * math.sin(TAU * (t + phase))
        if flake:
            canvas.circle(x, y, size, color)
        else:
            lean = math.sin(TAU * (laps * t + phase))
            canvas.poly(
                [
                    (x - size * 1.3, y - size * lean),
                    (x + size * 1.3, y + size * lean),
                    (x + size * 1.3, y + size * lean + size * 1.1),
                    (x - size * 1.3, y - size * lean + size * 1.1),
                ],
                color,
            )


def _sparkle(canvas: _Canvas, x: float, y: float, r: float, color: tuple) -> None:
    if r <= 0.002:
        return
    canvas.poly([(x, y - r), (x + r * 0.25, y), (x, y + r), (x - r * 0.25, y)], color)
    canvas.poly([(x - r, y), (x, y - r * 0.25), (x + r, y), (x, y + r * 0.25)], color)


def christmas_tree(t: float, size: int) -> Image.Image:
    canvas = _Canvas(size, NIGHT, (40, 52, 98))
    _falling(canvas, t, 11, 26, (SNOW, (198, 212, 240)), flake=True)
    canvas.draw.ellipse(
        [canvas.p(-0.3), canvas.p(0.84), canvas.p(1.3), canvas.p(1.3)], fill=SNOW
    )
    bob = 0.008 * math.sin(TAU * t)
    canvas.rect(0.455, 0.76 + bob, 0.545, 0.88, (140, 94, 60), r=0.012)
    tiers = ((0.80, 0.30, 0.58), (0.62, 0.24, 0.40), (0.45, 0.18, 0.25))
    for index, (base, half, top) in enumerate(tiers):
        fill = GREEN if index % 2 == 0 else DEEP_GREEN
        canvas.poly(
            [(0.5 - half, base + bob), (0.5 + half, base + bob), (0.5, top - 0.1 + bob)], fill
        )
    rng = random.Random(5)
    for index in range(13):
        base, half, top = tiers[index % 3]
        depth = rng.uniform(0.25, 0.9)
        y = top - 0.1 + (base - top + 0.1) * depth
        x = 0.5 + rng.uniform(-0.8, 0.8) * half * depth
        if abs(x - 0.5) < 0.1 and 0.5 < y < 0.68:
            continue  # keep the face clear
        on = 0.5 + 0.5 * math.sin(TAU * (t * 2 + index / 5))
        color = LIGHTS[index % len(LIGHTS)]
        canvas.circle(x, y + bob, 0.017 + 0.006 * on, _mix(DEEP_GREEN, color, 0.45 + 0.55 * on))
    canvas.face(0.5, 0.585 + bob, 0.062, blink=0.46 < t < 0.54)
    canvas.star(0.5, 0.135 + bob, 0.07 + 0.008 * math.sin(TAU * 2 * t), GOLD, turn=0.12 * math.sin(TAU * t))
    return canvas.done(size)


def christmas_gift(t: float, size: int) -> Image.Image:
    canvas = _Canvas(size, (255, 228, 232), (255, 204, 213))
    _falling(canvas, t, 23, 18, ((255, 255, 255), (255, 240, 244)), flake=True)
    hop = abs(math.sin(TAU * t))
    y = 0.16 * hop * 0.35
    squash = 1.0 - 0.05 * (1 - hop)
    canvas.draw.ellipse(
        [canvas.p(0.24 + 0.05 * hop), canvas.p(0.83), canvas.p(0.76 - 0.05 * hop), canvas.p(0.89)],
        fill=(240, 170, 186),
    )
    top = 0.86 - 0.42 * squash - y
    canvas.rect(0.25, top, 0.75, 0.86 - y, RED, r=0.04)
    canvas.rect(0.455, top, 0.545, 0.86 - y, GOLD)
    canvas.rect(0.22, top - 0.09, 0.78, top + 0.03, (255, 99, 132), r=0.035)
    canvas.rect(0.455, top - 0.09, 0.545, top + 0.03, GOLD)
    wag = 0.012 * math.sin(TAU * 2 * t)
    for side in (-1, 1):
        canvas.draw.ellipse(
            [
                canvas.p(0.5 + side * 0.01 - (0.13 if side < 0 else 0)),
                canvas.p(top - 0.2 + wag * side),
                canvas.p(0.5 + side * 0.01 + (0.13 if side > 0 else 0)),
                canvas.p(top - 0.08),
            ],
            fill=GOLD,
        )
    canvas.circle(0.5, top - 0.1, 0.035, (255, 190, 70))
    canvas.face(0.5, top + 0.2, 0.075, blink=0.20 < t < 0.27)
    for index, (sx, sy) in enumerate(((0.14, 0.22), (0.86, 0.3), (0.2, 0.62), (0.84, 0.66))):
        pulse = 0.5 + 0.5 * math.sin(TAU * (t * 2 + index / 4))
        _sparkle(canvas, sx, sy, 0.05 * pulse, (255, 255, 255))
    return canvas.done(size)


def _burst(canvas: _Canvas, x: float, y: float, reach: float, u: float, color: tuple, bg: tuple, rays: int) -> None:
    """One firework. u runs 0..1: rise, open, fade."""
    if u < 0.12:
        k = u / 0.12
        tail_y = 0.95 - (0.95 - y) * k
        canvas.line(x, tail_y + 0.05, x, tail_y, _mix(bg, GOLD, 0.8), 0.006)
        return
    k = (u - 0.12) / 0.88
    spread = 1 - (1 - k) ** 3
    glow = (1 - k) ** 0.7
    for ray in range(rays):
        angle = TAU * ray / rays
        for step, trail in enumerate((1.0, 0.82, 0.64)):
            r = reach * spread * trail
            px = x + r * math.cos(angle)
            py = y + r * math.sin(angle) + 0.07 * k * k
            canvas.circle(px, py, 0.017 * (1 - 0.25 * step) * (0.55 + 0.45 * glow), _mix(bg, color, glow * (1 - 0.3 * step)))
    if k < 0.25:
        canvas.circle(x, y, 0.03 * (1 - k / 0.25), (255, 255, 255))


def newyear_fireworks(t: float, size: int) -> Image.Image:
    bg = (14, 16, 40)
    canvas = _Canvas(size, bg, (36, 30, 78))
    rng = random.Random(3)
    for index in range(22):
        twinkle = 0.5 + 0.5 * math.sin(TAU * (t + index / 7))
        canvas.circle(rng.random(), rng.random() * 0.7, 0.004, _mix(bg, SNOW, 0.3 + 0.5 * twinkle))
    shows = (
        (0.30, 0.36, 0.30, 0.00, GOLD, 14),
        (0.72, 0.30, 0.27, 0.35, PINK, 12),
        (0.50, 0.52, 0.25, 0.68, BLUE, 12),
    )
    for x, y, reach, offset, color, rays in shows:
        _burst(canvas, x, y, reach, (t + offset) % 1.0, color, bg, rays)
    rng = random.Random(8)
    x = 0.0
    while x < 1.0:
        width = rng.uniform(0.07, 0.13)
        height = rng.uniform(0.1, 0.24)
        canvas.rect(x, 1 - height, x + width, 1.02, (8, 9, 24))
        for row in range(int(height / 0.045)):
            for col in range(2):
                if rng.random() < 0.55:
                    wx = x + 0.018 + col * (width - 0.05)
                    wy = 1 - height + 0.02 + row * 0.045
                    canvas.rect(wx, wy, wx + 0.016, wy + 0.02, (255, 214, 120))
        x += width + 0.008
    return canvas.done(size)


def newyear_clock(t: float, size: int) -> Image.Image:
    canvas = _Canvas(size, (40, 28, 84), (88, 50, 140))
    _falling(canvas, t, 31, 30, (GOLD, PINK, BLUE, TEAL, (255, 255, 255)), flake=False)
    bob = 0.012 * math.sin(TAU * t)
    cx, cy = 0.5, 0.53 + bob
    swing = 0.05 * math.sin(TAU * 2 * t)
    for side in (-1, 1):
        canvas.circle(cx + side * 0.19 + swing * 0.3, cy - 0.27, 0.075, GOLD)
    canvas.rect(cx - 0.015, cy - 0.36, cx + 0.015, cy - 0.27, (230, 170, 60))
    canvas.circle(cx, cy - 0.37, 0.028, (230, 170, 60))
    for side in (-1, 1):
        canvas.line(cx + side * 0.14, cy + 0.2, cx + side * 0.2, cy + 0.31, (230, 170, 60), 0.03)
    canvas.circle(cx, cy, 0.285, (230, 170, 60))
    canvas.circle(cx, cy, 0.25, (255, 250, 240))
    for hour in range(12):
        angle = TAU * hour / 12
        canvas.circle(cx + 0.215 * math.sin(angle), cy - 0.215 * math.cos(angle), 0.011 if hour % 3 else 0.017, VIOLET)
    # Both hands at twelve; the minute hand ticks a hair either side.
    tick = 0.03 * math.sin(TAU * 4 * t)
    canvas.line(cx, cy - 0.02, cx, cy - 0.13, INK, 0.022)
    canvas.line(cx, cy - 0.02, cx + 0.19 * math.sin(tick), cy - 0.02 - 0.19 * math.cos(tick), RED, 0.014)
    canvas.circle(cx, cy - 0.02, 0.02, INK)
    canvas.face(cx, cy + 0.07, 0.07, blink=0.6 < t < 0.67)
    for index, (sx, sy) in enumerate(((0.12, 0.2), (0.88, 0.24), (0.1, 0.74), (0.9, 0.78))):
        pulse = 0.5 + 0.5 * math.sin(TAU * (t * 2 + index / 4))
        _sparkle(canvas, sx, sy, 0.055 * pulse, GOLD)
    return canvas.done(size)


# group, output stem, scene
SCENES = (
    ("christmas", "tree", christmas_tree),
    ("christmas", "gift", christmas_gift),
    ("newyear", "fireworks", newyear_fireworks),
    ("newyear", "clock", newyear_clock),
)


def frames(scene, count: int, size: int) -> list:
    return [scene(index / count, size) for index in range(count)]
