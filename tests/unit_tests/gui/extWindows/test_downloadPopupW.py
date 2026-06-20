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
import builtins
import gc
import os
import pytest
import requests
import shutil
import unittest.mock as mock
from mw4.gui.extWindows.downloadPopupW import DownloadPopup
from mw4.gui.utilities.qtMain import MWidget
from pathlib import Path
from PySide6.QtCore import QEventLoop
from PySide6.QtWidgets import QApplication
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    widget = MWidget()
    widget.app = App()
    window = DownloadPopup(parentWidget=widget, url=Path(), dest=Path())
    yield window
    QApplication.processEvents()
    gc.collect()
    QApplication.processEvents()


@pytest.fixture
def mockedSleep(monkeypatch):
    monkeypatch.setattr("mw4.gui.extWindows.downloadPopupW.mainThreadSleep", lambda _: None)


def test_setIcon(function):
    function.setIcon()


def test_showWindow(function):
    with mock.patch.object(function, "show"):
        function.showWindow()
        function.show.assert_called_once()
        assert function.titleBar.windowFixed
        assert function.minimumHeight() <= 120
        assert function.minimumWidth() <= 400


def test_setProgressBarColor(function):
    function.setProgressBarColor("red")
    assert "red" in function.ui.progressBar.styleSheet()


def test_setProgressBarToValue(function):
    function.setProgressBarToValue(0)
    assert function.ui.progressBar.value() == 0


def test_setStatusTextToValue(function):
    function.setStatusTextToValue("test")
    assert function.ui.statusText.text() == "test"


def test_getFileFromUrl_1(function):
    class Response:
        headers = {}
        text = "test"
        status_code = 200

        @staticmethod
        def iter_content(_):
            return [b"s" * 512]

    function.cancel = False
    with (
        mock.patch.object(requests, "get", return_value=Response()),
        mock.patch.object(builtins, "open"),
    ):
        suc = function.getFileFromUrl(Path("http://local"), Path("tests/work/temp/test.txt"))
        assert suc


def test_getFileFromUrl_2(function):
    class Response:
        headers = {}
        text = "test"
        status_code = 200

        @staticmethod
        def iter_content(_):
            return [b"s" * 512]

    with (
        mock.patch.object(requests, "get", return_value=Response()),
        mock.patch.object(builtins, "open"),
    ):
        suc = function.getFileFromUrl(Path("http://local"), Path("tests/work/temp/test.txt"))
        assert suc


def test_getFileFromUrl_3(function):
    class Response:
        headers = {}
        text = "test"
        status_code = 500

        @staticmethod
        def iter_content(_):
            return [b"s" * 512]

    with (
        mock.patch.object(requests, "get", return_value=Response()),
        mock.patch.object(builtins, "open"),
    ):
        suc = function.getFileFromUrl(Path("http://local"), Path("tests/work/temp/test.txt"))
        assert not suc


def test_unzipFile(function):
    shutil.copy("tests/testData/test.json.gz", "tests/work/temp/test.json.gz")
    function.unzipFile(Path("tests/work/temp/test.json.gz"), Path("tests/work/temp/test.json"))
    assert os.path.isfile("tests/work/temp/test.json")


def test_downloadFileWorker_2(function):
    shutil.copy("tests/testData/visual.txt", "tests/work/temp/test.txt")
    with mock.patch.object(function, "getFileFromUrl", return_value=False):
        suc = function.downloadFileWorker(url=Path(), dest=Path("tests/work/temp/test.txt"))
        assert not suc


def test_downloadFileWorker_3(function):
    with mock.patch.object(
        function, "getFileFromUrl", return_value=True, side_effect=TimeoutError
    ):
        suc = function.downloadFileWorker(url=Path(), dest=Path("tests/work/temp/test.txt"))
        assert not suc


def test_downloadFileWorker_4(function):
    with mock.patch.object(
        function, "getFileFromUrl", return_value=True, side_effect=Exception
    ):
        suc = function.downloadFileWorker(url=Path(), dest=Path("tests/work/temp/test.txt"))
        assert not suc


def test_downloadFileWorker_5(function):
    with mock.patch.object(function, "getFileFromUrl", return_value=True):
        suc = function.downloadFileWorker(
            url=Path(), dest=Path("tests/work/temp/test.txt"), unzip=True
        )
        assert not suc


def test_downloadFileWorker_6(function):
    with mock.patch.object(
        function,
        "getFileFromUrl",
        return_value=True,
    ):
        suc = function.downloadFileWorker(
            url=Path(), dest=Path("tests/work/temp/test.txt"), unzip=False
        )
        assert suc


def test_downloadFileWorker_7(function):
    with (
        mock.patch.object(function, "getFileFromUrl", return_value=True),
        mock.patch.object(function, "unzipFile", side_effect=Exception),
    ):
        suc = function.downloadFileWorker(
            url=Path(), dest=Path("tests/work/temp/test.txt"), unzip=True
        )
        assert not suc


def test_downloadFileWorker_8(function):
    with (
        mock.patch.object(function, "getFileFromUrl", return_value=True),
        mock.patch.object(function, "unzipFile"),
    ):
        suc = function.downloadFileWorker(
            url=Path(), dest=Path("tests/work/temp/test.txt"), unzip=True
        )
        assert suc


def test_downloadFileWorker_9(function):
    with (
        mock.patch.object(function, "getFileFromUrl", return_value=False),
        mock.patch.object(function, "unzipFile"),
    ):
        suc = function.downloadFileWorker(url=Path(), dest=Path("tests/work/temp/test.txt"))
        assert not suc


def test_closePopup_1(function, mockedSleep):
    with mock.patch.object(function, "close"):
        function.closePopup(True)


def test_closePopup_2(function, mockedSleep):
    with mock.patch.object(function, "close"):
        function.closePopup(False)


def test_exec_1(function):
    with (
        mock.patch.object(function, "showWindow"),
        mock.patch.object(function.threadPool, "start"),
        mock.patch("mw4.gui.extWindows.downloadPopupW.QEventLoop") as mock_loop_cls,
    ):
        mock_loop = mock.MagicMock(spec=QEventLoop)
        mock_loop_cls.return_value = mock_loop
        function.returnValues["success"] = True
        result = function.exec()
        assert result
        mock_loop.exec.assert_called_once()


def test_exec_2(function):
    with (
        mock.patch.object(function, "showWindow"),
        mock.patch.object(function.threadPool, "start"),
        mock.patch("mw4.gui.extWindows.downloadPopupW.QEventLoop") as mock_loop_cls,
    ):
        mock_loop = mock.MagicMock(spec=QEventLoop)
        mock_loop_cls.return_value = mock_loop
        function.returnValues["success"] = False
        result = function.exec()
        assert not result
        mock_loop.exec.assert_called_once()


def test_download_1(function):
    with mock.patch.object(DownloadPopup, "exec", return_value=True):
        result = DownloadPopup.download(function.parentWidget, Path(), Path())
        assert result


def test_download_2(function):
    with mock.patch.object(DownloadPopup, "exec", return_value=False):
        result = DownloadPopup.download(function.parentWidget, Path(), Path())
        assert not result
