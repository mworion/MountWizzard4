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
# written in python 3, (c) 2019, 2020 by mworion
#
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
from gui.utilities.widget import MWidget
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
    suc = function.drawTwilight(None, None)
    assert not suc


def test_drawTwilight_2(function):
    function.twilight = function.embedMatplot(QWidget())
    ts = function.app.mount.obsSite.ts
    timeJD = function.app.mount.obsSite.timeJD
    t0 = ts.tt_jd(int(timeJD.tt) - 180)
    t1 = ts.tt_jd(int(timeJD.tt) + 180)

    function.civil = dict()
    function.nautical = dict()
    function.astronomical = dict()
    function.dark = dict()
    function.civil[0] = []
    function.nautical[0] = []
    function.astronomical[0] = []
    function.dark[0] = []

    axe, fig = function.generateFlat(widget=function.twilight)

    with mock.patch.object(function,
                           'generateFlat',
                           return_value=(axe, fig)):
        with mock.patch.object(axe.figure.canvas,
                               'draw'):
            suc = function.drawTwilight(t0, t1)
            assert suc


def test_drawTwilight_3(function):
    function.twilight = function.embedMatplot(QWidget())
    ts = function.app.mount.obsSite.ts
    timeJD = function.app.mount.obsSite.timeJD
    t0 = ts.tt_jd(int(timeJD.tt) - 180)
    t1 = ts.tt_jd(int(timeJD.tt) + 180)

    function.civil = dict()
    function.nautical = dict()
    function.astronomical = dict()
    function.dark = dict()
    function.civil[0] = [[t0, 10], [t0, 10]]
    function.nautical[0] = [[t0, 10], [t0, 10]]
    function.astronomical[0] = [[t0, 10], [t0, 10]]
    function.dark[0] = [[t0, 10], [t0, 10]]

    axe, fig = function.generateFlat(widget=function.twilight)

    with mock.patch.object(function,
                           'generateFlat',
                           return_value=(axe, fig)):
        with mock.patch.object(axe.figure.canvas,
                               'draw'):
            suc = function.drawTwilight(t0, t1)
            assert suc


def test_searchTwilightWorker_1(function):
    function.app.mount.obsSite.location = Topos(latitude_degrees=0,
                                                longitude_degrees=0,
                                                elevation_m=0)
    with mock.patch.object(function,
                           'drawTwilight'):
        suc = function.searchTwilightWorker(1)
        assert suc


def test_searchTwilightWorker_2(function):
    function.app.mount.obsSite.location = None
    with mock.patch.object(function,
                           'drawTwilight'):
        suc = function.searchTwilightWorker(1)
        assert not suc


def test_searchTwilight_1(function):
    with mock.patch.object(threading.Thread,
                           'start'):
        suc = function.searchTwilight()
        assert suc


def test_calcTwilightData_1(function):
    val = function.calcTwilightData()
    assert val == ([], [])


def test_calcTwilightData_2(function):
    function.app.mount.obsSite.location = Topos(latitude_degrees=0,
                                                longitude_degrees=0,
                                                elevation_m=0)
    val = function.calcTwilightData()
    assert val


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


def test_getMoonPhase_1(function):
    a, b, c = function.getMoonPhase()
    assert a is not None
    assert b is not None
    assert c is not None


def test_updateMoonPhase_1(function):
    with mock.patch.object(function,
                           'getMoonPhase',
                           return_value=(20, 45, .20)):
        suc = function.updateMoonPhase()
        assert suc


def test_updateMoonPhase_2(function):
    with mock.patch.object(function,
                           'getMoonPhase',
                           return_value=(45, 135, .45)):
        suc = function.updateMoonPhase()
        assert suc


def test_updateMoonPhase_3(function):
    with mock.patch.object(function,
                           'getMoonPhase',
                           return_value=(70, 225, .70)):
        suc = function.updateMoonPhase()
        assert suc


def test_updateMoonPhase_4(function):
    with mock.patch.object(function,
                           'getMoonPhase',
                           return_value=(95, 315, .95)):
        suc = function.updateMoonPhase()
        assert suc


def test_updateMoonPhase_5(function):
    with mock.patch.object(function,
                           'getMoonPhase',
                           return_value=(95, 315, 10)):
        suc = function.updateMoonPhase()
        assert suc


def test_lunarNodes_1(function):
    suc = function.lunarNodes()
    assert suc
