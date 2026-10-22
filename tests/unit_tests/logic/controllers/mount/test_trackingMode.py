# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import pytest
from mw4.logic.controllers.mount.trackingMode import activeTrackingMode
from types import SimpleNamespace


def makeSetting(lunar=False, sidereal=False, solar=False):
    return SimpleNamespace(
        checkRateLunar=lambda: lunar,
        checkRateSidereal=lambda: sidereal,
        checkRateSolar=lambda: solar,
    )


@pytest.mark.parametrize(
    "status, following, sett, expected",
    [
        (None, False, makeSetting(), None),
        (0, True, makeSetting(), "followSat"),
        (0, False, makeSetting(lunar=True), "setLunarTracking"),
        (0, False, makeSetting(sidereal=True), "setSiderealTracking"),
        (0, False, makeSetting(solar=True), "setSolarTracking"),
        (0, False, makeSetting(), "unchanged"),
    ],
)
def test_activeTrackingMode(status, following, sett, expected):
    assert activeTrackingMode(status, following, sett) == expected
