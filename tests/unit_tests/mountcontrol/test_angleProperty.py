# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import pytest
from mw4.mountcontrol.angleProperty import AngleProperty
from mw4.mountcontrol.convert import stringToAngle, valueToAngle
from mw4.mountcontrol.obsSite import ObsSite
from skyfield.api import Angle

VALUE_ATTRS = {
    "raJNow": "hours",
    "decJNow": "degrees",
    "angularPosRA": "degrees",
    "angularPosDEC": "degrees",
    "errorAngularPosRA": "degrees",
    "errorAngularPosDEC": "degrees",
    "angularPosRATarget": "degrees",
    "angularPosDECTarget": "degrees",
    "Alt": "degrees",
}
STRING_ATTRS = {
    "raJNowTarget": "hours",
    "decJNowTarget": "degrees",
    "AltTarget": "degrees",
    "AzTarget": "degrees",
}
INPUTS = [34, 34.5, -12.25, "34", "12:30:00.0", "+45*30:00", "34f", "", None, [1, 2], "E"]


@pytest.fixture
def obsSite(mountContext):
    return ObsSite(parent=mountContext)


def asDegrees(angle, preference):
    return angle.hours if preference == "hours" else angle.degrees


@pytest.mark.parametrize("name,preference", VALUE_ATTRS.items())
@pytest.mark.parametrize("value", INPUTS)
def test_valueParser(obsSite, name, preference, value):
    setattr(obsSite, name, value)
    expected = valueToAngle(value, preference=preference)
    assert asDegrees(getattr(obsSite, name), preference) == asDegrees(expected, preference)


@pytest.mark.parametrize("name,preference", STRING_ATTRS.items())
@pytest.mark.parametrize("value", INPUTS)
def test_stringParser(obsSite, name, preference, value):
    setattr(obsSite, name, value)
    expected = stringToAngle(value, preference=preference)
    assert asDegrees(getattr(obsSite, name), preference) == asDegrees(expected, preference)


@pytest.mark.parametrize("name,preference", {**VALUE_ATTRS, **STRING_ATTRS}.items())
def test_anglePassthrough(obsSite, name, preference):
    angle = Angle(degrees=12.5)
    setattr(obsSite, name, angle)
    assert getattr(obsSite, name) is angle


@pytest.mark.parametrize("name,preference", {**VALUE_ATTRS, **STRING_ATTRS}.items())
def test_backingAttribute(obsSite, name, preference):
    setattr(obsSite, name, 10)
    assert getattr(obsSite, f"_{name}") is getattr(obsSite, name)


def test_classAccessReturnsDescriptor():
    assert isinstance(ObsSite.raJNow, AngleProperty)
    assert isinstance(ObsSite.raJNowTarget, AngleProperty)


def test_setName_derivesBackingAttribute():
    class Holder:
        pointing = AngleProperty("degrees")

    holder = Holder()
    holder.pointing = "10"
    assert Holder.pointing.name == "pointing"
    assert holder._pointing.degrees == 10
    assert holder.pointing.degrees == 10
