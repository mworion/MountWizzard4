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
# License APL2.0
#
###########################################################
import pytest
from mw4.gui.mainWaddon.tabTools_IERSTime import IERSTime
from pathlib import Path
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from unittest import mock


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    mainW = mock.MagicMock()
    mainW.app = App()
    mainW.ui.iersSource.currentText.return_value = "Datacenter from IERS"

    patcher_dl = mock.patch("mw4.gui.mainWaddon.tabTools_IERSTime.DownloadPopup")
    patcher_ul = mock.patch("mw4.gui.mainWaddon.tabTools_IERSTime.UploadPopup")
    patcher_dl.start()
    patcher_ul.start()

    window = IERSTime(mainW)
    yield window

    mainW.app.threadPool.waitForDone(1000)
    patcher_dl.stop()
    patcher_ul.stop()


def test_initConfig_1(function):
    function.app.config["WindowMain"] = {}
    function.initConfig()
    assert function.tempDir == Path("tests/work/temp")


def test_storeConfig_1(function):
    function.app.config["WindowMain"] = {}
    function.storeConfig()
    assert "iersSource" in function.app.config["WindowMain"]


def test_setupIcons_1(function):
    function.setupIcons()


def test_setupIERSSourceURLsDropDown(function):
    function.setupIERSSourceURLsDropDown()


def test_finishProgEarthRotationData_1(function):
    class Test:
        returnValues = {"success": False}
        worker = mock.MagicMock()

    function.uploadPopup = Test()
    function.finishProgEarthRotationData()


def test_finishProgEarthRotationData_2(function):
    class Test:
        returnValues = {"success": True}
        worker = mock.MagicMock()

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
        worker = mock.MagicMock()

    function.downloadPopup = Test()
    function.finishLoadTimeDataFromSourceURLs()


def test_finishLoadTimeDataFromSourceURLs_2(function):
    class Test:
        returnValues = {"success": True}
        worker = mock.MagicMock()

    function.downloadPopup = Test()
    function.finishLoadTimeDataFromSourceURLs()


def test_finishLoadFinalsFromSourceURLs_1(function):
    class Test:
        returnValues = {"success": False}
        worker = mock.MagicMock()

    function.downloadPopup = Test()
    function.finishLoadFinalsFromSourceURLs()


def test_finishLoadFinalsFromSourceURLs_2(function):
    class Test:
        returnValues = {"success": True}
        worker = mock.MagicMock()

    function.downloadPopup = Test()
    function.finishLoadFinalsFromSourceURLs()


def test_loadTimeDataFromSourceURLs_1(function):
    function.ui.isOnline.isChecked.return_value = False
    function.loadTimeDataFromSourceURLs()


def test_loadTimeDataFromSourceURLs_2(function):
    function.ui.isOnline.isChecked.return_value = True
    function.loadTimeDataFromSourceURLs()


def test_loadTimeDataFromSourceURLs_when_online(function):
    """Test loadTimeDataFromSourceURLs when app is online (lines 122-131)."""
    function.app.isOnline = True
    # This test just verifies that the method executes the full code path
    # when app.isOnline is True (lines 122-131 will be executed)
    function.loadTimeDataFromSourceURLs()


