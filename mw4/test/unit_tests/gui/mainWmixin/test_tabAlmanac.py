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
import logging
from pathlib import Path
import faulthandler
faulthandler.enable()

# external packages
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import pyqtSignal
from mountcontrol.qtmount import Mount
from skyfield.api import Topos

# local import
from mw4.gui.mainWmixin.tabAlmanac import Almanac
from mw4.gui.widgets.main_ui import Ui_MainWindow
from mw4.gui.widget import MWidget
from mw4.base.loggerMW import CustomLogger


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown(qtbot):
    global ui, widget, Test, Test1, app

    class Test1(QObject):
        mount = Mount(host='localhost', MAC='00:00:00:00:00:00', expire=False, verbose=False,
                      pathToData=Path('mw4/test/data'))
        update10s = pyqtSignal()
        threadPool = QThreadPool()

    class Test(QObject):
        config = {'mainW': {}}
        threadPool = QThreadPool()
        update1s = pyqtSignal()
        update30m = pyqtSignal()
        message = pyqtSignal(str, int)
        mount = Mount(host='localhost', MAC='00:00:00:00:00:00', expire=False, verbose=False,
                      pathToData=Path('mw4/test/data'))
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
    app.close = MWidget().close
    app.deleteLater = MWidget().deleteLater
    app.guiSetText = MWidget().guiSetText
    app.embedMatplot = MWidget().embedMatplot
    app.generateFlat = MWidget().generateFlat
    app.COLOR_BLUE1 = MWidget().COLOR_BLUE1
    app.COLOR_BLUE2 = MWidget().COLOR_BLUE2
    app.COLOR_BLUE3 = MWidget().COLOR_BLUE3
    app.COLOR_BLUE4 = MWidget().COLOR_BLUE4
    app.COLOR_WHITE1 = MWidget().COLOR_WHITE1
    app.twilight = QWidget()
    app.deviceStat = dict()
    app.log = CustomLogger(logging.getLogger(__name__), {})
    app.threadPool = QThreadPool()

    qtbot.addWidget(app)

    yield

    app.threadPool.waitForDone(1000)


def test_initConfig_1():
    suc = app.initConfig()
    assert suc


def test_storeConfig_1():
    suc = app.storeConfig()
    assert suc


def test_updateMoonPhase_1():
    suc = app.updateMoonPhase()
    assert suc
