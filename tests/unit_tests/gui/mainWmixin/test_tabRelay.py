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
# written in python3 , (c) 2019, 2020 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
# external packages
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import pyqtSignal
from logic.powerswitch import KMRelay
from gui.mainWmixin.tabSettRelay import SettRelay

# local import
from gui.mainWmixin.tabRelay import Relay
from gui.widgets.main_ui import Ui_MainWindow
from gui.utilities.widget import MWidget


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown(qtbot):
    global ui, widget, Test, app

    class Test(QObject):
        config = {'mainW': {}}
        threadPool = QThreadPool()
        update1s = pyqtSignal()
        message = pyqtSignal(str, int)
        relay = KMRelay()

    widget = QWidget()
    ui = Ui_MainWindow()
    ui.setupUi(widget)

    app = Relay(app=Test(), ui=ui,
                clickable=MWidget().clickable)

    app.changeStyleDynamic = MWidget().changeStyleDynamic
    app.close = MWidget().close
    app.relayButtons = SettRelay(app=Test(), ui=ui,
                                 clickable=MWidget().clickable).relayButtons
    app.deleteLater = MWidget().deleteLater
    qtbot.addWidget(app)

    yield


def test_initConfig_1():
    app.app.config['mainW'] = {}
    suc = app.initConfig()
    assert suc


def test_storeConfig_1():
    suc = app.storeConfig()
    assert suc


def test_updateRelayGui(qtbot):
    app.relayButton = list()
    app.relayDropDown = list()
    app.relayText = list()
    app.app.relay.status = [0, 1, 0, 1, 0, 1, 0, 1]
    suc = app.updateRelayGui()
    assert suc

