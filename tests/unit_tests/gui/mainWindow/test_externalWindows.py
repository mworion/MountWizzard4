############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10_micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################

import unittest.mock as mock

import pytest


from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QPushButton, QWidget


import mw4.gui.utilities.toolsQtWidget
from mw4.base import packageConfig
from mw4.gui.mainWindow.externalWindows import ExternalWindows
from mw4.gui.widgets.main_ui import Ui_MainWindow
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    packageConfig.isAvailable = True
    window = QWidget()
    window.app = App()
    window.ui = Ui_MainWindow()
    window.ui.setupUi(window)

    func = ExternalWindows(window)
    yield func
    window.app.threadPool.waitForDone(10000)


def test_storeConfig_1(function):
    class Test:
        def storeConfig(self):
            return

    function.uiWindows["showMessageW"]["classObj"] = Test()
    function.storeConfigExtendedWindows()


def test_updateWindowsStats_1(function):
    function.uiWindows["showMessageW"]["classObj"] = None
    function.updateWindowsStats()


def test_updateWindowsStats_2(function):
    function.uiWindows["showMessageW"]["classObj"] = 1
    function.updateWindowsStats()


def test_deleteWindowResource_1(function):
    function.deleteWindowResource("showImageW")


def test_buildWindow_1(function):
    class Destroyed:
        def connect(self, a):
            return

    class Test:
        def __init__(self, app):
            self.app = app

        destroyed = Destroyed()

        @staticmethod
        def initConfig():
            return

        @staticmethod
        def showWindow():
            return

    function.uiWindows["showSatelliteW"]["class"] = Test
    function.buildWindow("showSatelliteW")


def test_toggleWindow_1(function):
    function.uiWindows["showImageW"]["classObj"] = None

    with mock.patch.object(function, "buildWindow"):
        function.toggleWindow("showImageW")


def test_toggleWindow_2(function):
    class Test(QObject):
        destroyed = Signal()

        @staticmethod
        def close():
            return

    function.uiWindows["showImageW"]["classObj"] = Test()
    with mock.patch.object(function, "buildWindow"):
        function.toggleWindow("showImageW")


def test_showExtendedWindows_1(function):
    function.app.config = {}
    test = function.uiWindows
    function.uiWindows = {"showSimulatorW": True}
    function.app.config["showMessageW"] = True
    with mock.patch.object(function, "buildWindow"):
        function.showExtendedWindows()
    function.uiWindows = test


def test_showExtendedWindows_2(function):
    test = function.uiWindows
    function.uiWindows = {"showMessageW": True}
    function.app.config["showMessageW"] = False
    with mock.patch.object(function, "buildWindow"):
        function.showExtendedWindows()
    function.uiWindows = test


def test_showExtendedWindows_3(function):
    test = function.uiWindows
    function.uiWindows = {"showMessageW": True}
    function.app.config["showMessageW"] = True
    with mock.patch.object(function, "buildWindow"):
        function.showExtendedWindows()
    function.app.config["showMessageW"] = False
    function.uiWindows = test


def test_waitCloseExtendedWindows_1(function):
    class Test:
        @staticmethod
        def close():
            function.uiWindows["showMessageW"]["classObj"] = None
            return

    test = function.uiWindows
    function.uiWindows = {
        "showMessageW": {"classObj": Test(), "button": QPushButton()},
        "showImageW": {"classObj": None, "button": QPushButton()},
    }
    with mock.patch.object(mw4.gui.utilities.toolsQtWidget, "sleepAndEvents"):
        suc = function.waitCloseExtendedWindows()
        assert suc
    function.uiWindows = test


def test_waitCloseExtendedWindows_2(function):
    test = function.uiWindows
    function.uiWindows = {"showMessageW": {"classObj": None, "button": QPushButton()}}
    with mock.patch.object(mw4.gui.utilities.toolsQtWidget, "sleepAndEvents"):
        suc = function.waitCloseExtendedWindows()
        assert suc
    function.uiWindows = test


def test_closeExtendedWindows_1(function):
    class Test:
        @staticmethod
        def close():
            function.uiWindows["showMessageW"]["classObj"] = None
            return

    test = function.uiWindows
    function.uiWindows = {"showMessageW": {"classObj": Test(), "button": QPushButton()}}
    with mock.patch.object(function, "waitCloseExtendedWindows"):
        function.closeExtendedWindows()
    function.uiWindows = test


def test_closeExtendedWindows_2(function):
    test = function.uiWindows
    function.uiWindows = {"showMessageW": {"classObj": None, "button": QPushButton()}}
    with mock.patch.object(function, "waitCloseExtendedWindows"):
        function.closeExtendedWindows()
    function.uiWindows = test


def test_collectWindows(function):
    class Test:
        @staticmethod
        def resize(a, b):
            return

        @staticmethod
        def move(a, b):
            return

        @staticmethod
        def activateWindow():
            return

    function.uiWindows = {"showMessageW": {"classObj": Test(), "button": QPushButton()}}
    function.collectWindows()
