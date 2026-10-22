# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import pytest
from mw4.base import platformInfo
from mw4.logic.drivers.frameworks.deviceFacade import DeviceFacade
from unittest import mock


class Backend:
    def __init__(self, parent):
        self.parent = parent
        self.startCommunication = mock.Mock()
        self.stopCommunication = mock.Mock()


@pytest.fixture
def function(makeApp):
    return DeviceFacade(app=makeApp())


def test_init(function):
    assert function.framework == ""
    assert function.data == {}
    assert function.run == {}
    assert function.threadPool is function.app.threadPool


def test_buildBackends(function):
    with mock.patch.object(platformInfo, "IS_WINDOWS", False):
        function.buildBackends({"indi": Backend, "alpaca": Backend}, {"ascom": lambda: Backend(1)})
    assert set(function.run) == {"indi", "alpaca"}
    assert function.run["indi"].parent is function


def test_buildBackends_windows(function):
    with mock.patch.object(platformInfo, "IS_WINDOWS", True):
        function.buildBackends({"indi": Backend}, {"ascom": lambda: Backend(function)})
    assert set(function.run) == {"indi", "ascom"}


def test_buildBackends_noWindowsBackends(function):
    function.buildBackends({"indi": Backend})
    assert set(function.run) == {"indi"}


def test_startStopCommunication(function):
    function.buildBackends({"indi": Backend})
    function.framework = "indi"
    function.startCommunication()
    function.stopCommunication()
    function.run["indi"].startCommunication.assert_called_once()
    function.run["indi"].stopCommunication.assert_called_once()
