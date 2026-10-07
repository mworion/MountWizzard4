# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import pytest
from mw4.mountcontrol.mountData import MountData
from skyfield.api import Angle
from types import SimpleNamespace


@pytest.fixture
def mountData():
    obsSite = SimpleNamespace(
        raJNow=Angle(degrees=10.0),
        decJNow=Angle(degrees=20.0),
        errorAngularPosRA=Angle(degrees=0.001),
        errorAngularPosDEC=Angle(degrees=0.002),
        status=0,
        statusSlew=False,
    )
    conn = SimpleNamespace(timeDiff=0.005, rtt=0.02)
    return MountData(obsSite, conn)


def test_init(mountData):
    assert mountData.data == {}
    assert mountData.raRef == 0.0
    assert mountData.decRef == 0.0


def test_reset(mountData):
    mountData.reset()
    assert mountData.raRef == 10.0
    assert mountData.decRef == 20.0


def test_collect_slewResetsReference(mountData):
    mountData.obsSite.statusSlew = True
    mountData.collect()
    assert mountData.raRef == 10.0
    assert mountData.decRef == 20.0
    assert mountData.data["deltaRaJNow"] == 0
    assert mountData.data["deltaDecJNow"] == 0


def test_collect_noSlewKeepsReference(mountData):
    mountData.raRef = 9.0
    mountData.decRef = 19.0
    mountData.collect()
    assert mountData.raRef == 9.0
    assert mountData.decRef == 19.0
    assert mountData.data["deltaRaJNow"] == pytest.approx(3600)
    assert mountData.data["deltaDecJNow"] == pytest.approx(3600)


def test_collect_values(mountData):
    mountData.collect()
    assert mountData.data["errorAngularPosRA"] == pytest.approx(3.6)
    assert mountData.data["errorAngularPosDEC"] == pytest.approx(7.2)
    assert mountData.data["status"] == 0
    assert mountData.data["timeDiff"] == pytest.approx(5.0)
    assert mountData.data["rtt"] == pytest.approx(20.0)
