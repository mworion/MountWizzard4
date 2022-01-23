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
# written in python3, (c) 2019-2022 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest

# external packages
from PyQt5.Qt3DCore import QEntity
from PyQt5.QtCore import QObject
from mountcontrol.mount import Mount
from skyfield.api import wgs84

# local import
from gui.extWindows.simulator.horizon import SimulatorHorizon


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    global app

    class Test1:
        horizonP = [(45, 45), (50, 50)]

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

    app = SimulatorHorizon(app=Test())
    yield


def test_createWall_1():
    val = app.createWall(QEntity(), 0, 0, 10)
    assert isinstance(val, QEntity)


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
    app.app.data.horizonP = None
    app.modelRoot = e
    app.model = {'test': {'e': e}}
    suc = app.create(e, True)
    assert not suc


def test_create_4(qtbot):
    app.horizon = [
        {'e': QEntity()},
    ]
    app.horizonRoot = QEntity()
    e = QEntity()
    app.modelRoot = e
    app.model = {'test': {'e': e}}
    suc = app.create(e, True)
    assert suc
