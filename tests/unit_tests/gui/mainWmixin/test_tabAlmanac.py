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
import threading
from unittest import mock

# external packages
from PyQt5.QtWidgets import QWidget
from skyfield.api import Topos

# local import
from tests.baseTestSetupMixins import App
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
            self.ui = Ui_MainWindow()
            self.ui.setupUi(self)
            Almanac.__init__(self)

    window = Mixin()
    yield window


def test_initConfig_1(function):
    with mock.patch.object(function,
                           'updateMoonPhase'):
        with mock.patch.object(function,
                               'searchTwilight'):
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


def test_drawTwilight_1(function):
    tsNow = function.app.mount.obsSite.ts.now()
    t = [tsNow, tsNow]
    e = [1, 1]
    widget = QWidget()
    function.twilight = function.embedMatplot(widget)
    suc = function.drawTwilight(t, e)
    assert suc


def test_calcTwilightData_1(function):
    function.app.mount.obsSite.location = Topos(latitude_degrees=0,
                                                longitude_degrees=0,
                                                elevation_m=0)
    val = function.calcTwilightData()
    assert val


def test_searchTwilightWorker_1(function):
    function.app.mount.obsSite.location = None
    suc = function.searchTwilightWorker(1)
    assert not suc


def test_searchTwilightWorker_2(function):
    function.app.mount.obsSite.location = Topos(latitude_degrees=0,
                                                longitude_degrees=0,
                                                elevation_m=0)
    tsNow = function.app.mount.obsSite.ts.now()
    t = [tsNow, tsNow]
    e = [1, 1]
    with mock.patch.object(function,
                           'drawTwilight'):
        with mock.patch.object(function,
                               'calcTwilightData',
                               return_value=(t, e)):
            suc = function.searchTwilightWorker(1)
            assert suc


def test_searchTwilight_1(function):
    with mock.patch.object(threading.Thread,
                           'start'):
        suc = function.searchTwilight()
        assert suc


def test_displayTwilightData_1(function):
    with mock.patch.object(function,
                           'calcTwilightData',
                           return_value=([], [])):
        suc = function.displayTwilightData()
        assert suc


def test_displayTwilightData_2(function):
    ts = function.app.mount.obsSite.ts
    timeJD = function.app.mount.obsSite.timeJD
    t0 = ts.tt_jd(int(timeJD.tt) - 180)
    with mock.patch.object(function,
                           'calcTwilightData',
                           return_value=([(t0, t0), (1, 1)])):
        suc = function.displayTwilightData()
        assert suc


def test_calcMoonPhase_1(function):
    a, b, c = function.calcMoonPhase()
    assert a is not None
    assert b is not None
    assert c is not None


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
                           return_value=(20, 45, .20)):
        suc = function.updateMoonPhase()
        assert suc


def test_updateMoonPhase_2(function):
    with mock.patch.object(function,
                           'calcMoonPhase',
                           return_value=(45, 135, .45)):
        suc = function.updateMoonPhase()
        assert suc


def test_lunarNodes_1(function):
    suc = function.lunarNodes()
    assert suc


def t_twilight(function):
    from matplotlib import pyplot as plt
    from dateutil.tz import tzlocal
    from skyfield.api import Topos

    color = ['red', 'blue', 'green', 'yellow', 'white']
    function.app.mount.obsSite.location = Topos(latitude_degrees=60.0,
                                                longitude_degrees=11.5,
                                                elevation_m=500)
    t, e = function.calcTwilightData(timeWindow=180)

    print()
    ax = plt.subplot(111)
    day_old = None
    for ti, event in zip(t, e):
        hour = int(ti.astimezone(tzlocal()).strftime('%H'))
        minute = int(ti.astimezone(tzlocal()).strftime('%M'))
        y = (hour + 12 + minute / 60) % 24
        day = round(ti.tt + 0.5, 0)
        print(day, event, y)

        if day_old != day:
            day_old = day
            ax.bar(day, height=24, bottom=0, width=1, color='white')

        ax.bar(day, height=24-y, bottom=y, width=1, color=color[event])

    ax.set_ylim(0, 24)
    plt.show()
