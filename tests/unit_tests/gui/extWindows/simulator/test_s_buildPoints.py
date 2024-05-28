############################################################
# -*- coding: utf-8 -*-
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PyQT5 for python
#
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
from unittest import mock

# external packages
from PyQt6.Qt3DCore import QEntity
from PyQt6.Qt3DExtras import QExtrudedTextMesh
import numpy as np

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.extWindows.simulatorW import SimulatorWindow


@pytest.fixture(autouse=True, scope='module')
def function(qapp):
    func = SimulatorWindow(app=App())
    with mock.patch.object(func,
                           'show'):
        yield func.buildPoints


def test_showEnable_1(function):
    function.parent.entityModel['buildPoints'] = QEntity()
    function.showEnable()


def test_clear_1(function):
    function.parent.entityModel = {}
    suc = function.clear()
    assert not suc


def test_clear_2(function):
    function.parent.entityModel['buildPoints'] = QEntity()
    suc = function.clear()
    assert suc


def test_updatePositions_1(function):
    function.app.mount.obsSite.haJNow = None
    suc = function.updatePositions()
    assert not suc


def test_updatePositions_2(function):
    function.app.mount.obsSite.haJNow = 10
    function.app.mount.obsSite.timeSidereal = '10:10:10'

    with mock.patch.object(function.app.mount,
                           'calcTransformationMatricesActual',
                           return_value=(0, 0, None, None, None)):
        suc = function.updatePositions()
        assert not suc


def test_updatePositions_3(function):
    function.app.mount.obsSite.haJNow = 10
    function.app.mount.obsSite.timeSidereal = '10:10:10'
    function.parent.entityModel['buildPoints'] = QEntity()
    with mock.patch.object(function.app.mount,
                           'calcTransformationMatricesActual',
                           return_value=(0, 0,
                                         np.array([1, 1, 1]),
                                         np.array([1, 1, 1]),
                                         np.array([1, 1, 1]))):
        suc = function.updatePositions()
        assert suc


def test_createLine_1(function):
    val = function.createLine(QEntity(), 1, 1, 1)
    assert isinstance(val, QEntity)


def test_createPoint_1(function):
    val = function.createPoint(QEntity(), 1, 1, True)
    assert isinstance(val[0], QEntity)


def test_createPoint_2(function):
    val = function.createPoint(QEntity(), 1, 1, False)
    assert isinstance(val[0], QEntity)


def test_createAnnotation_1(function):
    e = QEntity()
    with mock.patch.object(QExtrudedTextMesh,
                           'setText'):
        val = function.createAnnotation(e, 45, 45, 'test', True)
        assert isinstance(val, QEntity)


def test_createAnnotation_2(function):
    e = QEntity()
    with mock.patch.object(QExtrudedTextMesh,
                           'setText'):
        val = function.createAnnotation(e, 45, 45, 'test', False)
        assert isinstance(val, QEntity)


def test_createAnnotation_3(function):
    e = QEntity()
    with mock.patch.object(QExtrudedTextMesh,
                           'setText'):
        val = function.createAnnotation(e, 45, 45, 'test', True, faceIn=True)
        assert isinstance(val, QEntity)


def test_loopCreate_1(function):
    function.parent.entityModel['ref1000'] = QEntity()
    function.parent.ui.showNumbers.setChecked(True)
    function.parent.ui.showSlewPath.setChecked(True)
    function.app.data.buildP = [(0, 0, True), (10, 10, True)]
    function.points = []
    function.loopCreate(QEntity())
    assert function.points


def test_create_1(function):
    function.app.data.buildP = None
    suc = function.create()
    assert not suc


def test_create_2(function):
    function.parent.entityModel['ref1000'] = QEntity()
    function.app.data.buildP = [(0, 0, True), (10, 10, True)]
    with mock.patch.object(function,
                           'loopCreate'):
        with mock.patch.object(function,
                               'updatePositions'):
            with mock.patch.object(function,
                                   'showEnable'):
                suc = function.create()
        assert suc
