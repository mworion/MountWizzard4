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
from gui.extWindows.simulator import tools
from gui.extWindows.simulator.simulatorW import SimulatorWindow
from gui.utilities.toolsQtWidget import MWidget
from PySide6.Qt3DCore import Qt3DCore

# external packages
from PySide6.QtGui import QCloseEvent

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    func = SimulatorWindow(app=App())
    with mock.patch.object(func, "show"):
        yield func
        func.app.threadPool.waitForDone(10000)


def test_initConfig_1(function):
    function.initConfig()


def test_initConfig_2(function):
    function.app.config["simulatorW"] = {}
    function.app.config["simulatorW"]["winPosX"] = 100
    function.app.config["simulatorW"]["winPosY"] = 100
    function.initConfig()


def test_storeConfig_1(function):
    if "simulatorW" in function.app.config:
        del function.app.config["simulatorW"]

    function.storeConfig()


def test_storeConfig_2(function):
    function.app.config["simulatorW"] = {}
    function.storeConfig()


def test_closeEvent_1(function):
    with mock.patch.object(MWidget, "closeEvent"):
        function.showWindow()
        function.closeEvent(QCloseEvent)


def test_showWindow(function):
    with mock.patch.object(function, "show"):
        function.showWindow()


def test_setupCamera_1(function):
    function.setupCamera(Qt3DCore.QEntity())


def test_colorChange(function):
    function.colorChange()


def test_limitPositionZ_1(function):
    from PySide6.QtGui import QVector3D

    function.camera.setPosition(QVector3D(1, 1, 1))
    function.limitPositionZ()
    assert function.camera.position().y() == 1


def test_limitPositionZ_2(function):
    from PySide6.QtGui import QVector3D

    function.camera.setPosition(QVector3D(1, -10, 1))
    function.limitPositionZ()
    assert function.camera.position().y() == 0


def test_topView_1(function):
    function.topView()


def test_topEastView_1(function):
    function.topEastView()


def test_topWestView_1(function):
    function.topWestView()


def test_eastView_1(function):
    function.eastView()


def test_westView_1(function):
    function.westView()


def test_createReference_1(function):
    function.entityModel["root"] = {"entity": Qt3DCore.QEntity()}
    with mock.patch.object(tools, "linkModel"):
        function.createReference()


def test_createScene_1(function):
    function.entityModel["root"] = {"entity": Qt3DCore.QEntity()}
    with mock.patch.object(function, "createReference"):
        with mock.patch.object(function.telescope, "create"):
            with mock.patch.object(function.laser, "create"):
                with mock.patch.object(function.pointer, "create"):
                    with mock.patch.object(function.world, "create"):
                        with mock.patch.object(function.horizon, "create"):
                            with mock.patch.object(function.dome, "create"):
                                with mock.patch.object(function.buildPoints, "create"):
                                    function.createScene()
