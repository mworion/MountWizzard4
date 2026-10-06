# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import pytest
from mw4.gui.extWindows.image.imageSignals import ImageWindowSignals


@pytest.fixture(autouse=True, scope="module")
def function():
    func = ImageWindowSignals()
    yield func


def test_init(function):
    assert function
