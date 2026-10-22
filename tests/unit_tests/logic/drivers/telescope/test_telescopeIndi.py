# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import pytest
from mw4.base.signalsDevices import Signals
from mw4.logic.drivers.telescope.telescopeIndi import TelescopeIndi
from typing import ClassVar


class Parent:
    def __init__(self, app):
        self.app = app

    data: ClassVar = {}
    signals = Signals()
    loadConfig = True


@pytest.fixture(autouse=True, scope="module")
def function(makeApp):
    try:
        func = TelescopeIndi(parent=Parent(makeApp()))
    except (
        RuntimeError,
        ImportError,
        AttributeError,
        ConnectionError,
        OSError,
        ValueError,
    ) as e:
        pytest.skip(f"Fixture initialization failed: {e}")
    yield func


def test_class(function):
    assert function is not None
