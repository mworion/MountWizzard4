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
import unittest.mock as mock
import pytest
import webbrowser

# external packages

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.utilities.toolsQtWidget import MWidget
from gui.widgets.main_ui import Ui_MainWindow
from gui.mainWmixin.tabMount_Terminal import MountTerminal
import mountcontrol


@pytest.fixture(autouse=True, scope='module')
def function(qapp):
    class Mixin(MWidget, MountTerminal):
        def __init__(self):
            super().__init__()
            self.app = App()
            self.msg = self.app.msg
            self.deviceStat = self.app.deviceStat
            self.ui = Ui_MainWindow()
            self.ui.setupUi(self)
            MountTerminal.__init__(self)

    window = Mixin()
    yield window


def test_openCommandProtocol_1(function):
    with mock.patch.object(webbrowser,
                           'open',
                           return_value=True):
        suc = function.openCommandProtocol()
        assert suc


def test_openCommandProtocol_2(function):
    with mock.patch.object(webbrowser,
                           'open',
                           return_value=False):
        suc = function.openCommandProtocol()
        assert suc


def test_commandRaw_1(function):
    with mock.patch.object(mountcontrol.connection.Connection,
                           'communicateRaw',
                           return_value=(True, False, '')):
        suc = function.commandRaw()
        assert suc


def test_commandRaw_2(function):
    with mock.patch.object(mountcontrol.connection.Connection,
                           'communicateRaw',
                           return_value=(True, True, '')):
        suc = function.commandRaw()
        assert suc
