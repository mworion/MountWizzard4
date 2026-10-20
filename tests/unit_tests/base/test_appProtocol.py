# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import inspect
import pytest
from mw4.base.appProtocol import AppProtocol
from mw4.mainApp import MountWizzard4
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="module")
def app(qapp):
    testApp = App()
    yield testApp
    testApp.shutdown()


def test_stubSatisfiesProtocol(app):
    assert isinstance(app, AppProtocol)


def test_objectDoesNotSatisfyProtocol():
    assert not isinstance(object(), AppProtocol)


def test_missingMemberFailsProtocol(app):
    class Partial:
        pass

    partial = Partial()
    for name in ("dReg", "config", "timeMgr", "msg", "threadPool"):
        setattr(partial, name, getattr(app, name))
    assert not isinstance(partial, AppProtocol)


def test_protocolMembers():
    members = AppProtocol.__protocol_attrs__
    for name in ("dReg", "config", "msg", "initConfig", "storeConfig", "MAX_THREAD_COUNT"):
        assert name in members
    for name in ("mount", "relay", "measure", "deviceStat", "application"):
        assert name not in members


def test_concreteAppProvidesAllProtocolMembers():
    classMembers = set(dir(MountWizzard4))
    initSource = inspect.getsource(MountWizzard4.__init__)
    missing = [
        name
        for name in AppProtocol.__protocol_attrs__
        if name not in classMembers and f"self.{name}" not in initSource
    ]
    assert not missing
