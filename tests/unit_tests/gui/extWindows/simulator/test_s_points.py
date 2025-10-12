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
from unittest import mock

# external packages
from PyQt5.Qt3DCore import QEntity, QTransform
from PyQt5.Qt3DExtras import QExtrudedTextMesh
from PyQt5.QtCore import QObject
from mw4.mountcontrol.mount import Mount
from skyfield.api import wgs84
import numpy as np

# local import
from mw4.gui.extWindows.simulator.points import SimulatorBuildPoints


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    global app

    class Test1:
        buildP = [(45, 45, True), (50, 50, False)]

    class Test(QObject):
        data = Test1()
        mount = Mount(host='localhost', MAC='00:00:00:00:00:00', verbose=False,
                      pathToData='tests/workDir/data')
        mount.obsSite.location = wgs84.latlon(latitude_degrees=20,
                                              longitude_degrees=10,
                                              elevation_m=500)
        mwGlob = {'modelDir': 'tests/workDir/model',
                  'imageDir': 'tests/workDir/image'}
        uiWindows = {'showImageW': {'classObj': None}}

    app = SimulatorBuildPoints(app=Test())
    yield


def test_createAnnotation_1(qtbot):
    e = QEntity()
    with mock.patch.object(QExtrudedTextMesh,
                           'setText'):
        val = app.createAnnotation(e, 45, 45, 'test', True)
        assert isinstance(val, QEntity)


def test_createAnnotation_2(qtbot):
    e = QEntity()
    with mock.patch.object(QExtrudedTextMesh,
                           'setText'):
        val = app.createAnnotation(e, 45, 45, 'test', False)
        assert isinstance(val, QEntity)


def test_createAnnotation_3(qtbot):
    e = QEntity()
    with mock.patch.object(QExtrudedTextMesh,
                           'setText'):
        val = app.createAnnotation(e, 45, 45, 'test', True, faceIn=True)
        assert isinstance(val, QEntity)


def test_create_1(qtbot):
    e = QEntity()
    suc = app.create(e, False)
    assert not suc


def test_create_2(qtbot):
    e = QEntity()
    app.pointRoot = e
    app.points = [{'e': e}]
    suc = app.create(e, False)
    assert not suc


def test_create_3(qtbot):
    e = QEntity()
    app.pointRoot = e
    app.points = [{'e': e}]
    suc = app.create(e, True)
    assert suc


def test_create_4():
    e = QEntity()
    app.pointRoot = e
    app.app.data.buildP = None
    app.points = [{'e': e}]
    suc = app.create(e, True)
    assert not suc


def test_create_5():
    e = QEntity()
    app.pointRoot = e
    app.points = [{'e': e}]

    with mock.patch.object(app,
                           'createAnnotation',
                           return_value=(QEntity(), 1, 1, 1)):
        suc = app.create(e, True, numbers=True, path=True)
        assert suc


def test_updatePositions_1(qtbot):
    app.pointRoot = None
    suc = app.updatePositions()
    assert not suc


def test_updatePositions_2(qtbot):
    app.pointRoot = QEntity()
    app.model = {
        'laser': {
            'e': QEntity(),
            't': QTransform()
        },
    }

    suc = app.updatePositions()
    assert not suc


def test_updatePositions_3(qtbot):
    app.pointRoot = QEntity()
    app.transformPointRoot = QTransform()
    app.model = {
        'laser': {
            'e': QEntity(),
            't': QTransform()
        },
        'ref': {
            'e': QEntity(),
            't': QTransform()
        },
        'alt': {
            'e': QEntity(),
            't': QTransform()
        },
        'az': {
            'e': QEntity(),
            't': QTransform()
        },
    }

    app.app.mount.obsSite.raJNow = 10
    app.app.mount.obsSite.timeSidereal = '10:10:10'

    with mock.patch.object(app.app.mount,
                           'calcTransformationMatricesActual',
                           return_value=(0, 0,
                                         np.array([1, 1, 1]),
                                         np.array([1, 1, 1]),
                                         np.array([1, 1, 1]))):
        suc = app.updatePositions()
        assert suc
