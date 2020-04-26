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

# external packages
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import pyqtSignal
from mw4.powerswitch.kmRelay import KMRelay
from mw4.gui.mainWmixin.tabSettRelay import SettRelay

# local import
from mw4.gui.mainWmixin.tabRelay import Relay
from mw4.gui.widgets.main_ui import Ui_MainWindow
from mw4.gui.widget import MWidget


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

