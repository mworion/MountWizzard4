# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import importlib
import pytest
from mw4.base import platformInfo
from unittest import mock


@pytest.mark.parametrize(
    ("moduleName", "windowsBackendName"),
    [
        ("mw4.logic.drivers.cover.cover", "CoverAscom"),
        ("mw4.logic.drivers.dome.dome", "DomeAscom"),
        ("mw4.logic.drivers.environment.sensorWeather", "SensorWeatherAscom"),
        ("mw4.logic.drivers.filter.filter", "FilterAscom"),
        ("mw4.logic.drivers.focuser.focuser", "FocuserAscom"),
        ("mw4.logic.drivers.frameworks.ascomClass", "CoInitialize"),
        ("mw4.logic.drivers.lightPanel.lightPanel", "LightPanelAscom"),
        ("mw4.logic.drivers.telescope.telescope", "TelescopeAscom"),
    ],
)
def test_nonWindowsAscomImports(moduleName: str, windowsBackendName: str) -> None:
    module = importlib.import_module(moduleName)
    originalPlatform = platformInfo.IS_WINDOWS
    try:
        module.__dict__.pop(windowsBackendName, None)
        with mock.patch.object(platformInfo, "IS_WINDOWS", False):
            importlib.reload(module)
            assert windowsBackendName not in module.__dict__
    finally:
        with mock.patch.object(platformInfo, "IS_WINDOWS", originalPlatform):
            importlib.reload(module)
