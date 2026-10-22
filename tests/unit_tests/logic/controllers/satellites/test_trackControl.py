# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import pytest
from mw4.logic.controllers.satellites.trackControl import SatelliteTrackController
from types import SimpleNamespace
from unittest import mock


def makeController(stat=True, parked=False, unpark=True, slew=(True, "ok"), tracking=True):
    obsSite = SimpleNamespace(
        isParked=parked,
        unpark=mock.Mock(return_value=unpark),
        startTracking=mock.Mock(return_value=tracking),
    )
    satellite = SimpleNamespace(
        slewTLE=mock.Mock(return_value=slew), setTrackingOffsets=mock.Mock()
    )
    mount = SimpleNamespace(stat=stat, obsSite=obsSite, satellite=satellite)
    dome = SimpleNamespace(instance=SimpleNamespace(avoidFirstOvershoot=mock.Mock()))
    notify = mock.Mock()
    return SatelliteTrackController(mount, dome, notify), mount, dome, notify


def test_start_offline():
    controller, mount, _, notify = makeController(stat=False)
    assert not controller.start()
    notify.assert_called_once_with(2, "TLE", "Program", "Mount is not online")
    mount.satellite.slewTLE.assert_not_called()


def test_start_slewFailure():
    controller, mount, dome, notify = makeController(slew=(False, "bad"))
    assert not controller.start()
    dome.instance.avoidFirstOvershoot.assert_called_once()
    notify.assert_called_once_with(2, "TLE", "Command error", "bad")
    mount.satellite.setTrackingOffsets.assert_not_called()


def test_start_success():
    controller, mount, _, notify = makeController()
    assert controller.start()
    notify.assert_called_once_with(0, "TLE", "Command ", "ok")
    mount.obsSite.unpark.assert_not_called()
    mount.satellite.setTrackingOffsets.assert_called_once()


@pytest.mark.parametrize(
    "unpark, expected",
    [
        (True, (0, "TLE", "Command", "Mount unparked")),
        (False, (2, "TLE", "Command error", "Cannot unpark mount")),
    ],
)
def test_start_parked(unpark, expected):
    controller, mount, _, notify = makeController(parked=True, unpark=unpark)
    assert controller.start()
    mount.obsSite.unpark.assert_called_once()
    assert notify.call_args_list[0] == mock.call(*expected)


def test_stop_offline():
    controller, _, _, notify = makeController(stat=False)
    assert not controller.stop()
    notify.assert_called_once_with(2, "TLE", "Command", "Mount is not online")


def test_stop_failure():
    controller, _, _, notify = makeController(tracking=False)
    assert not controller.stop()
    notify.assert_called_once_with(2, "TLE", "Command", "Cannot stop tracking")


def test_stop_success():
    controller, _, _, notify = makeController()
    assert controller.stop()
    notify.assert_called_once_with(0, "TLE", "Command", "Stopped tracking")
