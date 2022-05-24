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
#
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock
import pytest
# external packages
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import pyqtSignal
from gui.mainWmixin.tabSettRelay import SettRelay

# local import
from logic.powerswitch.kmRelay import KMRelay
from gui.widgets.main_ui import Ui_MainWindow
from gui.utilities.toolsQtWidget import MWidget


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown(qtbot):
    global ui, widget, Test, app

    class Test(QObject):
        config = {'mainW': {}}
        threadPool = QThreadPool()
        update1s = pyqtSignal()
        mes = pyqtSignal(object, object, object, object)

        relay = KMRelay()

    widget = QWidget()
    ui = Ui_MainWindow()
    ui.setupUi(widget)

    app = SettRelay(app=Test(), ui=ui,
                    clickable=MWidget().clickable)

    app.changeStyleDynamic = MWidget().changeStyleDynamic
    app.close = MWidget().close

    app.deleteLater = MWidget().deleteLater
    yield


def test_initConfig_1():
    app.app.config['mainW'] = {}
    suc = app.initConfig()
    assert suc


def test_storeConfig_1():
    app.ui.relayDevice.setCurrentIndex(0)
    app.storeConfig()


def test_setupRelayGui(qtbot):
    assert 8 == len(app.relayDropDowns)
    assert 8 == len(app.relayButtonTexts)
    assert 8 == len(app.relayButtons)
    for dropDown in app.relayDropDowns:
        val = dropDown.count()
        assert 2 == val


def test_toggleRelay_1():
    def Sender():
        return ui.relayButton0
    app.sender = Sender

    app.ui.relayDevice.setCurrentIndex(0)
    suc = app.relayButtonPressed()
    assert not suc


def test_toggleRelay_2():
    def Sender():
        return ui.relayButton0
    app.sender = Sender
    app.ui.relayDevice.setCurrentIndex(1)
    with mock.patch.object(app.app.relay,
                           'switch',
                           return_value=False):
        suc = app.relayButtonPressed()
        assert not suc


def test_doRelayAction_1():
    app.relayDropDowns[7].setCurrentIndex(0)
    with mock.patch.object(app.app.relay,
                           'switch',
                           return_value=False):
        suc = app.doRelayAction(7)
        assert not suc


def test_doRelayAction_2():
    app.relayDropDowns[7].setCurrentIndex(0)
    with mock.patch.object(app.app.relay,
                           'switch',
                           return_value=True):
        suc = app.doRelayAction(7)
        assert suc


def test_doRelayAction_3():
    app.relayDropDowns[7].setCurrentIndex(2)
    suc = app.doRelayAction(7)
    assert not suc


def test_doRelayAction_4():
    app.relayDropDowns[7].setCurrentIndex(1)
    with mock.patch.object(app.app.relay,
                           'pulse',
                           return_value=False):
        suc = app.doRelayAction(7)
        assert not suc


def test_doRelayAction_5():
    app.relayDropDowns[7].setCurrentIndex(1)
    with mock.patch.object(app.app.relay,
                           'pulse',
                           return_value=True):
        suc = app.doRelayAction(7)
        assert suc


def test_relayButtonPressed_1():
    def Sender():
        return ui.relayButton0
    app.sender = Sender

    with mock.patch.object(app,
                           'doRelayAction',
                           return_value=False):
        suc = app.relayButtonPressed()
        assert not suc


def test_relayButtonPressed_2():
    def Sender():
        return ui.relayButton0
    app.sender = Sender

    with mock.patch.object(app,
                           'doRelayAction',
                           return_value=True):
        suc = app.relayButtonPressed()
        assert suc
