# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import pytest
from mw4.base import packageConfig
from mw4.gui.mainWindow.externalWindows import ExternalWindows
from mw4.gui.widgets.main_ui import Ui_MainWindow
from PySide6.QtCore import QCoreApplication, QEvent, QObject, Qt, Signal
from PySide6.QtWidgets import QPushButton, QWidget
from unittest import mock


@pytest.fixture(autouse=True, scope="module")
def function(qapp, makeApp):
    packageConfig.isAvailable = True
    window = QWidget()
    window.app = makeApp()
    window.ui = Ui_MainWindow()
    window.ui.setupUi(window)

    func = ExternalWindows(window)
    yield func
    window.app.threadPool.waitForDone(10000)
    qapp.processEvents()


@pytest.fixture(autouse=True)
def resetState(function):
    # Clear every window's classObj so tests don't inherit a leftover object.
    for window in function.uiWindows:
        function.uiWindows[window]["classObj"] = None
        function.uiWindows[window]["token"] = None
    yield


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
    token = object()
    function.uiWindows["showImageW"]["classObj"] = object()
    function.uiWindows["showImageW"]["token"] = token
    function.deleteWindowResource("showImageW", token)
    assert function.uiWindows["showImageW"]["classObj"] is None
    assert function.uiWindows["showImageW"]["token"] is None


def test_deleteWindowResource_stale(function):
    token = object()
    window = object()
    function.uiWindows["showImageW"]["classObj"] = window
    function.uiWindows["showImageW"]["token"] = token
    function.deleteWindowResource("showImageW", object())
    assert function.uiWindows["showImageW"]["classObj"] is window
    assert function.uiWindows["showImageW"]["token"] is token


def test_buildWindow_1(function):
    class Destroyed:
        def connect(self, a):
            return

    class Test:
        def __init__(self, app, title):
            self.app = app
            self.title = title

        destroyed = Destroyed()

        @staticmethod
        def initConfig():
            return

        @staticmethod
        def showWindow():
            return

    function.uiWindows["showSatelliteMapW"]["class"] = Test
    function.buildWindow("showSatelliteMapW")


def test_replacementSurvivesDeferredDestruction(function, qapp, monkeypatch):
    class TestWindow(QWidget):
        def __init__(self, app, title: str) -> None:
            super().__init__()
            self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        def initConfig(self) -> None:
            pass

        def showWindow(self) -> None:
            self.show()

    entry = function.uiWindows["showImageW"]
    monkeypatch.setitem(entry, "class", TestWindow)
    function.buildWindow("showImageW")
    oldWindow = entry["classObj"]
    function.closeExtendedWindows()
    function.buildWindow("showImageW")
    newWindow = entry["classObj"]
    assert newWindow is not oldWindow

    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    assert entry["classObj"] is newWindow
    assert newWindow.isVisible()

    function.closeExtendedWindows()
    assert not newWindow.isVisible()
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    assert entry["classObj"] is None
    assert entry["token"] is None


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


def test_closeExtendedWindows_1(function):
    class Test:
        @staticmethod
        def close():
            return

    test = function.uiWindows
    function.uiWindows = {"showMessageW": {"classObj": Test(), "button": QPushButton()}}
    function.closeExtendedWindows()
    function.uiWindows = test


def test_closeExtendedWindows_2(function):
    test = function.uiWindows
    function.uiWindows = {"showMessageW": {"classObj": None, "button": QPushButton()}}
    function.closeExtendedWindows()
    function.uiWindows = test


def test_createWindowTable(function):
    table = function.createWindowTable()
    assert table.keys() == function.uiWindows.keys()
    assert all(entry["classObj"] is None for entry in table.values())
