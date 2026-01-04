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

import numpy as np
import pytest
from mw4.gui.extWindows.simulator.simulatorW import SimulatorWindow
from PySide6.Qt3DCore import Qt3DCore
from PySide6.Qt3DExtras import Qt3DExtras
from skyfield.api import Angle
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from unittest import mock


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    func = SimulatorWindow(app=App())
    func.app.data.buildP = []
    with mock.patch.object(func, "show"):
        yield func.buildPoints


def test_showEnable_1(function):
    function.parent.entityModel["buildPoints"] = {"entity": Qt3DCore.QEntity()}
    function.showEnable()


def test_clear_1(function):
    function.parent.entityModel = {}
    function.clear()


def test_clear_2(function):
    function.parent.entityModel["buildPoints"] = {"entity": Qt3DCore.QEntity()}
    function.clear()


def test_updatePositions_1(function):
    function.app.mount.obsSite.haJNow = None
    function.updatePositions()


def test_updatePositions_2(function):
    function.app.mount.obsSite.haJNow = Angle(hours=10)
    function.app.mount.obsSite.timeSidereal = "10:10:10"

    with mock.patch.object(
        function.app.mount,
        "calcTransformationMatricesActual",
        return_value=(0, 0, None, None, None),
    ):
        function.updatePositions()


def test_updatePositions_3(function):
    function.app.mount.obsSite.haJNow = Angle(hours=10)
    function.app.mount.obsSite.timeSidereal = "10:10:10"
    function.parent.entityModel["buildPoints"] = {"entity": Qt3DCore.QEntity()}
    function.parent.entityModel["buildPoints"] = {"trans": Qt3DCore.QTransform()}
    with mock.patch.object(
        function.app.mount,
        "calcTransformationMatricesActual",
        return_value=(
            0,
            0,
            np.array([1, 1, 1]),
            np.array([1, 1, 1]),
            np.array([1, 1, 1]),
        ),
    ):
        function.updatePositions()


def test_createLine_1(function):
    val = function.createLine(Qt3DCore.QEntity(), 1, 1, 1)
    assert isinstance(val[0], Qt3DCore.QEntity)
    assert isinstance(val[2], Qt3DCore.QEntity)
    assert isinstance(val[4], Qt3DCore.QEntity)
    assert isinstance(val[1], Qt3DCore.QTransform)
    assert isinstance(val[3], Qt3DCore.QTransform)
    assert isinstance(val[5], Qt3DCore.QTransform)


def test_createPoint_1(function):
    val = function.createPoint(Qt3DCore.QEntity(), 1, 1, False)
    assert isinstance(val[0][0], Qt3DCore.QEntity)
    assert isinstance(val[0][2], Qt3DCore.QTransform)


def test_createPoint_2(function):
    val = function.createPoint(Qt3DCore.QEntity(), 1, 1, False)
    assert isinstance(val[0][0], Qt3DCore.QEntity)
    assert isinstance(val[0][2], Qt3DCore.QTransform)


def test_createAnnotation_1(function):
    e = Qt3DCore.QEntity()
    with mock.patch.object(Qt3DExtras.QExtrudedTextMesh, "setText"):
        val = function.createAnnotation(e, 45, 45, "test", True)
        assert isinstance(val[0], Qt3DCore.QEntity)
        assert isinstance(val[1], Qt3DCore.QTransform)
        assert isinstance(val[2], Qt3DCore.QEntity)
        assert isinstance(val[3], Qt3DCore.QTransform)
        assert isinstance(val[6], Qt3DCore.QEntity)
        assert isinstance(val[7], Qt3DCore.QTransform)


def test_createAnnotation_2(function):
    e = Qt3DCore.QEntity()
    with mock.patch.object(Qt3DExtras.QExtrudedTextMesh, "setText"):
        val = function.createAnnotation(e, 45, 45, "test", False)
        assert isinstance(val[0], Qt3DCore.QEntity)
        assert isinstance(val[1], Qt3DCore.QTransform)
        assert isinstance(val[2], Qt3DCore.QEntity)
        assert isinstance(val[3], Qt3DCore.QTransform)
        assert isinstance(val[6], Qt3DCore.QEntity)
        assert isinstance(val[7], Qt3DCore.QTransform)


def test_createAnnotation_3(function):
    e = Qt3DCore.QEntity()
    with mock.patch.object(Qt3DExtras.QExtrudedTextMesh, "setText"):
        val = function.createAnnotation(e, 45, 45, "test", True, faceIn=True)
        assert isinstance(val[0], Qt3DCore.QEntity)
        assert isinstance(val[1], Qt3DCore.QTransform)
        assert isinstance(val[2], Qt3DCore.QEntity)
        assert isinstance(val[3], Qt3DCore.QTransform)
        assert isinstance(val[6], Qt3DCore.QEntity)
        assert isinstance(val[7], Qt3DCore.QTransform)


def test_loopCreate_1(function):
    function.parent.entityModel["ref_fusion"] = {"entity": Qt3DCore.QEntity()}
    function.parent.ui.showNumbers.setChecked(True)
    function.parent.ui.showSlewPath.setChecked(True)
    function.app.data.buildP = [(0, 0, 1), (10, 10, 1)]
    function.points = []
    function.loopCreate(Qt3DCore.QEntity())
    assert function.points


def test_create_1(function):
    function.app.data.buildP = []
    suc = function.create()
    assert not suc


def test_create_2(function):
    function.app.data.buildP = [(0, 0, 1), (10, 10, 1)]
    function.parent.entityModel.clear()
    suc = function.create()
    assert not suc


def test_create_3(function):
    function.parent.entityModel["ref_fusion"] = {"entity": Qt3DCore.QEntity()}
    function.app.data.buildP = [(0, 0, 1), (10, 10, 1)]
    with mock.patch.object(function, "clear"):
        with mock.patch.object(function, "loopCreate"):
            with mock.patch.object(function, "updatePositions"):
                with mock.patch.object(function, "showEnable"):
                    suc = function.create()
                    assert suc
