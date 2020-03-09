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
from queue import Queue

# external packages
from PyQt5.QtWidgets import QInputDialog
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import pyqtSignal

# local import
from mw4.gui.mainWmixin.tabPower import Power
from mw4.gui.widgets.main_ui import Ui_MainWindow
from mw4.gui.widget import MWidget
from mw4.powerswitch.pegasusUPB import PegasusUPB


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    global ui, widget, Test

    class Test1:
        threadPool = QThreadPool()

    class Test(QObject):
        config = {'mainW': {}}
        messageQueue = Queue()
        threadPool = QThreadPool()
        update1s = pyqtSignal()
        power = PegasusUPB(app=Test1())
        sender = None

    widget = QWidget()
    ui = Ui_MainWindow()
    ui.setupUi(widget)

    yield

    del widget, ui, Test, Test1


def test_clearPowerGui_1(qtbot):
    app = Power(app=Test(), ui=ui,
                clickable=MWidget().clickable,
                change=MWidget().changeStyleDynamic)
    qtbot.addWidget(app)

    app.clearPowerGui()


def test_setGuiVersion_1(qtbot):
    app = Power(app=Test(), ui=ui,
                clickable=MWidget().clickable,
                change=MWidget().changeStyleDynamic)
    qtbot.addWidget(app)

    app.setGuiVersion()


def test_setGuiVersion_2(qtbot):
    app = Power(app=Test(), ui=ui,
                clickable=MWidget().clickable,
                change=MWidget().changeStyleDynamic)
    qtbot.addWidget(app)

    app.setGuiVersion(version=2)


def test_updatePowerGui_1(qtbot):
    app = Power(app=Test(), ui=ui,
                clickable=MWidget().clickable,
                change=MWidget().changeStyleDynamic)
    qtbot.addWidget(app)

    app.updatePowerGui()


def test_setDew_1(qtbot):
    @staticmethod
    def sender():
        @staticmethod
        def parent():
            return ui.dewA
        return parent

    app = Power(app=Test(), ui=ui,
                clickable=MWidget().clickable,
                change=MWidget().changeStyleDynamic)
    qtbot.addWidget(app)

    with mock.patch.object(QInputDialog,
                           'getInt',
                           return_value=(0, False)):
        with mock.patch.object(app.app,
                               'sender',
                               return_value=sender):
            app.setDew()

