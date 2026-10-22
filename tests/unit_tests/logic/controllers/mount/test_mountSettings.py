# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import pytest
from mw4.logic.controllers.mount.mountSettings import (
    SWITCHES,
    VALUES,
    MountSettingsController,
)
from types import SimpleNamespace
from unittest import mock


def makeController(**attributes):
    setting = SimpleNamespace(**attributes)
    notify = mock.Mock()
    return MountSettingsController(setting, notify), setting, notify


@pytest.mark.parametrize("key", list(SWITCHES))
@pytest.mark.parametrize("suc", [True, False])
def test_applySwitch(key, suc):
    spec = SWITCHES[key]
    controller, setting, notify = makeController()
    setter = mock.Mock(return_value=suc)
    setattr(setting, spec.setterName, setter)
    assert controller.applySwitch(spec, "ON") is suc
    setter.assert_called_once_with(True)
    if suc:
        notify.assert_called_once_with(0, "Mount", "Setting", f"{spec.label}: [ON]")
    else:
        label = spec.errorLabel or spec.label
        notify.assert_called_once_with(2, "Mount", "Setting", f"{label} cannot be set")


def test_applySwitch_off():
    controller, setting, _ = makeController(setWOL=mock.Mock(return_value=True))
    controller.applySwitch(SWITCHES["wol"], "OFF")
    setting.setWOL.assert_called_once_with(False)


@pytest.mark.parametrize("key", list(VALUES))
@pytest.mark.parametrize("suc", [True, False])
def test_applyValue(key, suc):
    spec = VALUES[key]
    controller, setting, notify = makeController()
    setter = mock.Mock(return_value=suc)
    setattr(setting, spec.setterName, setter)
    assert controller.applyValue(spec, 5) is suc
    setter.assert_called_once_with(5)
    if suc:
        notify.assert_called_once_with(0, "Mount", "Setting", f"{spec.label}: [5]")
    else:
        label = spec.errorLabel or spec.label
        notify.assert_called_once_with(2, "Mount", "Setting", f"{label} cannot be set")


@pytest.mark.parametrize("key", list(VALUES))
def test_currentValue_none(key):
    spec = VALUES[key]
    controller, _, _ = makeController(**{spec.attribute: None})
    assert controller.currentValue(spec) == 0


def test_currentValue_int():
    controller, _, _ = makeController(meridianLimitTrack=10.7, refractionTemp=10.7)
    assert controller.currentValue(VALUES["meridianTrack"]) == 10
    assert controller.currentValue(VALUES["refractionTemp"]) == 10.7


def test_valueRange_fixed():
    controller, _, _ = makeController()
    assert controller.valueRange(VALUES["horizonLow"]) == (-5, 90, "Value (-5 - 90):")


def test_valueRange_dynamic():
    controller, _, _ = makeController(slewRateMin=2.0, slewRateMax=9.0)
    assert controller.valueRange(VALUES["slewRate"]) == (2, 9, "Value (2...9):")


def test_valueRange_dynamicMissing():
    controller, _, _ = makeController(slewRateMin=None, slewRateMax=None)
    assert controller.valueRange(VALUES["slewRate"]) == (0, 0, "Value (0...0):")


@pytest.mark.parametrize(
    "key, value, expected",
    [
        ("unattendedFlip", None, 0),
        ("wol", "ON", 0),
        ("wol", "OFF", 1),
        ("apo", "ON", 0),
        ("apo", "None", 1),
    ],
)
def test_switchIndex(key, value, expected):
    spec = SWITCHES[key]
    controller, _, _ = makeController(wakeOnLan=value, autoPowerOn=value)
    assert controller.switchIndex(spec) == expected
