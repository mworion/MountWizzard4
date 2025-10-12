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
from unittest import mock
from PyQt5.QtWidgets import QInputDialog

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from mw4.gui.utilities.toolsQtWidget import MWidget
from mw4.gui.widgets.main_ui import Ui_MainWindow
from mw4.gui.mainWmixin.tabPower import Power


@pytest.fixture(autouse=True, scope='module')
def function(qapp):

    class Mixin(MWidget, Power):
        def __init__(self):
            super().__init__()
            self.app = App()
            self.msg = self.app.msg
            self.ui = Ui_MainWindow()
            self.ui.setupUi(self)
            Power.__init__(self)

    window = Mixin()
    yield window


def test_setGuiVersion_1(function, qtbot):
    function.setGuiVersion()


def test_setGuiVersion_2(function, qtbot):
    function.setGuiVersion(version=2)


def test_updatePowerGui_1(function, qtbot):
    function.updatePowerGui()


def test_updatePowerGui_2(function, qtbot):
    function.app.power.data = {'FIRMWARE_INFO.VERSION': '1.5'}
    function.updatePowerGui()


def test_setDew_1(function, qtbot):
    class Sender:
        @staticmethod
        def parent():
            return function.ui.dewA

    with mock.patch.object(QInputDialog,
                           'getInt',
                           return_value=(0, False)):
        function.sender = Sender
        function.setDew()


def test_setDew_2(function, qtbot):
    class Sender:
        @staticmethod
        def parent():
            return function.ui.dewA

    with mock.patch.object(QInputDialog,
                           'getInt',
                           return_value=(0, False)):
        function.sender = Sender
        function.setDew()


def test_setDew_3(function, qtbot):
    class Sender:
        @staticmethod
        def parent():
            return function.ui.dewA

    with mock.patch.object(QInputDialog,
                           'getInt',
                           return_value=(0, False)):
        function.sender = Sender
        function.ui.dewA.setText('10')
        function.setDew()


def test_setDew_4(function, qtbot):
    class Sender:
        @staticmethod
        def parent():
            return function.ui.dewA

    with mock.patch.object(QInputDialog,
                           'getInt',
                           return_value=(0, True)):
        function.sender = Sender
        function.ui.dewA.setText('10')
        function.setDew()


def test_setDew_5(function, qtbot):
    class Sender:
        @staticmethod
        def parent():
            return function.ui.dewA
    function.dew = {'test': function.ui.dewB}
    with mock.patch.object(QInputDialog,
                           'getInt',
                           return_value=(0, True)):
        function.sender = Sender
        function.ui.dewA.setText('10')
        function.setDew()


def test_togglePowerPort_1(function, qtbot):
    def Sender():
        return function.ui.powerPort1

    function.sender = Sender
    function.togglePowerPort()


def test_togglePowerPort_2(function, qtbot):
    def Sender():
        return function.ui.dewA

    function.sender = Sender
    function.togglePowerPort()


def test_togglePowerBootPort_1(function, qtbot):
    def Sender():
        return function.ui.powerBootPort1

    function.sender = Sender
    function.togglePowerBootPort()


def test_togglePowerBootPort_2(function, qtbot):
    def Sender():
        return function.ui.dewA

    function.sender = Sender
    function.togglePowerBootPort()


def test_toggleHubUSB_1(function, qtbot):
    function.toggleHubUSB()


def test_togglePortUSB_1(function, qtbot):
    def Sender():
        return function.ui.portUSB1

    function.sender = Sender
    function.togglePortUSB()


def test_togglePortUSB_2(function, qtbot):
    def Sender():
        return function.ui.dewA

    function.sender = Sender
    function.togglePortUSB()


def test_toggleAutoDew_1(function, qtbot):
    function.toggleAutoDew()


def test_setAdjustableOutput_2(function, qtbot):
    function.ui.adjustableOutput.setText('10')
    with mock.patch.object(QInputDialog,
                           'getDouble',
                           return_value=(0, False)):
        function.setAdjustableOutput()


def test_setAdjustableOutput_3(function, qtbot):
    function.ui.adjustableOutput.setText('10')
    with mock.patch.object(QInputDialog,
                           'getDouble',
                           return_value=(0, True)):
        function.setAdjustableOutput()


def test_rebootUPB_1(function):
    with mock.patch.object(function.app.power,
                           'reboot',
                           return_value=False):
        suc = function.rebootUPB()
        assert not suc


def test_rebootUPB_2(function):
    with mock.patch.object(function.app.power,
                           'reboot',
                           return_value=True):
        suc = function.rebootUPB()
        assert suc
