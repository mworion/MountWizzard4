# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import pytest
from mw4.gui.extWindows.simulator.materials import Materials
from mw4.gui.extWindows.simulator.simulatorW import SimulatorWindow
from PySide6.Qt3DCore import Qt3DCore
from PySide6.QtWidgets import QApplication
from unittest import mock


@pytest.fixture(autouse=True, scope="module")
def function(qapp, makeApp):
    func = SimulatorWindow(app=makeApp(), title="Simulator")
    with mock.patch.object(func, "show"):
        yield func.dome
        QApplication.processEvents()


@pytest.fixture(autouse=True)
def resetEntityModel(function):
    # Each test builds the entity nodes it needs; clear leftovers so iteration
    # over the model does not hit nodes missing expected keys.
    function.parentWindow.entityModel.clear()
    yield


def test_setTransparency_1(function):
    function.parentWindow.entityModel["domeWall"] = {"entity": Qt3DCore.QEntity()}
    mat = Materials().walls
    function.parentWindow.entityModel["domeWall"]["entity"].addComponent(mat)
    function.parentWindow.entityModel["domeWall"]["material"] = mat
    function.setTransparency()


def test_showEnable_1(function):
    function.parentWindow.entityModel["dome"] = {"entity": Qt3DCore.QEntity()}
    function.showEnable(True)


def test_showEnable_disconnect(function):
    """showEnable with no 'domeRoot' → disconnects updateSize (else branch, line 53)."""
    # Ensure updateSize is connected first via the if-branch
    entity = Qt3DCore.QEntity()
    function.parentWindow.entityModel["domeRoot"] = {"entity": entity}
    function.showEnable(True)
    # Now remove domeRoot so the else-branch fires and disconnects updateSize
    del function.parentWindow.entityModel["domeRoot"]
    function.showEnable(False)


@pytest.mark.parametrize(
    ("method_name", "device_name", "enabled"),
    [
        ("domeConnected", "Connected dome", True),
        ("domeDisconnected", "Disconnected dome", False),
    ],
)
def test_dome_connection_callbacks(function, method_name, device_name, enabled):
    with mock.patch.object(function, "showEnable") as show_enable:
        getattr(function, method_name)(device_name)

    show_enable.assert_called_once_with(enabled)


def test_updateSize_1(function):
    function.parentWindow.entityModel["domeFloor"] = {"entity": Qt3DCore.QEntity()}
    t = Qt3DCore.QTransform()
    function.parentWindow.entityModel["domeFloor"]["entity"].addComponent(t)
    function.parentWindow.entityModel["domeFloor"]["trans"] = t

    function.parentWindow.entityModel["domeWall"] = {"entity": Qt3DCore.QEntity()}
    t = Qt3DCore.QTransform()
    function.parentWindow.entityModel["domeWall"]["entity"].addComponent(t)
    function.parentWindow.entityModel["domeWall"]["trans"] = t

    function.parentWindow.entityModel["domeSphere"] = {"entity": Qt3DCore.QEntity()}
    t = Qt3DCore.QTransform()
    function.parentWindow.entityModel["domeSphere"]["entity"].addComponent(t)
    function.parentWindow.entityModel["domeSphere"]["trans"] = t
    function.updateSize()


def test_updateAzimuth_1(function):
    function.parentWindow.entityModel["domeSphere"] = {"entity": Qt3DCore.QEntity()}
    t = Qt3DCore.QTransform()
    function.parentWindow.entityModel["domeSphere"]["entity"].addComponent(t)
    function.parentWindow.entityModel["domeSphere"]["trans"] = t
    function.updateAzimuth(180.0)


def test_updateShutter_1(function):
    function.app.dReg.d["dome"].instance.clearOpening = 1.0
    function.app.dReg.d["dome"].instance.data = {
        "ABS_DOME_POSITION.DOME_ABSOLUTE_POSITION": 0,
        "DOME_SHUTTER.SHUTTER_OPEN": True,
    }
    function.parentWindow.entityModel["domeSlit1"] = {"entity": Qt3DCore.QEntity()}
    t = Qt3DCore.QTransform()
    function.parentWindow.entityModel["domeSlit1"]["entity"].addComponent(t)
    function.parentWindow.entityModel["domeSlit1"]["trans"] = t

    function.parentWindow.entityModel["domeDoor1"] = {"entity": Qt3DCore.QEntity()}
    t = Qt3DCore.QTransform()
    function.parentWindow.entityModel["domeDoor1"]["entity"].addComponent(t)
    function.parentWindow.entityModel["domeDoor1"]["trans"] = t

    function.parentWindow.entityModel["domeDoor2"] = {"entity": Qt3DCore.QEntity()}
    t = Qt3DCore.QTransform()
    function.parentWindow.entityModel["domeDoor2"]["entity"].addComponent(t)
    function.parentWindow.entityModel["domeDoor2"]["trans"] = t
    function.updateShutter()


def test_create_1(function):
    function.parentWindow.entityModel["ref_fusion_m"] = {"entity": Qt3DCore.QEntity()}
    with (
        mock.patch.object(function, "updateAzimuth"),
        mock.patch.object(function, "updateShutter"),
        mock.patch.object(function, "updateSize"),
    ):
        function.create()


def test_updateAzimuth_2(function):
    function.updateAzimuth(180.0)


def test_updateShutter_2(function):
    function.app.dReg.d["dome"].instance.data = {"DOME_SHUTTER.SHUTTER_OPEN": True}
    function.updateShutter()
