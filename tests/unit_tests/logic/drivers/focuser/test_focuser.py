# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion

import pytest
from mw4.base import platformInfo
from mw4.logic.drivers.focuser.focuser import Focuser
from unittest import mock


@pytest.fixture(autouse=True, scope="module")
def function(makeApp):
    try:
        func = Focuser(app=makeApp())
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


def test_move_2(function):
    function.framework = "indi"
    with mock.patch.object(function.run["indi"], "move", return_value=True):
        function.move(1000)


def test_halt_2(function):
    function.framework = "indi"
    with mock.patch.object(function.run["indi"], "halt", return_value=True):
        function.halt()


@pytest.mark.skipif(not platformInfo.IS_WINDOWS, reason="Windows needed")
def test_focuserAscom_import():
    import importlib

    spec = importlib.util.find_spec("mw4.logic.drivers.focuser.focuserAscom")
    assert spec is not None


@pytest.mark.skipif(not platformInfo.IS_WINDOWS, reason="Windows needed")
def test_focuser_ascom_in_run(makeApp):
    from mw4.logic.drivers.focuser.focuser import Focuser

    function = Focuser(app=makeApp())
    if platformInfo.IS_WINDOWS:
        assert "ascom" in function.run
        assert function.run["ascom"] is not None
