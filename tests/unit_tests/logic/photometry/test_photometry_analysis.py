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

import numpy as np
from mw4.logic.photometry.photometry_analysis import (
    computeAberrationImage,
    computeBackground,
    computeBackgroundRMS,
    computeGridGeometry,
    computeHFR,
    computeRoundness,
    computeTiltSquare,
    computeTiltSquareView,
    computeTiltTriangle,
    computeTiltTriangleView,
    tiltHint,
)

TILT = {
    "none": 5,
    "almost none": 10,
    "mild": 15,
    "moderate": 20,
    "severe": 30,
    "extreme": 1000,
}


def makeGeom(h=200, w=200):
    return computeGridGeometry(np.zeros((h, w)), 10)


def test_computeGridGeometry():
    geom = computeGridGeometry(np.zeros((300, 400)), 10)
    assert geom.h == 300
    assert geom.w == 400
    assert geom.filterConstW == int(400 / 30)
    assert geom.filterConstH == int(300 / 30)
    assert geom.xm.shape == geom.ym.shape


def test_computeHFR_inner():
    geom = makeGeom()
    xCoord = np.full(20, 100.0)
    yCoord = np.full(20, 100.0)
    hfr = np.linspace(1, 2, 20)
    res = computeHFR(geom, xCoord, yCoord, hfr)
    assert res.grid.shape == (20, 20)
    assert not np.isnan(res.inner)
    assert np.isnan(res.outer)


def test_computeHFR_outer():
    geom = makeGeom()
    xCoord = np.full(20, 199.0)
    yCoord = np.full(20, 199.0)
    hfr = np.linspace(1, 2, 20)
    res = computeHFR(geom, xCoord, yCoord, hfr)
    assert np.isnan(res.inner)
    assert not np.isnan(res.outer)


def test_computeRoundness():
    geom = makeGeom()
    rng = np.random.default_rng(1)
    xCoord = rng.uniform(0, 200, 20)
    yCoord = rng.uniform(0, 200, 20)
    elongation = rng.random(20) + 1
    res = computeRoundness(geom, xCoord, yCoord, elongation)
    assert res.grid.shape == (20, 20)
    assert res.roundnessMin <= res.roundnessMax


def test_computeTiltSquare():
    geom = makeGeom(300, 300)
    xCoord = np.linspace(0, 300, 20)
    yCoord = np.linspace(0, 300, 20)
    hfr = np.linspace(1, 2, 20)
    segHFR = computeTiltSquare(geom, xCoord, yCoord, hfr)
    assert segHFR.shape == (3, 3)


def test_computeTiltTriangle():
    geom = makeGeom(300, 300)
    xCoord = np.linspace(0, 300, 40)
    yCoord = np.linspace(0, 300, 40)
    hfr = np.linspace(1, 2, 40)
    segHFR = computeTiltTriangle(geom, xCoord, yCoord, hfr)
    assert segHFR.size == 72


def test_computeAberrationImage_cropped():
    image = np.random.rand(1000, 1000) + 1
    img, cropped = computeAberrationImage(image, 250)
    assert cropped
    assert img.shape == (750, 750)


def test_computeAberrationImage_tooSmall():
    image = np.random.rand(100, 100) + 1
    img, cropped = computeAberrationImage(image, 250)
    assert not cropped
    assert img.shape == (100, 100)


def test_computeBackground():
    geom = makeGeom(100, 100)
    backSignal = np.random.rand(100, 100) + 1
    res = computeBackground(geom, backSignal, 2.0)
    assert res.background.shape == (100, 100)
    assert res.backgroundMin <= res.backgroundMax


def test_computeBackgroundRMS():
    geom = makeGeom(100, 100)
    backRMS = np.random.rand(100, 100) + 1
    res = computeBackgroundRMS(geom, backRMS)
    assert res.shape == (100, 100)


def test_computeTiltSquareView():
    segHFR = np.arange(1, 10, dtype=float).reshape(3, 3)
    view = computeTiltSquareView(segHFR, 300, 300, 2.0, 3.0)
    assert view.points.shape == (8, 2)
    assert view.worst >= view.best
    assert view.tiltDiff == view.worst - view.best


def test_computeTiltTriangleView():
    segHFR = np.linspace(1, 2, 72)
    view = computeTiltTriangleView(segHFR, 0, 300, 300, 2.0, 1.5, 2.5)
    assert view.segData.size == 3
    assert view.points.shape == (4, 2)
    assert view.offAxisDiff == 2.5 - 1.5


def test_tiltHint_break():
    assert tiltHint(3, TILT) == "none"


def test_tiltHint_last():
    assert tiltHint(5000, TILT) == "extreme"
