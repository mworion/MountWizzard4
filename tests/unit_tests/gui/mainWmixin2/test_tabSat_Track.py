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
import skyfield.timelib
from PyQt5.QtCore import QObject
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QTableWidgetItem
from skyfield.api import EarthSatellite
from skyfield.api import Angle, wgs84
from sgp4.exporter import export_tle
import numpy as np

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.utilities.toolsQtWidget import MWidget
from gui.widgets.main_ui import Ui_MainWindow
from gui.mainWmixin.tabSat_Track import SatTrack
from gui.mainWmixin.tabSat_Search import SatSearch
from logic.databaseProcessing.dataWriter import DataWriter


@pytest.fixture(autouse=True, scope='module')
def function(qapp):

    class Mixin(MWidget, SatTrack, SatSearch):
        def __init__(self):
            super().__init__()
            self.app = App()
            self.msg = self.app.msg
            self.databaseProcessing = DataWriter(self.app)
            self.threadPool = QThreadPool()
            self.ui = Ui_MainWindow()
            self.ui.setupUi(self)
            SatSearch.__init__(self)
            SatTrack.__init__(self)

    window = Mixin()
    yield window
    window.closing = True
    window.threadPool.waitForDone(1000)

    
def test_initConfig_1(function):
    class Test:
        installPath = ''

    temp = function.app.automation
    function.app.automation = Test()
    suc = function.initConfig()
    assert suc
    assert function.installPath == 'tests/workDir/data'
    function.app.automation = temp


def test_initConfig_2(function):
    temp = function.app.automation
    function.app.automation = None
    suc = function.initConfig()
    assert suc
    assert function.installPath == 'tests/workDir/data'
    function.app.automation = temp


def test_initConfig_3(function):
    temp = function.app.automation.installPath
    function.app.automation.installPath = 'test'
    suc = function.initConfig()
    assert suc
    assert function.installPath == 'test'
    function.app.automation.installPath = temp


def test_storeConfig_1(function):
    suc = function.storeConfig()
    assert suc


def test_enableGuiFunctions_1(function):
    with mock.patch.object(function.app.mount.firmware,
                           'checkNewer',
                           return_value=None):
        suc = function.enableGuiFunctions()
        assert not suc


def test_enableGuiFunctions_2(function):
    with mock.patch.object(function.app.mount.firmware,
                           'checkNewer',
                           return_value=True):
        suc = function.enableGuiFunctions()
        assert suc


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


def test_extractOrbits_1(function):
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

    function.extractOrbits(now, times, events)
    assert len(function.satOrbits) == 3


def test_extractOrbits_2(function):
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

    function.extractOrbits(now, times, events)
    assert len(function.satOrbits) == 2


def test_extractOrbits_3(function):
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

    function.extractOrbits(now, times, events)
    assert len(function.satOrbits) == 1


def test_extractOrbits_4(function):
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

    function.extractOrbits(now, times, events)
    assert len(function.satOrbits) == 0


def test_extractOrbits_5(function):
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
    events = [0, 1, 2, 0, 1, 2, 0, 1, 1]

    function.extractOrbits(now, times, events)
    assert len(function.satOrbits) == 0


def test_extractOrbits_6(function):
    ts = function.app.mount.obsSite.ts

    now = ts.tt_jd(2459216.1)
    t0 = ts.tt_jd(2459215.5)

    times = np.array([t0])
    events = np.array([1])

    function.extractOrbits(now, times, events)
    assert len(function.satOrbits) == 1


def test_calcSatelliteMeridianTransit(function):
    tle = ['NOAA 8',
           '1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998',
           '2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954']

    satellite = EarthSatellite(tle[1], tle[2],  name=tle[0])
    loc = wgs84.latlon(latitude_degrees=48, longitude_degrees=11, elevation_m=500)
    function.calcSatelliteMeridianTransit(satellite, loc, 0)


def test_sortFlipEvents_0(function):
    ts = function.app.mount.obsSite.ts
    satOrbit = {'rise': ts.tt_jd(2459215.5),
                'settle': ts.tt_jd(2459215.7)}
    t0 = []
    t1 = [ts.tt_jd(2459215.5)]
    t2 = [ts.tt_jd(2459215.6)]
    suc = function.sortFlipEvents(satOrbit, t0, t1, t2)
    assert suc
    assert 'flip' not in satOrbit


def test_sortFlipEvents_1(function):
    ts = function.app.mount.obsSite.ts
    satOrbit = {'rise': ts.tt_jd(2459215.5),
                'settle': ts.tt_jd(2459215.7)}
    t0 = [ts.tt_jd(2459215.5)]
    t1 = [ts.tt_jd(2459215.5)]
    t2 = [ts.tt_jd(2459215.6)]
    suc = function.sortFlipEvents(satOrbit, t0, t1, t2)
    assert suc
    assert 'flip' in satOrbit


def test_sortFlipEvents_2(function):
    ts = function.app.mount.obsSite.ts
    satOrbit = {'rise': ts.tt_jd(2459215.5),
                'settle': ts.tt_jd(2459215.7)}
    t0 = [ts.tt_jd(2459215.5)]
    t1 = [ts.tt_jd(2459215.6)]
    t2 = [ts.tt_jd(2459215.5)]
    suc = function.sortFlipEvents(satOrbit, t0, t1, t2)
    assert suc


def test_sortFlipEvents_3(function):
    ts = function.app.mount.obsSite.ts
    satOrbit = {'rise': ts.tt_jd(2459215.5),
                'settle': ts.tt_jd(2459215.7)}
    t0 = [ts.tt_jd(2459215.5)]
    t1 = [ts.tt_jd(2459215.65)]
    t2 = []
    suc = function.sortFlipEvents(satOrbit, t0, t1, t2)
    assert suc
    assert 'flipLate' in satOrbit


def test_sortFlipEvents_4(function):
    ts = function.app.mount.obsSite.ts
    satOrbit = {'rise': ts.tt_jd(2459215.5),
                'settle': ts.tt_jd(2459215.7)}
    t0 = [ts.tt_jd(2459215.5)]
    t1 = [ts.tt_jd(2459215.55)]
    t2 = []
    suc = function.sortFlipEvents(satOrbit, t0, t1, t2)
    assert suc
    assert 'flipEarly' in satOrbit


def test_sortFlipEvents_5(function):
    ts = function.app.mount.obsSite.ts
    satOrbit = {'rise': ts.tt_jd(2459215.5),
                'settle': ts.tt_jd(2459215.7)}
    t0 = [ts.tt_jd(2459215.5)]
    t1 = []
    t2 = [ts.tt_jd(2459215.55)]
    suc = function.sortFlipEvents(satOrbit, t0, t1, t2)
    assert suc
    assert 'flipEarly' in satOrbit


def test_sortFlipEvents_6(function):
    ts = function.app.mount.obsSite.ts
    satOrbit = {'rise': ts.tt_jd(2459215.5),
                'settle': ts.tt_jd(2459215.7)}
    t0 = [ts.tt_jd(2459215.5)]
    t1 = []
    t2 = [ts.tt_jd(2459215.65)]
    suc = function.sortFlipEvents(satOrbit, t0, t1, t2)
    assert suc
    assert 'flipLate' in satOrbit


def test_addMeridianTransit_1(function):
    loc = wgs84.latlon(latitude_degrees=48, longitude_degrees=11, elevation_m=500)
    tle = ['NOAA 8',
           '1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998',
           '2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954']
    ts = function.app.mount.obsSite.ts
    function.satellite = EarthSatellite(tle[1], tle[2],  name=tle[0])

    function.satOrbits = [{'rise': ts.tt_jd(2459215.5),
                           'settle': ts.tt_jd(2459215.7)},
                          {'rise': ts.tt_jd(2459216.5),
                           'settle': ts.tt_jd(2459216.7)}]
    suc = function.addMeridianTransit(loc)
    assert suc


def test_addMeridianTransit_2(function):
    loc = wgs84.latlon(latitude_degrees=48, longitude_degrees=11, elevation_m=500)
    tle = ['NOAA 8',
           '1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998',
           '2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954']
    ts = function.app.mount.obsSite.ts
    function.app.mount.setting.meridianLimitTrack = None
    function.satellite = EarthSatellite(tle[1], tle[2],  name=tle[0])

    function.satOrbits = [{'rise': ts.tt_jd(2459215.5),
                           'settle': ts.tt_jd(2459215.7)},
                          {'rise': ts.tt_jd(2459216.5),
                           'settle': ts.tt_jd(2459216.7)}]
    suc = function.addMeridianTransit(loc)
    assert suc


def test_clearTrackingParameters(function):
    suc = function.clearTrackingParameters()
    assert suc


def test_updatePasses_1(function):
    function.app.mount.setting.meridianLimitTrack = 10
    function.lastMeridianLimit = 5
    with mock.patch.object(function,
                           'showSatPasses'):
        suc = function.updatePasses()
        assert suc
        assert function.lastMeridianLimit == 10


def test_updatePasses_2(function):
    function.app.mount.setting.meridianLimitTrack = None
    function.lastMeridianLimit = 5
    with mock.patch.object(function,
                           'showSatPasses'):
        suc = function.updatePasses()
        assert not suc
        assert function.lastMeridianLimit == 5


def test_sendSatelliteData_1(function):
    function.satellite = None
    function.satOrbits = None
    suc = function.signalSatelliteData()
    assert not suc


def test_sendSatelliteData_2(function):
    function.app.uiWindows = {'showSatelliteW': {'classObj': None}}
    function.satellite = 1
    function.satOrbits = 1
    suc = function.signalSatelliteData()
    assert not suc


def test_sendSatelliteData_3(function):
    class Test1(QObject):
        update = pyqtSignal(object, object, object)
        show = pyqtSignal(object, object, object, object, object)

    class Test(QObject):
        signals = Test1()

    function.app.uiWindows = {'showSatelliteW': {'classObj': Test()}}
    tle = ["NOAA 8",
           "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
           "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954"]
    function.satellite = EarthSatellite(tle[1], tle[2],  name=tle[0])
    function.satOrbits = 1
    suc = function.signalSatelliteData()
    assert suc


def test_showSatPasses_0(function):
    function.satellite = None
    suc = function.showSatPasses()
    assert not suc


def test_showSatPasses_1(function):
    ts = function.app.mount.obsSite.ts
    tle = ["NOAA 8",
           "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
           "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954"]
    function.satellite = EarthSatellite(tle[1], tle[2],  name=tle[0])
    function.satOrbits = [{'rise': ts.tt_jd(2459215.5),
                           'culminate': ts.tt_jd(2459215.6),
                           'settle': ts.tt_jd(2459215.7)},
                          {'rise': ts.tt_jd(2459216.5),
                           'settle': ts.tt_jd(2459216.7)}]
    with mock.patch.object(function,
                           'clearTrackingParameters'):
        with mock.patch.object(function,
                               'calcPassEvents',
                               return_value=(0, 0)):
            with mock.patch.object(function,
                                   'extractOrbits'):
                with mock.patch.object(function,
                                       'addMeridianTransit'):
                    with mock.patch.object(function,
                                           'progTrajectoryToMount'):
                        suc = function.showSatPasses()
                        assert suc


def test_showSatPasses_2(function):
    ts = function.app.mount.obsSite.ts
    tle = ["NOAA 8",
           "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
           "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954"]
    function.satellite = EarthSatellite(tle[1], tle[2],  name=tle[0])
    function.satOrbits = [{'rise': ts.tt_jd(2459215.5),
                           'culminate': ts.tt_jd(2459215.6),
                           'flip': ts.tt_jd(2459215.6),
                           'settle': ts.tt_jd(2459215.7)},
                          {'rise': ts.tt_jd(2459216.5),
                           'settle': ts.tt_jd(2459216.7)}]
    with mock.patch.object(function,
                           'clearTrackingParameters'):
        with mock.patch.object(function,
                               'calcPassEvents',
                               return_value=(0, 0)):
            with mock.patch.object(function,
                                   'extractOrbits'):
                with mock.patch.object(function,
                                       'addMeridianTransit'):
                    with mock.patch.object(function,
                                           'progTrajectoryToMount'):
                        suc = function.showSatPasses()
                        assert suc


def test_showSatPasses_3(function):
    ts = function.app.mount.obsSite.ts
    tle = ["NOAA 8",
           "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
           "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954"]
    function.satellite = EarthSatellite(tle[1], tle[2],  name=tle[0])
    function.satOrbits = [{'culminate': ts.tt_jd(2459215.6),
                           'flip': ts.tt_jd(2459215.6),},
                          {'rise': ts.tt_jd(2459216.5),
                           'settle': ts.tt_jd(2459216.7)}]
    with mock.patch.object(function,
                           'clearTrackingParameters'):
        with mock.patch.object(function,
                               'calcPassEvents',
                               return_value=(0, 0)):
            with mock.patch.object(function,
                                   'extractOrbits'):
                with mock.patch.object(function,
                                       'addMeridianTransit'):
                    with mock.patch.object(function,
                                           'progTrajectoryToMount'):
                        suc = function.showSatPasses()
                        assert suc


def test_extractSatelliteData_0(function):
    function.satellites = {'NOAA 8': 'sat',
                           'Test1': 'sat'}

    function.satTableBaseValid = False
    suc = function.extractSatelliteData(satName='Tjan')
    assert not suc


def test_extractSatelliteData_1(function):
    function.satellites = {'NOAA 8': 'sat',
                           'Test1': 'sat'}

    function.satTableBaseValid = True
    suc = function.extractSatelliteData(satName='Tjan')
    assert not suc


def test_extractSatelliteData_2(function):
    function.ui.listSatelliteNames.clear()
    function.satellites = {'Test0': '',
                           'Test1': ''}

    function.satTableBaseValid = True
    suc = function.extractSatelliteData(satName='NOAA 8')
    assert not suc


def test_extractSatelliteData_3(function):
    function.ui.listSatelliteNames.setRowCount(0)
    function.ui.listSatelliteNames.setColumnCount(2)
    function.ui.listSatelliteNames.insertRow(0)
    entry = QTableWidgetItem('NOAA 8')
    function.ui.listSatelliteNames.setItem(0, 1, entry)
    function.ui.listSatelliteNames.insertRow(0)
    entry = QTableWidgetItem('Test1')
    function.ui.listSatelliteNames.setItem(0, 1, entry)

    tle = ["NOAA 8",
           "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
           "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954"]
    sat = EarthSatellite(tle[1], tle[2],  name=tle[0])

    function.satellites = {'NOAA 8': sat,
                           'Test1': sat}
    function.satTableBaseValid = True
    ts = function.app.mount.obsSite.ts
    with mock.patch.object(function.app.mount.obsSite.ts,
                           'now',
                           return_value=ts.tt_jd(2458925.404976551)):
        with mock.patch.object(function,
                               'positionCursorInSatTable'):
            suc = function.extractSatelliteData(satName='NOAA 8')
            assert suc


def test_extractSatelliteData_4(function):
    function.ui.listSatelliteNames.setRowCount(0)
    function.ui.listSatelliteNames.setColumnCount(2)
    function.ui.listSatelliteNames.insertRow(0)
    entry = QTableWidgetItem('NOAA 8')
    function.ui.listSatelliteNames.setItem(0, 1, entry)
    function.ui.listSatelliteNames.insertRow(0)
    entry = QTableWidgetItem('Test1')
    function.ui.listSatelliteNames.setItem(0, 1, entry)

    tle = ["NOAA 8",
           "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
           "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954"]
    sat = EarthSatellite(tle[1], tle[2],  name=tle[0])

    function.satellites = {'NOAA 8': sat,
                           'Test1': sat}
    function.satTableBaseValid = True
    ts = function.app.mount.obsSite.ts
    with mock.patch.object(function.app.mount.obsSite.ts,
                           'now',
                           return_value=ts.tt_jd(2458930.404976551)):
        with mock.patch.object(function,
                               'positionCursorInSatTable'):
            suc = function.extractSatelliteData(satName='NOAA 8')
            assert suc


def test_extractSatelliteData_5(function):
    function.ui.listSatelliteNames.setRowCount(0)
    function.ui.listSatelliteNames.setColumnCount(2)
    function.ui.listSatelliteNames.insertRow(0)
    entry = QTableWidgetItem('NOAA 8')
    function.ui.listSatelliteNames.setItem(0, 1, entry)
    function.ui.listSatelliteNames.insertRow(0)
    entry = QTableWidgetItem('Test1')
    function.ui.listSatelliteNames.setItem(0, 1, entry)

    tle = ["NOAA 8",
           "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
           "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954"]
    sat = EarthSatellite(tle[1], tle[2],  name=tle[0])

    function.satellites = {'NOAA 8': sat,
                           'Test1': sat}
    function.satTableBaseValid = True
    ts = function.app.mount.obsSite.ts
    with mock.patch.object(function.app.mount.obsSite.ts,
                           'now',
                           return_value=ts.tt_jd(2458950.404976551)):
        with mock.patch.object(function,
                               'positionCursorInSatTable'):
            suc = function.extractSatelliteData(satName='NOAA 8')
            assert suc


def test_programDataToMount_1(function):
    suc = function.programDataToMount()
    assert not suc


def test_programDataToMount_2(function):
    suc = function.programDataToMount(satName='test')
    assert not suc


def test_programDataToMount_3(function):
    tle = ["TIANGONG 1",
           "1 37820U 11053A   14314.79851609  .00064249  00000-0  44961-3 0  5637",
           "2 37820  42.7687 147.7173 0010686 283.6368 148.1694 15.73279710179072"]
    function.satellite = EarthSatellite(tle[1], tle[2],  name=tle[0])
    function.satellites = {'TIANGONG 2': EarthSatellite(tle[1], tle[2],  name=tle[0])}
    function.app.mount.satellite.tleParams.name = 'TIANGONG 2'
    with mock.patch.object(function.app.mount.satellite,
                           'setTLE',
                           return_value=False):
        suc = function.programDataToMount(satName='TIANGONG 2')
        assert not suc


def test_programDataToMount_4(function):
    tle = ["TIANGONG 1",
           "1 37820U 11053A   14314.79851609  .00064249  00000-0  44961-3 0  5637",
           "2 37820  42.7687 147.7173 0010686 283.6368 148.1694 15.73279710179072"]
    function.satellite = EarthSatellite(tle[1], tle[2],  name=tle[0])
    function.satellites = {'TIANGONG 2': EarthSatellite(tle[1], tle[2],  name=tle[0])}
    function.app.mount.satellite.tleParams.name = 'TIANGONG 2'
    with mock.patch.object(function.app.mount.satellite,
                           'setTLE',
                           return_value=True):
        with mock.patch.object(function.app.mount,
                               'getTLE'):
            suc = function.programDataToMount(satName='TIANGONG 2')
            assert suc


def test_chooseSatellite_1(function):
    satTab = function.ui.listSatelliteNames
    function.app.deviceStat['mount'] = True
    with mock.patch.object(satTab,
                           'item'):
        with mock.patch.object(function,
                               'extractSatelliteData'):
            with mock.patch.object(function,
                                   'showSatPasses'):
                suc = function.chooseSatellite()
                assert suc


def test_chooseSatellite_2(function):
    satTab = function.ui.listSatelliteNames
    function.app.deviceStat['mount'] = False
    with mock.patch.object(satTab,
                           'item'):
        with mock.patch.object(function,
                               'extractSatelliteData'):
            with mock.patch.object(function,
                                   'showSatPasses'):
                suc = function.chooseSatellite()
                assert suc


def test_getSatelliteDataFromDatabase_1(function):
    class Name:
        name = ''
        jdStart = 1
        jdEnd = 1
        flip = False
        message = ''
        altitude = None
        azimuth = None

    function.app.mount.satellite.tleParams = Name()
    suc = function.getSatelliteDataFromDatabase()
    assert not suc


def test_getSatelliteDataFromDatabase_2(function):
    class Name:
        name = ''

    tleParams = Name()
    suc = function.getSatelliteDataFromDatabase(tleParams=tleParams)
    assert suc


def test_updateOrbit_1(function):
    function.satellite = None
    function.satSourceValid = False
    suc = function.updateOrbit()
    assert not suc


def test_updateOrbit_2(function):
    function.satellite = None
    function.satSourceValid = True
    suc = function.updateOrbit()
    assert not suc


def test_updateOrbit_3(function):
    function.satSourceValid = True
    function.satellite = 'test'
    function.app.uiWindows['showSatelliteW'] = {}
    suc = function.updateOrbit()
    assert not suc


def test_updateOrbit_4(function):
    class Test1(QObject):
        update = pyqtSignal(object, object)

    class Test(QObject):
        signals = Test1()

    function.satSourceValid = True
    function.satellite = 'test'
    function.app.uiWindows = {'showSatelliteW': {'classObj': Test()}}
    suc = function.updateOrbit()
    assert suc


def test_calcTrajectoryData_1(function):
    alt, az = function.calcTrajectoryData(100, 100)
    assert len(alt) == 0
    assert len(az) == 0


def test_calcTrajectoryData_2(function):
    tle = ['NOAA 8',
           '1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998',
           '2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954']

    function.satellite = EarthSatellite(tle[1], tle[2],  name=tle[0])
    start = 2459215.0
    alt, az = function.calcTrajectoryData(start, start + 2 / 86400)
    assert len(alt)
    assert len(az)


def test_filterHorizon_1(function):
    function.ui.avoidHorizon.setChecked(False)
    start = 100 / 86400
    end = 109 / 86400
    alt = [5, 6, 7, 45, 46, 47, 48, 7, 6, 5]
    az = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    function.app.data.horizonP = [(40, 40)]
    start, end, alt, az = function.filterHorizon(start, end, alt, az)
    assert alt == [5, 6, 7, 45, 46, 47, 48, 7, 6, 5]
    assert az == [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    assert start == 100  / 86400
    assert end == 109 / 86400


def test_filterHorizon_2(function):
    function.ui.avoidHorizon.setChecked(True)
    start = 100 / 86400
    end = 109 / 86400
    alt = [5, 6, 7, 45, 46, 47, 48, 7, 6, 5]
    az = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    function.app.data.horizonP = [(40, 40)]
    start, end, alt, az = function.filterHorizon(start, end, alt, az)
    assert np.array_equal(alt, [45, 46, 47, 48])
    assert np.array_equal(az, [40, 50, 60, 70])
    assert start == (100 + 3) / 86400
    assert end == (109 - 3) / 86400


def test_selectStartEnd_1(function):
    s, e = function.selectStartEnd()
    assert s == 0
    assert e == 0


def test_selectStartEnd_2(function):
    s, e = function.selectStartEnd()
    assert s == 0
    assert e == 0


def test_selectStartEnd_3(function):
    ts = function.app.mount.obsSite.ts
    function.satOrbits = [{'test': ts.tt_jd(2459215.5),
                           'test': ts.tt_jd(2459215.7)}]
    s, e = function.selectStartEnd()
    assert s == 0
    assert e == 0


def test_selectStartEnd_4(function):
    function.app.deviceStat['mount'] = True
    ts = function.app.mount.obsSite.ts
    function.satOrbits = [{'rise': ts.tt_jd(2459215.5),
                           'test': ts.tt_jd(2459215.6),
                           'test': ts.tt_jd(2459215.7)}]
    s, e = function.selectStartEnd()
    assert s == 0
    assert e == 0


def test_selectStartEnd_5(function):
    function.app.deviceStat['mount'] = True
    ts = function.app.mount.obsSite.ts
    function.satOrbits = [{'rise': ts.tt_jd(2459215.5),
                           'flip': ts.tt_jd(2459215.6),
                           'settle': ts.tt_jd(2459215.7)}]
    function.ui.satBeforeFlip.setChecked(False)
    function.ui.satAfterFlip.setChecked(False)
    s, e = function.selectStartEnd()
    assert s == 0
    assert e == 0


def test_selectStartEnd_6(function):
    function.app.deviceStat['mount'] = True
    ts = function.app.mount.obsSite.ts
    function.satOrbits = [{'rise': ts.tt_jd(2459215.5),
                           'flip': ts.tt_jd(2459215.6),
                           'settle': ts.tt_jd(2459215.7)}]
    function.ui.satBeforeFlip.setChecked(True)
    function.ui.satAfterFlip.setChecked(True)
    s, e = function.selectStartEnd()
    assert s == 2459215.5
    assert e == 2459215.7


def test_selectStartEnd_7(function):
    function.app.deviceStat['mount'] = True
    ts = function.app.mount.obsSite.ts
    function.satOrbits = [{'rise': ts.tt_jd(2459215.5),
                           'flipLate': ts.tt_jd(2459215.6),
                           'settle': ts.tt_jd(2459215.7)}]
    function.ui.satBeforeFlip.setChecked(True)
    function.ui.satAfterFlip.setChecked(False)
    s, e = function.selectStartEnd()
    assert s == 2459215.5
    assert e == 2459215.6


def test_selectStartEnd_8(function):
    function.app.deviceStat['mount'] = True
    ts = function.app.mount.obsSite.ts
    function.satOrbits = [{'rise': ts.tt_jd(2459215.5),
                           'flipEarly': ts.tt_jd(2459215.6),
                           'settle': ts.tt_jd(2459215.7)}]
    function.ui.satBeforeFlip.setChecked(False)
    function.ui.satAfterFlip.setChecked(True)
    s, e = function.selectStartEnd()
    assert s == 2459215.6
    assert e == 2459215.7


def test_progTrajectoryToMount_1(function):
    function.app.deviceStat['mount'] = True
    function.ui.useInternalSatCalc.setChecked(True)
    with mock.patch.object(function,
                           'selectStartEnd',
                           return_value=(0, 0)):
        suc = function.progTrajectoryToMount()
        assert not suc


def test_progTrajectoryToMount_2(function):
    function.app.deviceStat['mount'] = True
    function.ui.useInternalSatCalc.setChecked(True)
    with mock.patch.object(function,
                           'selectStartEnd',
                           return_value=(1, 1)):
        with mock.patch.object(function,
                               'calcTrajectoryData',
                               return_value=(0, 0)):
            with mock.patch.object(function,
                                   'filterHorizon',
                                   return_value=(0, 0, 0, 0)):
                with mock.patch.object(function,
                                       'signalSatelliteData'):
                    suc = function.progTrajectoryToMount()
                    assert suc


def test_progTrajectoryToMount_3(function):
    function.app.deviceStat['mount'] = False
    function.ui.useInternalSatCalc.setChecked(False)
    with mock.patch.object(function,
                           'selectStartEnd',
                           return_value=(1, 1)):
        with mock.patch.object(function.app.mount,
                               'calcTLE'):
            with mock.patch.object(function,
                                   'signalSatelliteData'):
                suc = function.progTrajectoryToMount()
                assert suc


def test_progTrajectoryToMount_4(function):
    function.app.deviceStat['mount'] = True
    function.ui.useInternalSatCalc.setChecked(False)
    with mock.patch.object(function,
                           'selectStartEnd',
                           return_value=(1, 1)):
        with mock.patch.object(function.app.mount,
                               'calcTLE'):
            with mock.patch.object(function,
                                   'signalSatelliteData'):
                suc = function.progTrajectoryToMount()
                assert suc


def test_startProg_1(function):
    with mock.patch.object(function,
                           'clearTrackingParameters'):
        with mock.patch.object(function,
                               'selectStartEnd',
                               return_value=(1, 2)):
            with mock.patch.object(function,
                                   'calcTrajectoryData',
                                   return_value=(0, 0)):
                with mock.patch.object(function,
                                       'filterHorizon',
                                       return_value=(0, 0, 0, 0)):
                    with mock.patch.object(function.app.mount,
                                           'progTrajectory'):
                        suc = function.startProg()
                        assert suc


def test_startProg_2(function):
    with mock.patch.object(function,
                           'clearTrackingParameters'):
        with mock.patch.object(function,
                               'selectStartEnd',
                               return_value=(0, 0)):
            suc = function.startProg()
            assert not suc


def test_trajectoryProgress_1(function):
    suc = function.trajectoryProgress(100)
    assert suc


def test_updateSatelliteTrackGui_1(function):
    suc = function.updateSatelliteTrackGui()
    assert not suc


def test_updateSatelliteTrackGui_2(function):
    ts = function.app.mount.obsSite.ts

    class Test:
        jdStart = ts.tt_jd(2459215.5)
        jdEnd = ts.tt_jd(2459215.6)
        flip = False
        message = 'e'
        altitude = 1

    function.satOrbits = [{'rise': ts.tt_jd(2459215.5),
                           'flip': ts.tt_jd(2459215.6),
                           'culminate': ts.tt_jd(2459215.6),
                           'settle': ts.tt_jd(2459215.7)}]

    suc = function.updateSatelliteTrackGui(Test())
    assert suc


def test_updateSatelliteTrackGui_3(function):
    ts = function.app.mount.obsSite.ts

    class Test:
        jdStart = None
        jdEnd = None
        flip = True
        message = 'e'
        altitude = 1

    function.satOrbits = [{'rise': ts.tt_jd(2459215.5),
                           'flip': ts.tt_jd(2459215.6),
                           'culminate': ts.tt_jd(2459215.6),
                           'settle': ts.tt_jd(2459215.7)}]

    suc = function.updateSatelliteTrackGui(Test())
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


def test_startTrack_1(function):
    function.app.deviceStat['mount'] = False
    suc = function.startTrack()
    assert not suc


def test_startTrack_2(function):
    function.app.deviceStat['mount'] = True
    with mock.patch.object(function.app.mount.satellite,
                           'slewTLE',
                           return_value=(False, 'test')):
        suc = function.startTrack()
        assert not suc


def test_startTrack_3(function):
    function.app.deviceStat['mount'] = True
    with mock.patch.object(function.app.mount.satellite,
                           'slewTLE',
                           return_value=(False, 'test')):
        suc = function.startTrack()
        assert not suc


def test_startTrack_4(function):
    function.app.deviceStat['mount'] = True
    function.app.mount.obsSite.status = 5
    with mock.patch.object(function.app.mount.satellite,
                           'slewTLE',
                           return_value=(False, 'test')):
        suc = function.startTrack()
        assert not suc


def test_startTrack_5(function):
    function.app.deviceStat['mount'] = True
    function.app.mount.obsSite.status = 5
    with mock.patch.object(function.app.mount.satellite,
                           'slewTLE',
                           return_value=(True, 'test')):
        suc = function.startTrack()
        assert suc


def test_startTrack_6(function):
    function.app.deviceStat['mount'] = True
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
    function.app.deviceStat['mount'] = True
    function.app.mount.obsSite.status = 5
    with mock.patch.object(function.app.mount.satellite,
                           'slewTLE',
                           return_value=(True, 'test')):
        with mock.patch.object(function.app.mount.obsSite,
                               'unpark',
                               return_value=False):
            with mock.patch.object(function.app.mount.satellite,
                                   'clearTrackingOffsets',
                                   return_value=True):
                suc = function.startTrack()
                assert suc


def test_stopTrack_1(function):
    function.app.deviceStat['mount'] = False
    suc = function.stopTrack()
    assert not suc


def test_stopTrack_2(function):
    function.app.deviceStat['mount'] = True
    with mock.patch.object(function.app.mount.obsSite,
                           'startTracking',
                           return_value=False):
        suc = function.stopTrack()
        assert not suc


def test_stopTrack_3(function):
    function.app.deviceStat['mount'] = True
    with mock.patch.object(function.app.mount.obsSite,
                           'startTracking',
                           return_value=True):
        suc = function.stopTrack()
        assert suc


def test_toggleTrackingOffset_1(function):
    class OBS:
        status = 10

    with mock.patch.object(function.app.mount.firmware,
                           'checkNewer',
                           return_value=True):
        suc = function.toggleTrackingOffset(obs=OBS())
        assert suc


def test_toggleTrackingOffset_2(function):
    class OBS:
        status = 1

    with mock.patch.object(function.app.mount.firmware,
                           'checkNewer',
                           return_value=True):
        suc = function.toggleTrackingOffset(obs=OBS())
        assert suc


def test_toggleTrackingOffset_3(function):
    class OBS:
        status = 1

    with mock.patch.object(function.app.mount.firmware,
                           'checkNewer',
                           return_value=False):
        suc = function.toggleTrackingOffset(obs=OBS())
        assert not suc


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
    obs.Az = Angle(degrees=1)
    obs.Alt = Angle(degrees=1)
    suc = function.followMount(obs)
    assert suc


def test_setTrackingOffsets_1(function):
    with mock.patch.object(function.app.mount.satellite,
                           'setTrackingOffsets',
                           return_value=True):
        suc = function.setTrackingOffsets()
        assert suc


def test_setTrackingOffsets_2(function):
    with mock.patch.object(function.app.mount.satellite,
                           'setTrackingOffsets',
                           return_value=False):
        suc = function.setTrackingOffsets()
        assert not suc
