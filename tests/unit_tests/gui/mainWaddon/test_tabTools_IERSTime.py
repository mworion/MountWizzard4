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


def test_progEarthRotationData_1(function):
    function.app.mount.host = ("127.0.0.1", 3294)
    with mock.patch.object(
        function.databaseProcessing, "writeEarthRotationData", return_value=False
    ):
        function.progEarthRotationData()


def test_progEarthRotationData_2(function):
    function.app.mount.host = ("127.0.0.1", 3294)
    with (
        mock.patch.object(
            function.databaseProcessing, "writeEarthRotationData", return_value=True
        ),
        mock.patch(
            "mw4.gui.mainWaddon.tabTools_IERSTime.UploadPopup.upload", return_value=True
        ),
    ):
        function.progEarthRotationData()


def test_progEarthRotationData_3(function):
    function.app.mount.host = ("127.0.0.1", 3294)
    with (
        mock.patch.object(
            function.databaseProcessing, "writeEarthRotationData", return_value=True
        ),
        mock.patch(
            "mw4.gui.mainWaddon.tabTools_IERSTime.UploadPopup.upload", return_value=False
        ),
    ):
        function.progEarthRotationData()


def test_loadTimeDataFromSourceURLs_1(function):
    function.app.isOnline = False
    function.loadTimeDataFromSourceURLs()


def test_loadTimeDataFromSourceURLs_2(function):
    function.app.isOnline = True
    with mock.patch(
        "mw4.gui.mainWaddon.tabTools_IERSTime.DownloadPopup.download", return_value=False
    ) as mock_dl:
        function.loadTimeDataFromSourceURLs()
        assert mock_dl.call_count == 1


def test_loadTimeDataFromSourceURLs_3(function):
    function.app.isOnline = True
    with mock.patch(
        "mw4.gui.mainWaddon.tabTools_IERSTime.DownloadPopup.download", return_value=True
    ) as mock_dl:
        function.loadTimeDataFromSourceURLs()
        assert mock_dl.call_count == 2


def test_loadTimeDataFromSourceURLs_4(function):
    function.app.isOnline = True
    with mock.patch(
        "mw4.gui.mainWaddon.tabTools_IERSTime.DownloadPopup.download",
        side_effect=[True, False],
    ) as mock_dl:
        function.loadTimeDataFromSourceURLs()
        assert mock_dl.call_count == 2
