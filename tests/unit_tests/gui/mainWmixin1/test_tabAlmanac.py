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
import threading
from unittest import mock

# external packages
from PyQt5.QtGui import QPixmap
from skyfield.api import wgs84
import numpy as np

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from mw4.gui.utilities.toolsQtWidget import MWidget
from mw4.gui.widgets.main_ui import Ui_MainWindow
from mw4.gui.mainWmixin.tabAlmanac import Almanac


@pytest.fixture(autouse=True, scope='module')
def function(qapp):

    class Mixin(MWidget, Almanac):
        def __init__(self):
            super().__init__()
            self.app = App()
            self.threadPool = self.app.threadPool
            self.ui = Ui_MainWindow()
            self.ui.setupUi(self)
            Almanac.__init__(self)

    window = Mixin()
    yield window
    window.threadPool.waitForDone(1000)


def test_initConfig_1(function):
    with mock.patch.object(function,
                           'showMoonPhase'):
        with mock.patch.object(function,
                               'showTwilightDataPlot'):
            with mock.patch.object(function,
                                   'showTwilightDataList'):
                with mock.patch.object(function,
                                       'listTwilightData'):
                    suc = function.initConfig()
                    assert suc


def test_storeConfig_1(function):
    function.thread = None
    suc = function.storeConfig()
    assert suc


def test_storeConfig_2(function):
    function.thread = threading.Thread()
    with mock.patch.object(threading.Thread,
                           'join'):
        suc = function.storeConfig()
        assert suc


def test_setColors(function):
    suc = function.setColors()
    assert suc


def test_colorChangeAlmanac(function):
    with mock.patch.object(function,
                           'showTwilightDataPlot'):
        suc = function.colorChangeAlmanac()
        assert suc


def test_plotTwilightData_1(function):
    function.closing = False
    ts = function.app.mount.obsSite.ts
    tsNow = ts.now()
    t = ts.tt_jd([tsNow.tt, tsNow.tt])
    e = np.array([1, 1])
    result = (ts, t, e)
    suc = function.plotTwilightData(result)
    assert suc


def test_plotTwilightData_2(function):
    function.closing = True
    ts = function.app.mount.obsSite.ts
    tsNow = ts.now()
    t = ts.tt_jd([tsNow.tt, tsNow.tt])
    e = np.array([1, 1])
    result = (ts, t, e)
    suc = function.plotTwilightData(result)
    assert suc


def test_calcTwilightData_1(function):
    ts = function.app.mount.obsSite.ts
    location = wgs84.latlon(latitude_degrees=0,
                            longitude_degrees=0,
                            elevation_m=0)
    val = function.calcTwilightData(ts, location, tWinL=0, tWinH=0)
    assert val


def test_searchTwilightWorker_1(function):
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


def test_searchTwilightPlot_1(function):
    function.app.mount.obsSite.location = None
    with mock.patch.object(threading.Thread,
                           'start'):
        suc = function.showTwilightDataPlot()
        assert not suc


def test_searchTwilightPLot_2(function):
    function.app.mount.obsSite.location = wgs84.latlon(latitude_degrees=0,
                                                       longitude_degrees=0,
                                                       elevation_m=0)
    with mock.patch.object(function.threadPool,
                           'start'):
        suc = function.showTwilightDataPlot()
        assert suc


def test_searchTwilightList_1(function):
    function.app.mount.obsSite.location = None
    with mock.patch.object(threading.Thread,
                           'start'):
        suc = function.showTwilightDataList()
        assert not suc


def test_searchTwilightList_2(function):
    function.app.mount.obsSite.location = wgs84.latlon(latitude_degrees=0,
                                                       longitude_degrees=0,
                                                       elevation_m=0)
    with mock.patch.object(function,
                           'listTwilightData'):
        suc = function.showTwilightDataList()
        assert suc


def test_displayTwilightData_1(function):
    tsNow = function.app.mount.obsSite.ts.now()
    t = [tsNow, tsNow]
    e = [1, 1]
    suc = function.listTwilightData(t, e)
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


def test_updateMoonPhase_1(function):
    ts = function.app.mount.obsSite.ts
    tsNow = ts.now()
    t = ts.tt_jd([tsNow.tt, tsNow.tt])
    val = (20, 45, .20, 0, t, [0, 1], t, [0, 1])
    with mock.patch.object(function,
                           'calcMoonPhase',
                           return_value=val):
        suc = function.showMoonPhase()
        assert suc


def test_updateMoonPhase_2(function):
    ts = function.app.mount.obsSite.ts
    tsNow = ts.now()
    t = ts.tt_jd([tsNow.tt, tsNow.tt])
    val = (20, 45, .20, 0, t, [0, 1], t, [0, 1])
    with mock.patch.object(function,
                           'calcMoonPhase',
                           return_value=val):
        suc = function.showMoonPhase()
        assert suc
