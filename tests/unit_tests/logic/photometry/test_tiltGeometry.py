# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import pytest
from mw4.logic.photometry.tiltGeometry import calcTriangleGeometry


def test_calcTriangleGeometry_rings():
    geo = calcTriangleGeometry(200, 100, 0)
    assert (geo.cx, geo.cy) == (100, 50)
    assert geo.rings[0] == (50, 0, 100, 100)
    assert geo.rings[1] == (87.5, 37.5, 25, 25)


def test_calcTriangleGeometry_segments():
    geo = calcTriangleGeometry(200, 200, 0)
    assert len(geo.separators) == 3
    assert len(geo.textPositions) == 3
    x1, y1, x2, y2 = geo.separators[0]
    assert (x1, y1) == pytest.approx((100 + 25 * -0.8660254, 100 + 25 * -0.5))
    assert (x2, y2) == pytest.approx((100 + 100 * -0.8660254, 100 + 100 * -0.5))
    assert geo.textPositions[0] == pytest.approx((100, 100 - 62.5))


def test_calcTriangleGeometry_offsetRotates():
    base = calcTriangleGeometry(200, 200, 0)
    rotated = calcTriangleGeometry(200, 200, 120)
    assert rotated.separators[0] == pytest.approx(base.separators[1])
