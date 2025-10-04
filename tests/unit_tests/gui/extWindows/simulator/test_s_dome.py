############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock

import pytest

# external packages
from PySide6.Qt3DCore import Qt3DCore

from mw4.gui.extWindows.simulator.materials import Materials
from mw4.gui.extWindows.simulator.simulatorW import SimulatorWindow

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    func = SimulatorWindow(app=App())
    with mock.patch.object(func, "show"):
        yield func.dome


def test_setTransparency_1(function):
    function.parent.entityModel["domeWall"] = {"entity": Qt3DCore.QEntity()}
    mat = Materials().walls
    function.parent.entityModel["domeWall"]["entity"].addComponent(mat)
    function.parent.entityModel["domeWall"]["material"] = mat
    function.setTransparency()


def test_showEnable_1(function):
    function.parent.entityModel["dome"] = {"entity": Qt3DCore.QEntity()}
    function.showEnable(True)


def test_updateSize_1(function):
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
    function.app.dome.data = {
        "ABS_DOME_POSITION.DOME_ABSOLUTE_POSITION": 0,
        "DOME_SHUTTER.SHUTTER_OPEN": True,
    }
    function.parent.entityModel["domeSphere"] = {"entity": Qt3DCore.QEntity()}
    t = Qt3DCore.QTransform()
    function.parent.entityModel["domeSphere"]["entity"].addComponent(t)
    function.parent.entityModel["domeSphere"]["trans"] = t
    function.updateAzimuth()


def test_updateShutter_1(function):
    function.app.dome.data = {
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
    with mock.patch.object(function, "updateAzimuth"):
        with mock.patch.object(function, "updateShutter"):
            with mock.patch.object(function, "updateSize"):
                function.create()
