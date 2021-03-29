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
from unittest import mock
import os

# external packages
from PyQt5.QtCore import QObject
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget
from skyfield.api import EarthSatellite
from skyfield.api import Angle
from sgp4.exporter import export_tle

# local import
from tests.baseTestSetupMixins import App
from gui.utilities.toolsQtWidget import MWidget
from gui.widgets.main_ui import Ui_MainWindow
from gui.mainWmixin.tabSatellite import Satellite
from logic.databaseProcessing.dataWriter import DataWriter


@pytest.fixture(autouse=True, scope='module')
def module(qapp):
    yield


@pytest.fixture(autouse=True, scope='function')
def function(module):

    class Mixin(MWidget, Satellite):
        def __init__(self):
            super().__init__()
            self.app = App()
            self.databaseProcessing = DataWriter(self.app)
            self.threadPool = QThreadPool()
            self.ui = Ui_MainWindow()
            self.ui.setupUi(self)
            Satellite.__init__(self)

    window = Mixin()
    yield window


def test_sources(function):
    assert len(function.satelliteSourceURLs) == 13


def test_initConfig_1(function):
    class Test:
        installPath = ''

    function.app.automation = Test()
    suc = function.initConfig()
    assert suc
    assert function.installPath == 'tests/data'


def test_initConfig_2(function):
    function.app.automation = None
    suc = function.initConfig()
    assert suc
    assert function.installPath == 'tests/data'


def test_initConfig_3(function):
    function.app.automation.installPath = 'test'
    suc = function.initConfig()
    assert suc
    assert function.installPath == 'test'


def test_setupSatelliteSourceURLsDropDown(function):
    suc = function.setupSatelliteSourceURLsDropDown()
    assert suc
    assert len(function.ui.satelliteSource) == len(function.satelliteSourceURLs)


def test_filterSatelliteNamesList_1(function):
    suc = function.filterSatelliteNamesList()
    assert suc


def test_filterSatelliteNamesList_2(function):
    function.ui.listSatelliteNames.addItem('test')
    function.ui.filterSatellite.setText('abc')
    suc = function.filterSatelliteNamesList()
    assert suc


def test_setupSatelliteNameList_1(function):
    suc = function.setupSatelliteNameList()
    assert suc


def test_setupSatelliteNameList_2(function):
    class Test1:
        satnum = 12345

    class Test:
        model = Test1()

    function.satellites = {'sat1': Test()}
    suc = function.setupSatelliteNameList()
    assert suc


def test_setupSatelliteNameList_3(function):
    class Test1:
        satnum = 12345

    class Test:
        model = Test1()

    function.satellites = {0: Test()}
    suc = function.setupSatelliteNameList()
    assert suc


def test_loadSatelliteSourceWorker_1(function):
    suc = function.loadTLEDataFromSourceURLsWorker()
    assert not suc


def test_loadSatelliteSourceWorker_2(function):
    source = 'test'
    with mock.patch.object(function.app.mount.obsSite.loader,
                           'tle_file',
                           return_value={}):
        with mock.patch.object(os.path,
                               'isfile',
                               return_value=False):
            suc = function.loadTLEDataFromSourceURLsWorker(source=source, isOnline=False)
            assert not suc


def test_loadSatelliteSourceWorker_3(function):
    source = 'test'
    with mock.patch.object(function.app.mount.obsSite.loader,
                           'tle_file',
                           return_value={}):
        with mock.patch.object(os.path,
                               'isfile',
                               return_value=True):
            suc = function.loadTLEDataFromSourceURLsWorker(source=source, isOnline=False)
            assert suc


def test_loadTLEDataFromSourceURLs_1(function):
    suc = function.loadTLEDataFromSourceURLs()
    assert not suc


def test_loadTLEDataFromSourceURLs_2(function):
    function.ui.satelliteSource.addItem('Active')
    suc = function.loadTLEDataFromSourceURLs()
    assert suc


def test_updateOrbit_1(function):
    suc = function.updateOrbit()
    assert not suc


def test_updateOrbit_2(function):
    function.satellite = 'test'
    function.app.uiWindows['showSatelliteW'] = None
    suc = function.updateOrbit()
    assert not suc


def test_updateOrbit_3(function):
    function.satellite = 'test'
    function.ui.mainTabWidget.setCurrentIndex(1)
    function.app.uiWindows = {'showSatelliteW': {'test': 1}}
    suc = function.updateOrbit()
    assert not suc


def test_updateOrbit_4(function):
    class Test1(QObject):
        update = pyqtSignal(object, object, object)

    class Test(QObject):
        signals = Test1()

    tle = ["TIANGONG 1",
           "1 37820U 11053A   14314.79851609  .00064249  00000-0  44961-3 0  5637",
           "2 37820  42.7687 147.7173 0010686 283.6368 148.1694 15.73279710179072"]
    function.satellite = EarthSatellite(tle[1], tle[2],  name=tle[0])
    function.ui.mainTabWidget.setCurrentIndex(1)
    function.app.uiWindows = {'showSatelliteW': {'classObj': Test()}}
    suc = function.updateOrbit()
    assert suc


def test_updateOrbit_5(function):
    tle = ["TIANGONG 1",
           "1 37820U 11053A   14314.79851609  .00064249  00000-0  44961-3 0  5637",
           "2 37820  42.7687 147.7173 0010686 283.6368 148.1694 15.73279710179072"]
    function.satellite = EarthSatellite(tle[1], tle[2],  name=tle[0])
    function.ui.mainTabWidget.setCurrentIndex(5)
    function.app.uiWindows = {'showSatelliteW': {'test': 1}}
    suc = function.updateOrbit()
    assert not suc


def test_updateOrbit_6(function):
    class Test1(QObject):
        update = pyqtSignal(object, object, object)

    class Test(QObject):
        signals = Test1()

    tle = ["TIANGONG 1",
           "1 37820U 11053A   14314.79851609  .00064249  00000-0  44961-3 0  5637",
           "2 37820  42.7687 147.7173 0010686 283.6368 148.1694 15.73279710179072"]
    function.satellite = EarthSatellite(tle[1], tle[2],  name=tle[0])
    tabWidget = function.ui.mainTabWidget.findChild(QWidget, 'Satellite')
    tabIndex = function.ui.mainTabWidget.indexOf(tabWidget)
    function.ui.mainTabWidget.setCurrentIndex(tabIndex)
    function.app.uiWindows = {'showSatelliteW': {'classObj': None}}
    suc = function.updateOrbit()
    assert suc


def test_programTLEToMount_1(function):
    function.app.mount.mountUp = False
    suc = function.programTLEDataToMount()
    assert not suc


def test_programTLEToMount_2(function):
    class Test:
        name = 'TIANGONG 1'

    function.satellite = Test()
    function.app.mount.mountUp = True
    function.app.mount.satellite.tleParams.name = 'TIANGONG 1'
    suc = function.programTLEDataToMount()
    assert suc


def test_programTLEToMount_3(function):
    tle = ["TIANGONG 1",
           "1 37820U 11053A   14314.79851609  .00064249  00000-0  44961-3 0  5637",
           "2 37820  42.7687 147.7173 0010686 283.6368 148.1694 15.73279710179072"]
    function.satellite = EarthSatellite(tle[1], tle[2],  name=tle[0])
    tle = ["TIANGONG 1",
           "1 37820U 11053A   14314.79851609  .00064249  00000-0  44961-3 0  5637",
           "2 37820  42.7687 147.7173 0010686 283.6368 148.1694 15.73279710179072"]
    function.satellitesRawTLE = {tle[0].strip('\n'):
                            {'line0': tle[0].strip('\n'),
                             'line1': tle[1].strip('\n'),
                             'line2': tle[2].strip('\n'),
                             }
                            }

    function.app.mount.mountUp = True
    function.app.mount.satellite.tleParams.name = 'TIANGONG 2'
    with mock.patch.object(function.app.mount.satellite,
                           'setTLE',
                           return_value=False):
        suc = function.programTLEDataToMount()
        assert not suc


def test_programTLEToMount_4(function):
    tle = ["TIANGONG 1",
           "1 37820U 11053A   14314.79851609  .00064249  00000-0  44961-3 0  5637",
           "2 37820  42.7687 147.7173 0010686 283.6368 148.1694 15.73279710179072"]
    function.satellite = EarthSatellite(tle[1], tle[2],  name=tle[0])
    tle = ["TIANGONG 1",
           "1 37820U 11053A   14314.79851609  .00064249  00000-0  44961-3 0  5637",
           "2 37820  42.7687 147.7173 0010686 283.6368 148.1694 15.73279710179072"]
    function.satellitesRawTLE = {tle[0].strip('\n'):
                            {'line0': tle[0].strip('\n'),
                             'line1': tle[1].strip('\n'),
                             'line2': tle[2].strip('\n'),
                             }
                            }
    function.app.mount.mountUp = True
    function.app.mount.satellite.tleParams.name = 'TIANGONG 2'
    with mock.patch.object(function.app.mount.satellite,
                           'setTLE',
                           return_value=True):
        suc = function.programTLEDataToMount()
        assert suc


def test_calcTLEParams_1(function):
    with mock.patch.object(function.app.mount,
                           'calcTLE'):
        suc = function.calcOrbitFromTLEInMount()
        assert not suc


def test_calcTLEParams_2(function):
    function.satellite = 'test'
    with mock.patch.object(function.app.mount,
                           'calcTLE'):
        suc = function.calcOrbitFromTLEInMount()
        assert suc


def test_tle_export_1(function):
    tle = ['NOAA 8',
           '1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998',
           '2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954']

    satellite = EarthSatellite(tle[1], tle[2],  name=tle[0])
    line1, line2 = export_tle(satellite.model)

    assert tle[0] == satellite.name
    assert tle[1] == line1
    assert tle[2] == line2


def test_showRises_1(function):
    tle = ['NOAA 8',
           '1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998',
           '2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954']

    function.satellite = EarthSatellite(tle[1], tle[2], name=tle[0])
    function.app.mount.setting.horizonLimitLow = None

    with mock.patch.object(EarthSatellite,
                           'find_events',
                           return_value=([function.app.mount.obsSite.timeJD], [1])):
        val = function.showRises()
        assert isinstance(val, dict)


def test_showRises_2(function):
    t0 = function.app.mount.obsSite.timeJD
    t1 = function.app.mount.obsSite.ts.tt_jd(function.app.mount.obsSite.timeJD.tt + 0.1)
    t2 = function.app.mount.obsSite.ts.tt_jd(function.app.mount.obsSite.timeJD.tt + 0.2)

    tle = ["NOAA 8",
           "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
           "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954"]
    function.satellite = EarthSatellite(tle[1], tle[2],  name=tle[0])
    with mock.patch.object(EarthSatellite,
                           'find_events',
                           return_value=([t0, t1, t2],
                                         [0, 2, 1])):
        val = function.showRises()
        assert isinstance(val, dict)


def test_showRises_3(function):
    t0 = function.app.mount.obsSite.timeJD
    t1 = function.app.mount.obsSite.ts.tt_jd(function.app.mount.obsSite.timeJD.tt + 0.1)
    t2 = function.app.mount.obsSite.ts.tt_jd(function.app.mount.obsSite.timeJD.tt + 0.2)
    t3 = function.app.mount.obsSite.ts.tt_jd(function.app.mount.obsSite.timeJD.tt + 0.3)

    tle = ["NOAA 8",
           "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
           "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954"]
    function.satellite = EarthSatellite(tle[1], tle[2],  name=tle[0])
    with mock.patch.object(EarthSatellite,
                           'find_events',
                           return_value=([t0, t1, t2, t3],
                                         [2, 2, 2, 2])):
        val = function.showRises()
        assert isinstance(val, dict)


def test_extractSatelliteData_1(function):
    tle = ["NOAA 8",
           "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
           "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954"]
    sat = EarthSatellite(tle[1], tle[2],  name=tle[0])

    function.satellites = {'NOAA 8': sat,
                           'Test1': sat}

    suc = function.extractSatelliteData(satName='Tjan')
    assert not suc


def test_extractSatelliteData_2(function):
    function.ui.listSatelliteNames.clear()
    function.satellites = {'NOAA 8': '',
                           'Test1': ''}

    suc = function.extractSatelliteData(satName='NOAA 8')
    assert not suc


def test_extractSatelliteData_3(function):
    class Test1(QObject):
        update = pyqtSignal(object, object, object)
        show = pyqtSignal(object, object)

    class Test(QObject):
        signals = Test1()

    function.app.uiWindows = {'showSatelliteW': {'classObj': None}}
    function.ui.listSatelliteNames.clear()
    function.ui.listSatelliteNames.addItem('NOAA 8')
    function.ui.listSatelliteNames.addItem('Test1')

    tle = ["NOAA 8",
           "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
           "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954"]
    sat = EarthSatellite(tle[1], tle[2],  name=tle[0])

    function.satellites = {'NOAA 8': sat,
                           'Test1': sat}
    ts = function.app.mount.obsSite.ts
    with mock.patch.object(function.app.mount.obsSite.ts,
                           'now',
                           return_value=ts.tt_jd(2458925.404976551)):
        suc = function.extractSatelliteData(satName='NOAA 8')
        assert not suc


def test_extractSatelliteData_4(function):
    class Test1(QObject):
        update = pyqtSignal(object, object, object)
        show = pyqtSignal(object, object)

    class Test(QObject):
        signals = Test1()

    function.app.uiWindows = {'showSatelliteW': {'classObj': None}}
    function.ui.listSatelliteNames.clear()
    function.ui.listSatelliteNames.addItem('NOAA 8')
    function.ui.listSatelliteNames.addItem('Test1')

    tle = ["NOAA 8",
           "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
           "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954"]
    sat = EarthSatellite(tle[1], tle[2],  name=tle[0])

    function.satellites = {'NOAA 8': sat,
                           'Test1': sat}
    ts = function.app.mount.obsSite.ts
    with mock.patch.object(function.app.mount.obsSite.ts,
                           'now',
                           return_value=ts.tt_jd(2458930.404976551)):
        suc = function.extractSatelliteData(satName='NOAA 8')
        assert not suc


def test_extractSatelliteData_5(function):
    class Test1(QObject):
        update = pyqtSignal(object, object, object)
        show = pyqtSignal(object, object)

    class Test(QObject):
        signals = Test1()

    function.app.uiWindows = {'showSatelliteW': {'classObj': None}}
    function.ui.listSatelliteNames.clear()
    function.ui.listSatelliteNames.addItem('NOAA 8')
    function.ui.listSatelliteNames.addItem('Test1')

    tle = ["NOAA 8",
           "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
           "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954"]
    sat = EarthSatellite(tle[1], tle[2],  name=tle[0])

    function.satellites = {'NOAA 8': sat,
                           'Test1': sat}
    ts = function.app.mount.obsSite.ts
    with mock.patch.object(function.app.mount.obsSite.ts,
                           'now',
                           return_value=ts.tt_jd(2458950.404976551)):
        suc = function.extractSatelliteData(satName='NOAA 8')
        assert not suc


def test_extractSatelliteData_6(function):
    class Test1(QObject):
        update = pyqtSignal(object, object, object)
        show = pyqtSignal(object, object)

    class Test(QObject):
        signals = Test1()

    function.app.uiWindows = {'showSatelliteW': {'classObj': Test()}}
    function.ui.listSatelliteNames.clear()
    function.ui.listSatelliteNames.addItem('        NOAA 8')
    function.ui.listSatelliteNames.addItem('        Test1')

    tle = ["NOAA 8",
           "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
           "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954"]
    sat = EarthSatellite(tle[1], tle[2],  name=tle[0])

    function.satellites = {'NOAA 8': sat,
                           'Test1': sat}

    with mock.patch.object(function,
                           'showRises'):
        suc = function.extractSatelliteData(satName='NOAA 8')
        assert suc


def test_sendSatelliteData_1(function):
    function.satellite = None
    function.satOrbits = None
    suc = function.sendSatelliteData()
    assert not suc


def test_sendSatelliteData_2(function):
    function.app.uiWindows = {'showSatelliteW': {'classObj': None}}
    function.satellite = 1
    function.satOrbits = 1
    suc = function.sendSatelliteData()
    assert not suc


def test_sendSatelliteData_3(function):
    class Test1(QObject):
        update = pyqtSignal(object, object, object)
        show = pyqtSignal(object, object)

    class Test(QObject):
        signals = Test1()

    function.app.uiWindows = {'showSatelliteW': {'classObj': Test()}}
    function.satellite = 1
    function.satOrbits = 1
    suc = function.sendSatelliteData()
    assert suc


def test_signalExtractSatelliteData_1(function):
    function.ui.listSatelliteNames.addItem('Test 1234567')
    function.ui.listSatelliteNames.setCurrentRow(0)
    with mock.patch.object(function,
                           'extractSatelliteData',):
        suc = function.signalExtractSatelliteData()
        assert suc


def test_getSatelliteDataFromDatabase_1(function):
    suc = function.getSatelliteDataFromDatabase()
    assert not suc


def test_getSatelliteDataFromDatabase_2(function):
    class Test:
        name = 'test'

    suc = function.getSatelliteDataFromDatabase(Test())
    assert suc


def test_updateSatelliteTrackGui_1(function):
    suc = function.updateSatelliteTrackGui()
    assert not suc


def test_updateSatelliteTrackGui_2(function):
    class Test:
        jdStart = None
        jdEnd = None
        flip = False
        message = None
        altitude = None

    suc = function.updateSatelliteTrackGui(Test())
    assert suc


def test_updateSatelliteTrackGui_3(function):
    class Test:
        jdStart = 2458715.14771
        jdEnd = 2458715.15
        flip = True
        message = 'test'
        altitude = Angle(degrees=50)

    suc = function.updateSatelliteTrackGui(Test())
    assert suc


def test_startTrack_1(function):
    function.app.mount.mountUp = False
    suc = function.startTrack()
    assert not suc


def test_startTrack_2(function):
    function.app.mount.mountUp = True
    with mock.patch.object(function.app.mount.satellite,
                           'slewTLE',
                           return_value=(False, 'test')):
        suc = function.startTrack()
        assert not suc


def test_startTrack_3(function):
    function.app.mount.mountUp = True
    with mock.patch.object(function.app.mount.satellite,
                           'slewTLE',
                           return_value=(False, 'test')):
        suc = function.startTrack()
        assert not suc


def test_startTrack_4(function):
    function.app.mount.mountUp = True
    function.app.mount.obsSite.status = 5
    with mock.patch.object(function.app.mount.satellite,
                           'slewTLE',
                           return_value=(False, 'test')):
        suc = function.startTrack()
        assert not suc


def test_startTrack_5(function):
    function.app.mount.mountUp = True
    function.app.mount.obsSite.status = 5
    with mock.patch.object(function.app.mount.satellite,
                           'slewTLE',
                           return_value=(True, 'test')):
        suc = function.startTrack()
        assert suc


def test_startTrack_6(function):
    function.app.mount.mountUp = True
    function.app.mount.obsSite.status = 5
    with mock.patch.object(function.app.mount.satellite,
                           'slewTLE',
                           return_value=(True, 'test')):
        with mock.patch.object(function.app.mount.obsSite,
                               'unpark',
                               return_value=True):
            suc = function.startTrack()
            assert suc


def test_startTrack_7(function):
    function.app.mount.mountUp = True
    function.app.mount.obsSite.status = 5
    with mock.patch.object(function.app.mount.satellite,
                           'slewTLE',
                           return_value=(True, 'test')):
        with mock.patch.object(function.app.mount.obsSite,
                               'unpark',
                               return_value=False):
            suc = function.startTrack()
            assert suc


def test_stopTrack_1(function):
    function.app.mount.mountUp = False
    suc = function.stopTrack()
    assert not suc


def test_stopTrack_2(function):
    function.app.mount.mountUp = True
    with mock.patch.object(function.app.mount.obsSite,
                           'stopTracking',
                           return_value=False):
        suc = function.stopTrack()
        assert not suc


def test_stopTrack_3(function):
    function.app.mount.mountUp = True
    with mock.patch.object(function.app.mount.obsSite,
                           'stopTracking',
                           return_value=True):
        suc = function.stopTrack()
        assert suc


def test_progSatellitesFiltered_1(function):
    class Satnum:
        satnum = 1

    class Model:
        model = Satnum()

    function.ui.satelliteSource.clear()
    function.ui.satelliteSource.addItem('Comet')
    function.ui.satelliteSource.setCurrentIndex(0)
    function.ui.filterSatellite.setText('test')
    function.satellites = {'test': Model(), '0815': Model(), 0: Model()}

    with mock.patch.object(function,
                           'messageDialog',
                           return_value=False):
        suc = function.progSatellitesFiltered()
        assert not suc


def test_progSatellitesFiltered_2(function):
    class Satnum:
        satnum = 1

    class Model:
        model = Satnum()

    function.ui.satelliteSource.clear()
    function.ui.satelliteSource.addItem('Comet')
    function.ui.satelliteSource.setCurrentIndex(0)
    function.ui.filterSatellite.setText('test')
    function.satellites = {'test': Model(), '0815': Model(), 0: Model()}

    with mock.patch.object(function,
                           'messageDialog',
                           return_value=True):
        with mock.patch.object(function.databaseProcessing,
                               'writeSatelliteTLE',
                               return_value=False):
            suc = function.progSatellitesFiltered()
            assert not suc


def test_progSatellitesFiltered_3(function):
    class Satnum:
        satnum = 1

    class Model:
        model = Satnum()

    function.app.automation = None
    function.ui.satelliteSource.clear()
    function.ui.satelliteSource.addItem('Comet')
    function.ui.satelliteSource.setCurrentIndex(0)
    function.ui.filterSatellite.setText('test')
    function.satellites = {'test': Model(), '0815': Model(), 0: Model()}

    with mock.patch.object(function,
                           'messageDialog',
                           return_value=True):
        with mock.patch.object(function.databaseProcessing,
                               'writeSatelliteTLE',
                               return_value=True):
            suc = function.progSatellitesFiltered()
            assert not suc


def test_progSatellitesFiltered_3b(function):
    class Satnum:
        satnum = 1

    class Model:
        model = Satnum()

    function.app.automation.installPath = ''
    function.ui.satelliteSource.clear()
    function.ui.satelliteSource.addItem('Comet')
    function.ui.satelliteSource.setCurrentIndex(0)
    function.ui.filterSatellite.setText('test')
    function.satellites = {'test': Model(), '0815': Model(), 0: Model()}

    with mock.patch.object(function,
                           'messageDialog',
                           return_value=True):
        with mock.patch.object(function.databaseProcessing,
                               'writeSatelliteTLE',
                               return_value=True):
            suc = function.progSatellitesFiltered()
            assert not suc


def test_progSatellitesFiltered_4(function):
    class Satnum:
        satnum = 1

    class Model:
        model = Satnum()

    function.app.automation.installPath = 'test'
    function.ui.satelliteSource.clear()
    function.ui.satelliteSource.addItem('Comet')
    function.ui.satelliteSource.setCurrentIndex(0)
    function.ui.filterSatellite.setText('test')
    function.satellites = {'test': Model(), '0815': Model(), 0: Model()}

    with mock.patch.object(function,
                           'messageDialog',
                           return_value=True):
        with mock.patch.object(function.databaseProcessing,
                               'writeSatelliteTLE',
                               return_value=True):
            with mock.patch.object(function.app.automation,
                                   'uploadTLEData',
                                   return_value=False):
                suc = function.progSatellitesFiltered()
                assert not suc


def test_progSatellitesFiltered_5(function):
    class Satnum:
        satnum = 1

    class Model:
        model = Satnum()

    function.ui.satelliteSource.clear()
    function.ui.satelliteSource.addItem('Comet')
    function.ui.satelliteSource.setCurrentIndex(0)
    function.ui.filterSatellite.setText('test')
    function.satellites = {'test': Model(), '0815': Model(), 0: Model()}
    with mock.patch.object(function,
                           'messageDialog',
                           return_value=True):
        with mock.patch.object(function.databaseProcessing,
                               'writeSatelliteTLE',
                               return_value=True):
            with mock.patch.object(function.app.automation,
                                   'uploadTLEData',
                                   return_value=True):
                suc = function.progSatellitesFiltered()
                assert suc


def test_progSatellitesFull_1(function):
    class Satnum:
        satnum = 1

    class Model:
        model = Satnum()

    function.app.automation = None
    function.ui.satelliteSource.clear()
    function.ui.satelliteSource.addItem('Comet')
    function.ui.satelliteSource.setCurrentIndex(0)
    function.ui.filterSatellite.setText('test')
    function.satellites = {'test': Model(), '0815': Model(), 0: Model()}

    with mock.patch.object(function,
                           'messageDialog',
                           return_value=False):
        suc = function.progSatellitesFull()
        assert not suc


def test_progSatellitesFull_2(function):
    class Satnum:
        satnum = 1

    class Model:
        model = Satnum()

    function.ui.satelliteSource.clear()
    function.ui.satelliteSource.addItem('Comet')
    function.ui.satelliteSource.setCurrentIndex(0)
    function.ui.filterSatellite.setText('test')
    function.satellites = {'test': Model(), '0815': Model(), 0: Model()}

    with mock.patch.object(function,
                           'messageDialog',
                           return_value=True):
        with mock.patch.object(function.databaseProcessing,
                               'writeSatelliteTLE',
                               return_value=False):
            suc = function.progSatellitesFull()
            assert not suc


def test_progSatellitesFull_3(function):
    class Satnum:
        satnum = 1

    class Model:
        model = Satnum()

    function.app.automation = None
    function.ui.satelliteSource.clear()
    function.ui.satelliteSource.addItem('Comet')
    function.ui.satelliteSource.setCurrentIndex(0)
    function.ui.filterSatellite.setText('test')
    function.satellites = {'test': Model(), '0815': Model(), 0: Model()}

    with mock.patch.object(function,
                           'messageDialog',
                           return_value=True):
        with mock.patch.object(function.databaseProcessing,
                               'writeSatelliteTLE',
                               return_value=True):
            suc = function.progSatellitesFull()
            assert not suc


def test_progSatellitesFull_3b(function):
    class Satnum:
        satnum = 1

    class Model:
        model = Satnum()

    function.app.automation.installPath = ''
    function.ui.satelliteSource.clear()
    function.ui.satelliteSource.addItem('Comet')
    function.ui.satelliteSource.setCurrentIndex(0)
    function.ui.filterSatellite.setText('test')
    function.satellites = {'test': Model(), '0815': Model(), 0: Model()}

    with mock.patch.object(function,
                           'messageDialog',
                           return_value=True):
        with mock.patch.object(function.databaseProcessing,
                               'writeSatelliteTLE',
                               return_value=True):
            suc = function.progSatellitesFull()
            assert not suc


def test_progSatellitesFull_4(function):
    class Satnum:
        satnum = 1

    class Model:
        model = Satnum()

    function.app.automation.installPath = 'test'
    function.ui.satelliteSource.clear()
    function.ui.satelliteSource.addItem('Comet')
    function.ui.satelliteSource.setCurrentIndex(0)
    function.ui.filterSatellite.setText('test')
    function.satellites = {'test': Model(), '0815': Model(), 0: Model()}

    with mock.patch.object(function,
                           'messageDialog',
                           return_value=True):
        with mock.patch.object(function.databaseProcessing,
                               'writeSatelliteTLE',
                               return_value=True):
            with mock.patch.object(function.app.automation,
                                   'uploadTLEData',
                                   return_value=False):
                suc = function.progSatellitesFull()
                assert not suc


def test_progSatellitesFull_5(function):
    class Satnum:
        satnum = 1

    class Model:
        model = Satnum()

    function.ui.satelliteSource.clear()
    function.ui.satelliteSource.addItem('Comet')
    function.ui.satelliteSource.setCurrentIndex(0)
    function.ui.filterSatellite.setText('test')
    function.satellites = {'test': Model(), '0815': Model(), 0: Model()}

    with mock.patch.object(function,
                           'messageDialog',
                           return_value=True):
        with mock.patch.object(function.databaseProcessing,
                               'writeSatelliteTLE',
                               return_value=True):
            with mock.patch.object(function.app.automation,
                                   'uploadTLEData',
                                   return_value=True):
                suc = function.progSatellitesFull()
                assert suc
