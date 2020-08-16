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
# written in python3 , (c) 2019, 2020 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
import unittest.mock as mock
from queue import Queue

# external packages
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QCheckBox
from PyQt5.QtWidgets import QDoubleSpinBox
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.Qt3DCore import QTransform
from mountcontrol.qtmount import Mount

# local import
from gui.extWindows.simulatorW import SimulatorWindow


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    global Test, app

    class Test1a:
        checkDomeGeometry = QCheckBox()
        domeNorthOffset = QDoubleSpinBox()
        domeEastOffset = QDoubleSpinBox()
        domeVerticalOffset = QDoubleSpinBox()
        simulator = QHBoxLayout()

    class Test1:
        ui = Test1a()

    class Test(QObject):
        config = {'mainW': {}}
        update1s = pyqtSignal()
        updateDomeSettings = pyqtSignal()
        drawBuildPoints = pyqtSignal()
        drawHorizonPoints = pyqtSignal()
        messageQueue = Queue()
        deviceStat = {'dome': True}
        mount = Mount(host='localhost', MAC='00:00:00:00:00:00', verbose=False,
                      pathToData='tests/data')
        mainW = Test1()

    with mock.patch.object(SimulatorWindow,
                           'show'):
        app = SimulatorWindow(app=Test())
    yield


def test_initConfig_1(qtbot):
    suc = app.initConfig()
    assert suc


def test_initConfig_2(qtbot):
    app.app.config['simulatorW'] = {'winPosX': 10000}
    suc = app.initConfig()
    assert suc


def test_initConfig_3(qtbot):
    app.app.config['simulatorW'] = {'winPosY': 10000}
    suc = app.initConfig()
    assert suc


def test_initConfig_4(qtbot):
    app.app.config['simulatorW'] = {'cameraPositionX': 1,
                                    'cameraPositionY': 1,
                                    'cameraPositionZ': 1,
                                    }
    suc = app.initConfig()
    assert suc


def test_storeConfig_1(qtbot):
    if 'simulatorW' in app.app.config:
        del app.app.config['simulatorW']
    suc = app.storeConfig()
    assert suc


def test_storeConfig_2(qtbot):
    app.app.config['simulatorW'] = {}
    suc = app.storeConfig()
    assert suc


def test_closeEvent_1(qtbot):
    app.closeEvent(QCloseEvent())


def test_buildPointsCreate_1(qtbot):
    suc = app.buildPointsCreate()
    assert suc


def test_domeCreate_1(qtbot):
    suc = app.domeCreate()
    assert suc


def test_horizonCreate_1(qtbot):
    suc = app.horizonCreate()
    assert suc


def test_pointerCreate_1(qtbot):
    suc = app.pointerCreate()
    assert suc


def test_setDomeTransparency_1(qtbot):
    suc = app.setDomeTransparency()
    assert suc


def test_setPL_1(qtbot):
    suc = app.setPL()
    assert suc


def test_topView_1(qtbot):
    suc = app.topView()
    assert suc


def test_topEastView_1(qtbot):
    suc = app.topEastView()
    assert suc


def test_topWestView_1(qtbot):
    suc = app.topWestView()
    assert suc


def test_eastView_1(qtbot):
    suc = app.eastView()
    assert suc


def test_westView_1(qtbot):
    suc = app.westView()
    assert suc


def test_updateSettings_1(qtbot):
    app.world = None
    suc = app.updateSettings()
    assert not suc


def test_updateSettings_2(qtbot):
    app.world = {'test'}
    app.app.mainW = None
    suc = app.updateSettings()
    assert not suc


def test_updateSettings_3(qtbot):
    app.world = {
        'domeColumn': {'t': QTransform()},
        'domeCompassRose': {'t': QTransform()},
        'domeCompassRoseChar': {'t': QTransform()},
    }
    suc = app.updateSettings()
    assert suc
