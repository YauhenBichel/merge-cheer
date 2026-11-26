#!/usr/bin/env python3
"""Seasonal GIFs drawn in code: christmas, newyear, halloween,
hacktoberfest and birthday.

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


ORANGE = (255, 146, 43)
DEEP_ORANGE = (232, 106, 23)
BROWN = (140, 94, 60)
CREAM = (255, 244, 224)
AUTUMN = (ORANGE, RED, GOLD, (196, 98, 45), (224, 168, 60))


def _leaves(canvas: _Canvas, t: float, seed: int, count: int) -> None:
    """Autumn leaves: pointed ovals that turn as they fall."""
    rng = random.Random(seed)
    for _ in range(count):
        x0, y0 = rng.random(), rng.random()
        laps = rng.choice((1, 1, 2))
        sway = rng.uniform(0.02, 0.06)
        phase = rng.random()
        size = rng.uniform(0.022, 0.036)
        color = rng.choice(AUTUMN)
        y = (y0 + laps * t) % 1.0 * 1.12 - 0.06
        x = x0 + sway * math.sin(TAU * (t + phase))
        turn = TAU * (laps * t + phase)
        ax, ay = math.cos(turn) * size, math.sin(turn) * size
        bx, by = -ay * 0.45, ax * 0.45
        canvas.poly([(x + ax, y + ay), (x + bx, y + by), (x - ax, y - ay), (x - bx, y - by)], color)


def _bat(canvas: _Canvas, x: float, y: float, s: float, flap: float, color: tuple) -> None:
    lift = s * (0.2 + 0.6 * flap)
    for side in (-1, 1):
        canvas.poly(
            [
                (x, y),
                (x + side * s * 0.6, y - lift),
                (x + side * s * 1.3, y - lift * 0.2),
                (x + side * s * 0.9, y + s * 0.2),
                (x + side * s * 0.55, y),
                (x + side * s * 0.3, y + s * 0.25),
            ],
            color,
        )
    canvas.circle(x, y, s * 0.28, color)


def _bats(canvas: _Canvas, t: float, color: tuple) -> None:
    for index, (y, s, offset, direction) in enumerate(
        ((0.16, 0.05, 0.0, 1), (0.3, 0.035, 0.45, -1), (0.1, 0.03, 0.7, 1))
    ):
        along = (t + offset) % 1.0
        x = -0.15 + 1.3 * along if direction > 0 else 1.15 - 1.3 * along
        flap = 0.5 + 0.5 * math.sin(TAU * (4 * t + index / 3))
        _bat(canvas, x, y + 0.02 * math.sin(TAU * (2 * t + offset)), s, flap, color)


def halloween_pumpkin(t: float, size: int) -> Image.Image:
    bg = (38, 22, 60)
    canvas = _Canvas(size, bg, (98, 44, 96))
    canvas.circle(0.78, 0.2, 0.13, (255, 236, 170))
    canvas.circle(0.74, 0.17, 0.025, (240, 214, 140))
    canvas.circle(0.82, 0.24, 0.018, (240, 214, 140))
    _bats(canvas, t, (20, 12, 34))
    canvas.draw.ellipse([canvas.p(-0.3), canvas.p(0.84), canvas.p(1.3), canvas.p(1.3)], fill=(24, 14, 40))
    bob = 0.01 * math.sin(TAU * t)
    flicker = 0.5 + 0.5 * math.sin(TAU * 3 * t)
    cy = 0.64 + bob
    canvas.circle(0.5, cy, 0.3 + 0.015 * flicker, _mix(bg, ORANGE, 0.22 + 0.1 * flicker))
    canvas.rect(0.47, cy - 0.3, 0.53, cy - 0.17, (96, 140, 70), r=0.015)
    for dx, rx, color in ((-0.15, 0.13, DEEP_ORANGE), (0.15, 0.13, DEEP_ORANGE), (-0.07, 0.14, ORANGE), (0.07, 0.14, ORANGE), (0, 0.11, (255, 165, 70))):
        canvas.draw.ellipse(
            [canvas.p(0.5 + dx - rx), canvas.p(cy - 0.2), canvas.p(0.5 + dx + rx), canvas.p(cy + 0.2)],
            fill=color,
        )
    canvas.face(0.5, cy - 0.01, 0.075, blink=0.4 < t < 0.47)
    return canvas.done(size)


def halloween_ghost(t: float, size: int) -> Image.Image:
    bg = (20, 40, 60)
    canvas = _Canvas(size, bg, (44, 72, 96))
    rng = random.Random(4)
    for index in range(18):
        twinkle = 0.5 + 0.5 * math.sin(TAU * (t + index / 6))
        canvas.circle(rng.random(), rng.random() * 0.8, 0.005, _mix(bg, SNOW, 0.3 + 0.6 * twinkle))
    _bats(canvas, (t + 0.3) % 1.0, (10, 22, 36))
    lift = 0.03 * math.sin(TAU * t)
    lean = 0.02 * math.sin(TAU * t + 1.2)
    cx, cy = 0.5 + lean, 0.46 + lift
    canvas.draw.ellipse(
        [canvas.p(0.32 - lift), canvas.p(0.86), canvas.p(0.68 + lift), canvas.p(0.91)],
        fill=_mix(bg, (0, 0, 0), 0.35),
    )
    white = (250, 250, 255)
    canvas.circle(cx, cy, 0.2, white)
    canvas.rect(cx - 0.2, cy, cx + 0.2, cy + 0.26, white)
    wave = 0.012 * math.sin(TAU * 2 * t)
    for index in range(4):
        canvas.circle(cx - 0.15 + index * 0.1, cy + 0.26 + (wave if index % 2 else -wave), 0.05, white)
    for side in (-1, 1):
        wag = 0.03 * math.sin(TAU * 2 * t + side)
        canvas.circle(cx + side * 0.22, cy + 0.08 + wag, 0.05, white)
    canvas.face(cx, cy - 0.01, 0.07, blink=0.7 < t < 0.77)
    for index, (sx, sy) in enumerate(((0.14, 0.3), (0.86, 0.42), (0.16, 0.72), (0.86, 0.76))):
        pulse = 0.5 + 0.5 * math.sin(TAU * (t * 2 + index / 4))
        _sparkle(canvas, sx, sy, 0.045 * pulse, GOLD)
    return canvas.done(size)


def hacktoberfest_leaves(t: float, size: int) -> Image.Image:
    canvas = _Canvas(size, (255, 238, 214), (255, 212, 160))
    _leaves(canvas, t, 17, 9)
    bob = 0.008 * math.sin(TAU * t)
    canvas.draw.ellipse([canvas.p(0.18), canvas.p(0.82), canvas.p(0.82), canvas.p(0.88)], fill=(236, 180, 120))
    canvas.rect(0.22, 0.26 + bob, 0.78, 0.7 + bob, (58, 52, 78), r=0.04)
    canvas.rect(0.255, 0.295 + bob, 0.745, 0.665 + bob, (36, 32, 54), r=0.02)
    canvas.rect(0.14, 0.7 + bob, 0.86, 0.78 + bob, (92, 84, 118), r=0.03)
    canvas.rect(0.42, 0.715 + bob, 0.58, 0.735 + bob, (58, 52, 78), r=0.01)
    # A small merge on the screen: two commits join one.
    glow = 0.5 + 0.5 * math.sin(TAU * 2 * t)
    canvas.line(0.33, 0.6 + bob, 0.33, 0.36 + bob, TEAL, 0.012)
    canvas.line(0.33, 0.56 + bob, 0.43, 0.48 + bob, VIOLET, 0.012)
    canvas.line(0.43, 0.48 + bob, 0.33, 0.4 + bob, VIOLET, 0.012)
    canvas.circle(0.33, 0.6 + bob, 0.02, TEAL)
    canvas.circle(0.43, 0.48 + bob, 0.02, VIOLET)
    canvas.circle(0.33, 0.37 + bob, 0.022 + 0.008 * glow, _mix(TEAL, (255, 255, 255), 0.5 * glow))
    canvas.circle(0.58, 0.47 + bob, 0.1, GOLD)
    canvas.face(0.58, 0.45 + bob, 0.05, blink=0.3 < t < 0.37)
    _leaves(canvas, (t + 0.5) % 1.0, 29, 5)
    return canvas.done(size)


def _along(points: list, k: float) -> tuple:
    lengths = [math.dist(points[i], points[i + 1]) for i in range(len(points) - 1)]
    target = k * sum(lengths)
    for index, length in enumerate(lengths):
        if target <= length or index == len(lengths) - 1:
            part = 0.0 if length == 0 else min(1.0, target / length)
            (x0, y0), (x1, y1) = points[index], points[index + 1]
            return x0 + (x1 - x0) * part, y0 + (y1 - y0) * part
        target -= length
    return points[-1]


def hacktoberfest_branch(t: float, size: int) -> Image.Image:
    bg = (34, 26, 52)
    canvas = _Canvas(size, bg, (70, 40, 70))
    _leaves(canvas, t, 41, 8)
    main = [(0.34, 0.9), (0.34, 0.3)]
    branch = [(0.34, 0.78), (0.66, 0.66), (0.66, 0.46), (0.34, 0.3)]
    canvas.line(*main[0], *main[1], TEAL, 0.022)
    for a, b in zip(branch, branch[1:]):
        canvas.line(*a, *b, ORANGE, 0.022)
    for x, y in ((0.34, 0.9), (0.34, 0.78), (0.34, 0.6), (0.34, 0.45)):
        canvas.circle(x, y, 0.03, TEAL)
    for x, y in branch[1:3]:
        canvas.circle(x, y, 0.03, ORANGE)
    # A commit rides the branch home; the merge commit swells as it lands.
    x, y = _along(branch, t)
    canvas.circle(x, y, 0.03, (255, 255, 255))
    canvas.circle(x, y, 0.018, GOLD)
    landing = max(0.0, math.cos(TAU * t)) ** 3
    radius = 0.1 + 0.02 * landing
    canvas.circle(0.34, 0.3, radius + 0.015, _mix(bg, GOLD, 0.3 + 0.6 * landing))
    canvas.circle(0.34, 0.3, radius, GOLD)
    canvas.face(0.34, 0.285, 0.042, blink=0.5 < t < 0.56)
    for index, (sx, sy) in enumerate(((0.8, 0.2), (0.86, 0.84), (0.12, 0.14))):
        pulse = 0.5 + 0.5 * math.sin(TAU * (t * 2 + index / 3))
        _sparkle(canvas, sx, sy, 0.05 * pulse, CREAM)
    return canvas.done(size)


def birthday_cake(t: float, size: int) -> Image.Image:
    canvas = _Canvas(size, (220, 242, 255), (188, 224, 255))
    _falling(canvas, t, 37, 22, (GOLD, PINK, BLUE, TEAL, VIOLET), flake=False)
    bob = 0.006 * math.sin(TAU * t)
    canvas.draw.ellipse([canvas.p(0.14), canvas.p(0.8), canvas.p(0.86), canvas.p(0.9)], fill=(255, 255, 255))
    canvas.rect(0.22, 0.56 + bob, 0.78, 0.85, (255, 170, 190), r=0.04)
    canvas.rect(0.3, 0.38 + bob, 0.7, 0.58 + bob, CREAM, r=0.04)
    for index in range(7):
        drip = 0.012 * math.sin(TAU * t + index)
        canvas.circle(0.26 + index * 0.08, 0.57 + bob + abs(drip), 0.042, CREAM)
    for index in range(5):
        canvas.circle(0.34 + index * 0.08, 0.385 + bob, 0.035, (255, 99, 132))
    for index, x in enumerate((0.4, 0.5, 0.6)):
        color = (BLUE, GOLD, TEAL)[index]
        canvas.rect(x - 0.014, 0.25 + bob, x + 0.014, 0.37 + bob, color, r=0.006)
        flame = 0.5 + 0.5 * math.sin(TAU * (3 * t + index / 3))
        lean = 0.008 * math.sin(TAU * (2 * t + index / 3))
        canvas.draw.ellipse(
            [canvas.p(x - 0.022 + lean), canvas.p(0.17 + bob - 0.02 * flame), canvas.p(x + 0.022 + lean), canvas.p(0.25 + bob)],
            fill=ORANGE,
        )
        canvas.draw.ellipse(
            [canvas.p(x - 0.011 + lean), canvas.p(0.2 + bob - 0.01 * flame), canvas.p(x + 0.011 + lean), canvas.p(0.245 + bob)],
            fill=GOLD,
        )
    canvas.face(0.5, 0.68 + bob, 0.07, blink=0.15 < t < 0.22)
    return canvas.done(size)


def birthday_balloons(t: float, size: int) -> Image.Image:
    canvas = _Canvas(size, (255, 246, 214), (255, 226, 170))
    _falling(canvas, t, 43, 18, (PINK, BLUE, TEAL, VIOLET, RED), flake=False)
    knot = (0.5, 0.9)
    balloons = ((0.27, 0.4, 0.13, BLUE, 0.0), (0.73, 0.38, 0.13, TEAL, 0.33), (0.5, 0.33, 0.17, RED, 0.66))
    for x, y, r, color, phase in balloons:
        bx = x + 0.02 * math.sin(TAU * (t + phase))
        by = y + 0.025 * math.sin(TAU * (t + phase) + 1.5)
        canvas.line(bx, by + r * 1.2, knot[0], knot[1], (150, 120, 90), 0.006)
        canvas.draw.ellipse(
            [canvas.p(bx - r), canvas.p(by - r * 1.15), canvas.p(bx + r), canvas.p(by + r * 1.15)], fill=color
        )
        canvas.poly([(bx, by + r * 1.1), (bx - r * 0.14, by + r * 1.32), (bx + r * 0.14, by + r * 1.32)], color)
        canvas.draw.ellipse(
            [canvas.p(bx - r * 0.6), canvas.p(by - r * 0.85), canvas.p(bx - r * 0.25), canvas.p(by - r * 0.35)],
            fill=_mix(color, (255, 255, 255), 0.55),
        )
        if color == RED:
            canvas.face(bx, by + 0.01, 0.06, blink=0.8 < t < 0.87)
    canvas.circle(knot[0], knot[1], 0.014, (150, 120, 90))
    return canvas.done(size)


# group, output stem, scene
SCENES = (
    ("christmas", "tree", christmas_tree),
    ("christmas", "gift", christmas_gift),
    ("newyear", "fireworks", newyear_fireworks),
    ("newyear", "clock", newyear_clock),
    ("halloween", "pumpkin", halloween_pumpkin),
    ("halloween", "ghost", halloween_ghost),
    ("hacktoberfest", "leaves", hacktoberfest_leaves),
    ("hacktoberfest", "branch", hacktoberfest_branch),
    ("birthday", "cake", birthday_cake),
    ("birthday", "balloons", birthday_balloons),
)


def frames(scene, count: int, size: int) -> list:
    return [scene(index / count, size) for index in range(count)]
