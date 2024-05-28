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
import unittest.mock as mock

# external packages
from PyQt6.Qt3DCore import QEntity, QTransform

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.extWindows.simulatorW import SimulatorWindow
from gui.extWindows.simulator.materials import Materials


@pytest.fixture(autouse=True, scope='module')
def function(qapp):
    func = SimulatorWindow(app=App())
    with mock.patch.object(func,
                           'show'):
        yield func.dome


def test_setTransparency_1(function):
    function.parent.entityModel['domeWall'] = QEntity()
    mat = Materials().dome2
    function.parent.entityModel['domeWall'].addComponent(mat)
    function.setTransparency()


def test_showEnable_1(function):
    function.parent.entityModel['dome'] = QEntity()
    function.showEnable(True)


def test_updateSize_1(function):
    function.parent.entityModel['domeWall'] = QEntity()
    t = QTransform()
    function.parent.entityModel['domeWall'].addComponent(t)
    function.parent.entityModel['domeSphere'] = QEntity()
    t = QTransform()
    function.parent.entityModel['domeSphere'].addComponent(t)
    function.updateSize()


def test_updateAzimuth_1(function):
    function.app.dome.data = {'ABS_DOME_POSITION.DOME_ABSOLUTE_POSITION': 0,
                              'DOME_SHUTTER.SHUTTER_OPEN': True}
    function.parent.entityModel['domeSphere'] = QEntity()
    t = QTransform()
    function.parent.entityModel['domeSphere'].addComponent(t)
    function.updateAzimuth()


def test_updateShutter_1(function):
    function.app.dome.data = {'ABS_DOME_POSITION.DOME_ABSOLUTE_POSITION': 0,
                              'DOME_SHUTTER.SHUTTER_OPEN': True}
    function.parent.entityModel['domeSlit1'] = QEntity()
    t = QTransform()
    function.parent.entityModel['domeSlit1'].addComponent(t)
    function.parent.entityModel['domeDoor1'] = QEntity()
    t = QTransform()
    function.parent.entityModel['domeDoor1'].addComponent(t)
    function.parent.entityModel['domeDoor2'] = QEntity()
    t = QTransform()
    function.parent.entityModel['domeDoor2'].addComponent(t)
    function.updateShutter()


def test_create_1(function):
    with mock.patch.object(function,
                           'updateAzimuth'):
        with mock.patch.object(function,
                               'updateShutter'):
            with mock.patch.object(function,
                                   'updateSize'):
                function.create()

