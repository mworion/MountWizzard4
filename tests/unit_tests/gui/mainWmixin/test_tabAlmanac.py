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
# written in python3, (c) 2019-2022 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
import threading
from unittest import mock

# external packages
from PyQt5.QtWidgets import QWidget
from skyfield.api import wgs84

# local import
from tests.unit_tests.unitTestAddOns.baseTestSetupMixins import App
from gui.utilities.toolsQtWidget import MWidget
from gui.widgets.main_ui import Ui_MainWindow
from gui.mainWmixin.tabAlmanac import Almanac


@pytest.fixture(autouse=True, scope='module')
def module(qapp):
    yield


@pytest.fixture(autouse=True, scope='function')
def function(module):

    class Mixin(MWidget, Almanac):
        def __init__(self):
            super().__init__()
            self.app = App()
            self.threadPool = self.app.threadPool
            self.ui = Ui_MainWindow()
            self.ui.setupUi(self)
            self.closing = False
            Almanac.__init__(self)

    window = Mixin()
    yield window


def test_initConfig_1(function):
    with mock.patch.object(function,
                           'updateMoonPhase'):
        with mock.patch.object(function,
                               'searchTwilightPlot'):
            with mock.patch.object(function,
                                   'searchTwilightList'):
                with mock.patch.object(function,
                                       'displayTwilightData'):
                    with mock.patch.object(function,
                                           'lunarNodes'):
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
                           'searchTwilightPlot'):
        suc = function.colorChangeAlmanac()
        assert suc


def test_plotTwilightData_1(function):
    function.closing = False
    ts = function.app.mount.obsSite.ts
    tsNow = ts.now()
    t = [tsNow, tsNow]
    e = [1, 1]
    result = (ts, t, e)
    widget = QWidget()
    function.twilight = function.embedMatplot(widget)
    suc = function.plotTwilightData(result)
    assert suc


def test_plotTwilightData_2(function):
    function.closing = True
    ts = function.app.mount.obsSite.ts
    tsNow = ts.now()
    t = [tsNow, tsNow]
    e = [1, 1]
    result = (ts, t, e)
    widget = QWidget()
    function.twilight = function.embedMatplot(widget)
    suc = function.plotTwilightData(result)
    assert not suc


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
    t = [tsNow, tsNow]
    e = [1, 1]
    with mock.patch.object(function,
                           'calcTwilightData',
                           return_value=(t, e)):
        suc = function.searchTwilightWorker(ts, location, timeWindow=0)
        assert suc


def test_searchTwilightPlot_1(function):
    function.app.mount.obsSite.location = None
    with mock.patch.object(threading.Thread,
                           'start'):
        suc = function.searchTwilightPlot()
        assert not suc


def test_searchTwilightPLot_2(function):
    function.app.mount.obsSite.location = wgs84.latlon(latitude_degrees=0,
                                                       longitude_degrees=0,
                                                       elevation_m=0)
    with mock.patch.object(function.threadPool,
                           'start'):
        suc = function.searchTwilightPlot()
        assert suc


def test_searchTwilightList_1(function):
    function.app.mount.obsSite.location = None
    with mock.patch.object(threading.Thread,
                           'start'):
        suc = function.searchTwilightList()
        assert not suc


def test_searchTwilightList_2(function):
    function.app.mount.obsSite.location = wgs84.latlon(latitude_degrees=0,
                                                       longitude_degrees=0,
                                                       elevation_m=0)
    with mock.patch.object(function,
                           'displayTwilightData'):
        suc = function.searchTwilightList()
        assert suc


def test_displayTwilightData_1(function):
    tsNow = function.app.mount.obsSite.ts.now()
    t = [tsNow, tsNow]
    e = [1, 1]
    suc = function.displayTwilightData(t, e)
    assert suc


def test_calcMoonPhase_1(function):
    a, b, c, d = function.calcMoonPhase()
    assert a is not None
    assert b is not None
    assert c is not None
    assert d is not None


def test_generateMoonMask_1(function):
    function.generateMoonMask(64, 64, 45)


def test_generateMoonMask_2(function):
    function.generateMoonMask(64, 64, 135)


def test_generateMoonMask_3(function):
    function.generateMoonMask(64, 64, 225)


def test_generateMoonMask_4(function):
    function.generateMoonMask(64, 64, 315)


def test_updateMoonPhase_1(function):
    with mock.patch.object(function,
                           'calcMoonPhase',
                           return_value=(20, 45, .20, 0)):
        suc = function.updateMoonPhase()
        assert suc


def test_updateMoonPhase_2(function):
    with mock.patch.object(function,
                           'calcMoonPhase',
                           return_value=(45, 135, .45, 0)):
        suc = function.updateMoonPhase()
        assert suc


def test_lunarNodes_1(function):
    suc = function.lunarNodes()
    assert suc
