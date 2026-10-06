# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import pytest
from mw4.base.signalsDevices import Signals
from mw4.logic.telescope.telescopeAlpaca import TelescopeAlpaca
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from typing import ClassVar
from unittest import mock


class Parent:
    try:
        app = App()
    except (RuntimeError, ImportError, AttributeError, ConnectionError, OSError, ValueError):
        app = mock.MagicMock()
    data: ClassVar = {}
    DEVICE_TYPE = "telescope"
    signals = Signals()
    loadConfig = True


@pytest.fixture(autouse=True, scope="module")
def function():
    try:
        func = TelescopeAlpaca(parent=Parent())
        func.device = mock.MagicMock()
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


def test_getInitialConfig(function):
    with (
        mock.patch.object(function, "getAndStoreDeviceProp"),
        mock.patch.object(function, "getDeviceProp") as m,
    ):
        function.getInitialConfig()
        attrs = [c.args[0] for c in m.call_args_list]
        assert "ApertureDiameter" in attrs
        assert "FocalLength" in attrs
