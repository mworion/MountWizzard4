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
import unittest.mock as mock
import pytest
import astropy
import webbrowser

# external packages
import PySide6
from PySide6.QtWidgets import QWidget, QInputDialog
from skyfield.api import Angle, wgs84

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.widgets.main_ui import Ui_MainWindow
from gui.mainWaddon.tabMountCommand import MountCommand
import gui.mainWaddon.tabMount
import mountcontrol


@pytest.fixture(autouse=True, scope='module')
def function(qapp):

    mainW = QWidget()
    mainW.app = App()
    mainW.threadPool = mainW.app.threadPool
    mainW.ui = Ui_MainWindow()
    mainW.ui.setupUi(mainW)
    window = MountCommand(mainW)
    yield window


def test_openCommandProtocol_1(function):
    with mock.patch.object(webbrowser,
                           'open',
                           return_value=True):
        function.openCommandProtocol()


def test_openCommandProtocol_2(function):
    with mock.patch.object(webbrowser,
                           'open',
                           return_value=False):
        function.openCommandProtocol()


def test_openUpdateTimeDelta_1(function):
    with mock.patch.object(webbrowser,
                           'open',
                           return_value=True):
        function.openUpdateTimeDelta()


def test_openUpdateTimeDelta_2(function):
    with mock.patch.object(webbrowser,
                           'open',
                           return_value=False):
        function.openUpdateTimeDelta()


def test_openUpdateFirmware_1(function):
    with mock.patch.object(webbrowser,
                           'open',
                           return_value=True):
        function.openUpdateFirmware()


def test_openUpdateFirmware_2(function):
    with mock.patch.object(webbrowser,
                           'open',
                           return_value=False):
        function.openUpdateFirmware()


def test_openMountDocumentation_1(function):
    function.app.mount.firmware.product = 'tester'
    with mock.patch.object(webbrowser,
                           'open',
                           return_value=True):
        suc = function.openMountDocumentation()
        assert not suc


def test_openMountDocumentation_2(function):
    function.app.mount.firmware.product = '10micron GM1000HPS'
    with mock.patch.object(webbrowser,
                           'open',
                           return_value=False):
        suc = function.openMountDocumentation()
        assert suc


def test_openMountDocumentation_3(function):
    function.app.mount.firmware.product = '10micron GM1000HPS'
    with mock.patch.object(webbrowser,
                           'open',
                           return_value=True):
        suc = function.openMountDocumentation()
        assert suc


def test_commandRaw_1(function):
    with mock.patch.object(mountcontrol.connection.Connection,
                           'communicateRaw',
                           return_value=(True, False, '')):
        function.commandRaw()


def test_commandRaw_2(function):
    with mock.patch.object(mountcontrol.connection.Connection,
                           'communicateRaw',
                           return_value=(True, True, '')):
        function.commandRaw()
