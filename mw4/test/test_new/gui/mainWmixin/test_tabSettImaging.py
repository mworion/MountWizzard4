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
# Python  v3.7.5
#
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
from unittest import mock
import logging

# external packages
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import pyqtSignal
from mountcontrol.qtmount import Mount

# local import
from mw4.gui.mainWmixin.tabSettImaging import SettImaging
from mw4.gui.widgets.main_ui import Ui_MainWindow
from mw4.gui.widget import MWidget
from mw4.imaging.camera import Camera
from mw4.imaging.focuser import Focuser
from mw4.telescope.telescope import Telescope
from mw4.base.loggerMW import CustomLogger


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown(qtbot):
    global ui, widget, Test, Test1, app

    class Test1(QObject):
        mount = Mount()
        update1s = pyqtSignal()
        threadPool = QThreadPool()

    class Test(QObject):
        config = {'mainW': {}}
        threadPool = QThreadPool()
        update1s = pyqtSignal()
        message = pyqtSignal(str, int)
        camera = Camera(app=Test1())
        focuser = Focuser(app=Test1())
        telescope = Telescope(app=Test1())

    widget = QWidget()
    ui = Ui_MainWindow()
    ui.setupUi(widget)

    app = SettImaging(app=Test(), ui=ui,
                      clickable=MWidget().clickable)
    app.changeStyleDynamic = MWidget().changeStyleDynamic
    app.guiSetText = MWidget().guiSetText
    app.close = MWidget().close
    app.deleteLater = MWidget().deleteLater
    app.log = CustomLogger(logging.getLogger(__name__), {})

    qtbot.addWidget(app)

    yield

    del widget, ui, Test, Test1, app


def test_initConfig_1():
    suc = app.initConfig()
    assert suc


def test_storeConfig_1():
    suc = app.storeConfig()
    assert suc


def test_updateParameters_1():
    suc = app.updateParameters()
    assert suc


def test_setDownloadModeFast():
    suc = app.setDownloadModeFast()
    assert suc


def test_setDownloadModeSlow():
    suc = app.setDownloadModeSlow()
    assert suc


def test_setCoolerOn():
    suc = app.setCoolerOn()
    assert suc


def test_setCoolerOff():
    suc = app.setCoolerOff()
    assert suc
