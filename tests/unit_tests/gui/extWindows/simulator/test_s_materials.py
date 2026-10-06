# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion

import pytest
from mw4.gui.extWindows.simulator.materials import Materials


@pytest.fixture(autouse=True, scope="module")
def module_setup_teardown():
    global app
    app = Materials()
    yield


def test_1():
    assert app.white
