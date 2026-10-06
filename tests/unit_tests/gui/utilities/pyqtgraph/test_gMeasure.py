# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion

import pytest
from mw4.gui.utilities.pyqtgraph.gMeasure import Measure


@pytest.fixture(autouse=True, scope="module")
def module(qapp):
    yield


def test_Measure():
    Measure()
