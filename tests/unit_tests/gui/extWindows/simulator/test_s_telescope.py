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
from PyQt6.Qt3DCore import QEntity, QTransform
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
    function.parent.entityModel['mountBase'] = QEntity()
    function.parent.entityModel['mountBase'].addComponent(QTransform())
    function.parent.entityModel['lat'] = QEntity()
    function.parent.entityModel['lat'].addComponent(QTransform())
    function.parent.entityModel['gem'] = QEntity()
    function.parent.entityModel['gem'].addComponent(QTransform())
    function.parent.entityModel['gemCorr'] = QEntity()
    function.parent.entityModel['gemCorr'].addComponent(QTransform())
    function.parent.entityModel['otaRing'] = QEntity()
    function.parent.entityModel['otaRing'].addComponent(QTransform())
    function.parent.entityModel['otaTube'] = QEntity()
    function.parent.entityModel['otaTube'].addComponent(QTransform())
    function.parent.entityModel['otaImagetrain'] = QEntity()
    function.parent.entityModel['otaImagetrain'].addComponent(QTransform())

    function.updatePositions()


def test_updateRotation_1(function):
    function.app.mount.obsSite.angularPosRA = None
    function.app.mount.obsSite.angularPosDEC = None
    suc = function.updateRotation()
    assert not suc


def test_updateRotation_2(function):
    function.app.mount.obsSite.angularPosRA = Angle(degrees=10)
    function.app.mount.obsSite.angularPosDEC = Angle(degrees=10)
    function.parent.entityModel['ra'] = QEntity()
    function.parent.entityModel['ra'].addComponent(QTransform())
    function.parent.entityModel['dec'] = QEntity()
    function.parent.entityModel['dec'].addComponent(QTransform())
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

