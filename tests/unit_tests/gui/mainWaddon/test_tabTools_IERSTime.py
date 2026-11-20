# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import pytest
from mw4.gui.mainWaddon.tabTools_IERSTime import IERSTime
from pathlib import Path
from PySide6.QtCore import QObject
from unittest import mock


@pytest.fixture(autouse=True, scope="module")
def function(qapp, makeApp):
    mainW = QObject()
    mainW.app = makeApp()
    mainW.ui = mock.MagicMock()
    mainW.wIcon = mock.MagicMock()
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
    with (
        mock.patch.object(
            function.databaseProcessing, "writeEarthRotationData", return_value=False
        ),
        mock.patch("mw4.gui.mainWaddon.tabTools_IERSTime.startWorker") as worker,
    ):
        function.progEarthRotationData()
        worker.assert_not_called()


def test_progEarthRotationData_2(function):
    function.app.mount.host = ("127.0.0.1", 3294)
    with (
        mock.patch.object(function.databaseProcessing, "writeEarthRotationData", return_value=True),
        mock.patch("mw4.gui.mainWaddon.tabTools_IERSTime.UploadPopup.upload", return_value=True),
        mock.patch("mw4.gui.mainWaddon.tabTools_IERSTime.startWorker", return_value=None) as worker,
    ):
        function.progEarthRotationData()
        worker.assert_called_once_with(None, function.app.threadPool, function.runnerReloadDeltaT)


def test_progEarthRotationData_3(function):
    function.app.mount.host = ("127.0.0.1", 3294)
    with (
        mock.patch.object(function.databaseProcessing, "writeEarthRotationData", return_value=True),
        mock.patch("mw4.gui.mainWaddon.tabTools_IERSTime.UploadPopup.upload", return_value=False),
        mock.patch("mw4.gui.mainWaddon.tabTools_IERSTime.startWorker") as worker,
    ):
        function.progEarthRotationData()
        worker.assert_not_called()


def test_progEarthRotationData_reloadBusy(function):
    with (
        mock.patch.object(function, "workerReloadDeltaT", mock.Mock(locked=True)),
        mock.patch.object(function.databaseProcessing, "writeEarthRotationData") as write,
        mock.patch.object(function, "msg") as msg,
    ):
        function.progEarthRotationData()
        write.assert_not_called()
        msg.emit.assert_called_once_with(
            2, "IERS", "Reload", "Earth rotation data reload is still running"
        )


@pytest.mark.parametrize("success", [True, False])
def test_reloadDeltaT(function, success):
    with mock.patch(
        "mw4.gui.mainWaddon.tabTools_IERSTime.reloadDeltaT", return_value=success
    ) as reload:
        assert function.runnerReloadDeltaT() is success
        reload.assert_called_once_with(function.app.dReg.mount.obsSite)


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
