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
import unittest.mock as mock
from mw4.gui.extWindows.simulator.materials import Materials
from mw4.gui.extWindows.simulator.simulatorW import SimulatorWindow
from PySide6.Qt3DCore import Qt3DCore
from PySide6.QtWidgets import QApplication
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    func = SimulatorWindow(app=App(), title="Simulator")
    with mock.patch.object(func, "show"):
        yield func.dome
        QApplication.processEvents()


@pytest.fixture(autouse=True)
def resetEntityModel(function):
    # Each test builds the entity nodes it needs; clear leftovers so iteration
    # over the model does not hit nodes missing expected keys.
    function.parent.entityModel.clear()
    yield


def test_setTransparency_1(function):
    function.parent.entityModel["domeWall"] = {"entity": Qt3DCore.QEntity()}
    mat = Materials().walls
    function.parent.entityModel["domeWall"]["entity"].addComponent(mat)
    function.parent.entityModel["domeWall"]["material"] = mat
    function.setTransparency()


def test_showEnable_1(function):
    function.parent.entityModel["dome"] = {"entity": Qt3DCore.QEntity()}
    function.showEnable(True)


def test_showEnable_disconnect(function):
    """showEnable with no 'domeRoot' → disconnects updateSize (else branch, line 53)."""
    # Ensure updateSize is connected first via the if-branch
    entity = Qt3DCore.QEntity()
    function.parent.entityModel["domeRoot"] = {"entity": entity}
    function.showEnable(True)
    # Now remove domeRoot so the else-branch fires and disconnects updateSize
    del function.parent.entityModel["domeRoot"]
    function.showEnable(False)


def test_updateSize_1(function):
    function.parent.entityModel["domeFloor"] = {"entity": Qt3DCore.QEntity()}
    t = Qt3DCore.QTransform()
    function.parent.entityModel["domeFloor"]["entity"].addComponent(t)
    function.parent.entityModel["domeFloor"]["trans"] = t

    function.parent.entityModel["domeWall"] = {"entity": Qt3DCore.QEntity()}
    t = Qt3DCore.QTransform()
    function.parent.entityModel["domeWall"]["entity"].addComponent(t)
    function.parent.entityModel["domeWall"]["trans"] = t

    function.parent.entityModel["domeSphere"] = {"entity": Qt3DCore.QEntity()}
    t = Qt3DCore.QTransform()
    function.parent.entityModel["domeSphere"]["entity"].addComponent(t)
    function.parent.entityModel["domeSphere"]["trans"] = t
    function.updateSize()


def test_updateAzimuth_1(function):
    function.parent.entityModel["domeSphere"] = {"entity": Qt3DCore.QEntity()}
    t = Qt3DCore.QTransform()
    function.parent.entityModel["domeSphere"]["entity"].addComponent(t)
    function.parent.entityModel["domeSphere"]["trans"] = t
    function.updateAzimuth(180.0)


def test_updateShutter_1(function):
    function.app.dReg.d["dome"].instance.clearOpening = 1.0
    function.app.dReg.d["dome"].instance.data = {
        "ABS_DOME_POSITION.DOME_ABSOLUTE_POSITION": 0,
        "DOME_SHUTTER.SHUTTER_OPEN": True,
    }
    function.parent.entityModel["domeSlit1"] = {"entity": Qt3DCore.QEntity()}
    t = Qt3DCore.QTransform()
    function.parent.entityModel["domeSlit1"]["entity"].addComponent(t)
    function.parent.entityModel["domeSlit1"]["trans"] = t

    function.parent.entityModel["domeDoor1"] = {"entity": Qt3DCore.QEntity()}
    t = Qt3DCore.QTransform()
    function.parent.entityModel["domeDoor1"]["entity"].addComponent(t)
    function.parent.entityModel["domeDoor1"]["trans"] = t

    function.parent.entityModel["domeDoor2"] = {"entity": Qt3DCore.QEntity()}
    t = Qt3DCore.QTransform()
    function.parent.entityModel["domeDoor2"]["entity"].addComponent(t)
    function.parent.entityModel["domeDoor2"]["trans"] = t
    function.updateShutter()


def test_create_1(function):
    function.parent.entityModel["ref_fusion_m"] = {"entity": Qt3DCore.QEntity()}
    with (
        mock.patch.object(function, "updateAzimuth"),
        mock.patch.object(function, "updateShutter"),
        mock.patch.object(function, "updateSize"),
    ):
        function.create()
