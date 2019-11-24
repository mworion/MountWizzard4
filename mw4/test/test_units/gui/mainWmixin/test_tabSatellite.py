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
# Python  v3.7.5
#
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock
import pytest
# external packages
from skyfield.api import Angle
# local import
from mw4.test.test_units.setupQt import setupQt


@pytest.fixture(autouse=True, scope='module')
def module_setup_teardown():
    global app, spy, mwGlob, test
    app, spy, mwGlob, test = setupQt()
    yield


def test_initConfig_1():
    app.config['mainW'] = {}
    suc = app.mainW.initConfig()
    assert suc


def test_initConfig_2():
    del app.config['mainW']
    suc = app.mainW.initConfig()
    assert suc


def test_storeConfig_1():
    suc = app.storeConfig()
    assert suc


def test_setupIcons():
    suc = app.mainW.setupIcons()
    assert suc


def test_sources():
    assert len(app.mainW.satelliteSourceDropDown) == 13


def test_setupSatelliteSourceGui():
    suc = app.mainW.setupSatelliteSourceGui()
    assert suc
    assert len(app.mainW.ui.satelliteSource) == len(app.mainW.satelliteSourceDropDown)


def test_prepare_1():
    suc = app.mainW.prepare()
    assert not suc


def test_prepare_2():
    class Test:
        name = 'test'

    suc = app.mainW.prepare(Test())
    assert suc


def test_setupSatelliteGui_1():
    suc = app.mainW.setupSatelliteGui()
    assert suc


def test_loadTLEData_1():
    suc = app.mainW.loadTLEData()
    assert not suc


def test_loadTLEData_2():
    suc = app.mainW.loadTLEData(f'{mwGlob["dataDir"]}/act.txt')
    assert not suc


def test_loadTLEData_3():
    suc = app.mainW.loadTLEData(f'{mwGlob["dataDir"]}/active.txt')
    assert suc


def test_loadSatelliteSourceWorker_1():
    suc = app.mainW.loadSatelliteSourceWorker()
    assert suc


def test_loadSatelliteSource_1():
    suc = app.mainW.loadSatelliteSource()
    assert suc


def test_updateSatelliteData_1():
    suc = app.mainW.updateSatelliteData()
    assert not suc


def test_updateSatelliteData_2():
    app.mainW.satellite = 'test'
    suc = app.mainW.updateSatelliteData()
    assert not suc


def test_updateSatelliteData_3():
    app.mainW.loadTLEData(f'{mwGlob["dataDir"]}/active.txt')
    app.mainW.satellite = app.mainW.satellites['ZARYA']
    app.mainW.ui.mainTabWidget.setCurrentIndex(5)
    suc = app.mainW.updateSatelliteData()
    assert suc


def test_updateSatelliteData_4():
    app.mainW.loadTLEData(f'{mwGlob["dataDir"]}/active.txt')
    app.mount.obsSite.setRefractionPress = 1000
    app.mount.obsSite.setRefractionTemp = 10
    app.mainW.loadSatelliteSourceWorker()
    app.mainW.satellite = app.mainW.satellites['ZARYA']
    app.mainW.ui.mainTabWidget.setCurrentIndex(5)
    suc = app.mainW.updateSatelliteData()
    assert suc


def test_programTLEToMount_1():
    app.mount.mountUp = False
    suc = app.mainW.programTLEToMount()
    assert not suc


def test_programTLEToMount_2():
    app.mainW.loadTLEData(f'{mwGlob["dataDir"]}/active.txt')
    app.mount.mountUp = True

    with mock.patch.object(app.mount.satellite,
                           'setTLE',
                           return_value=False):
        suc = app.mainW.programTLEToMount()
        assert not suc


def test_programTLEToMount_3():
    app.mainW.loadTLEData(f'{mwGlob["dataDir"]}/active.txt')
    app.mount.mountUp = True

    with mock.patch.object(app.mount.satellite,
                           'setTLE',
                           return_value=True):
        suc = app.mainW.programTLEToMount()
        assert suc


def test_calcTLEParams_1():
    with mock.patch.object(app.mount,
                           'calcTLE'):
        suc = app.mainW.calcTLEParams()
        assert suc


def test_calcTLEParams_2():
    app.mainW.satellite = None
    with mock.patch.object(app.mount,
                           'calcTLE'):
        suc = app.mainW.calcTLEParams()
        assert not suc


def test_extractSatelliteData_1():

    suc = app.mainW.extractSatelliteData('test', satName='test')
    assert not suc


def test_extractSatelliteData_2():

    suc = app.mainW.extractSatelliteData('test', satName=0)
    assert not suc


def test_extractSatelliteData_3():

    suc = app.mainW.extractSatelliteData('test', satName='ZARYA')
    assert not suc


def test_extractSatelliteData_4():

    suc = app.mainW.extractSatelliteData('test', satName='ZARYA')
    assert not suc


def test_enableTrack_1():
    suc = app.mainW.enableTrack()
    assert not suc


def test_enableTrack_2():
    class Test:
        jdStart = None
        jdEnd = None
        flip = False
        message = None
        altitude = None

    suc = app.mainW.enableTrack(Test())
    assert suc


def test_enableTrack_3():
    class Test:
        jdStart = 2458715.14771
        jdEnd = 2458715.15
        flip = False
        message = 'test'
        altitude = Angle(degrees=50)

    suc = app.mainW.enableTrack(Test())
    assert suc


def test_startTrack_1():
    app.mount.mountUp = False
    suc = app.mainW.startTrack()
    assert not suc


def test_startTrack_2():
    app.mount.mountUp = True
    with mock.patch.object(app.mount.satellite,
                           'slewTLE',
                           return_value=(False, 'test')):
        suc = app.mainW.startTrack()
        assert not suc


def test_startTrack_3():
    app.mount.mountUp = True
    with mock.patch.object(app.mount.satellite,
                           'slewTLE',
                           return_value=(False, 'test')):
        suc = app.mainW.startTrack()
        assert not suc


def test_startTrack_4():
    app.mount.mountUp = True
    app.mount.obsSite.status = 5
    with mock.patch.object(app.mount.satellite,
                           'slewTLE',
                           return_value=(False, 'test')):
        suc = app.mainW.startTrack()
        assert not suc


def test_startTrack_5():
    app.mount.mountUp = True
    app.mount.obsSite.status = 5
    with mock.patch.object(app.mount.satellite,
                           'slewTLE',
                           return_value=(True, 'test')):
        suc = app.mainW.startTrack()
        assert suc


def test_stopTrack_1():
    app.mount.mountUp = False
    suc = app.mainW.stopTrack()
    assert not suc


def test_stopTrack_2():
    app.mount.mountUp = True
    with mock.patch.object(app.mount.obsSite,
                           'stopTracking',
                           return_value=False):
        suc = app.mainW.stopTrack()
        assert not suc


def test_stopTrack_3():
    app.mount.mountUp = True
    with mock.patch.object(app.mount.obsSite,
                           'stopTracking',
                           return_value=True):
        suc = app.mainW.stopTrack()
        assert suc
