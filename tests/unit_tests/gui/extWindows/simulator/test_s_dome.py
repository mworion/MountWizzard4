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
# written in python3, (c) 2019-2023 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest

# external packages
from PyQt5.Qt3DCore import QEntity, QTransform

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.extWindows.simulator.dome import SimulatorDome


@pytest.fixture(autouse=True, scope='function')
def function():
    func = SimulatorDome(app=App())
    yield func


def test_create_1(function):
    function.app.dome.data = {'ABS_DOME_POSITION.DOME_ABSOLUTE_POSITION': 0,
                         'DOME_SHUTTER.SHUTTER_OPEN': True}
    function.modelRoot = QEntity()
    suc = function.create(QEntity(), False, False)
    assert not suc


def test_create_2(function):
    function.app.dome.data = {'ABS_DOME_POSITION.DOME_ABSOLUTE_POSITION': 0,
                         'DOME_SHUTTER.SHUTTER_OPEN': True}
    function.modelRoot = QEntity()
    function.model = {'test': {'e': QEntity()}}
    suc = function.create(QEntity(), False, False)
    assert not suc


def test_create_3(function):
    function.app.dome.data = {'ABS_DOME_POSITION.DOME_ABSOLUTE_POSITION': 0,
                         'DOME_SHUTTER.SHUTTER_OPEN': True}
    function.modelRoot = QEntity()
    function.model = {'test': {'e': QEntity()}}
    suc = function.create(function.modelRoot, True, False)
    assert suc


def test_create_4(function):
    function.app.dome.data = {'ABS_DOME_POSITION.DOME_ABSOLUTE_POSITION': 0,
                         'DOME_SHUTTER.SHUTTER_OPEN': True}
    function.modelRoot = QEntity()
    function.model = {'test': {'e': QEntity()}}
    suc = function.create(function.modelRoot, True, True)
    assert suc


def test_updateSettings_1(function):
    suc = function.updateSettings()
    assert not suc


def test_updateSettings_2(function):
    function.model = {
        'domeWall': {
            'e': QEntity(),
            't': QTransform()
        },
        'domeSphere': {
            'e': QEntity(),
            't': QTransform()
        },
        'domeFloor': {
            'e': QEntity(),
            't': QTransform()
        },
    }

    suc = function.updateSettings()
    assert suc


def test_updatePositions_1(function):
    suc = function.updatePositions()
    assert not suc


def test_updatePositions_2(function):
    function.model = {
        'domeSphere': {
            'e': QEntity(),
            't': QTransform()
        },
        'domeDoor1': {
            'e': QEntity(),
            't': QTransform()
        },
        'domeDoor2': {
            'e': QEntity(),
            't': QTransform()
        },
        'domeSlit1': {
            'e': QEntity(),
            't': QTransform()
        },
        'domeSlit2': {
            'e': QEntity(),
            't': QTransform()
        },
    }

    function.app.dome.data = {'ABS_DOME_POSITION.DOME_ABSOLUTE_POSITION': 0,
                         'DOME_SHUTTER.SHUTTER_OPEN': True}

    suc = function.updatePositions()
    assert suc


def test_updatePositions_4(function):
    function.model = {
        'domeSphere': {
            'e': QEntity(),
            't': QTransform()
        },
        'domeDoor1': {
            'e': QEntity(),
            't': QTransform()
        },
        'domeDoor2': {
            'e': QEntity(),
            't': QTransform()
        },
        'domeSlit1': {
            'e': QEntity(),
            't': QTransform()
        },
        'domeSlit2': {
            'e': QEntity(),
            't': QTransform()
        },
    }

    function.app.dome.data = {'ABS_DOME_POSITION.DOME_ABSOLUTE_POSITION': 0,
                         'DOME_SHUTTER.SHUTTER_OPEN': False}

    suc = function.updatePositions()
    assert suc
