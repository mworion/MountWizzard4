############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
from pathlib import Path
from unittest import mock

import mw4.gui.utilities
import pytest
from mw4.gui.extWindows.uploadPopupW import UploadPopup
from mw4.gui.mainWaddon.tabTools_IERSTime import IERSTime
from mw4.gui.widgets.main_ui import Ui_MainWindow

# external packages
from PySide6.QtWidgets import QWidget

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    mainW = QWidget()
    mainW.app = App()
    mainW.ui = Ui_MainWindow()
    mainW.ui.setupUi(mainW)
    window = IERSTime(mainW)
    yield window
    mainW.app.threadPool.waitForDone(1000)


def test_initConfig_1(function):
    suc = function.initConfig()
    assert suc
    assert function.tempDir == Path("tests/work/temp")


def test_initConfig_2(function):
    suc = function.initConfig()
    assert suc
    assert function.tempDir == Path("tests/work/temp")


def test_storeConfig_1(function):
    function.thread = None
    suc = function.storeConfig()
    assert suc


def test_setupIERSSourceURLsDropDown(function):
    suc = function.setupIERSSourceURLsDropDown()
    assert suc


def test_finishProgEarthRotationData_1(function):
    class Test:
        returnValues = {"success": False}

    function.uploadPopup = Test()
    suc = function.finishProgEarthRotationData()
    assert suc


def test_finishProgEarthRotationData_2(function):
    class Test:
        returnValues = {"success": True}

    function.uploadPopup = Test()
    suc = function.finishProgEarthRotationData()
    assert suc


def test_progEarthRotationData_1(function):
    function.app.mount.host = ("127.0.0.1", 3294)
    with mock.patch.object(
        function.databaseProcessing, "writeEarthRotationData", return_value=False
    ):
        with mock.patch.object(UploadPopup, "show"):
            suc = function.progEarthRotationData()
            assert not suc


def test_progEarthRotationData_2(function):
    function.app.mount.host = ("127.0.0.1", 3294)
    with mock.patch.object(
        function.databaseProcessing, "writeEarthRotationData", return_value=True
    ):
        with mock.patch.object(UploadPopup, "show"):
            with mock.patch.object(UploadPopup, "show"):
                suc = function.progEarthRotationData()
                assert suc


def test_finishLoadTimeDataFromSourceURLs_1(function):
    class Test:
        returnValues = {"success": False}

    function.downloadPopup = Test()
    suc = function.finishLoadTimeDataFromSourceURLs()
    assert suc


def test_finishLoadTimeDataFromSourceURLs_2(function):
    class Test:
        returnValues = {"success": True}

    function.downloadPopup = Test()
    suc = function.finishLoadTimeDataFromSourceURLs()
    assert suc


def test_finishLoadFinalsFromSourceURLs_1(function):
    class Test:
        returnValues = {"success": False}

    function.downloadPopup = Test()
    with mock.patch.object(mw4.gui.mainWaddon.tabTools_IERSTime, "DownloadPopup"):
        suc = function.finishLoadFinalsFromSourceURLs()
        assert not suc


def test_finishLoadFinalsFromSourceURLs_2(function):
    class Test:
        returnValues = {"success": True}

    function.downloadPopup = Test()
    with mock.patch.object(mw4.gui.mainWaddon.tabTools_IERSTime, "DownloadPopup"):
        suc = function.finishLoadFinalsFromSourceURLs()
        assert suc


def test_loadTimeDataFromSourceURLs_1(function):
    function.ui.isOnline.setChecked(False)
    with mock.patch.object(mw4.gui.mainWaddon.tabTools_IERSTime, "DownloadPopup"):
        suc = function.loadTimeDataFromSourceURLs()
        assert not suc


def test_loadTimeDataFromSourceURLs_2(function):
    function.ui.isOnline.setChecked(True)
    with mock.patch.object(mw4.gui.mainWaddon.tabTools_IERSTime, "DownloadPopup"):
        suc = function.loadTimeDataFromSourceURLs()
        assert suc
