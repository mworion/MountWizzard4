# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import pytest
from mw4.base.driverProtocol import FrameworkDriver
from mw4.logic.drivers.frameworks.driverProtocols import (
    CameraDriver,
    CoverDriver,
    DomeDriver,
    FilterDriver,
    FocuserDriver,
    LightPanelDriver,
    PlateSolveDriver,
    PowerSwitchDriver,
)

FAMILIES = {
    "camera": CameraDriver,
    "dome": DomeDriver,
    "focuser": FocuserDriver,
    "filter": FilterDriver,
    "cover": CoverDriver,
    "lightPanel": LightPanelDriver,
    "power": PowerSwitchDriver,
}


@pytest.fixture
def function(makeApp):
    return makeApp()


@pytest.mark.parametrize("name", FAMILIES)
def test_backendsConformToFamilyProtocol(function, name):
    device = getattr(function.dReg, name)
    assert device.run
    for backend in device.run.values():
        assert isinstance(backend, FrameworkDriver)
        assert isinstance(backend, FAMILIES[name])


def test_plateSolveBackendsConform(function):
    plateSolve = function.dReg.plateSolve
    assert plateSolve.run
    for backend in plateSolve.run.values():
        assert isinstance(backend, PlateSolveDriver)
