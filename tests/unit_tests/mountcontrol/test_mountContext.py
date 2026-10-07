# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import pytest
from mw4.mountcontrol.mount import MountDevice
from mw4.mountcontrol.mountContext import MountContext
from tests.unit_tests.unitTestAddOns.baseTestApp import App

EXPECTED = {
    "config",
    "loggingTrace",
    "mountIsUp",
    "signals",
    "obsSite",
    "firmware",
    "threadPool",
    "pathToData",
    "domeConfig",
    "updateDomeSettings",
}


@pytest.fixture(scope="module")
def mountDevice():
    return MountDevice(app=App())


def test_mountContext_members():
    assert set(MountContext.__annotations__) == EXPECTED


def test_mountContext_satisfiedByMountDevice(mountDevice):
    for name in MountContext.__annotations__:
        assert hasattr(mountDevice, name)


def test_mountContext_satisfiedByFixture(mountContext):
    for name in MountContext.__annotations__:
        assert hasattr(mountContext, name)
