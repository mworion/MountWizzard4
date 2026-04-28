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
# Licence APL2.0
#
###########################################################

import pytest
from mw4.base.signalsDevices import Signals

EXPECTED_SIGNALS = [
    "serverConnected",
    "serverDisconnected",
    "deviceConnected",
    "deviceDisconnected",
    "exposed",
    "downloaded",
    "saved",
    "azimuth",
    "slewed",
    "message",
    "version",
    "result",
]


@pytest.fixture(scope="module")
def signals():
    return Signals()


def test_instantiation(signals):
    assert signals is not None


def test_signalCount(signals):
    assert len(EXPECTED_SIGNALS) == 12


def test_serverConnected(signals):
    assert hasattr(signals, "serverConnected")
    assert callable(signals.serverConnected.connect)


def test_serverDisconnected(signals):
    assert hasattr(signals, "serverDisconnected")
    assert callable(signals.serverDisconnected.connect)


def test_deviceConnected(signals):
    assert hasattr(signals, "deviceConnected")
    assert callable(signals.deviceConnected.connect)


def test_deviceDisconnected(signals):
    assert hasattr(signals, "deviceDisconnected")
    assert callable(signals.deviceDisconnected.connect)


def test_exposed(signals):
    assert hasattr(signals, "exposed")
    assert callable(signals.exposed.connect)


def test_downloaded(signals):
    assert hasattr(signals, "downloaded")
    assert callable(signals.downloaded.connect)


def test_saved(signals):
    assert hasattr(signals, "saved")
    assert callable(signals.saved.connect)


def test_azimuth(signals):
    assert hasattr(signals, "azimuth")
    assert callable(signals.azimuth.connect)


def test_slewed(signals):
    assert hasattr(signals, "slewed")
    assert callable(signals.slewed.connect)


def test_message(signals):
    assert hasattr(signals, "message")
    assert callable(signals.message.connect)


def test_version(signals):
    assert hasattr(signals, "version")
    assert callable(signals.version.connect)


def test_result(signals):
    assert hasattr(signals, "result")
    assert callable(signals.result.connect)


def test_allSignalsDeclared(signals):
    for signalName in EXPECTED_SIGNALS:
        assert hasattr(signals, signalName), f"Signal '{signalName}' not found"
        assert callable(getattr(signals, signalName).connect), (
            f"'{signalName}' does not have a callable connect method"
        )
