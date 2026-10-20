# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import pytest
from mw4.logic.photometry.imageStats import (
    calcFocus,
    calcFov,
    calcImageStats,
    calcOpticsLimits,
    calcResolution,
)


def test_calcResolution():
    resX, resY = calcResolution(1000, 4, 5)
    assert resX == pytest.approx(0.82506)
    assert resY == pytest.approx(1.031325)


@pytest.mark.parametrize("args", [(0, 4, 5), (1000, 0, 5), (1000, 4, 0)])
def test_calcResolution_missingValues(args):
    assert calcResolution(*args) == (None, None)


def test_calcOpticsLimits():
    dawes, rayleigh, magLimit = calcOpticsLimits(100)
    assert dawes == pytest.approx(1.16)
    assert rayleigh == pytest.approx(1.38)
    assert magLimit == pytest.approx(12.7)


def test_calcOpticsLimits_noAperture():
    assert calcOpticsLimits(0) == (None, None, None)


def test_calcFov():
    fovX, fovY, hint = calcFov(1000, 4, 4, 1000, 2000)
    assert fovX == pytest.approx(0.2291833)
    assert fovY == pytest.approx(0.4583667)
    assert hint == pytest.approx((fovX**2 + fovY**2) ** 0.5)


@pytest.mark.parametrize("args", [(0, 4, 4, 10, 10), (1000, 4, 0, 10, 10), (1000, 4, 4, 0, 10)])
def test_calcFov_missingValues(args):
    assert calcFov(*args) == (None, None, 0)


def test_calcFocus():
    ccd, red, green, blue = calcFocus(5, 4)
    assert ccd == 20
    assert red == pytest.approx(4.88 * 25 * 0.65)
    assert green == pytest.approx(4.88 * 25 * 0.51)
    assert blue == pytest.approx(4.88 * 25 * 0.475)


@pytest.mark.parametrize("args", [(None, 4), (5, 0)])
def test_calcFocus_missingValues(args):
    assert calcFocus(*args) == (None, None, None, None)


def test_calcImageStats():
    stats = calcImageStats(1000, 200, 4, 4, 1000, 2000)
    assert stats.speed == 5
    assert stats.focusCCD == 20
    assert stats.fovHint > 0


def test_calcImageStats_empty():
    stats = calcImageStats(0, 0, 0, 0, 0, 0)
    assert stats.speed is None
    assert stats.fovHint == 0
    assert stats.dawes is None
