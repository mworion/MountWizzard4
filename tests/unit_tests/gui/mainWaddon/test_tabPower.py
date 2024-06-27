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
from unittest import mock
from PySide6.QtWidgets import QInputDialog, QWidget

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.widgets.main_ui import Ui_MainWindow
from gui.mainWaddon.tabPower import Power


@pytest.fixture(autouse=True, scope='module')
def function(qapp):

    mainW = QWidget()
    mainW.app = App()
    mainW.threadPool = mainW.app.threadPool
    mainW.ui = Ui_MainWindow()
    mainW.ui.setupUi(mainW)
    window = Power(mainW)
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
