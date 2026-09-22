############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10_micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2026 by mworion
# License APL2.0
#
###########################################################
"""Pure numeric photometry analysis without any Qt dependency.

This module turns the flat source arrays and background maps produced by the
photometry core into the derived maps and tilt metrics the image window
displays. All functions are pure NumPy/SciPy and return plain dataclasses, so
they can be tested and reused independently of the Qt adapter and the GUI.
"""

import numpy as np
from dataclasses import dataclass
from scipy.interpolate import griddata
from scipy.ndimage import uniform_filter


@dataclass
class GridGeometry:
    h: int
    w: int
    filterConstW: int
    filterConstH: int
    xm: np.ndarray
    ym: np.ndarray


@dataclass
class HFRResult:
    grid: np.ndarray
    hfrMin: float
    hfrMax: float
    percentile: float
    median: float
    inner: float
    outer: float


@dataclass
class RoundnessResult:
    grid: np.ndarray
    roundnessMin: float
    roundnessMax: float
    percentile: float


@dataclass
class BackgroundResult:
    background: np.ndarray
    backgroundMin: float
    backgroundMax: float


@dataclass
class TiltSquareView:
    points: np.ndarray
    best: float
    worst: float
    tiltDiff: float
    tiltPercent: float
    offAxisDiff: float
    offAxisPercent: float


@dataclass
class TiltTriangleView:
    segData: np.ndarray
    points: np.ndarray
    best: float
    worst: float
    tiltDiff: float
    tiltPercent: float
    offAxisDiff: float
    offAxisPercent: float


def computeGridGeometry(image: np.ndarray, filterScale: int) -> GridGeometry:
    h, w = image.shape
    filterConstW = int(w / (filterScale * 3))
    filterConstH = int(h / (filterScale * 3))
    rangeX = np.linspace(0, w, int(w / filterScale))
    rangeY = np.linspace(0, h, int(h / filterScale))
    xm, ym = np.meshgrid(rangeX, rangeY)
    return GridGeometry(h, w, filterConstW, filterConstH, xm, ym)


def computeHFR(
    geom: GridGeometry, xCoord: np.ndarray, yCoord: np.ndarray, hfr: np.ndarray
) -> HFRResult:
    x = xCoord - geom.w / 2
    y = yCoord - geom.h / 2
    radius = np.sqrt(x * x + y * y)
    diag = np.sqrt(geom.h * geom.h / 4 + geom.w * geom.w / 4)
    maskOuter = diag * 0.75 < radius
    maskInner = diag * 0.25 > radius
    outerHFR = hfr[maskOuter]
    innerHFR = hfr[maskInner]
    inner = float(np.median(innerHFR)) if innerHFR.size > 0 else np.nan
    outer = float(np.median(outerHFR)) if outerHFR.size > 0 else np.nan
    percentile = np.percentile(hfr, 90)
    median = np.median(hfr)

    img = griddata(
        (xCoord, yCoord),
        hfr,
        (geom.xm, geom.ym),
        method="nearest",
        fill_value=np.min(hfr),
    )
    grid = uniform_filter(img, size=[geom.filterConstH, geom.filterConstW])
    minB, maxB = np.percentile(grid, (50, 95))
    return HFRResult(grid, minB, maxB, percentile, median, inner, outer)


def computeRoundness(
    geom: GridGeometry, xCoord: np.ndarray, yCoord: np.ndarray, elongation: np.ndarray
) -> RoundnessResult:
    minB, maxB = np.percentile(elongation, (50, 95))
    img = griddata(
        (xCoord, yCoord),
        elongation,
        (geom.xm, geom.ym),
        method="linear",
        fill_value=np.min(elongation),
    )
    grid = uniform_filter(img, size=[geom.filterConstH, geom.filterConstW])
    percentile = np.percentile(elongation, 90)
    return RoundnessResult(grid, minB, maxB, percentile)


def computeTiltSquare(
    geom: GridGeometry, xCoord: np.ndarray, yCoord: np.ndarray, hfr: np.ndarray
) -> np.ndarray:
    stepY = int(geom.h / 3)
    stepX = int(geom.w / 3)
    xRange = [0, stepX, 2 * stepX, 3 * stepX]
    yRange = [0, stepY, 2 * stepY, 3 * stepY]
    segHFR = np.zeros((3, 3))
    for ix in range(3):
        for iy in range(3):
            xMin = xRange[ix]
            xMax = xRange[ix + 1]
            yMin = yRange[iy]
            yMax = yRange[iy + 1]
            sel = hfr[(xCoord > xMin) & (xCoord < xMax) & (yCoord > yMin) & (yCoord < yMax)]
            if sel.size > 0:
                segHFR[ix][iy] = np.median(sel)
    return segHFR


def computeTiltTriangle(
    geom: GridGeometry, xCoord: np.ndarray, yCoord: np.ndarray, hfr: np.ndarray
) -> np.ndarray:
    x = xCoord - geom.w / 2
    y = yCoord - geom.h / 2
    radius = min(geom.h / 2, geom.w / 2)
    mask1 = np.sqrt(geom.h * geom.h + geom.w * geom.w) * 0.25 < radius
    mask2 = np.sqrt(geom.h * geom.h + geom.w * geom.w) > radius
    segHFR = np.zeros(36)
    angles = np.mod(np.arctan2(y, x), 2 * np.pi)
    rangeA = np.radians(range(0, 361, 10))
    for i in range(36):
        mask3 = rangeA[i] < angles
        mask4 = rangeA[i + 1] > angles
        sel = hfr[mask1 & mask2 & mask3 & mask4]
        if sel.size > 0:
            segHFR[i] = np.median(sel)
    return np.concatenate([segHFR, segHFR])


def computeAberrationImage(image: np.ndarray, aberrationSize: int) -> tuple[np.ndarray, bool]:
    size = aberrationSize
    h, w = image.shape
    if w < 3 * size or h < 3 * size:
        return image, False

    dw = int((w - 3 * size) / 2)
    dh = int((h - 3 * size) / 2)
    img = np.delete(image, np.s_[size : size + dh], axis=0)
    img = np.delete(img, np.s_[size * 2 : size * 2 + dh], axis=0)
    img = np.delete(img, np.s_[size : size + dw], axis=1)
    img = np.delete(img, np.s_[size * 2 : size * 2 + dw], axis=1)
    return img, True


def computeBackground(
    geom: GridGeometry, backSignal: np.ndarray, globalback: float
) -> BackgroundResult:
    maxB = float(np.max(backSignal)) / globalback
    minB = float(np.min(backSignal)) / globalback
    img = backSignal / globalback
    background = uniform_filter(img, size=[geom.filterConstH, geom.filterConstW])
    return BackgroundResult(background, minB, maxB)


def computeBackgroundRMS(geom: GridGeometry, backRMS: np.ndarray) -> np.ndarray:
    return uniform_filter(backRMS, size=[geom.filterConstH, geom.filterConstW])


def computeTiltSquareView(
    segHFR: np.ndarray, w: int, h: int, hfrMedian: float, hfrOuter: float
) -> TiltSquareView:
    w3 = w / 3
    h3 = h / 3
    corners = np.array(
        [
            segHFR[0][2],
            segHFR[1][2],
            segHFR[2][2],
            segHFR[0][1],
            segHFR[2][1],
            segHFR[0][0],
            segHFR[1][0],
            segHFR[2][0],
        ]
    )
    vectors = np.array(
        [
            [-w3, h3],
            [0, h3],
            [w3, h3],
            [-w3, 0],
            [w3, 0],
            [-w3, -h3],
            [0, -h3],
            [w3, -h3],
        ]
    )
    best = float(np.min(corners))
    worst = float(np.max(corners))
    centre = np.array([w / 2, h / 2])
    points = np.array(
        [vector * corner / worst + centre for vector, corner in zip(vectors, corners)]
    )
    tiltDiff = worst - best
    tiltPercent = 100 * tiltDiff / hfrMedian
    offAxisDiff = hfrOuter - segHFR[1][1]
    offAxisPercent = 100 * offAxisDiff / hfrMedian
    return TiltSquareView(
        points, best, worst, tiltDiff, tiltPercent, offAxisDiff, offAxisPercent
    )


def computeTiltTriangleView(
    segHFR: np.ndarray,
    offsetTiltAngle: float,
    w: int,
    h: int,
    hfrMedian: float,
    hfrInner: float,
    hfrOuter: float,
) -> TiltTriangleView:
    r95 = 0.95 * min(h, w) / 2
    centre = np.array([w / 2, h / 2])
    segData = np.zeros(3)
    vectors = np.zeros((3, 2))
    for i, angle in enumerate(range(0, 360, 120)):
        angleText = np.radians(angle + offsetTiltAngle + 270)
        startIndexSeg = int((angle + offsetTiltAngle + 210) / 10)
        endIndexSeg = int((angle + offsetTiltAngle + 330) / 10)
        segData[i] = np.mean(segHFR[startIndexSeg:endIndexSeg])
        vectors[i][0] = r95 * np.cos(angleText)
        vectors[i][1] = r95 * np.sin(angleText)

    best = float(np.min(segData))
    worst = float(np.max(segData))
    tiltDiff = worst - best
    tiltPercent = 100 * tiltDiff / hfrMedian
    points = np.array(
        [centre]
        + [vector * corner / worst + centre for vector, corner in zip(vectors, segData)]
    )
    offAxisDiff = hfrOuter - hfrInner
    offAxisPercent = 100 * offAxisDiff / hfrMedian
    return TiltTriangleView(
        segData, points, best, worst, tiltDiff, tiltPercent, offAxisDiff, offAxisPercent
    )


def tiltHint(tiltPercent: float, tiltTable: dict) -> str:
    hint = ""
    for hint, limit in tiltTable.items():
        if tiltPercent < limit:
            break
    return hint
