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
    with mock.patch.object(function.app.mount,
                           'calcTransformationMatricesActual',
                           return_value=(0, 0, None, None, None)):
        suc = function.updatePositions()
        assert not suc


def test_updatePositions_2(function):
    function.parent.entityModel['displacement'] = {'entity': Qt3DCore.QEntity()}
    function.parent.entityModel['displacement'].addComponent(Qt3DCore.QTransform())
    function.parent.entityModel['az'] = {'entity': Qt3DCore.QEntity()}
    function.parent.entityModel['az'].addComponent(Qt3DCore.QTransform())
    function.parent.entityModel['alt'] = {'entity': Qt3DCore.QEntity()}
    function.parent.entityModel['alt'].addComponent(Qt3DCore.QTransform())
    with mock.patch.object(function.app.mount,
                           'calcTransformationMatricesActual',
                           return_value=(0, 0,
                                         np.array([1, 1, 1]),
                                         np.array([1, 1, 1]),
                                         np.array([1, 1, 1]))):
        suc = function.updatePositions()
        assert suc


def test_create_1(function):
    with mock.patch.object(function,
                           'updatePositions'):
        with mock.patch.object(function,
                               'showEnable'):
            function.create()
