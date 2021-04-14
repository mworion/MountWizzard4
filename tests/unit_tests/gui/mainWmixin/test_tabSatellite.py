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
import skyfield.timelib
from PyQt5.QtCore import QObject
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget
from skyfield.api import EarthSatellite
from skyfield.api import Angle, Topos
from sgp4.exporter import export_tle
import numpy as np

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


def test_storeConfig_1(function):
    suc = function.storeConfig()
    assert suc


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
    function.ui.mainTabWidget.setCurrentIndex(6)
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
                             'line2': tle[2].strip('\n'),}
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


def test_calcPassEvents_1(function):
    tle = ['NOAA 8',
           '1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998',
           '2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954']

    function.satellite = EarthSatellite(tle[1], tle[2],  name=tle[0])
    obsSite = function.app.mount.obsSite
    function.app.mount.setting.horizonLimitLow = None
    t, e = function.calcPassEvents(obsSite)
    assert type(t) == skyfield.timelib.Time
    assert type(e) == np.ndarray


def test_calcPassEvents_2(function):
    tle = ['NOAA 8',
           '1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998',
           '2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954']

    function.satellite = EarthSatellite(tle[1], tle[2],  name=tle[0])
    obsSite = function.app.mount.obsSite
    function.app.mount.setting.horizonLimitLow = 0
    t, e = function.calcPassEvents(obsSite)
    assert type(t) == skyfield.timelib.Time
    assert type(e) == np.ndarray


def test_extractFirstOrbits_1(function):
    ts = function.app.mount.obsSite.ts

    now = ts.tt_jd(2459215.4)
    t0 = ts.tt_jd(2459215.5)
    t1 = ts.tt_jd(2459215.6)
    t2 = ts.tt_jd(2459215.7)
    t3 = ts.tt_jd(2459215.8)
    t4 = ts.tt_jd(2459215.9)
    t5 = ts.tt_jd(2459216.0)
    t6 = ts.tt_jd(2459216.1)
    t7 = ts.tt_jd(2459216.2)
    t8 = ts.tt_jd(2459216.3)

    times = [t0, t1, t2, t3, t4, t5, t6, t7, t8]
    events = [0, 1, 2, 0, 1, 2, 0, 1, 2]

    function.extractFirstOrbits(now, times, events)
    assert len(function.satOrbits) == 3


def test_extractFirstOrbits_2(function):
    ts = function.app.mount.obsSite.ts

    now = ts.tt_jd(2459215.4)
    t0 = ts.tt_jd(2459215.5)
    t1 = ts.tt_jd(2459215.6)
    t2 = ts.tt_jd(2459215.7)
    t3 = ts.tt_jd(2459215.8)
    t4 = ts.tt_jd(2459215.9)
    t5 = ts.tt_jd(2459216.0)
    t6 = ts.tt_jd(2459216.1)
    t7 = ts.tt_jd(2459216.2)
    t8 = ts.tt_jd(2459216.3)

    times = [t0, t1, t2, t3, t4, t5, t6, t7, t8]
    events = [0, 1, 2, 1, 1, 2, 0, 1, 2]

    function.extractFirstOrbits(now, times, events)
    assert len(function.satOrbits) == 2


def test_extractFirstOrbits_3(function):
    ts = function.app.mount.obsSite.ts

    now = ts.tt_jd(2459216.1)
    t0 = ts.tt_jd(2459215.5)
    t1 = ts.tt_jd(2459215.6)
    t2 = ts.tt_jd(2459215.7)
    t3 = ts.tt_jd(2459215.8)
    t4 = ts.tt_jd(2459215.9)
    t5 = ts.tt_jd(2459216.0)
    t6 = ts.tt_jd(2459216.1)
    t7 = ts.tt_jd(2459216.2)
    t8 = ts.tt_jd(2459216.3)

    times = [t0, t1, t2, t3, t4, t5, t6, t7, t8]
    events = [0, 1, 2, 0, 1, 2, 0, 1, 2]

    function.extractFirstOrbits(now, times, events)
    print(function.satOrbits)
    assert len(function.satOrbits) == 1


def test_extractFirstOrbits_4(function):
    ts = function.app.mount.obsSite.ts

    now = ts.tt_jd(2459217.1)
    t0 = ts.tt_jd(2459215.5)
    t1 = ts.tt_jd(2459215.6)
    t2 = ts.tt_jd(2459215.7)
    t3 = ts.tt_jd(2459215.8)
    t4 = ts.tt_jd(2459215.9)
    t5 = ts.tt_jd(2459216.0)
    t6 = ts.tt_jd(2459216.1)
    t7 = ts.tt_jd(2459216.2)
    t8 = ts.tt_jd(2459216.3)

    times = [t0, t1, t2, t3, t4, t5, t6, t7, t8]
    events = [0, 1, 2, 0, 1, 2, 0, 1, 2]

    function.extractFirstOrbits(now, times, events)
    assert len(function.satOrbits) == 0


def test_calcSatelliteMeridianTransit(function):
    tle = ['NOAA 8',
           '1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998',
           '2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954']

    satellite = EarthSatellite(tle[1], tle[2],  name=tle[0])
    loc = Topos(latitude_degrees=48, longitude_degrees=11, elevation_m=500)
    function.calcSatelliteMeridianTransit(satellite, loc)


def test_addMeridianTransit_1(function):
    loc = Topos(latitude_degrees=48, longitude_degrees=11, elevation_m=500)
    tle = ['NOAA 8',
           '1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998',
           '2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954']
    ts = function.app.mount.obsSite.ts
    function.satellite = EarthSatellite(tle[1], tle[2],  name=tle[0])

    function.satOrbits = [{'rise': ts.tt_jd(2459215.5),
                           'settle': ts.tt_jd(2459215.7)},
                          {'rise': ts.tt_jd(2459216.5),
                           'settle': ts.tt_jd(2459216.7)}]
    function.addMeridianTransit(loc)


def test_showSatPasses_1(function):
    ts = function.app.mount.obsSite.ts
    function.satOrbits = [{'rise': ts.tt_jd(2459215.5),
                           'culminate': ts.tt_jd(2459215.6),
                           'settle': ts.tt_jd(2459215.7)},
                          {'rise': ts.tt_jd(2459216.5),
                           'settle': ts.tt_jd(2459216.7)}]
    with mock.patch.object(function,
                           'calcPassEvents',
                           return_value=(0, 0)):
        with mock.patch.object(function,
                               'extractFirstOrbits'):
            with mock.patch.object(function,
                                   'addMeridianTransit'):
                suc = function.showSatPasses()
                assert suc


def test_calcDuration_1(function):
    val = function.calcDuration(2000 / 1440, 3000 / 1440)
    assert val == 1000


def test_calcDuration_2(function):
    val = function.calcDuration(2000 / 1440, 5000 / 1440)
    assert val == 1440


def test_calcDuration_3(function):
    val = function.calcDuration(2000 / 1440, 1000 / 1440)
    assert val == 1


def test_calcSegments_1(function):
    ts = function.app.mount.obsSite.ts
    function.ui.satBeforeFlip.setChecked(True)
    function.ui.satAfterFlip.setChecked(False)
    function.satOrbits = [{'rise': ts.tt_jd(2459215.5),
                           'transit': ts.tt_jd(2459215.6),
                           'flip': ts.tt_jd(2459215.6),
                           'settle': ts.tt_jd(2459215.7)}]
    with mock.patch.object(function.app.mount.satellite,
                           'calcTLE'):
        with mock.patch.object(function,
                               'updateSatelliteTrackGui'):
            with mock.patch.object(function,
                                   'sendSatelliteData'):
                suc = function.calcSegments()
                assert suc


def test_calcSegments_2(function):
    ts = function.app.mount.obsSite.ts
    function.ui.satBeforeFlip.setChecked(False)
    function.ui.satAfterFlip.setChecked(True)
    function.satOrbits = [{'rise': ts.tt_jd(2459215.5),
                           'transit': ts.tt_jd(2459215.6),
                           'flip': ts.tt_jd(2459215.6),
                           'settle': ts.tt_jd(2459215.7)}]
    with mock.patch.object(function.app.mount.satellite,
                           'calcTLE'):
        with mock.patch.object(function,
                               'updateSatelliteTrackGui'):
            with mock.patch.object(function,
                                   'sendSatelliteData'):
                suc = function.calcSegments()
                assert suc
    function.ui.satBeforeFlip.setChecked(True)
    function.ui.satAfterFlip.setChecked(True)


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
        with mock.patch.object(function,
                               'showSatPasses'):
            with mock.patch.object(function,
                                   'sendSatelliteData'):
                with mock.patch.object(function,
                                       'programTLEDataToMount'):
                    with mock.patch.object(function,
                                           'calcOrbitFromTLEInMount'):
                        suc = function.extractSatelliteData(satName='NOAA 8')
                        assert suc


def test_extractSatelliteData_4(function):
    class Test1(QObject):
        update = pyqtSignal(object, object, object)
        show = pyqtSignal(object, object)

    class Test(QObject):
        signals = Test1()

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
        with mock.patch.object(function,
                               'showSatPasses'):
            with mock.patch.object(function,
                                   'sendSatelliteData'):
                with mock.patch.object(function,
                                       'programTLEDataToMount'):
                    with mock.patch.object(function,
                                           'calcOrbitFromTLEInMount'):
                        suc = function.extractSatelliteData(satName='NOAA 8')
                        assert suc


def test_extractSatelliteData_5(function):
    class Test1(QObject):
        update = pyqtSignal(object, object, object)
        show = pyqtSignal(object, object)

    class Test(QObject):
        signals = Test1()

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
        with mock.patch.object(function,
                               'showSatPasses'):
            with mock.patch.object(function,
                                   'sendSatelliteData'):
                with mock.patch.object(function,
                                       'programTLEDataToMount'):
                    with mock.patch.object(function,
                                           'calcOrbitFromTLEInMount'):
                        suc = function.extractSatelliteData(satName='NOAA 8')
                        assert suc


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
                           'showSatPasses'):
        with mock.patch.object(function,
                               'sendSatelliteData'):
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
        show = pyqtSignal(object, object, object)

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


def test_followMount_1(function):
    obs = function.app.mount.obsSite
    function.ui.domeAutoFollowSat.setChecked(False)
    obs.status = 1
    suc = function.followMount(obs)
    assert not suc


def test_followMount_2(function):
    obs = function.app.mount.obsSite
    obs.status = 10
    function.ui.domeAutoFollowSat.setChecked(False)
    suc = function.followMount(obs)
    assert not suc


def test_followMount_3(function):
    obs = function.app.mount.obsSite
    obs.status = 10
    function.ui.domeAutoFollowSat.setChecked(True)
    function.app.deviceStat['dome'] = False
    suc = function.followMount(obs)
    assert not suc


def test_followMount_4(function):
    obs = function.app.mount.obsSite
    obs.status = 10
    function.ui.domeAutoFollowSat.setChecked(True)
    function.app.deviceStat['dome'] = True
    function.lastAzimuth = 1
    obs.Az = Angle(degrees=1)
    obs.Alt = Angle(degrees=1)
    suc = function.followMount(obs)
    assert not suc


def test_followMount_5(function):
    obs = function.app.mount.obsSite
    obs.status = 10
    function.ui.domeAutoFollowSat.setChecked(True)
    function.app.deviceStat['dome'] = True
    function.lastAzimuth = 10
    obs.Az = Angle(degrees=1)
    obs.Alt = Angle(degrees=1)
    suc = function.followMount(obs)
    assert suc
