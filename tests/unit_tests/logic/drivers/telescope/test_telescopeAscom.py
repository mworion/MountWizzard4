# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion

import pytest
from mw4.base import platformInfo
from mw4.base.signalsDevices import Signals
from mw4.logic.drivers.telescope.telescopeAscom import TelescopeAscom
from typing import ClassVar
from unittest import mock

if not platformInfo.IS_WINDOWS:
    pytest.skip("skipping windows-only tests", allow_module_level=True)


class Parent:
    def __init__(self, app):
        self.app = app

    data: ClassVar = {}
    signals = Signals()
    deviceType = ""
    loadConfig = True


@pytest.fixture(autouse=True, scope="module")
def function(makeApp):
    func = TelescopeAscom(parent=Parent(makeApp()))
    func.device = mock.MagicMock()
    func.device.ApertureDiameter = 0.1
    func.device.FocalLength = 0.57
    yield func


def test_getInitialConfig_floatValues(function):
    with (
        mock.patch.object(function, "getAndStoreDeviceProp"),
        mock.patch.object(function, "getDeviceProp", return_value=0.57),
    ):
        function.getInitialConfig()
    assert function.data["TELESCOPE_INFO.TELESCOPE_APERTURE"] == 570.0
    assert function.data["TELESCOPE_INFO.TELESCOPE_FOCAL_LENGTH"] == 570.0


def test_getInitialConfig_nonFloatValues(function):
    with (
        mock.patch.object(function, "getAndStoreDeviceProp"),
        mock.patch.object(function, "getDeviceProp", return_value=None),
    ):
        function.getInitialConfig()
