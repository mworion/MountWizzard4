# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import numpy as np
from mw4.logic.controllers.satellites.trackProgram import prepareTrajectory


def horizonPass(start, end, alt, az):
    return start, end, alt, az


def test_prepareTrajectory_noPass():
    result = prepareTrajectory(
        select=lambda: (0, 0), calc=lambda s, e: (None, None), horizon=horizonPass
    )
    assert result.reason == "noPass"
    assert not result.isValid


def test_prepareTrajectory_noData():
    result = prepareTrajectory(
        select=lambda: (1, 2),
        calc=lambda s, e: (np.array([10.0]), np.array([20.0])),
        horizon=lambda s, e, alt, az: (s, e, np.array([]), np.array([])),
    )
    assert result.reason == "noData"


def test_prepareTrajectory_filtered():
    result = prepareTrajectory(
        select=lambda: (1, 2),
        calc=lambda s, e: (np.array([10.0, 11.0]), np.array([20.0, 21.0])),
        horizon=lambda s, e, alt, az: (s + 0.5, e - 0.5, alt[1:], az[1:]),
    )
    assert result.isValid
    assert (result.start, result.end) == (1.5, 1.5)
    assert result.alt.degrees.tolist() == [11.0]
    assert result.az.degrees.tolist() == [21.0]


def test_prepareTrajectory_reduced():
    alt = np.linspace(10, 50, 1800)
    result = prepareTrajectory(
        select=lambda: (1, 2), calc=lambda s, e: (alt, alt), horizon=horizonPass
    )
    assert len(result.alt.degrees) == 900
