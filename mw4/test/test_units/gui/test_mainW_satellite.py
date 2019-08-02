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
# Python  v3.7.4
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
    app.mainW.loadSatelliteSource()
    app.mainW.satellite = app.mainW.satellites['ZARYA']
    app.mainW.ui.mainTabWidget.setCurrentIndex(5)
    suc = app.mainW.updateSatelliteData()
    assert suc


def test_programTLEToMount_1():
    app.mount.mountUp = False
    suc = app.mainW.programTLEToMount()
    assert not suc


def test_programTLEToMount_2():
    app.mainW.loadSatelliteSource()
    app.mount.mountUp = True

    with mock.patch.object(app.mount.satellite,
                           'setTLE',
                           return_value=False):
        suc = app.mainW.programTLEToMount()
        assert not suc


def test_programTLEToMount_3():
    app.mainW.loadSatelliteSource()
    app.mount.mountUp = True

    with mock.patch.object(app.mount.satellite,
                           'setTLE',
                           return_value=True):
        suc = app.mainW.programTLEToMount()
        assert suc

