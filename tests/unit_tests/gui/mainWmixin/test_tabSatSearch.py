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
from PyQt5.QtCore import QThreadPool, QRect
from PyQt5.QtCore import pyqtSignal, QModelIndex
from PyQt5.QtWidgets import QTableWidgetItem
from skyfield.api import EarthSatellite, Angle, wgs84
from skyfield.units import Distance, Velocity, AngleRate, Rate
from sgp4.exporter import export_tle
import numpy as np

# local import
from tests.unit_tests.unitTestAddOns.baseTestSetupMixins import App
from gui.utilities.toolsQtWidget import MWidget
from gui.widgets.main_ui import Ui_MainWindow
from gui.mainWmixin.tabSatSearch import SatSearch
from gui.mainWmixin.tabSatTrack import  SatTrack
from logic.databaseProcessing.dataWriter import DataWriter


@pytest.fixture(autouse=True, scope='module')
def module(qapp):
    yield


@pytest.fixture(autouse=True, scope='function')
def function(module):

    class Mixin(MWidget, SatSearch, SatTrack):
        def __init__(self):
            super().__init__()
            self.app = App()
            self.databaseProcessing = DataWriter(self.app)
            self.threadPool = QThreadPool()
            self.ui = Ui_MainWindow()
            self.closing = False
            self.ui.setupUi(self)
            SatSearch.__init__(self)
            SatTrack.__init__(self)

    window = Mixin()
    yield window
    window.closing = True


def test_sources(function):
    assert len(function.satelliteSourceURLs) == 13


def test_initConfig_1(function):
    class Test:
        installPath = ''

    function.app.automation = Test()
    suc = function.initConfig()
    assert suc
    assert function.installPath == 'tests/workDir/data'


def test_initConfig_2(function):
    function.app.automation = None
    suc = function.initConfig()
    assert suc
    assert function.installPath == 'tests/workDir/data'


def test_initConfig_3(function):
    function.app.automation.installPath = 'test'
    suc = function.initConfig()
    assert suc
    assert function.installPath == 'test'


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


def test_chooseSatellite_1(function):
    satTab = function.ui.listSatelliteNames
    function.ui.switchToTrackingTab.setChecked(True)
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
    function.ui.switchToTrackingTab.setChecked(False)
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


def test_findSunlit(function):
    class SAT:
        class FRAME:
            def __init__(self, x):
                pass

            @staticmethod
            def is_sunlit(x):
                return True

        at = FRAME

    sat = SAT()
    eph = None
    tEv = None
    val = function.findSunlit(sat, eph, tEv)
    assert val


def test_findSatUp_1(function):
    class SAT:
        @staticmethod
        def find_events(x, y, z, altitude_degrees):
            return [], []

    sat = SAT()
    val = function.findSatUp(sat, 0, 0, 0, alt=0)
    assert not val[0]
    assert not len(val[1])


def test_findSatUp_2(function):
    class SAT:
        @staticmethod
        def find_events(x, y, z, altitude_degrees):
            return np.array([5, 7, 7]), np.array([1, 0, 0])

    sat = SAT()
    val = function.findSatUp(sat, 0, 0, 0, alt=0)
    assert val[0]
    assert val[1] == [5]


def test_setSatTableEntry(function):
    function.ui.listSatelliteNames.setRowCount(0)
    function.ui.listSatelliteNames.insertRow(0)
    entry = QTableWidgetItem('test')
    suc = function.setSatTableEntry(0, 0, entry)
    assert suc


def test_updateTableEntries_1(function):
    param = [1, 2, 3, 4]
    suc = function.updateTableEntries(0, param)
    assert not suc


def test_updateTableEntries_2(function):
    param = [1, 2, 3, 4]
    ts = function.app.mount.obsSite.ts.now()
    isUp = (True, [ts])
    suc = function.updateTableEntries(0, param, isUp)
    assert suc


def test_updateTableEntries_3(function):
    param = [1, 2, 3, 4]
    ts = function.app.mount.obsSite.ts.now()
    isUp = (False, [ts])
    suc = function.updateTableEntries(0, param, isUp)
    assert suc


def test_satCalcDynamicTable_1(function):
    function.satTableDynamicValid = False
    suc = function.satCalcDynamicTable()
    assert not suc


def test_satCalcDynamicTable_2(function):
    function.satTableDynamicValid = True
    function.ui.satTabWidget.setCurrentIndex(1)
    function.ui.mainTabWidget.setCurrentIndex(1)
    suc = function.satCalcDynamicTable()
    assert not suc


def test_satCalcDynamicTable_3(function):
    function.satTableDynamicValid = True
    function.ui.satTabWidget.setCurrentIndex(0)
    function.ui.mainTabWidget.setCurrentIndex(1)
    suc = function.satCalcDynamicTable()
    assert not suc


def test_satCalcDynamicTable_4(function):
    function.satTableDynamicValid = True
    function.ui.satTabWidget.setCurrentIndex(0)
    function.ui.mainTabWidget.setCurrentIndex(6)
    suc = function.satCalcDynamicTable()
    assert suc


def test_satCalcDynamicTable_5(function):
    function.satTableDynamicValid = True
    function.ui.satTabWidget.setCurrentIndex(0)
    function.ui.mainTabWidget.setCurrentIndex(6)
    function.ui.listSatelliteNames.setRowCount(0)
    function.ui.listSatelliteNames.insertRow(0)
    entry = QTableWidgetItem('test')
    function.ui.listSatelliteNames.setItem(0, 0, entry)
    with mock.patch.object(QRect,
                           'intersects',
                           return_value=False):
        suc = function.satCalcDynamicTable()
        assert suc


def test_satCalcDynamicTable_6(function):
    function.satTableDynamicValid = True
    function.ui.satTabWidget.setCurrentIndex(0)
    function.ui.mainTabWidget.setCurrentIndex(6)
    function.ui.listSatelliteNames.setRowCount(0)
    function.ui.listSatelliteNames.insertRow(0)
    entry = QTableWidgetItem('test')
    function.ui.listSatelliteNames.setItem(0, 0, entry)
    function.ui.listSatelliteNames.setRowHidden(0, True)
    with mock.patch.object(QRect,
                           'intersects',
                           return_value=True):
        suc = function.satCalcDynamicTable()
        assert suc


def test_satCalcDynamicTable_7(function):
    tle = ["NOAA 8",
           "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
           "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954"]
    sat = EarthSatellite(tle[1], tle[2],  name=tle[0])

    function.satTableDynamicValid = True
    function.ui.satTabWidget.setCurrentIndex(0)
    function.ui.mainTabWidget.setCurrentIndex(6)
    function.ui.listSatelliteNames.setRowCount(0)
    function.ui.listSatelliteNames.setColumnCount(2)
    function.ui.listSatelliteNames.insertRow(0)
    entry = QTableWidgetItem('NOAA 8')
    function.ui.listSatelliteNames.setItem(0, 1, entry)
    function.ui.listSatelliteNames.setRowHidden(0, False)
    function.satellites = {'NOAA 8': sat}
    with mock.patch.object(function,
                           'updateTableEntries'):
        with mock.patch.object(function,
                               'findRangeRate'):
            with mock.patch.object(QRect,
                                   'intersects',
                                   return_value=True):
                suc = function.satCalcDynamicTable()
                assert suc


def test_filterSatelliteNamesList_1(function):
    suc = function.filterSatelliteNamesList()
    assert suc


def test_filterSatelliteNamesList_2(function):
    function.ui.satIsUp.setEnabled(True)
    function.ui.satIsUp.setChecked(True)
    function.ui.satIsSunlit.setEnabled(True)
    function.ui.satIsSunlit.setChecked(True)
    function.ui.listSatelliteNames.setRowCount(0)
    function.ui.listSatelliteNames.setColumnCount(9)
    function.ui.listSatelliteNames.insertRow(0)
    entry = QTableWidgetItem('NOAA 8')
    function.ui.listSatelliteNames.setItem(0, 1, entry)
    entry = QTableWidgetItem('*')
    function.ui.listSatelliteNames.setItem(0, 8, entry)
    entry = QTableWidgetItem('1234')
    function.ui.listSatelliteNames.setItem(0, 7, entry)
    suc = function.filterSatelliteNamesList()
    assert suc


def test_workerSatCalcTable_1(function):
    function.ui.listSatelliteNames.setRowCount(0)
    suc = function.workerSatCalcTable()
    assert suc
    assert function.satTableDynamicValid


def test_workerSatCalcTable_2(function):
    class Test1:
        satnum = 12345

    class Test:
        model = Test1()

    function.satellites = {'sat1': Test()}

    function.ui.listSatelliteNames.setRowCount(0)
    function.ui.listSatelliteNames.setColumnCount(9)
    function.ui.listSatelliteNames.insertRow(0)
    entry = QTableWidgetItem('sat1')
    function.ui.listSatelliteNames.setItem(0, 1, entry)

    function.satTableBaseValid = False
    function.satTableDynamicValid = False
    function.ui.satUpTimeWindow.setValue(0)
    with mock.patch.object(function,
                           'findRangeRate'):
        with mock.patch.object(function,
                               'findSunlit'):
            with mock.patch.object(function,
                                   'findSatUp'):
                with mock.patch.object(function,
                                       'updateTableEntries'):
                    suc = function.workerSatCalcTable()
                    assert not suc


def test_workerSatCalcTable_3(function):
    class Test1:
        satnum = 12345

    class Test:
        model = Test1()

    function.satellites = {'sat1': Test()}

    function.ui.listSatelliteNames.setRowCount(0)
    function.ui.listSatelliteNames.setColumnCount(9)
    function.ui.listSatelliteNames.insertRow(0)
    entry = QTableWidgetItem('sat1')
    function.ui.listSatelliteNames.setItem(0, 1, entry)

    function.satTableBaseValid = True
    function.satTableDynamicValid = False
    function.ui.satUpTimeWindow.setValue(2)
    with mock.patch.object(function,
                           'findRangeRate'):
        with mock.patch.object(function,
                               'findSunlit'):
            with mock.patch.object(function,
                                   'findSatUp'):
                with mock.patch.object(function,
                                       'updateTableEntries'):
                    suc = function.workerSatCalcTable()
                    assert suc
                    assert function.satTableDynamicValid


def test_satCalcTable_1(function):
    function.satTableBaseValid = False
    suc = function.satCalcTable()
    assert not suc


def test_satCalcTable_2(function):
    function.satTableBaseValid = True
    function.satTableDynamicValid = True
    with mock.patch.object(function.threadPool,
                           'start'):
        suc = function.satCalcTable()
        assert suc
        assert not function.satTableDynamicValid


def test_prepareSatTable_1(function):
    suc = function.prepareSatTable()
    assert suc


def test_setupSatelliteNameList_1(function):
    class Test1:
        satnum = 12345

    class Test:
        model = Test1()

    function.satSourceValid = False
    function.satellites = {'sat1': Test()}
    with mock.patch.object(function,
                           'prepareSatTable'):
        suc = function.setupSatelliteNameList()
        assert not suc


def test_setupSatelliteNameList_2(function):
    class Test1:
        satnum = 12345

    class Test:
        model = Test1()

    function.satSourceValid = True
    function.satellites = {'sat1': Test()}

    with mock.patch.object(function,
                           'prepareSatTable'):
        with mock.patch.object(function,
                               'filterSatelliteNamesList'):
            with mock.patch.object(function,
                                   'satCalcTable'):
                suc = function.setupSatelliteNameList()
                assert suc
                assert function.satTableBaseValid


def test_workerLoadDataFromSourceURLs_1(function):
    suc = function.workerLoadDataFromSourceURLs()
    assert not suc


def test_workerLoadDataFromSourceURLs_2(function):
    source = 'test'
    with mock.patch.object(function.app.mount.obsSite.loader,
                           'tle_file',
                           return_value={}):
        with mock.patch.object(os.path,
                               'isfile',
                               return_value=False):
            suc = function.workerLoadDataFromSourceURLs(source=source, isOnline=False)
            assert not suc


def test_workerLoadDataFromSourceURLs_3(function):
    source = 'test'
    with mock.patch.object(function.app.mount.obsSite.loader,
                           'tle_file',
                           return_value={}):
        with mock.patch.object(os.path,
                               'isfile',
                               return_value=True):
            suc = function.workerLoadDataFromSourceURLs(source=source, isOnline=False)
            assert suc


def test_loadTLEDataFromSourceURLs_1(function):
    suc = function.loadDataFromSourceURLs()
    assert not suc


def test_loadTLEDataFromSourceURLs_2(function):
    function.ui.satelliteSource.addItem('Active')
    suc = function.loadDataFromSourceURLs()
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
