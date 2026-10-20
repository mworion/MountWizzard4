# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import inspect
import pytest
from mw4.base.appProtocol import (
    AppProtocol,
    HasBuildPoints,
    HasConfig,
    HasDevices,
    HasMainWindow,
    HasMessaging,
    HasMountState,
    HasThreadPool,
    HasTime,
)
from mw4.base.appSignals import AppSignals
from mw4.mainApp import MountWizzard4
from PySide6.QtCore import QObject, SignalInstance
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from unittest import mock


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
    for name in ("dReg", "config", "timeMgr", "signals", "threadPool"):
        setattr(partial, name, getattr(app, name))
    assert not isinstance(partial, AppProtocol)


def test_protocolMembers():
    members = AppProtocol.__protocol_attrs__
    for name in ("dReg", "config", "signals", "initConfig", "storeConfig", "MAX_THREAD_COUNT"):
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


ROLES = (
    HasConfig,
    HasThreadPool,
    HasDevices,
    HasMessaging,
    HasTime,
    HasMountState,
    HasBuildPoints,
    HasMainWindow,
)


def test_appProtocolIsUnionOfRoles():
    union = set()
    for role in ROLES:
        union |= set(role.__protocol_attrs__)
    assert set(AppProtocol.__protocol_attrs__) == union


def test_stubSatisfiesEachRole(app):
    for role in ROLES:
        assert isinstance(app, role)


def test_concreteAppProvidesEachRoleMember():
    classMembers = set(dir(MountWizzard4))
    initSource = inspect.getsource(MountWizzard4.__init__)
    for role in ROLES:
        for name in role.__protocol_attrs__:
            assert name in classMembers or f"self.{name}" in initSource


def groupSignals(group):
    return {
        name for name in dir(type(group)) if not name.startswith("_") and name not in dir(QObject)
    }


def test_everySignalLivesInExactlyOneGroup(app):
    groups = [app.signals.ui, app.signals.hemisphere, app.signals.model, app.signals.system]
    seen = []
    for group in groups:
        seen += sorted(groupSignals(group))
    assert len(seen) == len(set(seen)) == 24


def test_protocolListsNoFlatSignals(app):
    flat = set()
    for group in vars(app.signals).values():
        flat |= groupSignals(group)
    assert not flat & set(AppProtocol.__protocol_attrs__)
    assert not flat & set(dir(MountWizzard4))


def test_everyGroupSignalConnectsAndEmits(app):
    assert isinstance(app.signals, AppSignals)
    for group in vars(app.signals).values():
        for name in groupSignals(group):
            signal = getattr(group, name)
            assert isinstance(signal, SignalInstance)
            slot = mock.MagicMock()
            signal.connect(slot)
            signal.disconnect(slot)
