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
from skyfield.api import Angle

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.extWindows.simulatorW import SimulatorWindow


@pytest.fixture(autouse=True, scope='module')
def function(qapp):
    func = SimulatorWindow(app=App())
    with mock.patch.object(func,
                           'show'):
        yield func.telescope


def test_updatePositions_1(function):
    function.parent.entityModel['mountBase'] = {'entity': Qt3DCore.QEntity()}
    function.parent.entityModel['mountBase'].addComponent(Qt3DCore.QTransform())
    function.parent.entityModel['lat'] = {'entity': Qt3DCore.QEntity()}
    function.parent.entityModel['lat'].addComponent(Qt3DCore.QTransform())
    function.parent.entityModel['gem'] = {'entity': Qt3DCore.QEntity()}
    function.parent.entityModel['gem'].addComponent(Qt3DCore.QTransform())
    function.parent.entityModel['gemCorr'] = {'entity': Qt3DCore.QEntity()}
    function.parent.entityModel['gemCorr'].addComponent(Qt3DCore.QTransform())
    function.parent.entityModel['otaRing'] = {'entity': Qt3DCore.QEntity()}
    function.parent.entityModel['otaRing'].addComponent(Qt3DCore.QTransform())
    function.parent.entityModel['otaTube'] = {'entity': Qt3DCore.QEntity()}
    function.parent.entityModel['otaTube'].addComponent(Qt3DCore.QTransform())
    function.parent.entityModel['otaImagetrain'] = {'entity': Qt3DCore.QEntity()}
    function.parent.entityModel['otaImagetrain'].addComponent(Qt3DCore.QTransform())

    function.updatePositions()


def test_updateRotation_1(function):
    function.app.mount.obsSite.angularPosRA = None
    function.app.mount.obsSite.angularPosDEC = None
    suc = function.updateRotation()
    assert not suc


def test_updateRotation_2(function):
    function.app.mount.obsSite.angularPosRA = Angle(degrees=10)
    function.app.mount.obsSite.angularPosDEC = Angle(degrees=10)
    function.parent.entityModel['ra'] = {'entity': Qt3DCore.QEntity()}
    function.parent.entityModel['ra'].addComponent(Qt3DCore.QTransform())
    function.parent.entityModel['dec'] = {'entity': Qt3DCore.QEntity()}
    function.parent.entityModel['dec'].addComponent(Qt3DCore.QTransform())
    suc = function.updateRotation()
    assert suc


def test_create_1(function):
    function.app.mount.obsSite.location.latitude = Angle(degrees=10)
    with mock.patch.object(function,
                           'updatePositions'):
        with mock.patch.object(function,
                               'updateRotation'):
            function.create()


def test_create_2(function):
    function.app.mount.obsSite.location.latitude = Angle(degrees=-10)
    with mock.patch.object(function,
                           'updatePositions'):
        with mock.patch.object(function,
                               'updateRotation'):
            function.create()

