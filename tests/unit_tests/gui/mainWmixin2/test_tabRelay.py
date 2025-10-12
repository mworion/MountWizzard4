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
# written in python3, (c) 2019-2023 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest

# external packages

# local import
from mw4.gui.mainWmixin.tabSett_Relay import SettRelay
from mw4.gui.mainWmixin.tabRelay import Relay
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from mw4.gui.utilities.toolsQtWidget import MWidget
from mw4.gui.widgets.main_ui import Ui_MainWindow


@pytest.fixture(autouse=True, scope='module')
def function(qapp):

    class Mixin(MWidget, Relay, SettRelay):
        def __init__(self):
            super().__init__()
            self.app = App()
            self.msg = self.app.msg
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

