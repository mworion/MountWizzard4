# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion

import pytest
from mw4.mountcontrol.mountSignals import MountSignals
from mw4.mountcontrol.obsSite import ObsSite

EXPECTED_SIGNALS = [
    "pointDone",
    "settingDone",
    "getModelDone",
    "namesDone",
    "firmwareDone",
    "locationDone",
    "calcTLEdone",
    "statTLEdone",
    "getTLEdone",
    "calcTrajectoryDone",
    "mountIsUp",
    "slewed",
    "alert",
]


@pytest.fixture(scope="module")
def mountSignals():
    return MountSignals()


def test_instantiation(mountSignals):
    assert mountSignals is not None


def test_signalCount(mountSignals):
    assert len(EXPECTED_SIGNALS) == 13


def test_pointDone(mountSignals):
    assert hasattr(mountSignals, "pointDone")
    assert callable(mountSignals.pointDone.connect)


def test_domeDoneRemoved(mountSignals):
    assert not hasattr(mountSignals, "domeDone")


def test_mountIsUpIsBool(mountSignals, qtbot):
    with qtbot.waitSignal(mountSignals.mountIsUp) as blocker:
        mountSignals.mountIsUp.emit(True)
    assert blocker.args == [True]


def test_domainPayloadPassesThrough(mountSignals, qtbot):
    payload = object.__new__(ObsSite)
    with qtbot.waitSignal(mountSignals.pointDone) as blocker:
        mountSignals.pointDone.emit(payload)
    assert blocker.args[0] is payload


def test_settingDone(mountSignals):
    assert hasattr(mountSignals, "settingDone")
    assert callable(mountSignals.settingDone.connect)


def test_getModelDone(mountSignals):
    assert hasattr(mountSignals, "getModelDone")
    assert callable(mountSignals.getModelDone.connect)


def test_namesDone(mountSignals):
    assert hasattr(mountSignals, "namesDone")
    assert callable(mountSignals.namesDone.connect)


def test_firmwareDone(mountSignals):
    assert hasattr(mountSignals, "firmwareDone")
    assert callable(mountSignals.firmwareDone.connect)


def test_locationDone(mountSignals):
    assert hasattr(mountSignals, "locationDone")
    assert callable(mountSignals.locationDone.connect)


def test_calcTLEdone(mountSignals):
    assert hasattr(mountSignals, "calcTLEdone")
    assert callable(mountSignals.calcTLEdone.connect)


def test_statTLEdone(mountSignals):
    assert hasattr(mountSignals, "statTLEdone")
    assert callable(mountSignals.statTLEdone.connect)


def test_getTLEdone(mountSignals):
    assert hasattr(mountSignals, "getTLEdone")
    assert callable(mountSignals.getTLEdone.connect)


def test_calcTrajectoryDone(mountSignals):
    assert hasattr(mountSignals, "calcTrajectoryDone")
    assert callable(mountSignals.calcTrajectoryDone.connect)


def test_mountIsUp(mountSignals):
    assert hasattr(mountSignals, "mountIsUp")
    assert callable(mountSignals.mountIsUp.connect)


def test_slewed(mountSignals):
    assert hasattr(mountSignals, "slewed")
    assert callable(mountSignals.slewed.connect)


def test_alert(mountSignals):
    assert hasattr(mountSignals, "alert")
    assert callable(mountSignals.alert.connect)


def test_allSignalsDeclared(mountSignals):
    for signalName in EXPECTED_SIGNALS:
        assert hasattr(mountSignals, signalName), f"Signal '{signalName}' not found"
        assert callable(getattr(mountSignals, signalName).connect), (
            f"'{signalName}' does not have a callable connect method"
        )
