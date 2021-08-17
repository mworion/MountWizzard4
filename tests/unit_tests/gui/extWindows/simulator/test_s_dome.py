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
# written in python3, (c) 2019-2021 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest

# external packages
from PyQt5.Qt3DCore import QEntity, QTransform
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QDoubleSpinBox
from mountcontrol.mount import Mount
from skyfield.api import wgs84

# local import
from gui.extWindows.simulator.dome import SimulatorDome


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    global app

    class Test3:
        data = None
        clearOpening = 0

    class Test2:
        domeRadius = QDoubleSpinBox()
        domeRadius.setValue(1)
        clearOpening = QDoubleSpinBox()
        clearOpening.setValue(40)

    class Test1:
        ui = Test2()

    class Test(QObject):
        mount = Mount(host='localhost', MAC='00:00:00:00:00:00', verbose=False,
                      pathToData='tests/workDir/data')
        mount.obsSite.location = wgs84.latlon(latitude_degrees=20,
                                              longitude_degrees=10,
                                              elevation_m=500)
        mwGlob = {'modelDir': 'tests/workDir/model',
                  'imageDir': 'tests/workDir/image'}
        uiWindows = {'showImageW': {'classObj': None}}
        mainW = Test1()
        dome = Test3()

    app = SimulatorDome(app=Test())
    yield


def test_create_1(qtbot):
    app.app.dome.data = {'ABS_DOME_POSITION.DOME_ABSOLUTE_POSITION': 0,
                         'DOME_SHUTTER.SHUTTER_OPEN': True}
    app.modelRoot = QEntity()
    suc = app.create(QEntity(), False)
    assert not suc


def test_create_2(qtbot):
    app.app.dome.data = {'ABS_DOME_POSITION.DOME_ABSOLUTE_POSITION': 0,
                         'DOME_SHUTTER.SHUTTER_OPEN': True}
    app.modelRoot = QEntity()
    app.model = {'test': {'e': QEntity()}}
    suc = app.create(QEntity(), False)
    assert not suc


def test_create_3(qtbot):
    app.app.dome.data = {'ABS_DOME_POSITION.DOME_ABSOLUTE_POSITION': 0,
                         'DOME_SHUTTER.SHUTTER_OPEN': True}
    app.modelRoot = QEntity()
    app.model = {'test': {'e': QEntity()}}
    suc = app.create(app.modelRoot, True)
    assert suc


def test_setTransparency_1(qtbot):
    app.model = {
        'domeWall': {
            'e': QEntity()
        },
        'domeSphere': {
            'e': QEntity()
        },
        'domeSlit1': {
            'e': QEntity()
        },
        'domeSlit2': {
            'e': QEntity()
        },
        'domeDoor1': {
            'e': QEntity()
        },
        'domeDoor2': {
            'e': QEntity()
        },
    }

    suc = app.setTransparency(True)
    assert suc


def test_setTransparency_2(qtbot):
    app.model = {
        'domeWall': {
            'e': QEntity()
        },
        'domeSphere': {
            'e': QEntity()
        },
        'domeSlit1': {
            'e': QEntity()
        },
        'domeSlit2': {
            'e': QEntity()
        },
        'domeDoor1': {
            'e': QEntity()
        },
        'domeDoor2': {
            'e': QEntity()
        },
    }

    suc = app.setTransparency(False)
    assert suc


def test_setTransparency_3(qtbot):
    suc = app.setTransparency(False)
    assert not suc


def test_updateSettings_1(qtbot):
    suc = app.updateSettings()
    assert not suc


def test_updateSettings_2(qtbot):
    app.model = {
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

    suc = app.updateSettings()
    assert suc


def test_updatePositions_1(qtbot):
    suc = app.updatePositions()
    assert not suc


def test_updatePositions_2(qtbot):
    app.model = {
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

    app.app.dome.data = {'ABS_DOME_POSITION.DOME_ABSOLUTE_POSITION': 0,
                         'DOME_SHUTTER.SHUTTER_OPEN': True}

    suc = app.updatePositions()
    assert suc


def test_updatePositions_4(qtbot):
    app.model = {
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

    app.app.dome.data = {'ABS_DOME_POSITION.DOME_ABSOLUTE_POSITION': 0,
                         'DOME_SHUTTER.SHUTTER_OPEN': False}

    suc = app.updatePositions()
    assert suc
