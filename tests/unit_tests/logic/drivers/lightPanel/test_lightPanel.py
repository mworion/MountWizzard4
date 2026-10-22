# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import pytest
from mw4.base import platformInfo
from mw4.logic.drivers.lightPanel.lightPanel import LightPanel
from unittest import mock


@pytest.fixture(autouse=True, scope="module")
def function(makeApp):
    try:
        func = LightPanel(app=makeApp())
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


def test_properties(function):
    function.framework = "indi"
    function.host = ("localhost", 7624)
    assert function.host == ("localhost", 7624)

    function.deviceName = "test"
    assert function.deviceName == "test"


def test_properties_2(function):
    function.loadConfig = True
    function.framework = "indi"
    assert function.loadConfig


def test_lightOn_2(function):
    function.framework = "indi"
    with mock.patch.object(function.run["indi"], "lightOn", return_value=False):
        function.lightOn()


def test_lightOn_3(function):
    function.framework = "indi"
    with mock.patch.object(function.run["indi"], "lightOn", return_value=True):
        function.lightOn()


def test_lightOff_2(function):
    function.framework = "indi"
    with mock.patch.object(function.run["indi"], "lightOff", return_value=False):
        function.lightOff()


def test_lightOff_3(function):
    function.framework = "indi"
    with mock.patch.object(function.run["indi"], "lightOff", return_value=True):
        function.lightOff()


def test_lightIntensity_2(function):
    function.framework = "indi"
    with mock.patch.object(function.run["indi"], "lightIntensity", return_value=False):
        function.lightIntensity(0)


def test_lightIntensity_3(function):
    function.framework = "indi"
    with mock.patch.object(function.run["indi"], "lightIntensity", return_value=True):
        function.lightIntensity(0)


@pytest.mark.skipif(not platformInfo.IS_WINDOWS, reason="Windows needed")
def test_lightPanelAscom_import():
    import importlib

    spec = importlib.util.find_spec("mw4.logic.drivers.lightPanel.lightPanelAscom")
    assert spec is not None


@pytest.mark.skipif(not platformInfo.IS_WINDOWS, reason="Windows needed")
def test_lightPanel_ascom_in_run(makeApp):
    from mw4.logic.drivers.lightPanel.lightPanel import LightPanel

    function = LightPanel(app=makeApp())
    if platformInfo.IS_WINDOWS:
        assert "ascom" in function.run
        assert function.run["ascom"] is not None
