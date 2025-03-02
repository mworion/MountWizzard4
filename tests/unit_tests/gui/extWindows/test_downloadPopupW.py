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
# GUI with PySide for python
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock
import pytest
import os
import shutil
import builtins

# external packages
from PySide6.QtWidgets import QWidget
import requests

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.extWindows.downloadPopupW import DownloadPopup


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    widget = QWidget()
    widget.app = App()
    with mock.patch.object(DownloadPopup, "show"):
        with mock.patch.object(DownloadPopup, "downloadFile"):
            window = DownloadPopup(parentWidget=widget, url="", dest="")
        yield window


@pytest.fixture
def mocked_sleepAndEvents(monkeypatch, function):
    def test(a):
        function.pollStatusRunState = False

    monkeypatch.setattr("gui.extWindows.downloadPopupW.sleepAndEvents", test)


def set_setIcon(function):
    function.setIcon()


def set_setProgressBarColor(function):
    function.setProgressBarColor("red")


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
        def iter_content(a):
            return [b"s" * 512]

    function.cancel = False
    with mock.patch.object(requests, "get", return_value=Response()):
        with mock.patch.object(builtins, "open"):
            suc = function.getFileFromUrl("http://local", "tests/work/temp/test.txt")
            assert suc


def test_getFileFromUrl_2(function):
    class Response:
        headers = {}
        text = "test"
        status_code = 200

        @staticmethod
        def iter_content(a):
            return [b"s" * 512]

    with mock.patch.object(requests, "get", return_value=Response()):
        with mock.patch.object(builtins, "open"):
            suc = function.getFileFromUrl("http://local", "tests/work/temp/test.txt")
            assert suc


def test_getFileFromUrl_3(function):
    class Response:
        headers = {}
        text = "test"
        status_code = 500

        @staticmethod
        def iter_content(a):
            return [b"s" * 512]

    with mock.patch.object(requests, "get", return_value=Response()):
        with mock.patch.object(builtins, "open"):
            suc = function.getFileFromUrl("http://local", "tests/work/temp/test.txt")
            assert not suc


def test_unzipFile(function):
    shutil.copy("tests/testData/test.json.gz", "tests/work/temp/test.json.gz")
    function.unzipFile("tests/work/temp/test.json.gz", "tests/work/temp/test.json")
    assert os.path.isfile("tests/work/temp/test.json")


def test_downloadFileWorker_2(function):
    shutil.copy("tests/testData/visual.txt", "tests/work/temp/test.txt")
    with mock.patch.object(function, "getFileFromUrl", return_value=False):
        suc = function.downloadFileWorker(url="", dest="tests/work/temp/test.txt")
        assert not suc


def test_downloadFileWorker_3(function):
    with mock.patch.object(
        function, "getFileFromUrl", return_value=True, side_effect=TimeoutError
    ):
        suc = function.downloadFileWorker(url="", dest="test/workDir/temp/test.txt")
        assert not suc


def test_downloadFileWorker_4(function):
    with mock.patch.object(
        function, "getFileFromUrl", return_value=True, side_effect=Exception
    ):
        suc = function.downloadFileWorker(url="", dest="test/workDir/temp/test.txt")
        assert not suc


def test_downloadFileWorker_5(function):
    with mock.patch.object(function, "getFileFromUrl", return_value=True):
        suc = function.downloadFileWorker(
            url="", dest="test/workDir/temp/test.txt", unzip=True
        )
        assert not suc


def test_downloadFileWorker_6(function):
    with mock.patch.object(
        function,
        "getFileFromUrl",
        return_value=True,
    ):
        suc = function.downloadFileWorker(
            url="", dest="test/workDir/temp/test.txt", unzip=False
        )
        assert suc


def test_downloadFileWorker_7(function):
    with mock.patch.object(
        function,
        "getFileFromUrl",
        return_value=True,
    ):
        with mock.patch.object(function, "unzipFile", side_effect=Exception):
            suc = function.downloadFileWorker(
                url="", dest="test/workDir/temp/test.txt", unzip=True
            )
            assert not suc


def test_downloadFileWorker_8(function):
    with mock.patch.object(
        function,
        "getFileFromUrl",
        return_value=True,
    ):
        with mock.patch.object(function, "unzipFile"):
            suc = function.downloadFileWorker(
                url="", dest="test/workDir/temp/test.txt", unzip=True
            )
            assert suc


def test_downloadFileWorker_9(function, mocked_sleepAndEvents):
    with mock.patch.object(
        function,
        "getFileFromUrl",
        return_value=False,
    ):
        with mock.patch.object(function, "unzipFile"):
            suc = function.downloadFileWorker(url="", dest="test/workDir/temp/test.txt")
            assert not suc


def test_closePopup_1(function, mocked_sleepAndEvents):
    function.pollStatusRunState = True
    with mock.patch.object(function, "close"):
        function.closePopup(True)


def test_closePopup_2(function, mocked_sleepAndEvents):
    function.pollStatusRunState = True
    with mock.patch.object(function, "close"):
        function.closePopup(False)


def test_downloadFile_1(function):
    function.callBack = 1
    with mock.patch.object(function.threadPool, "start"):
        function.downloadFile("", "")


def test_downloadFile_2(function):
    function.callBack = None
    with mock.patch.object(function.threadPool, "start"):
        function.downloadFile("", "")
