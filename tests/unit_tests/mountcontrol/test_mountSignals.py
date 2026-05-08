############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10_micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2026 by mworion
# License APL2.0
#
###########################################################

import pytest
from mw4.mountcontrol.mountSignals import MountSignals

EXPECTED_SIGNALS = [
    "pointDone",
    "domeDone",
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
    assert len(EXPECTED_SIGNALS) == 14


def test_pointDone(mountSignals):
    assert hasattr(mountSignals, "pointDone")
    assert callable(mountSignals.pointDone.connect)


def test_domeDone(mountSignals):
    assert hasattr(mountSignals, "domeDone")
    assert callable(mountSignals.domeDone.connect)


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
