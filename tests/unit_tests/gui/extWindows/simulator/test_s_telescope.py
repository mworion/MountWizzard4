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
from PyQt5.QtWidgets import QDoubleSpinBox
from PyQt5.Qt3DCore import QEntity, QTransform
from PyQt5.QtCore import QObject
from PyQt5.Qt3DExtras import QCuboidMesh
from mountcontrol.mount import Mount
from skyfield.api import wgs84

# local import
from gui.extWindows.simulator.telescope import SimulatorTelescope


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    global app

    class Test2:
        domeRadius = QDoubleSpinBox()
        domeRadius.setValue(1)
        domeShutterWidth = QDoubleSpinBox()
        domeShutterWidth.setValue(40)
        domeNorthOffset = QDoubleSpinBox()
        domeNorthOffset.setValue(40)
        domeEastOffset = QDoubleSpinBox()
        domeEastOffset.setValue(40)
        domeVerticalOffset = QDoubleSpinBox()
        domeVerticalOffset.setValue(40)
        offLAT = QDoubleSpinBox()
        offLAT.setValue(40)

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

    app = SimulatorTelescope(app=Test())
    yield


def test_create_1(qtbot):
    e = QEntity()
    suc = app.create(e, False)
    assert not suc


def test_create_2(qtbot):
    e = QEntity()
    app.modelRoot = e
    app.model = {'test': {'e': e}}
    suc = app.create(e, False)
    assert not suc


def test_create_3(qtbot):
    e = QEntity()
    app.modelRoot = e
    app.model = {'test': {'e': e}}
    suc = app.create(e, True)
    assert suc


def test_create_4(qtbot):
    e = QEntity()
    app.modelRoot = e
    app.model = {'test': {'e': e}}
    suc = app.create(e, True, -10)
    assert suc


def test_updateSettings_1(qtbot):
    suc = app.updateSettings()
    assert not suc


def test_updateSettings_2(qtbot):
    app.model = {
        'mountBase': {
            'e': QEntity(),
            't': QTransform()
        },
        'lat': {
            'e': QEntity(),
            't': QTransform()
        },
        'gem': {
            'm': QCuboidMesh(),
            'e': QEntity(),
            't': QTransform()
        },
        'gemCorr': {
            'e': QEntity(),
            't': QTransform()
        },
        'otaRing': {
            'e': QEntity(),
            't': QTransform()
        },
        'otaTube': {
            'e': QEntity(),
            't': QTransform()
        },
        'otaImagetrain': {
            'e': QEntity(),
            't': QTransform()
        },
    }

    app.app.mount.geometry.offGemPlate = 10
    suc = app.updateSettings()
    assert suc


def test_updatePositions_1(qtbot):
    suc = app.updatePositions()
    assert not suc


def test_updatePositions_2(qtbot):
    app.model = {
        'ra': {
            'e': QEntity(),
            't': QTransform()
        },
        'dec': {
            'e': QEntity(),
            't': QTransform()
        },
    }

    suc = app.updatePositions()
    assert not suc


def test_updatePositions_3(qtbot):
    app.model = {
        'ra': {
            'e': QEntity(),
            't': QTransform()
        },
        'dec': {
            'e': QEntity(),
            't': QTransform()
        },
    }
    app.app.mount.obsSite.angularPosRA = 10
    app.app.mount.obsSite.angularPosDEC = 10
    suc = app.updatePositions()
    assert suc
