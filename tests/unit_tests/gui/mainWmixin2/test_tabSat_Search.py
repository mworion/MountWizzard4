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
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
from unittest import mock
import os

# external packages
from PySide6.QtCore import QThreadPool, QRect
from PySide6.QtWidgets import QTableWidgetItem
from skyfield.api import EarthSatellite
import numpy as np

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
import gui
from gui.utilities.toolsQtWidget import MWidget
from gui.widgets.main_ui import Ui_MainWindow
from gui.extWindows.uploadPopupW import UploadPopup
from gui.mainWmixin.tabSat_Search import SatSearch
from gui.mainWmixin.tabSat_Track import SatTrack
from logic.databaseProcessing.dataWriter import DataWriter


@pytest.fixture(autouse=True, scope='module')
def function(qapp):

    class Mixin(MWidget, SatSearch, SatTrack):
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


def test_sources(function):
    assert len(function.satelliteSourceURLs) == 14


def test_initConfig_1(function):
    suc = function.initConfig()
    assert suc


def test_storeConfig_1(function):
    suc = function.storeConfig()
    assert suc


def test_chooseSatellite_1(function):
    tle = ["NOAA 8",
           "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
           "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954"]
    sat = EarthSatellite(tle[1], tle[2],  name=tle[0])
    function.satellites = {'NOAA 8': sat}
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


def test_setSatTableEntry(function):
    function.ui.listSatelliteNames.setRowCount(0)
    function.ui.listSatelliteNames.insertRow(0)
    entry = QTableWidgetItem('test')
    suc = function.setSatTableEntry(0, 0, entry)
    assert suc


def test_updateTableEntries_1(function):
    param = [1, 2, 3, 4]
    suc = function.updateTableEntries(0, param)
    assert suc


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


def test_updateTableEntries_4(function):
    param = [1, 2, 3, 4]
    ts = function.app.mount.obsSite.ts.now()
    isUp = (False, [ts])
    suc = function.updateTableEntries(0, param, isUp, True, 5)
    assert suc


def test_updateTableEntries_5(function):
    param = [1, 2, 3, 4]
    ts = function.app.mount.obsSite.ts.now()
    isUp = (False, [ts])
    suc = function.updateTableEntries(0, param, isUp, False, 5, 4)
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
        with mock.patch.object(gui.mainWmixin.tabSat_Search,
                               'calcAppMag',
                               return_value=10):
            with mock.patch.object(gui.mainWmixin.tabSat_Search,
                                   'findSunlit',
                                   return_value=True):
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
    with mock.patch.object(gui.mainWmixin.tabSat_Search,
                           'findSunlit',
                           return_value=True):
        with mock.patch.object(gui.mainWmixin.tabSat_Search,
                               'calcAppMag',
                               return_value=10):
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
        with mock.patch.object(gui.mainWmixin.tabSat_Search,
                               'findRangeRate',
                               return_value=[1, 2, 3]):
            with mock.patch.object(gui.mainWmixin.tabSat_Search,
                                   'findSunlit',
                                   return_value=False):
                with mock.patch.object(QRect,
                                       'intersects',
                                       return_value=True):
                    suc = function.satCalcDynamicTable()
                    assert suc


def test_satCalcDynamicTable_8(function):
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
        with mock.patch.object(gui.mainWmixin.tabSat_Search,
                               'findRangeRate',
                               return_value=[1, 2, 3]):
            with mock.patch.object(gui.mainWmixin.tabSat_Search,
                                   'findSunlit',
                                   return_value=True):
                with mock.patch.object(gui.mainWmixin.tabSat_Search,
                                       'calcAppMag',
                                       return_value=10):
                    with mock.patch.object(QRect,
                                           'intersects',
                                           return_value=True):
                        suc = function.satCalcDynamicTable()
                        assert suc


def test_satCalcDynamicTable_9(function):
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
        with mock.patch.object(gui.mainWmixin.tabSat_Search,
                               'findRangeRate',
                               return_value=[np.nan, 2, 3]):
            with mock.patch.object(gui.mainWmixin.tabSat_Search,
                                   'findSunlit',
                                   return_value=True):
                with mock.patch.object(gui.mainWmixin.tabSat_Search,
                                       'calcAppMag',
                                       return_value=10):
                    with mock.patch.object(QRect,
                                           'intersects',
                                           return_value=True):
                        suc = function.satCalcDynamicTable()
                        assert suc


def test_positionCursorInSatTable_1(function):
    satTab = function.ui.listSatelliteNames
    satTab.setRowCount(0)
    satTab.setColumnCount(2)
    satTab.insertRow(0)
    entry = QTableWidgetItem('NOAA 8')
    satTab.setItem(0, 1, entry)

    suc = function.positionCursorInSatTable(satTab, 'test')
    assert not suc


def test_positionCursorInSatTable_2(function):
    satTab = function.ui.listSatelliteNames
    satTab.setRowCount(0)
    satTab.setColumnCount(2)
    satTab.insertRow(0)
    entry = QTableWidgetItem('NOAA 8')
    satTab.setItem(0, 1, entry)

    suc = function.positionCursorInSatTable(satTab, 'NOAA 8')
    assert suc


def test_filterSatelliteNamesList_1(function):
    function.ui.satFilterGroup.setEnabled(True)
    function.ui.satIsUp.setEnabled(True)
    function.ui.satIsUp.setChecked(True)
    function.ui.satIsSunlit.setEnabled(True)
    function.ui.satIsSunlit.setChecked(True)
    function.ui.satRemoveSO.setChecked(True)
    function.ui.listSatelliteNames.clear()
    function.ui.listSatelliteNames.setRowCount(0)
    function.ui.listSatelliteNames.setColumnCount(9)
    function.ui.listSatelliteNames.insertRow(0)
    entry = QTableWidgetItem('1234')
    function.ui.listSatelliteNames.setItem(0, 0, entry)
    entry = QTableWidgetItem('NOAA 8')
    function.ui.listSatelliteNames.setItem(0, 1, entry)
    entry = QTableWidgetItem('1')
    function.ui.listSatelliteNames.setItem(0, 8, entry)
    entry = QTableWidgetItem('1234')
    function.ui.listSatelliteNames.setItem(0, 7, entry)
    with mock.patch.object(function.ui.satTwilight,
                           'currentIndex',
                           return_value=1):
        suc = function.filterSatelliteNamesList()
        assert suc


def test_checkSatOk_1(function):
    tle = ["STARLINK-1914",
           "1 47180U 20088BL  21303.19708368  .16584525  12000-4  30219-2 0  9999",
           "2 47180  53.0402 223.8709 0008872 210.0671 150.2394 16.31518727 52528"]
    ts = function.app.mount.obsSite.ts
    tEnd = ts.tt_jd(2459523.2430)
    sat = EarthSatellite(tle[1], tle[2],  name=tle[0])
    suc = function.checkSatOk(sat, tEnd)
    assert not suc


def test_checkSatOk_2(function):
    tle = ["CALSPHERE 1",
           "1 00900U 64063C   21307.74429300  .00000461  00000-0  48370-3 0  9996",
           "2 00900  90.1716  36.8626 0025754 343.8320 164.5583 13.73613883839670"]
    ts = function.app.mount.obsSite.ts
    tEnd = ts.tt_jd(2459523.2430)
    sat = EarthSatellite(tle[1], tle[2],  name=tle[0])
    suc = function.checkSatOk(sat, tEnd)
    assert suc


def test_workerSatCalcTable_1(function):
    function.ui.listSatelliteNames.setRowCount(0)
    suc = function.workerSatCalcTable()
    assert suc
    assert function.satTableDynamicValid


def test_workerSatCalcTable_2(function):
    tle = ["NOAA 8",
           "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
           "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954"]
    sat = EarthSatellite(tle[1], tle[2],  name=tle[0])

    function.satellites = {'sat1': sat}

    function.ui.listSatelliteNames.setRowCount(0)
    function.ui.listSatelliteNames.setColumnCount(9)
    function.ui.listSatelliteNames.insertRow(0)
    entry = QTableWidgetItem('sat1')
    function.ui.listSatelliteNames.setItem(0, 1, entry)

    function.satTableBaseValid = False
    function.satTableDynamicValid = False
    function.ui.satUpTimeWindow.setValue(0)
    with mock.patch.object(gui.mainWmixin.tabSat_Search,
                           'findRangeRate'):
        with mock.patch.object(gui.mainWmixin.tabSat_Search,
                               'findSunlit',
                               return_value=False):
            with mock.patch.object(gui.mainWmixin.tabSat_Search,
                                   'findSatUp'):
                with mock.patch.object(function,
                                       'updateTableEntries'):
                    suc = function.workerSatCalcTable()
                    assert not suc


def test_workerSatCalcTable_3a(function):
    tle = ["STARLINK-1914",
           "1 47180U 20088BL  21303.19708368  .16584525  12000-4  30219-2 0  9999",
           "2 47180  53.0402 223.8709 0008872 210.0671 150.2394 16.31518727 52528"]

    function.satellites = {'sat1': EarthSatellite(tle[1], tle[2],  name=tle[0])}

    function.ui.listSatelliteNames.setRowCount(0)
    function.ui.listSatelliteNames.setColumnCount(9)
    function.ui.listSatelliteNames.insertRow(0)
    entry = QTableWidgetItem('sat1')
    function.ui.listSatelliteNames.setItem(0, 1, entry)

    function.satTableBaseValid = True
    function.satTableDynamicValid = False
    function.ui.satUpTimeWindow.setValue(2)
    with mock.patch.object(function,
                           'checkSatOk',
                           return_value=False):
        suc = function.workerSatCalcTable()
        assert suc
        assert function.satTableDynamicValid


def test_workerSatCalcTable_3b(function):
    tle = ["NOAA 8",
           "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
           "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954"]
    sat = EarthSatellite(tle[1], tle[2],  name=tle[0])

    function.satellites = {'sat1': sat}

    function.ui.listSatelliteNames.setRowCount(0)
    function.ui.listSatelliteNames.setColumnCount(9)
    function.ui.listSatelliteNames.insertRow(0)
    entry = QTableWidgetItem('sat1')
    function.ui.listSatelliteNames.setItem(0, 1, entry)

    function.satTableBaseValid = True
    function.satTableDynamicValid = False
    function.ui.satUpTimeWindow.setValue(2)
    with mock.patch.object(function,
                           'checkSatOk',
                           return_value=True):
        with mock.patch.object(gui.mainWmixin.tabSat_Search,
                               'findRangeRate',
                               return_value=(0, 0, 0, 0)):
            with mock.patch.object(gui.mainWmixin.tabSat_Search,
                                   'findSunlit',
                                   return_value=False):
                with mock.patch.object(gui.mainWmixin.tabSat_Search,
                                       'findSatUp'):
                    with mock.patch.object(gui.mainWmixin.tabSat_Search,
                                           'checkTwilight'):
                        with mock.patch.object(gui.mainWmixin.tabSat_Search,
                                               'calcAppMag',
                                               return_value=0):
                            with mock.patch.object(function,
                                                   'updateTableEntries'):
                                suc = function.workerSatCalcTable()
                                assert suc
                                assert function.satTableDynamicValid


def test_workerSatCalcTable_4(function):
    tle = ["NOAA 8",
           "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
           "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954"]
    sat = EarthSatellite(tle[1], tle[2],  name=tle[0])

    function.satellites = {'sat1': sat}

    function.ui.listSatelliteNames.setRowCount(0)
    function.ui.listSatelliteNames.setColumnCount(9)
    function.ui.listSatelliteNames.insertRow(0)
    entry = QTableWidgetItem('sat1')
    function.ui.listSatelliteNames.setItem(0, 1, entry)

    function.satTableBaseValid = True
    function.satTableDynamicValid = False
    function.ui.satUpTimeWindow.setValue(2)
    with mock.patch.object(function,
                           'checkSatOk',
                           return_value=True):
        with mock.patch.object(gui.mainWmixin.tabSat_Search,
                               'findRangeRate'):
            with mock.patch.object(gui.mainWmixin.tabSat_Search,
                                   'findSunlit',
                                   return_value=True):
                with mock.patch.object(gui.mainWmixin.tabSat_Search,
                                       'findSatUp'):
                    with mock.patch.object(gui.mainWmixin.tabSat_Search,
                                           'checkTwilight'):
                        with mock.patch.object(function,
                                               'updateTableEntries'):
                            with mock.patch.object(gui.mainWmixin.tabSat_Search,
                                                   'calcAppMag',
                                                   return_value=0):
                                suc = function.workerSatCalcTable()
                                assert suc
                                assert function.satTableDynamicValid


def test_workerSatCalcTable_5(function):
    tle = ["NOAA 8",
           "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
           "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954"]
    sat = EarthSatellite(tle[1], tle[2],  name=tle[0])

    function.satellites = {'sat1': sat}

    function.ui.listSatelliteNames.setRowCount(0)
    function.ui.listSatelliteNames.setColumnCount(9)
    function.ui.listSatelliteNames.insertRow(0)
    entry = QTableWidgetItem('sat1')
    function.ui.listSatelliteNames.setItem(0, 1, entry)

    function.satTableBaseValid = True
    function.satTableDynamicValid = False
    function.ui.satUpTimeWindow.setValue(2)
    with mock.patch.object(function,
                           'checkSatOk',
                           return_value=True):
        with mock.patch.object(gui.mainWmixin.tabSat_Search,
                               'findRangeRate',
                               return_value=[np.nan]):
            with mock.patch.object(gui.mainWmixin.tabSat_Search,
                                   'findSunlit',
                                   return_value=True):
                with mock.patch.object(gui.mainWmixin.tabSat_Search,
                                       'findSatUp'):
                    with mock.patch.object(function,
                                           'updateTableEntries'):
                        with mock.patch.object(gui.mainWmixin.tabSat_Search,
                                               'calcAppMag',
                                               return_value=0):
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


def test_updateSatTable_1(function):
    function.ui.satCyclicUpdates.setChecked(False)
    suc = function.updateSatTable()
    assert not suc


def test_updateSatTable_2(function):
    function.ui.satCyclicUpdates.setChecked(True)
    with mock.patch.object(function,
                           'satCalcTable'):
        suc = function.updateSatTable()
        assert suc


def test_prepareSatTable_1(function):
    suc = function.prepareSatTable()
    assert suc


def test_setupSatelliteNameList_1(function):
    tle = ["NOAA 8",
           "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
           "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954"]
    sat = EarthSatellite(tle[1], tle[2],  name=tle[0])

    function.satSourceValid = False
    function.satellites = {'sat1': sat}
    with mock.patch.object(function,
                           'prepareSatTable'):
        suc = function.setupSatelliteNameList()
        assert not suc


def test_setupSatelliteNameList_2(function):
    tle = ["NOAA 8",
           "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
           "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954"]
    sat = EarthSatellite(tle[1], tle[2],  name=tle[0])

    function.satSourceValid = True
    function.satellites = {'sat1': sat}

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
    function.satSourceValid = False
    function.ui.isOnline.setChecked(True)
    with mock.patch.object(function.app.mount.obsSite.loader,
                           'tle_file',
                           return_value={}):
        with mock.patch.object(os.path,
                               'isfile',
                               return_value=True):
            with mock.patch.object(function.app.mount.obsSite.loader,
                                   'days_old',
                                   return_value=0.5):
                suc = function.workerLoadDataFromSourceURLs()
                assert suc
                assert function.satSourceValid


def test_workerLoadDataFromSourceURLs_2(function):
    function.satSourceValid = False
    function.ui.isOnline.setChecked(False)
    with mock.patch.object(function.app.mount.obsSite.loader,
                           'tle_file',
                           return_value={}):
        with mock.patch.object(os.path,
                               'isfile',
                               return_value=True):
            with mock.patch.object(function.app.mount.obsSite.loader,
                                   'days_old',
                                   return_value=2):
                suc = function.workerLoadDataFromSourceURLs()
                assert not suc
                assert not function.satSourceValid


def test_loadDataFromSourceURLs_1(function):
    function.ui.satelliteSource.clear()
    suc = function.loadDataFromSourceURLs()
    assert not suc


def test_loadDataFromSourceURLs_2(function):
    function.ui.satelliteSource.clear()
    suc = function.loadDataFromSourceURLs()
    assert not suc


def test_loadDataFromSourceURLs_3(function):
    function.ui.satelliteSource.addItem('Active')
    function.ui.satelliteSource.setCurrentIndex(0)
    suc = function.loadDataFromSourceURLs()
    assert suc


def test_finishProgSatellites_1(function):
    class Test:
        returnValues = {'success': False}
    function.uploadPopup = Test()
    suc = function.finishProgSatellites()
    assert suc


def test_finishProgSatellites_2(function):
    class Test:
        returnValues = {'success': True}
    function.uploadPopup = Test()
    suc = function.finishProgSatellites()
    assert suc


def test_progSatellites_1(function):
    raw = 'test'
    with mock.patch.object(function.databaseProcessing,
                           'writeSatelliteTLE',
                           return_value=False):
        suc = function.progSatellites(raw)
        assert not suc


def test_progSatellites_2(function):
    raw = 'test'
    function.app.mount.host=('127.0.0.1', 3294)
    with mock.patch.object(function.databaseProcessing,
                           'writeSatelliteTLE',
                           return_value=True):
        with mock.patch.object(UploadPopup,
                               'show'):
            suc = function.progSatellites(raw)
            assert suc


def test_satelliteFilter_1(function):
    class SatNum:
        satnum = 1

    class Model:
        model = SatNum()

    raw = {'test': Model(), '0815': Model(), 0: Model()}
    function.ui.filterSatellite.setText('test')

    val = function.satelliteFilter(raw)
    assert 'test' in val


def test_satelliteGUI_1(function):
    with mock.patch.object(function,
                           'checkUpdaterOK',
                           return_value=False):
        suc = function.satelliteGUI()
        assert suc


def test_progSatellitesFiltered_1(function):
    with mock.patch.object(function,
                           'satelliteGUI',
                           return_value=False):
        suc = function.progSatellitesFiltered()
        assert not suc


def test_progSatellitesFiltered_2(function):
    with mock.patch.object(function,
                           'satelliteGUI',
                           return_value=True):
        with mock.patch.object(function,
                               'progSatellites'):
            with mock.patch.object(function,
                                   'satelliteFilter'):
                suc = function.progSatellitesFiltered()
                assert suc


def test_progSatellitesFull_1(function):
    with mock.patch.object(function,
                           'satelliteGUI',
                           return_value=False):
        suc = function.progSatellitesFull()
        assert not suc


def test_progSatellitesFull_2(function):
    with mock.patch.object(function,
                           'satelliteGUI',
                           return_value=True):
        with mock.patch.object(function,
                               'progSatellites'):
            suc = function.progSatellitesFull()
            assert suc
