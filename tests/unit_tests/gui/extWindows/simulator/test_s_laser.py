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
import astropy
from unittest import mock

# external packages
from PySide6.Qt3DCore import Qt3DCore
import numpy as np

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.extWindows.simulatorW import SimulatorWindow


@pytest.fixture(autouse=True, scope='module')
def function(qapp):
    func = SimulatorWindow(app=App())
    with mock.patch.object(func,
                           'show'):
        yield func.laser


def test_showEnable_1(function):
    function.parent.entityModel['laser'] = {'entity': Qt3DCore.QEntity()}
    function.showEnable()


def test_updatePositions_1(function):
    function.app.deviceStat['mount'] = False
    function.updatePositions()


def test_updatePositions_2(function):
    function.app.deviceStat['mount'] = True
    with mock.patch.object(function.app.mount,
                           'calcTransformationMatricesActual',
                           return_value=(0, 0, None, None, None)):
        function.updatePositions()


def test_updatePositions_3(function):
    function.app.deviceStat['mount'] = True
    function.parent.entityModel['displacement'] = {'entity': Qt3DCore.QEntity()}
    t = Qt3DCore.QTransform()
    function.parent.entityModel['displacement']['entity'].addComponent(t)
    function.parent.entityModel['displacement']['trans'] = t

    function.parent.entityModel['az'] = {'entity': Qt3DCore.QEntity()}
    t = Qt3DCore.QTransform()
    function.parent.entityModel['az']['trans'] = t
    function.parent.entityModel['az']['entity'].addComponent(t)

    function.parent.entityModel['alt'] = {'entity': Qt3DCore.QEntity()}
    t = Qt3DCore.QTransform()
    function.parent.entityModel['alt']['trans'] = t
    function.parent.entityModel['alt']['entity'].addComponent(t)
    with mock.patch.object(function.app.mount,
                           'calcTransformationMatricesActual',
                           return_value=(0, 0,
                                         np.array([1, 1, 1]),
                                         np.array([1, 1, 1]),
                                         np.array([1, 1, 1]))):
        function.updatePositions()


def test_create_1(function):
    with mock.patch.object(function,
                           'updatePositions'):
        with mock.patch.object(function,
                               'showEnable'):
            function.create()
