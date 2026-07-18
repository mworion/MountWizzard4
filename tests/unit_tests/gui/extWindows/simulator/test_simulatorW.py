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
from mw4.gui.extWindows.simulator import tools
from mw4.gui.extWindows.simulator.simulatorW import SimulatorWindow
from mw4.gui.utilities.qtMain import MWidget
from PySide6.Qt3DCore import Qt3DCore
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QApplication
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    func = SimulatorWindow(app=App(), title="Simulator")
    with mock.patch.object(func, "show"):
        yield func
        QApplication.processEvents()


def test_initConfig_1(function):
    function.initConfig()


def test_initConfig_2(function):
    function.app.config["WindowSimulator"] = {}
    function.app.config["WindowSimulator"]["winPosX"] = 100
    function.app.config["WindowSimulator"]["winPosY"] = 100
    function.initConfig()


def test_storeConfig_1(function):
    if "WindowSimulator" in function.app.config:
        del function.app.config["WindowSimulator"]

    function.storeConfig()


def test_storeConfig_2(function):
    function.app.config["WindowSimulator"] = {}
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


def test_findFrameGraphNode_1(function):
    from PySide6.Qt3DExtras import Qt3DExtras

    fg = function.window3D.activeFrameGraph()
    result = function.findFrameGraphNode(fg, Qt3DExtras.QForwardRenderer)
    assert result is not None


def test_findFrameGraphNode_2(function):
    from PySide6.Qt3DRender import Qt3DRender

    fg = function.window3D.activeFrameGraph()
    result = function.findFrameGraphNode(fg, Qt3DRender.QRenderSurfaceSelector)
    assert result is not None


def test_findFrameGraphNode_3(function):
    from PySide6.Qt3DRender import Qt3DRender

    fg = function.window3D.activeFrameGraph()
    result = function.findFrameGraphNode(fg, Qt3DRender.QDebugOverlay)
    assert result is not None


def test_findFrameGraphNode_4(function):
    from unittest.mock import MagicMock

    node = MagicMock()
    node.childNodes.return_value = []
    result = function.findFrameGraphNode(node, type(None))
    assert result is None


def test_setupRenderSortPolicy_1(function):
    from PySide6.Qt3DRender import Qt3DRender

    function.setupRenderSortPolicy()
    fg = function.window3D.activeFrameGraph()
    sortPolicy = function.findFrameGraphNode(fg, Qt3DRender.QSortPolicy)
    assert sortPolicy is not None


def test_setupRenderSortPolicy_2(function):
    with mock.patch.object(function, "findFrameGraphNode", return_value=None):
        function.setupRenderSortPolicy()


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
    with (
        mock.patch.object(function, "createReference"),
        mock.patch.object(function.telescope, "create"),
        mock.patch.object(function.laser, "create"),
        mock.patch.object(function.pointer, "create"),
        mock.patch.object(function.world, "create"),
        mock.patch.object(function.horizon, "create"),
        mock.patch.object(function.dome, "create"),
        mock.patch.object(function.buildPoints, "create"),
    ):
        function.createScene()
