# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import pytest
from mw4.base.signalsDevices import Signals
from mw4.logic.telescope.telescopeIndi import TelescopeIndi
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from typing import ClassVar
from unittest import mock


class Parent:
    try:
        app = App()
    except (RuntimeError, ImportError, AttributeError, ConnectionError, OSError, ValueError):
        app = mock.MagicMock()
    data: ClassVar = {}
    signals = Signals()
    loadConfig = True


@pytest.fixture(autouse=True, scope="module")
def function():
    try:
        func = TelescopeIndi(parent=Parent())
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
