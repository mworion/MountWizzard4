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
from unittest import mock
from queue import Queue
# external packages
from PyQt5.QtWidgets import QInputDialog
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import pyqtSignal

# local import
from gui.mainWmixin.tabPower import Power
from gui.widgets.main_ui import Ui_MainWindow
from gui.utilities.widget import MWidget
from logic.powerswitch import PegasusUPB


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown(qtbot):
    global ui, widget, Test, Test1, app

    class Test1:
        threadPool = QThreadPool()

    class Test(QObject):
        config = {'mainW': {}}
        messageQueue = Queue()
        threadPool = QThreadPool()
        update1s = pyqtSignal()
        power = PegasusUPB(app=Test1())

    widget = QWidget()
    ui = Ui_MainWindow()
    ui.setupUi(widget)

    app = Power(app=Test(), ui=ui,
                clickable=MWidget().clickable)
    app.changeStyleDynamic = MWidget().changeStyleDynamic
    app.close = MWidget().close
    app.deleteLater = MWidget().deleteLater
    qtbot.addWidget(app)

    yield


def test_clearPowerGui_1(qtbot):

    app.clearPowerGui()


def test_setGuiVersion_1(qtbot):

    app.setGuiVersion()


def test_setGuiVersion_2(qtbot):

    app.setGuiVersion(version=2)


def test_updatePowerGui_1(qtbot):

    app.updatePowerGui()


def test_setDew_1(qtbot):
    class Sender:
        @staticmethod
        def parent():
            return ui.dewA

    with mock.patch.object(QInputDialog,
                           'getInt',
                           return_value=(0, False)):
        app.sender = Sender
        app.setDew()


def test_setDew_2(qtbot):
    class Sender:
        @staticmethod
        def parent():
            return ui.dewA

    with mock.patch.object(QInputDialog,
                           'getInt',
                           return_value=(0, False)):
        app.sender = Sender
        app.setDew()


def test_setDew_3(qtbot):
    class Sender:
        @staticmethod
        def parent():
            return ui.dewA

    with mock.patch.object(QInputDialog,
                           'getInt',
                           return_value=(0, False)):
        app.sender = Sender
        app.ui.dewA.setText('10')
        app.setDew()


def test_setDew_4(qtbot):
    class Sender:
        @staticmethod
        def parent():
            return ui.dewA

    with mock.patch.object(QInputDialog,
                           'getInt',
                           return_value=(0, True)):
        app.sender = Sender
        app.ui.dewA.setText('10')
        app.setDew()


def test_togglePowerPort_1(qtbot):
    def Sender():
        return ui.powerPort1

    app.sender = Sender
    app.togglePowerPort()


def test_togglePowerPort_2(qtbot):
    def Sender():
        return ui.dewA

    app.sender = Sender
    app.togglePowerPort()


def test_togglePowerBootPort_1(qtbot):
    def Sender():
        return ui.powerBootPort1

    app.sender = Sender
    app.togglePowerBootPort()


def test_togglePowerBootPort_2(qtbot):
    def Sender():
        return ui.dewA

    app.sender = Sender
    app.togglePowerBootPort()


def test_toggleHubUSB_1(qtbot):
    app.toggleHubUSB()


def test_togglePortUSB_1(qtbot):
    def Sender():
        return ui.portUSB1

    app.sender = Sender
    app.togglePortUSB()


def test_togglePortUSB_2(qtbot):
    def Sender():
        return ui.dewA

    app.sender = Sender
    app.togglePortUSB()


def test_toggleAutoDew_1(qtbot):
    app.toggleAutoDew()


def test_setAdjustableOutput_2(qtbot):
    app.ui.adjustableOutput.setText('10')
    with mock.patch.object(QInputDialog,
                           'getDouble',
                           return_value=(0, False)):
        app.setAdjustableOutput()


def test_setAdjustableOutput_3(qtbot):
    app.ui.adjustableOutput.setText('10')
    with mock.patch.object(QInputDialog,
                           'getDouble',
                           return_value=(0, True)):
        app.setAdjustableOutput()

