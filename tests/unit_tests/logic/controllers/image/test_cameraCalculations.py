# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import pytest
from mw4.logic.controllers.image.cameraCalculations import filterSlotRange, pickListEntry


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
