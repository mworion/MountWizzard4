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

# external packages
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import pyqtSignal

# local import
from logic.powerswitch.kmRelay import KMRelay
from gui.mainWmixin.tabSettRelay import SettRelay
from gui.mainWmixin.tabRelay import Relay
from tests.baseTestSetupMixins import App
from gui.utilities.toolsQtWidget import MWidget
from gui.widgets.main_ui import Ui_MainWindow


@pytest.fixture(autouse=True, scope='module')
def module(qapp):
    yield


@pytest.fixture(autouse=True, scope='function')
def function(module):

    class Mixin(MWidget, Relay, SettRelay):
        def __init__(self):
            super().__init__()
            self.app = App()
            self.ui = Ui_MainWindow()
            self.ui.setupUi(self)
            Relay.__init__(self)
            SettRelay.__init__(self)

    window = Mixin()
    yield window


def test_initConfig_1(function):
    function.app.config['mainW'] = {}
    suc = function.initConfig()
    assert suc


def test_storeConfig_1(function):
    suc = function.storeConfig()
    assert suc


def test_updateRelayGui(function, qtbot):
    function.relayButton = list()
    function.relayDropDown = list()
    function.relayText = list()
    function.app.relay.status = [0, 1, 0, 1, 0, 1, 0, 1]
    suc = function.updateRelayGui()
    assert suc

