# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import numpy as np
from dataclasses import dataclass

SEGMENT_ANGLES = range(0, 360, 120)
# link pairs between center (0) and the three segment points (1..3)
TRIANGLE_LINKS = [[0, 1], [0, 2], [0, 3], [1, 2], [2, 3], [3, 1]]


@dataclass(frozen=True)
class TriangleGeometry:
    cx: float
    cy: float
    rings: list[tuple[float, float, float, float]]
    separators: list[tuple[float, float, float, float]]
    textPositions: list[tuple[float, float]]


def calcTriangleGeometry(w: float, h: float, offsetTiltAngle: float) -> TriangleGeometry:
    r = min([h, w]) / 2
    cx = w / 2
    cy = h / 2
    r25 = 0.25 * r
    r62 = 0.625 * r
    rings = [(cx - rad, cy - rad, 2 * rad, 2 * rad) for rad in [r, r25]]
    separators = []
    textPositions = []
    for angle in SEGMENT_ANGLES:
        angleSep = np.radians(angle + offsetTiltAngle + 210)
        angleText = np.radians(angle + offsetTiltAngle + 270)
        separators.append(
            (
                cx + r25 * np.cos(angleSep),
                cy + r25 * np.sin(angleSep),
                cx + r * np.cos(angleSep),
                cy + r * np.sin(angleSep),
            )
        )
        textPositions.append((cx + r62 * np.cos(angleText), cy + r62 * np.sin(angleText)))
    return TriangleGeometry(cx, cy, rings, separators, textPositions)
