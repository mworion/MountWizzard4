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
import threading
from unittest import mock

# external packages
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget
from skyfield.api import wgs84
import numpy as np

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.widgets.main_ui import Ui_MainWindow
from gui.mainWaddon.tabAlmanac import Almanac


@pytest.fixture(autouse=True, scope='module')
def function(qapp):

    mainW = QWidget()
    mainW.app = App()
    mainW.threadPool = mainW.app.threadPool
    mainW.ui = Ui_MainWindow()
    mainW.ui.setupUi(mainW)

    window = Almanac(mainW)
    yield window


def test_initConfig_1(function):
    function.initConfig()


def test_storeConfig_1(function):
    function.thread = None
    function.storeConfig()


def test_storeConfig_2(function):
    function.thread = threading.Thread()
    with mock.patch.object(threading.Thread,
                           'join'):
        function.storeConfig()


def test_setColors(function):
    function.setColors()


def test_updateColorSet(function):
    with mock.patch.object(function,
                           'showTwilightDataPlot'):
        with mock.patch.object(function,
                               'showTwilightDataList'):
            with mock.patch.object(function,
                                   'showMoonPhase'):
                with mock.patch.object(function,
                                       'showMoonPhase'):
                    function.updateColorSet()


def test_plotTwilightData_1(function):
    function.closing = False
    ts = function.app.mount.obsSite.ts
    tsNow = ts.now()
    t = ts.tt_jd([tsNow.tt, tsNow.tt])
    e = np.array([1, 1])
    result = (ts, t, e)
    function.plotTwilightData(result)


def test_plotTwilightData_2(function):
    function.closing = True
    ts = function.app.mount.obsSite.ts
    tsNow = ts.now()
    t = ts.tt_jd([tsNow.tt, tsNow.tt])
    e = np.array([1, 1])
    result = (ts, t, e)
    function.plotTwilightData(result)


def test_listTwilightData_1(function):
    tsNow = function.app.mount.obsSite.ts.now()
    t = [tsNow, tsNow]
    e = [1, 1]
    function.listTwilightData(t, e)


def test_calcTwilightData_1(function):
    ts = function.app.mount.obsSite.ts
    location = wgs84.latlon(latitude_degrees=0,
                            longitude_degrees=0,
                            elevation_m=0)
    val = function.calcTwilightData(ts, location, tWinL=0, tWinH=0)
    assert val


def test_workerCalcTwilightDataPlot_1(function):
    location = wgs84.latlon(latitude_degrees=0,
                            longitude_degrees=0,
                            elevation_m=0)
    ts = function.app.mount.obsSite.ts
    tsNow = ts.now()
    t = ts.tt_jd([tsNow.tt, tsNow.tt])
    e = np.array([1, 1])
    with mock.patch.object(function,
                           'calcTwilightData',
                           return_value=(t, e)):
        suc = function.workerCalcTwilightDataPlot(ts, location, timeWindow=0)
        assert suc


def test_showTwilightDataPlot_1(function):
    function.app.mount.obsSite.location = None
    with mock.patch.object(threading.Thread,
                           'start'):
        suc = function.showTwilightDataPlot()
        assert not suc


def test_showTwilightDataPlot_2(function):
    function.app.mount.obsSite.location = wgs84.latlon(latitude_degrees=0,
                                                       longitude_degrees=0,
                                                       elevation_m=0)
    with mock.patch.object(function.mainW.threadPool,
                           'start'):
        suc = function.showTwilightDataPlot()
        assert suc


def test_showTwilightDataList_1(function):
    function.app.mount.obsSite.location = None
    with mock.patch.object(threading.Thread,
                           'start'):
        suc = function.showTwilightDataList()
        assert not suc


def test_showTwilightDataList_2(function):
    function.app.mount.obsSite.location = wgs84.latlon(latitude_degrees=0,
                                                       longitude_degrees=0,
                                                       elevation_m=0)
    with mock.patch.object(function,
                           'listTwilightData'):
        suc = function.showTwilightDataList()
        assert suc


def test_calcMoonPhase_1(function):
    val = function.calcMoonPhase()
    assert len(val) == 8


def test_generateMoonMask_1(function):
    q = QPixmap(64, 64)
    function.generateMoonMask(q, 45)


def test_generateMoonMask_2(function):
    q = QPixmap(64, 64)
    function.generateMoonMask(q, 135)


def test_generateMoonMask_3(function):
    q = QPixmap(64, 64)
    function.generateMoonMask(q, 225)


def test_generateMoonMask_4(function):
    q = QPixmap(64, 64)
    function.generateMoonMask(q, 315)


def test_showMoonPhase_1(function):
    ts = function.app.mount.obsSite.ts
    tsNow = ts.now()
    t = ts.tt_jd([tsNow.tt, tsNow.tt])
    val = (20, 45, .20, 0, t, [0, 1], t, [0, 1])
    with mock.patch.object(function,
                           'calcMoonPhase',
                           return_value=val):
        function.showMoonPhase()


def test_showMoonPhase_2(function):
    ts = function.app.mount.obsSite.ts
    tsNow = ts.now()
    t = ts.tt_jd([tsNow.tt, tsNow.tt])
    val = (20, 45, .20, 0, t, [0, 1], t, [0, 1])
    with mock.patch.object(function,
                           'calcMoonPhase',
                           return_value=val):
        function.showMoonPhase()
