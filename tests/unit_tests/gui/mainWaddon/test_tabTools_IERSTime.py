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
# written in python3, (c) 2019-2026 by mworion
# Licence APL2.0
#
###########################################################

import mw4.gui.utilities
import pytest
from mw4.gui.mainWaddon.tabTools_IERSTime import IERSTime
from mw4.gui.utilities.toolsQtWidget import MWidget
from mw4.gui.widgets.main_ui import Ui_MainWindow
from pathlib import Path
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from unittest import mock


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    mainW = MWidget()
    mainW.app = App()
    mainW.ui = Ui_MainWindow()
    mainW.ui.setupUi(mainW)
    window = IERSTime(mainW)
    yield window
    mainW.app.threadPool.waitForDone(1000)


def test_initConfig_1(function):
    function.initConfig()
    assert function.tempDir == Path("tests/work/temp")


def test_initConfig_2(function):
    function.initConfig()
    assert function.tempDir == Path("tests/work/temp")


def test_storeConfig_1(function):
    function.thread = None
    function.storeConfig()


def test_setupIcons_1(function):
    function.setupIcons()


def test_setupIERSSourceURLsDropDown(function):
    function.setupIERSSourceURLsDropDown()


def test_finishProgEarthRotationData_1(function):
    class Test:
        returnValues = {"success": False}

    function.uploadPopup = Test()
    function.finishProgEarthRotationData()


def test_finishProgEarthRotationData_2(function):
    class Test:
        returnValues = {"success": True}

    function.uploadPopup = Test()
    function.finishProgEarthRotationData()


def test_progEarthRotationData_1(function):
    function.app.mount.host = ("127.0.0.1", 3294)
    with mock.patch.object(
        function.databaseProcessing, "writeEarthRotationData", return_value=False
    ):
        function.progEarthRotationData()


def test_progEarthRotationData_2(function):
    function.app.mount.host = ("127.0.0.1", 3294)
    with mock.patch.object(
        function.databaseProcessing, "writeEarthRotationData", return_value=True
    ):
        function.progEarthRotationData()


def test_finishLoadTimeDataFromSourceURLs_1(function):
    class Test:
        returnValues = {"success": False}

    function.downloadPopup = Test()
    function.finishLoadTimeDataFromSourceURLs()


def test_finishLoadTimeDataFromSourceURLs_2(function):
    class Test:
        returnValues = {"success": True}

    function.downloadPopup = Test()
    function.finishLoadTimeDataFromSourceURLs()


def test_finishLoadFinalsFromSourceURLs_1(function):
    class Test:
        returnValues = {"success": False}

    function.downloadPopup = Test()
    with mock.patch.object(mw4.gui.mainWaddon.tabTools_IERSTime, "DownloadPopup"):
        function.finishLoadFinalsFromSourceURLs()


def test_finishLoadFinalsFromSourceURLs_2(function):
    class Test:
        returnValues = {"success": True}

    function.downloadPopup = Test()
    with mock.patch.object(mw4.gui.mainWaddon.tabTools_IERSTime, "DownloadPopup"):
        function.finishLoadFinalsFromSourceURLs()


def test_loadTimeDataFromSourceURLs_1(function):
    function.ui.isOnline.setChecked(False)
    with mock.patch.object(mw4.gui.mainWaddon.tabTools_IERSTime, "DownloadPopup"):
        function.loadTimeDataFromSourceURLs()


def test_loadTimeDataFromSourceURLs_2(function):
    function.ui.isOnline.setChecked(True)
    with mock.patch.object(mw4.gui.mainWaddon.tabTools_IERSTime, "DownloadPopup"):
        function.loadTimeDataFromSourceURLs()
