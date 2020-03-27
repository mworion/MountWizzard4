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
import pytest
from unittest import mock
import logging

# external packages
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import Qt
from mountcontrol.qtmount import Mount
from skyfield.toposlib import Topos
import numpy as np
from skyfield.api import EarthSatellite
from skyfield.api import Angle

# local import
from mw4.gui.mainWmixin.tabSatellite import Satellite
from mw4.gui.widgets.main_ui import Ui_MainWindow
from mw4.gui.widget import MWidget
from mw4.environment.skymeter import Skymeter
from mw4.base.loggerMW import CustomLogger


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown(qtbot):
    global ui, widget, Test, Test1, app

    class Test1(QObject):
        mount = Mount(expire=False, verbose=False, pathToData='mw4/test/data')
        update10s = pyqtSignal()
        threadPool = QThreadPool()

    class Test(QObject):
        config = {'mainW': {}}
        threadPool = QThreadPool()
        update1s = pyqtSignal()
        update3s = pyqtSignal()
        message = pyqtSignal(str, int)
        mount = Mount(expire=False, verbose=False, pathToData='mw4/test/data')
        mwGlob = {'dataDir': 'mw4/test/data'}
        uiWindows = {'showSatelliteW': None}
        mount.obsSite.location = Topos(latitude_degrees=50,
                                       longitude_degrees=10,
                                       elevation_m=500)
        skymeter = Skymeter(app=Test1())

    widget = QWidget()
    ui = Ui_MainWindow()
    ui.setupUi(widget)

    app = Satellite(app=Test(), ui=ui,
                    clickable=MWidget().clickable)
    app.changeStyleDynamic = MWidget().changeStyleDynamic
    app.close = MWidget().close
    app.deleteLater = MWidget().deleteLater
    app.deviceStat = dict()
    app.log = CustomLogger(logging.getLogger(__name__), {})
    app.threadPool = QThreadPool()

    qtbot.addWidget(app)

    yield

    app.threadPool.waitForDone(1000)
    del widget, ui, Test, Test1, app


def test_sources():
    assert len(app.satelliteSourceURLs) == 13


def test_initConfig_1():
    suc = app.initConfig()
    assert suc


def test_setupSatelliteSourceGui():
    suc = app.setupSatelliteSourceURLsDropDown()
    assert suc
    assert len(app.ui.satelliteSource) == len(app.satelliteSourceURLs)


def test_setupSatelliteGui_1():
    suc = app.setupSatelliteNameList()
    assert suc


def test_setupSatelliteGui_2():
    class Test1:
        satnum = 12345

    class Test:
        model = Test1()

    app.satellites = {'sat1': Test()}
    suc = app.setupSatelliteNameList()
    assert suc


def test_loadTLEData_1():
    suc = app.loadRawTLEData()
    assert not suc


def test_loadTLEData_2():
    suc = app.loadRawTLEData('mw4/test/testData/act.txt')
    assert not suc


def test_loadTLEData_3():
    suc = app.loadRawTLEData('mw4/test/testData/active.txt')
    assert suc


def test_loadSatelliteSourceWorker_1():
    suc = app.loadTLEDataFromSourceURLsWorker()
    assert not suc


def test_loadSatelliteSourceWorker_2():
    app.ui.satelliteSource.addItem('Active')
    with mock.patch.object(app,
                           'loadRawTLEData',
                           return_value=False):
        suc = app.loadTLEDataFromSourceURLsWorker()
        assert not suc


def test_loadSatelliteSourceWorker_3():
    app.ui.satelliteSource.addItem('Active')
    with mock.patch.object(app,
                           'loadRawTLEData',
                           return_value=True):
        suc = app.loadTLEDataFromSourceURLsWorker()
        assert suc


def test_loadSatelliteSource_1():
    suc = app.loadTLEDataFromSourceURLs()
    assert suc


def test_updateSatelliteData_1():
    suc = app.updateOrbit()
    assert not suc


def test_updateSatelliteData_2():
    app.satellite = 'test'
    suc = app.updateOrbit()
    assert not suc


def test_updateSatelliteData_3():
    app.satellite = 'test'
    app.ui.mainTabWidget.setCurrentIndex(1)
    app.app.uiWindows = {'showSatelliteW': {'test': 1}}
    suc = app.updateOrbit()
    assert not suc


def test_updateSatelliteData_4():
    class Test1(QObject):
        update = pyqtSignal(object, object, object)

    class Test(QObject):
        signals = Test1()

    tle = ["TIANGONG 1",
           "1 37820U 11053A   14314.79851609  .00064249  00000-0  44961-3 0  5637",
           "2 37820  42.7687 147.7173 0010686 283.6368 148.1694 15.73279710179072"]
    app.satellite = EarthSatellite(*tle[1:3], name=tle[0])
    app.ui.mainTabWidget.setCurrentIndex(1)
    app.app.uiWindows = {'showSatelliteW': {'classObj': Test()}}
    suc = app.updateOrbit()
    assert suc


def test_updateSatelliteData_5():
    tle = ["TIANGONG 1",
           "1 37820U 11053A   14314.79851609  .00064249  00000-0  44961-3 0  5637",
           "2 37820  42.7687 147.7173 0010686 283.6368 148.1694 15.73279710179072"]
    app.satellite = EarthSatellite(*tle[1:3], name=tle[0])
    app.ui.mainTabWidget.setCurrentIndex(5)
    app.app.uiWindows = {'showSatelliteW': {'test': 1}}
    suc = app.updateOrbit()
    assert suc


def test_programTLEToMount_1():
    app.app.mount.mountUp = False
    suc = app.programTLEDataToMount()
    assert not suc


def test_programTLEToMount_2():
    class Test:
        name = 'TIANGONG 1'

    app.satellite = Test()
    app.app.mount.mountUp = True
    app.app.mount.satellite.tleParams.name = 'TIANGONG 1'
    suc = app.programTLEDataToMount()
    assert suc


def test_programTLEToMount_3():
    tle = ["TIANGONG 1",
           "1 37820U 11053A   14314.79851609  .00064249  00000-0  44961-3 0  5637",
           "2 37820  42.7687 147.7173 0010686 283.6368 148.1694 15.73279710179072"]
    app.satellite = EarthSatellite(*tle[1:3], name=tle[0])
    tle = ["TIANGONG 1",
           "1 37820U 11053A   14314.79851609  .00064249  00000-0  44961-3 0  5637",
           "2 37820  42.7687 147.7173 0010686 283.6368 148.1694 15.73279710179072"]
    app.satellitesRawTLE = {tle[0].strip('\n'):
                            {'line0': tle[0].strip('\n'),
                             'line1': tle[1].strip('\n'),
                             'line2': tle[2].strip('\n'),
                             }
                            }

    app.app.mount.mountUp = True
    app.app.mount.satellite.tleParams.name = 'TIANGONG 2'
    with mock.patch.object(app.app.mount.satellite,
                           'setTLE',
                           return_value=False):
        suc = app.programTLEDataToMount()
        assert not suc


def test_programTLEToMount_4():
    tle = ["TIANGONG 1",
           "1 37820U 11053A   14314.79851609  .00064249  00000-0  44961-3 0  5637",
           "2 37820  42.7687 147.7173 0010686 283.6368 148.1694 15.73279710179072"]
    app.satellite = EarthSatellite(*tle[1:3], name=tle[0])
    tle = ["TIANGONG 1",
           "1 37820U 11053A   14314.79851609  .00064249  00000-0  44961-3 0  5637",
           "2 37820  42.7687 147.7173 0010686 283.6368 148.1694 15.73279710179072"]
    app.satellitesRawTLE = {tle[0].strip('\n'):
                            {'line0': tle[0].strip('\n'),
                             'line1': tle[1].strip('\n'),
                             'line2': tle[2].strip('\n'),
                             }
                            }
    app.app.mount.mountUp = True
    app.app.mount.satellite.tleParams.name = 'TIANGONG 2'
    with mock.patch.object(app.app.mount.satellite,
                           'setTLE',
                           return_value=True):
        suc = app.programTLEDataToMount()
        assert suc


def test_calcTLEParams_1():
    with mock.patch.object(app.app.mount,
                           'calcTLE'):
        suc = app.calcOrbitFromTLEInMount()
        assert not suc


def test_calcTLEParams_2():
    app.satellite = 'test'
    with mock.patch.object(app.app.mount,
                           'calcTLE'):
        suc = app.calcOrbitFromTLEInMount()
        assert suc


def test_showRises_1():
    tle = ["NOAA 8",
           "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
           "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954"]
    app.satellite = EarthSatellite(*tle[1:3], name=tle[0])
    with mock.patch.object(EarthSatellite,
                           'find_events',
                           return_value=(app.app.mount.obsSite.timeJD, [1])):
        suc = app.showRises()
        assert suc


def test_showRises_2():
    t0 = app.app.mount.obsSite.timeJD
    t1 = app.app.mount.obsSite.ts.tt_jd(app.app.mount.obsSite.timeJD.tt + 0.1)
    t2 = app.app.mount.obsSite.ts.tt_jd(app.app.mount.obsSite.timeJD.tt + 0.2)

    tle = ["NOAA 8",
           "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
           "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954"]
    app.satellite = EarthSatellite(*tle[1:3], name=tle[0])
    with mock.patch.object(EarthSatellite,
                           'find_events',
                           return_value=([t0, t1, t2],
                                         [0, 2, 1])):
        suc = app.showRises()
        assert suc


def test_showRises_3():
    t0 = app.app.mount.obsSite.timeJD
    t1 = app.app.mount.obsSite.ts.tt_jd(app.app.mount.obsSite.timeJD.tt + 0.1)
    t2 = app.app.mount.obsSite.ts.tt_jd(app.app.mount.obsSite.timeJD.tt + 0.2)
    t3 = app.app.mount.obsSite.ts.tt_jd(app.app.mount.obsSite.timeJD.tt + 0.3)

    tle = ["NOAA 8",
           "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
           "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954"]
    app.satellite = EarthSatellite(*tle[1:3], name=tle[0])
    with mock.patch.object(EarthSatellite,
                           'find_events',
                           return_value=([t0, t1, t2, t3],
                                         [2, 2, 2, 2])):
        suc = app.showRises()
        assert suc


def test_signalExtractSatelliteData_1():
    pass
    widget = app.ui.listSatelliteNames
    widget.addItem('test12345')


def test_extractSatelliteData_1():
    suc = app.extractSatelliteData(satName='')
    assert not suc


def test_extractSatelliteData_2():
    tle = ["NOAA 8",
           "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
           "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954"]
    sat = EarthSatellite(*tle[1:3], name=tle[0])

    app.satellites = {'NOAA 8': sat,
                      'Test1': sat}

    suc = app.extractSatelliteData(satName='NOAA 8')
    assert not suc


def test_extractSatelliteData_3():
    app.ui.listSatelliteNames.clear()
    app.ui.listSatelliteNames.addItem('NOAA 8')
    app.ui.listSatelliteNames.addItem('Test1')

    tle = ["NOAA 8",
           "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
           "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954"]
    sat = EarthSatellite(*tle[1:3], name=tle[0])

    app.satellites = {'NOAA 8': sat,
                      'Test1': sat}

    suc = app.extractSatelliteData(satName='TIANGONG 1')
    assert not suc


def test_extractSatelliteData_4():
    class Test1(QObject):
        update = pyqtSignal(object, object, object)
        show = pyqtSignal(object)

    class Test(QObject):
        signals = Test1()

    app.app.uiWindows = {'showSatelliteW': {'classObj': Test()}}
    app.ui.listSatelliteNames.clear()
    app.ui.listSatelliteNames.addItem('        NOAA 8')
    app.ui.listSatelliteNames.addItem('        Test1')

    tle = ["NOAA 8",
           "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
           "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954"]
    sat = EarthSatellite(*tle[1:3], name=tle[0])

    app.satellites = {'NOAA 8': sat,
                      'Test1': sat}

    with mock.patch.object(app,
                           'showRises'):
        suc = app.extractSatelliteData(satName='NOAA 8')
        assert suc


def test_getSatelliteDataFromDatabase_1():
    suc = app.getSatelliteDataFromDatabase()
    assert not suc


def test_getSatelliteDataFromDatabase_2():
    class Test:
        name = 'test'

    suc = app.getSatelliteDataFromDatabase(Test())
    assert suc


def test_enableTrack_1():
    suc = app.updateSatelliteTrackGui()
    assert not suc


def test_enableTrack_2():
    class Test:
        jdStart = None
        jdEnd = None
        flip = False
        message = None
        altitude = None

    suc = app.updateSatelliteTrackGui(Test())
    assert suc


def test_enableTrack_3():
    class Test:
        jdStart = 2458715.14771
        jdEnd = 2458715.15
        flip = False
        message = 'test'
        altitude = Angle(degrees=50)

    suc = app.updateSatelliteTrackGui(Test())
    assert suc


def test_startTrack_1():
    app.app.mount.mountUp = False
    suc = app.startTrack()
    assert not suc


def test_startTrack_2():
    app.app.mount.mountUp = True
    with mock.patch.object(app.app.mount.satellite,
                           'slewTLE',
                           return_value=(False, 'test')):
        suc = app.startTrack()
        assert not suc


def test_startTrack_3():
    app.app.mount.mountUp = True
    with mock.patch.object(app.app.mount.satellite,
                           'slewTLE',
                           return_value=(False, 'test')):
        suc = app.startTrack()
        assert not suc


def test_startTrack_4():
    app.app.mount.mountUp = True
    app.app.mount.obsSite.status = 5
    with mock.patch.object(app.app.mount.satellite,
                           'slewTLE',
                           return_value=(False, 'test')):
        suc = app.startTrack()
        assert not suc


def test_startTrack_5():
    app.app.mount.mountUp = True
    app.app.mount.obsSite.status = 5
    with mock.patch.object(app.app.mount.satellite,
                           'slewTLE',
                           return_value=(True, 'test')):
        suc = app.startTrack()
        assert suc


def test_startTrack_6():
    app.app.mount.mountUp = True
    app.app.mount.obsSite.status = 5
    with mock.patch.object(app.app.mount.satellite,
                           'slewTLE',
                           return_value=(True, 'test')):
        with mock.patch.object(app.app.mount.obsSite,
                               'unpark',
                               return_value=True):
            suc = app.startTrack()
            assert suc


def test_stopTrack_1():
    app.app.mount.mountUp = False
    suc = app.stopTrack()
    assert not suc


def test_stopTrack_2():
    app.app.mount.mountUp = True
    with mock.patch.object(app.app.mount.obsSite,
                           'stopTracking',
                           return_value=False):
        suc = app.stopTrack()
        assert not suc


def test_stopTrack_3():
    app.app.mount.mountUp = True
    with mock.patch.object(app.app.mount.obsSite,
                           'stopTracking',
                           return_value=True):
        suc = app.stopTrack()
        assert suc
