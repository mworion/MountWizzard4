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
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest

# external packages
from PySide6.QtWidgets import QWidget

# local import
from gui.mainWaddon.tabRelay import Relay
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.widgets.main_ui import Ui_MainWindow


@pytest.fixture(autouse=True, scope='module')
def function(qapp):

    mainW = QWidget()
    mainW.app = App()
    mainW.threadPool = mainW.app.threadPool
    mainW.ui = Ui_MainWindow()
    mainW.ui.setupUi(mainW)
    window = Relay(mainW)
    yield window


def test_updateRelayGui(function, qtbot):
    function.relayButton = list()
    function.relayDropDown = list()
    function.relayText = list()
    function.app.relay.status = [0, 1, 0, 1, 0, 1, 0, 1]
    suc = function.updateRelayGui()
    assert suc

