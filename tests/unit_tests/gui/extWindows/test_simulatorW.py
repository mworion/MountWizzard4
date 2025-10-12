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
import unittest.mock as mock

# external packages
from PyQt5.QtGui import QCloseEvent
from PyQt5.Qt3DCore import QTransform, QEntity
from skyfield.api import Angle

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from mw4.gui.utilities.toolsQtWidget import MWidget
from mw4.gui.extWindows.simulatorW import SimulatorWindow
from mw4.gui.extWindows.simulator import tools


@pytest.fixture(autouse=True, scope='module')
def function(qapp):
    func = SimulatorWindow(app=App())
    with mock.patch.object(func,
                           'show'):
        yield func


def test_initConfig_1(function):
    suc = function.initConfig()
    assert suc


def test_initConfig_5(function):
    function.app.config['simulatorW'] = {}
    function.app.config['simulatorW']['winPosX'] = 100
    function.app.config['simulatorW']['winPosY'] = 100
    suc = function.initConfig()
    assert suc


def test_storeConfig_1(function):
    if 'simulatorW' in function.app.config:
        del function.app.config['simulatorW']

    suc = function.storeConfig()
    assert suc


def test_storeConfig_2(function):
    function.app.config['simulatorW'] = {}
    suc = function.storeConfig()
    assert suc


def test_closeEvent_1(function):
    with mock.patch.object(function,
                           'createScene'):
        with mock.patch.object(MWidget,
                               'closeEvent'):
            function.showWindow()
            function.closeEvent(QCloseEvent)


def test_showWindow(function):
    with mock.patch.object(function,
                           'createScene'):
        with mock.patch.object(function,
                               'show'):
            suc = function.showWindow()
            assert suc


def test_colorChange(function):
    with mock.patch.object(function,
                           'createScene'):
        suc = function.colorChange()
        assert suc


def test_limitPositionZ_1(function):
    from PyQt5.QtGui import QVector3D

    function.camera.setPosition(QVector3D(1, 1, 1))
    suc = function.limitPositionZ()
    assert suc
    assert function.camera.position()[1] == 1


def test_limitPositionZ_2(function):
    from PyQt5.QtGui import QVector3D

    function.camera.setPosition(QVector3D(1, -10, 1))
    suc = function.limitPositionZ()
    assert suc
    assert function.camera.position()[1] == 0


def test_buildPointsCreate_1(function):
    function.world = {
        'ref1000': {
            'parent': None,
            'rot': [-90, 90, 0],
            'e': QEntity(),
        },
        'ref': {
            'parent': 'ref1000',
            'scale': [0.001, 0.001, 0.001],
            'e': QEntity(),
        }
    }
    suc = function.buildPointsCreate()
    assert suc


def test_horizonCreate_1(function):
    function.world = {
        'ref1000': {
            'parent': None,
            'rot': [-90, 90, 0],
            'e': QEntity(),
        },
        'ref': {
            'parent': 'ref1000',
            'scale': [0.001, 0.001, 0.001],
            'e': QEntity(),
        }
    }
    suc = function.horizonCreate()
    assert suc


def test_pointerCreate_1(function):
    function.world = {
        'ref1000': {
            'parent': None,
            'rot': [-90, 90, 0],
            'e': QEntity(),
        },
        'ref': {
            'parent': 'ref1000',
            'scale': [0.001, 0.001, 0.001],
            'e': QEntity(),
        }
    }
    suc = function.pointerCreate()
    assert suc


def test_laserCreate_1(function):
    function.world = {
        'ref1000': {
            'parent': None,
            'rot': [-90, 90, 0],
            'e': QEntity(),
        },
        'ref': {
            'parent': 'ref1000',
            'scale': [0.001, 0.001, 0.001],
            'e': QEntity(),
        }
    }
    suc = function.laserCreate()
    assert suc


def test_topView_1(function):
    suc = function.topView()
    assert suc


def test_topEastView_1(function):
    suc = function.topEastView()
    assert suc


def test_topWestView_1(function):
    suc = function.topWestView()
    assert suc


def test_eastView_1(function):
    suc = function.eastView()
    assert suc


def test_westView_1(function):
    suc = function.westView()
    assert suc


def test_createWorld_1(function):
    with mock.patch.object(tools,
                           'linkModel'):
        function.createWorld(QEntity())
        assert 'environ' in function.world


def test_createScene_1(function):
    function.createMutex.lock()
    suc = function.createScene()
    assert not suc
    function.createMutex.unlock()


def test_createScene_2(function):
    function.app.deviceStat['dome'] = True
    function.app.mount.obsSite.location.latitude = Angle(degrees=10)
    function.ui.checkShowNumbers.setChecked(True)
    function.ui.checkShowSlewPath.setChecked(True)
    function.ui.checkShowPointer.setChecked(True)
    function.ui.checkShowHorizon.setChecked(True)
    function.ui.checkShowBuildPoints.setChecked(True)
    suc = function.createScene()
    assert suc


def test_createScene_3(function):
    function.app.deviceStat['dome'] = False
    function.app.mount.obsSite.location.latitude = Angle(degrees=10)
    function.ui.checkShowNumbers.setChecked(True)
    function.ui.checkShowSlewPath.setChecked(True)
    function.ui.checkShowPointer.setChecked(True)
    function.ui.checkShowHorizon.setChecked(True)
    function.ui.checkShowBuildPoints.setChecked(True)
    suc = function.createScene()
    assert suc


def test_updateSettings_1(function):
    function.world = None
    suc = function.updateSettings()
    assert not suc


def test_updateSettings_2(function):
    function.world = {
        'domeColumn': {'t': QTransform()},
        'domeCompassRose': {'t': QTransform()},
        'domeCompassRoseChar': {'t': QTransform()},
    }
    suc = function.updateSettings()
    assert suc
