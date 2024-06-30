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
import astropy
from unittest import mock

# external packages
from PySide6.QtCore import QRect
from PySide6.QtWidgets import QTableWidgetItem, QWidget
from skyfield.api import EarthSatellite
import numpy as np

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
import gui
from gui.widgets.main_ui import Ui_MainWindow
from gui.mainWaddon.tabSat_Search import SatSearch


@pytest.fixture(autouse=True, scope='module')
def function(qapp):
    class Test:
        objects = {}

    mainW = QWidget()
    mainW.app = App()
    mainW.satellites = Test()
    mainW.ui = Ui_MainWindow()
    mainW.ui.setupUi(mainW)
    window = SatSearch(mainW)
    yield window
    mainW.app.threadPool.waitForDone(5000)


def test_initConfig_1(function):
    function.initConfig()


def test_initConfigDelayedSat_1(function):
    with mock.patch.object(function.ui.satSourceList,
                           'setCurrentIndex'):
        function.initConfigDelayedSat()


def test_storeConfig_1(function):
    function.storeConfig()


def test_prepareSatTable_1(function):
    function.prepareSatTable()


def test_processSatelliteSource(function):
    tle = ["NOAA 8",
           "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
           "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954"]
    sat = EarthSatellite(tle[1], tle[2],  name=tle[0])

    with mock.patch.object(function.app.mount.obsSite.loader,
                           'tle_file',
                           return_value=[sat]):
        function.processSatelliteSource()


def test_filterListSats_1(function):
    function.ui.satFilterGroup.setEnabled(True)
    function.ui.satIsUp.setEnabled(True)
    function.ui.satIsUp.setChecked(True)
    function.ui.satIsSunlit.setEnabled(True)
    function.ui.satIsSunlit.setChecked(True)
    function.ui.satRemoveSO.setChecked(True)
    function.ui.listSats.clear()
    function.ui.listSats.setRowCount(0)
    function.ui.listSats.setColumnCount(9)
    function.ui.listSats.insertRow(0)
    entry = QTableWidgetItem('1234')
    function.ui.listSats.setItem(0, 0, entry)
    entry = QTableWidgetItem('NOAA 8')
    function.ui.listSats.setItem(0, 1, entry)
    entry = QTableWidgetItem('1')
    function.ui.listSats.setItem(0, 8, entry)
    entry = QTableWidgetItem('1234')
    function.ui.listSats.setItem(0, 7, entry)
    with mock.patch.object(function.ui.satTwilight,
                           'currentIndex',
                           return_value=1):
        function.filterListSats()


def test_setListSatsEntry(function):
    function.ui.listSats.setRowCount(0)
    function.ui.listSats.insertRow(0)
    entry = QTableWidgetItem('test')
    function.setListSatsEntry(0, 0, entry)


def test_updateListSats_1(function):
    param = [1, 2, 3, 4]
    function.updateListSats(0, param)


def test_updateListSats_2(function):
    param = [1, 2, 3, 4]
    ts = function.app.mount.obsSite.ts.now()
    isUp = (True, [ts])
    function.updateListSats(0, param, isUp)


def test_updateListSats_3(function):
    param = [1, 2, 3, 4]
    ts = function.app.mount.obsSite.ts.now()
    isUp = (False, [ts])
    function.updateListSats(0, param, isUp)


def test_updateListSats_4(function):
    param = [1, 2, 3, 4]
    ts = function.app.mount.obsSite.ts.now()
    isUp = (False, [ts])
    function.updateListSats(0, param, isUp, True, 5)


def test_updateListSats_5(function):
    param = [1, 2, 3, 4]
    ts = function.app.mount.obsSite.ts.now()
    isUp = (False, [ts])
    function.updateListSats(0, param, isUp, False, 5, 4)


def test_calcSatListDynamic_1(function):
    function.ui.satTabWidget.setCurrentIndex(1)
    function.ui.mainTabWidget.setCurrentIndex(1)
    function.calcSatListDynamic()


def test_calcSatListDynamic_2(function):
    function.ui.satTabWidget.setCurrentIndex(0)
    function.ui.mainTabWidget.setCurrentIndex(1)
    function.calcSatListDynamic()


def test_calcSatListDynamic_3(function):
    function.ui.satTabWidget.setCurrentIndex(0)
    function.ui.mainTabWidget.setCurrentIndex(5)
    function.calcSatListDynamic()


def test_calcSatListDynamic_4(function):
    function.satellites.dataValid = True
    tle = ["NOAA 8",
           "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
           "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954"]
    sat = EarthSatellite(tle[1], tle[2],  name=tle[0])
    function.satellites.objects = {'NOAA 8': sat}

    function.ui.satTabWidget.setCurrentIndex(0)
    function.ui.mainTabWidget.setCurrentIndex(5)
    function.ui.listSats.setRowCount(0)
    function.ui.listSats.insertRow(0)
    entry = QTableWidgetItem('test')
    function.ui.listSats.setItem(0, 0, entry)
    with mock.patch.object(QRect,
                           'intersects',
                           return_value=False):
        with mock.patch.object(gui.mainWaddon.tabSat_Search,
                               'calcAppMag',
                               return_value=10):
            with mock.patch.object(gui.mainWaddon.tabSat_Search,
                                   'findSunlit',
                                   return_value=True):
                function.calcSatListDynamic()


def test_calcSatListDynamic_5(function):
    function.satellites.dataValid = True
    tle = ["NOAA 8",
           "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
           "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954"]
    sat = EarthSatellite(tle[1], tle[2],  name=tle[0])
    function.satellites.objects = {'NOAA 8': sat}

    function.ui.satTabWidget.setCurrentIndex(0)
    function.ui.mainTabWidget.setCurrentIndex(5)
    function.ui.listSats.setRowCount(0)
    function.ui.listSats.insertRow(0)
    entry = QTableWidgetItem('test')
    function.ui.listSats.setItem(0, 0, entry)
    function.ui.listSats.setRowHidden(0, True)
    with mock.patch.object(gui.mainWaddon.tabSat_Search,
                           'findSunlit',
                           return_value=True):
        with mock.patch.object(gui.mainWaddon.tabSat_Search,
                               'calcAppMag',
                               return_value=10):
            with mock.patch.object(QRect,
                                   'intersects',
                                   return_value=True):
                function.calcSatListDynamic()


def test_calcSatListDynamic_6(function):
    function.satellites.dataValid = True
    tle = ["NOAA 8",
           "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
           "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954"]
    sat = EarthSatellite(tle[1], tle[2],  name=tle[0])

    function.ui.satTabWidget.setCurrentIndex(0)
    function.ui.mainTabWidget.setCurrentIndex(5)
    function.ui.listSats.setRowCount(0)
    function.ui.listSats.setColumnCount(2)
    function.ui.listSats.insertRow(0)
    entry = QTableWidgetItem('NOAA 8')
    function.ui.listSats.setItem(0, 1, entry)
    function.ui.listSats.setRowHidden(0, False)
    function.satellites.objects = {'NOAA 8': sat}
    with mock.patch.object(function,
                           'updateListSats'):
        with mock.patch.object(gui.mainWaddon.tabSat_Search,
                               'findRangeRate',
                               return_value=[1, 2, 3]):
            with mock.patch.object(gui.mainWaddon.tabSat_Search,
                                   'findSunlit',
                                   return_value=False):
                with mock.patch.object(QRect,
                                       'intersects',
                                       return_value=True):
                    function.calcSatListDynamic()


def test_calcSatListDynamic_7(function):
    function.satellites.dataValid = True
    tle = ["NOAA 8",
           "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
           "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954"]
    sat = EarthSatellite(tle[1], tle[2],  name=tle[0])

    function.ui.satTabWidget.setCurrentIndex(0)
    function.ui.mainTabWidget.setCurrentIndex(5)
    function.ui.listSats.setRowCount(0)
    function.ui.listSats.setColumnCount(2)
    function.ui.listSats.insertRow(0)
    entry = QTableWidgetItem('NOAA 8')
    function.ui.listSats.setItem(0, 1, entry)
    function.ui.listSats.setRowHidden(0, False)
    function.satellites.objects = {'NOAA 8': sat}
    with mock.patch.object(function,
                           'updateListSats'):
        with mock.patch.object(gui.mainWaddon.tabSat_Search,
                               'findRangeRate',
                               return_value=[1, 2, 3]):
            with mock.patch.object(gui.mainWaddon.tabSat_Search,
                                   'findSunlit',
                                   return_value=True):
                with mock.patch.object(gui.mainWaddon.tabSat_Search,
                                       'calcAppMag',
                                       return_value=10):
                    with mock.patch.object(QRect,
                                           'intersects',
                                           return_value=True):
                        function.calcSatListDynamic()


def test_calcSatListDynamic_8(function):
    function.satellites.dataValid = True
    tle = ["NOAA 8",
           "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
           "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954"]
    sat = EarthSatellite(tle[1], tle[2],  name=tle[0])
    function.ui.satTabWidget.setCurrentIndex(0)
    function.ui.mainTabWidget.setCurrentIndex(5)
    function.ui.listSats.setRowCount(0)
    function.ui.listSats.setColumnCount(2)
    function.ui.listSats.insertRow(0)
    entry = QTableWidgetItem('NOAA 8')
    function.ui.listSats.setItem(0, 1, entry)
    function.ui.listSats.setRowHidden(0, False)
    function.satellites.objects = {'NOAA 8': sat}
    with mock.patch.object(function,
                           'updateListSats'):
        with mock.patch.object(gui.mainWaddon.tabSat_Search,
                               'findRangeRate',
                               return_value=[np.nan, 2, 3]):
            with mock.patch.object(gui.mainWaddon.tabSat_Search,
                                   'findSunlit',
                                   return_value=True):
                with mock.patch.object(gui.mainWaddon.tabSat_Search,
                                       'calcAppMag',
                                       return_value=10):
                    with mock.patch.object(QRect,
                                           'intersects',
                                           return_value=True):
                        function.calcSatListDynamic()


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


def test_calcSat_1(function):
    tle = ["NOAA 8",
           "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
           "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954"]
    sat = EarthSatellite(tle[1], tle[2],  name=tle[0])

    with mock.patch.object(gui.mainWaddon.tabSat_Search,
                           'findRangeRate',
                           return_value=(1, 1, 1, 1)):
        with mock.patch.object(gui.mainWaddon.tabSat_Search,
                               'findSunlit',
                               return_value=False):
            with mock.patch.object(gui.mainWaddon.tabSat_Search,
                                   'findSatUp'):
                with mock.patch.object(gui.mainWaddon.tabSat_Search,
                                       'checkTwilight'):
                    with mock.patch.object(function,
                                           'updateListSats'):
                        function.calcSat(sat, 0, 0, 0, 0, 0, 0)


def test_calcSat_2(function):
    tle = ["NOAA 8",
           "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
           "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954"]
    sat = EarthSatellite(tle[1], tle[2],  name=tle[0])

    with mock.patch.object(gui.mainWaddon.tabSat_Search,
                           'findRangeRate',
                           return_value=(1, 1, 1, 1)):
        with mock.patch.object(gui.mainWaddon.tabSat_Search,
                               'findSunlit',
                               return_value=True):
            with mock.patch.object(gui.mainWaddon.tabSat_Search,
                                   'findSatUp'):
                with mock.patch.object(gui.mainWaddon.tabSat_Search,
                                       'checkTwilight'):
                    with mock.patch.object(gui.mainWaddon.tabSat_Search,
                                           'calcAppMag',
                                           return_value=0):
                        with mock.patch.object(function,
                                               'updateListSats'):
                            function.calcSat(sat, 0, 0, 0, 0, 0, 0)


def test_calcSat_3(function):
    tle = ["NOAA 8",
           "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
           "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954"]
    sat = EarthSatellite(tle[1], tle[2],  name=tle[0])

    with mock.patch.object(gui.mainWaddon.tabSat_Search,
                           'findRangeRate',
                           return_value=(np.nan, 0, 0, 0)):
        with mock.patch.object(function,
                               'updateListSats'):
            function.calcSat(sat, 0, 0, 0, 0, 0, 0)


def test_workerCalcSatList_1(function):
    function.ui.listSats.setRowCount(0)
    function.workerCalcSatList()


def test_workerCalcSatList_2(function):
    tle = ["NOAA 8",
           "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
           "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954"]
    sat = EarthSatellite(tle[1], tle[2],  name=tle[0])

    class Test:
        objects = {'sat1': sat}

    function.satellites = Test()
    function.ui.listSats.setRowCount(0)
    function.ui.listSats.setColumnCount(9)
    function.ui.listSats.insertRow(0)
    entry = QTableWidgetItem('sat1')
    function.ui.listSats.setItem(0, 1, entry)

    with mock.patch.object(function,
                           'checkSatOk',
                           return_value=False):
        function.workerCalcSatList()


def test_workerCalcSatList_3(function):
    tle = ["NOAA 8",
           "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
           "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954"]
    sat = EarthSatellite(tle[1], tle[2],  name=tle[0])

    class Test:
        objects = {'sat1': sat}

    function.satellites = Test()
    function.ui.listSats.setRowCount(0)
    function.ui.listSats.setColumnCount(9)
    function.ui.listSats.insertRow(0)
    entry = QTableWidgetItem('sat1')
    function.ui.listSats.setItem(0, 1, entry)

    with mock.patch.object(function,
                           'checkSatOk',
                           return_value=True):
        with mock.patch.object(function,
                               'calcSat'):
            function.workerCalcSatList()


def test_calcSatList_1(function):
    with mock.patch.object(function.app.threadPool,
                           'start'):
        function.calcSatList()


def test_fillSatListName_1(function):
    tle = ["NOAA 8",
           "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
           "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954"]
    sat = EarthSatellite(tle[1], tle[2],  name=tle[0])

    function.satellites.objects = {'sat1': sat}
    with mock.patch.object(function,
                           'calcSatList'):
        function.fillSatListName()
