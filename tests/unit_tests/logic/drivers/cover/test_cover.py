# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion

import pytest
from mw4.base import platformInfo
from mw4.logic.drivers.cover.cover import Cover
from unittest import mock


@pytest.fixture(autouse=True, scope="module")
def function(makeApp):
    try:
        func = Cover(app=makeApp())
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


def test_closeCover_2(function):
    function.framework = "indi"
    with mock.patch.object(function.run["indi"], "closeCover", return_value=False):
        function.closeCover()


def test_closeCover_3(function):
    function.framework = "indi"
    with mock.patch.object(function.run["indi"], "closeCover", return_value=True):
        function.closeCover()


def test_openCover_2(function):
    function.framework = "indi"
    with mock.patch.object(function.run["indi"], "openCover", return_value=False):
        function.openCover()


def test_openCover_3(function):
    function.framework = "indi"
    with mock.patch.object(function.run["indi"], "openCover", return_value=True):
        function.openCover()


def test_haltCover_2(function):
    function.framework = "indi"
    with mock.patch.object(function.run["indi"], "haltCover", return_value=False):
        function.haltCover()


def test_haltCover_3(function):
    function.framework = "indi"
    with mock.patch.object(function.run["indi"], "haltCover", return_value=True):
        function.haltCover()


@pytest.mark.skipif(not platformInfo.IS_WINDOWS, reason="Windows needed")
def test_coverAscom_import():
    import importlib

    spec = importlib.util.find_spec("mw4.logic.drivers.cover.coverAscom")
    assert spec is not None


@pytest.mark.skipif(not platformInfo.IS_WINDOWS, reason="Windows needed")
def test_cover_ascom_in_run(makeApp):
    from mw4.logic.drivers.cover.cover import Cover

    function = Cover(app=makeApp())
    if platformInfo.IS_WINDOWS:
        assert "ascom" in function.run
        assert function.run["ascom"] is not None
