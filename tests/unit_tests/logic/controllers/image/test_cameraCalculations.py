# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import pytest
from mw4.logic.controllers.image.cameraCalculations import (
    CameraCapabilities,
    RangeSpec,
    cameraCapabilities,
    describeRange,
    filterNames,
    filterNumberForName,
    filterSlotRange,
    hidDomeAction,
    optimalBinning,
    pickListEntry,
    strictPairState,
    switchPairState,
)


@pytest.mark.parametrize(
    "index, expected", [(1, "a"), (2, "b"), (3, "c"), (9, "c"), (0, "c"), (-4, "c")]
)
def test_pickListEntry(index, expected):
    assert pickListEntry(index, ["a", "b", "c"]) == expected


def test_filterSlotRange_indi():
    data = {"FILTER_NAME.FILTER_SLOT_NAME_1": "L", "FILTER_NAME.FILTER_SLOT_NAME_2": "R", "x": 1}
    assert filterSlotRange(data) == (1, 2)


def test_filterSlotRange_alpaca():
    data = {"FILTER_NAME.FILTER_SLOT_NAME_0": "L", "FILTER_NAME.FILTER_SLOT_NAME_1": "R"}
    assert filterSlotRange(data) == (0, 1)


def test_describeRange_list():
    data = {"CCD_GAIN.GAIN_LIST": ("a", "b"), "CCD_GAIN.GAIN_MIN": 0, "CCD_GAIN.GAIN_MAX": 10}
    spec = describeRange(data, "CCD_GAIN.GAIN")
    assert spec.kind == "list"
    assert spec.values == ["a", "b"]


def test_describeRange_range():
    data = {"CCD_GAIN.GAIN_LIST": None, "CCD_GAIN.GAIN_MIN": 0.0, "CCD_GAIN.GAIN_MAX": 100.0}
    spec = describeRange(data, "CCD_GAIN.GAIN")
    assert spec == RangeSpec(kind="range", minVal=0, maxVal=100, step=5)


@pytest.mark.parametrize(
    "data",
    [
        {},
        {"CCD_GAIN.GAIN_MIN": 0},
        {"CCD_GAIN.GAIN_MAX": 10},
        {"CCD_GAIN.GAIN_MIN": None, "CCD_GAIN.GAIN_MAX": None},
    ],
)
def test_describeRange_free(data):
    assert describeRange(data, "CCD_GAIN.GAIN").kind == "free"


def test_cameraCapabilities_none():
    assert cameraCapabilities({}) == CameraCapabilities(False, False, False, False)


@pytest.mark.parametrize(
    "key, flag",
    [
        ("CCD_TEMPERATURE.CCD_TEMPERATURE_VALUE", "hasCooler"),
        ("CCD_GAIN.GAIN", "hasGain"),
        ("CCD_OFFSET.OFFSET", "hasOffset"),
        ("CCD_INFO.CCD_MAX_X", "hasSensor"),
    ],
)
def test_cameraCapabilities_flag(key, flag):
    caps = cameraCapabilities({key: 0})
    assert getattr(caps, flag)
    assert sum(vars(caps).values()) == 1


@pytest.mark.parametrize(
    "pixelX, pixelY, expected",
    [(0, 0, 1), (1000, 4000, 1), (4000, 4000, 2), (8000, 6000, 3)],
)
def test_optimalBinning(pixelX, pixelY, expected):
    assert optimalBinning(pixelX, pixelY) == expected


@pytest.mark.parametrize(
    "value, expected", [(1, (True, False)), (None, (False, False)), (0, (False, True))]
)
def test_switchPairState(value, expected):
    assert switchPairState(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [(True, (True, False)), (False, (False, True)), (None, (False, False)), (1, (False, False))],
)
def test_strictPairState(value, expected):
    assert strictPairState(value) == expected


def test_filterNames():
    data = {"A": 1, "FILTER_NAME.FILTER_SLOT_NAME_1": "L", "FILTER_NAME.FILTER_SLOT_NAME_2": "R"}
    assert filterNames(data) == ["L", "R"]


def test_filterNumberForName_indi():
    data = {"FILTER_NAME.FILTER_SLOT_NAME_1": "L", "FILTER_NAME.FILTER_SLOT_NAME_2": "R"}
    assert filterNumberForName(data, "R") == 2


def test_filterNumberForName_alpaca():
    data = {"FILTER_NAME.FILTER_SLOT_NAME_0": "L", "FILTER_NAME.FILTER_SLOT_NAME_1": "R"}
    assert filterNumberForName(data, "R") == 1


@pytest.mark.parametrize(
    "turnVal, openVal, expected",
    [
        (10, 10, ("ccw", "open")),
        (250, 250, ("cw", "close")),
        (128, 128, ("abort", None)),
    ],
)
def test_hidDomeAction(turnVal, openVal, expected):
    assert hidDomeAction(turnVal, openVal) == expected
