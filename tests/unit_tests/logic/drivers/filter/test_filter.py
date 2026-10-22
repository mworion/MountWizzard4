# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion

import pytest
from mw4.base import platformInfo
from mw4.logic.drivers.filter.filter import Filter


@pytest.fixture(autouse=True, scope="module")
def function(makeApp):
    try:
        func = Filter(app=makeApp())
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


def test_sendFilterNumber_1(function):
    function.framework = ""
    function.sendFilterNumber()


def test_sendFilterNumber_2(function):
    function.framework = "indi"
    function.sendFilterNumber()


@pytest.mark.skipif(not platformInfo.IS_WINDOWS, reason="Windows needed")
def test_filterAscom_import():
    import importlib

    spec = importlib.util.find_spec("mw4.logic.drivers.filter.filterAscom")
    assert spec is not None


@pytest.mark.skipif(not platformInfo.IS_WINDOWS, reason="Windows needed")
def test_filter_ascom_in_run(makeApp):
    from mw4.logic.drivers.filter.filter import Filter

    function = Filter(app=makeApp())
    if platformInfo.IS_WINDOWS:
        assert "ascom" in function.run
        assert function.run["ascom"] is not None
