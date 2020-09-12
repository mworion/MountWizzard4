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
import os
import pytest
import threading
from unittest import mock
import logging
from pathlib import Path
import shutil

# external packages
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import pyqtSignal
from mountcontrol.qtmount import Mount
from skyfield.api import Topos

# local import
from gui.mainWmixin.tabAlmanac import Almanac
from gui.widgets.main_ui import Ui_MainWindow
from gui.utilities.widget import MWidget
from base.loggerMW import CustomLogger


@pytest.fixture(autouse=True, scope='function')
def app(qtbot):

    shutil.copy2('tests/testData/de421_23.bsp', 'tests/data/de421_23.bsp',
                 follow_symlinks=True)

    class Test(QObject):
        config = {'mainW': {}}
        threadPool = QThreadPool()
        update1s = pyqtSignal()
        update30m = pyqtSignal()
        message = pyqtSignal(str, int)
        mount = Mount(host='localhost', MAC='00:00:00:00:00:00', verbose=False,
                      pathToData=Path('tests/data'))
        mount.obsSite.location = Topos(latitude_degrees=20,
                                       longitude_degrees=10,
                                       elevation_m=500)
        ephemeris = mount.obsSite.loader('de421_23.bsp')

    widget = QWidget()
    ui = Ui_MainWindow()
    ui.setupUi(widget)

    app = Almanac(app=Test(), ui=ui,
                  clickable=MWidget().clickable)

    app.changeStyleDynamic = MWidget().changeStyleDynamic
    app.guiSetText = MWidget().guiSetText
    app.embedMatplot = MWidget().embedMatplot
    app.generateFlat = MWidget().generateFlat
    app.COLOR_BLUE1 = MWidget().COLOR_BLUE1
    app.COLOR_BLUE2 = MWidget().COLOR_BLUE2
    app.COLOR_BLUE3 = MWidget().COLOR_BLUE3
    app.COLOR_BLUE4 = MWidget().COLOR_BLUE4
    app.COLOR_WHITE1 = MWidget().COLOR_WHITE1
    app.M_GREY = MWidget().M_GREY
    app.M_BLUE1 = MWidget().M_BLUE1
    app.M_BLUE2 = MWidget().M_BLUE2
    app.M_BLUE3 = MWidget().M_BLUE3
    app.M_BLUE4 = MWidget().M_BLUE4
    app.M_WHITE = MWidget().M_WHITE
    app.twilight = MWidget().embedMatplot(QWidget())
    app.deviceStat = dict()
    app.log = CustomLogger(logging.getLogger(__name__), {})
    app.threadPool = QThreadPool()

    yield app


def test_initConfig_1(app):
    suc = app.initConfig()
    assert suc


def test_storeConfig_1(app):
    suc = app.storeConfig()
    assert suc


def test_storeConfig_2(app):
    app.thread = threading.Thread()
    with mock.patch.object(threading.Thread,
                           'join'):
        suc = app.storeConfig()
        assert suc


def test_drawTwilight_1(app):
    ts = app.app.mount.obsSite.ts
    timeJD = app.app.mount.obsSite.timeJD
    t0 = ts.tt_jd(int(timeJD.tt) - 182)
    t1 = ts.tt_jd(int(timeJD.tt) + 182)

    app.civil = dict()
    app.nautical = dict()
    app.astronomical = dict()
    app.dark = dict()
    app.civil[0] = [[t0, 10], [t0, 10]]
    app.nautical[0] = [[t0, 10], [t0, 10]]
    app.astronomical[0] = [[t0, 10], [t0, 10]]
    app.dark[0] = [[t0, 10], [t0, 10]]

    axe, fig = app.generateFlat(widget=app.twilight)

    with mock.patch.object(app,
                           'generateFlat',
                           return_value=(axe, fig)):
        with mock.patch.object(axe.figure.canvas,
                               'draw'):
            suc = app.drawTwilight(t0, t1)
            assert suc


def test_searchTwilightWorker_1(app):
    with mock.patch.object(app,
                           'drawTwilight'):
        suc = app.searchTwilightWorker()
        assert suc


def test_searchTwilight_1(app):
    with mock.patch.object(threading.Thread,
                           'start'):
        suc = app.searchTwilight()
        assert suc


def test_displayTwilightData_1(app):
    suc = app.displayTwilightData()
    assert suc


def test_getMoonPhase_1(app):
    a, b, c = app.getMoonPhase()
    assert a is not None
    assert b is not None
    assert c is not None


def test_updateMoonPhase_1(app):
    with mock.patch.object(app,
                           'getMoonPhase',
                           return_value=(20, 45, 20)):
        suc = app.updateMoonPhase()
        assert suc


def test_updateMoonPhase_2(app):
    with mock.patch.object(app,
                           'getMoonPhase',
                           return_value=(45, 135, 45)):
        suc = app.updateMoonPhase()
        assert suc


def test_updateMoonPhase_3(app):
    with mock.patch.object(app,
                           'getMoonPhase',
                           return_value=(70, 225, 70)):
        suc = app.updateMoonPhase()
        assert suc


def test_updateMoonPhase_4(app):
    with mock.patch.object(app,
                           'getMoonPhase',
                           return_value=(95, 315, 95)):
        suc = app.updateMoonPhase()
        assert suc
