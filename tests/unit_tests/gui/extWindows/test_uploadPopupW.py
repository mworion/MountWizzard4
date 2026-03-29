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
import builtins
import pytest
import requests
import unittest.mock as mock
from mw4.gui.extWindows.uploadPopupW import UploadPopup
from mw4.gui.utilities.toolsQtWidget import MWidget
from pathlib import Path
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="function")
def function(qapp):
    widget = MWidget()
    widget.app = App()
    window = UploadPopup(widget, "", "", Path())
    yield window
    window.threadPool.waitForDone(10000)


@pytest.fixture
def mocked_sleepAndEvents(monkeypatch, function):
    def test(a):
        function.pollStatusRunState = False

    monkeypatch.setattr("mw4.gui.extWindows.uploadPopupW.sleepAndEvents", test)


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


def test_prepareFiles_1(function):
    function.dataTypes = ["comet"]
    with mock.patch.object(builtins, "open"):
        val = function.prepareFiles()
        assert val


def test_prepareFiles_2(function):
    function.dataTypes = ["test"]
    with mock.patch.object(builtins, "open"):
        val = function.prepareFiles()
        assert not val

def test_generateURL(function):
    val = function.generateURL()
    assert "http://" in val
    assert "/bin/upload" in val


def test_deleteHostData_1(function):
    class Test:
        status_code = 200

    with mock.patch.object(requests, "delete", return_value=Test()):
        val = function.deleteHostData()
        assert val


def test_deleteHostData_2(function):
    class Test:
        status_code = 400

    with mock.patch.object(requests, "delete", return_value=Test()):
        val = function.deleteHostData()
        assert not val


def test_postHostData_1(function):
    class Test:
        status_code = 202

    with mock.patch.object(requests, "post", return_value=Test()):
        val = function.postHostData({})
        assert val


def test_postHostData_2(function):
    class Test:
        status_code = 400

    with mock.patch.object(requests, "post", return_value=Test()):
        val = function.postHostData({})
        assert not val


def test_uploadFileWorker_1(function):
    function.dataTypes = ["test"]
    with mock.patch.object(function, "deleteHostData"):
        with mock.patch.object(function, "prepareFiles"):
            with mock.patch.object(function.threadPool, "start"):
                with mock.patch.object(function, "postHostData"):
                    function.uploadFileWorker()


def test_sendProgressValue(function):
    function.sendProgressValue("12")


def test_pollDispatcherHelper(function):
    text = "Processing"
    function.pollDispatcherHelper(text)
    assert not function.pollStatusRunState


def test_pollDispatcher_0(function):
    text = [""]
    function.pollDispatcher(text)


def test_pollDispatcher_1(function):
    text = ["Uploading"]
    function.pollDispatcher(text)


def test_pollDispatcher_2(function):
    text = ["Processing"]
    function.pollDispatcher(text)


def test_pollDispatcher_3(function):
    text = ["Processing", "elements file."]
    with mock.patch.object(function, "sendProgressValue"):
        function.pollDispatcher(text)
        assert not function.returnValues["successMount"]


def test_pollDispatcher_4(function):
    text = ["Processing", "file failed"]
    with mock.patch.object(function, "sendProgressValue"):
        function.pollDispatcher(text)
        assert not function.returnValues["successMount"]


def test_pollDispatcher_5(function):
    text = ["Processing", "elements saved."]
    with mock.patch.object(function, "sendProgressValue"):
        function.pollDispatcher(text)
        assert function.returnValues["successMount"]
        assert function.returnValues["success"]
        assert not function.pollStatusRunState


def test_pollDispatcher_6(function):
    text = ["Processing", "data updated."]
    with mock.patch.object(function, "sendProgressValue"):
        function.pollDispatcher(text)
        assert function.returnValues["successMount"]
        assert function.returnValues["success"]
        assert not function.pollStatusRunState


def test_pollDispatcher_7(function):
    text = ["Processing", "90"]
    with mock.patch.object(function, "sendProgressValue"):
        function.pollDispatcher(text)


def test_pollDispatcher_8(function):
    text = ["test"]
    function.pollDispatcher(text)


def test_pollStatus_1(function):
    function.pollStatusRunState = False
    function.pollStatus()


def test_pollStatus_2(function):
    class Test:
        status_code = 202
        text = "test"

    function.pollStatusRunState = True
    with mock.patch.object(requests, "get", return_value=Test()):
        function.pollStatus()
        assert not function.pollStatusRunState
        assert not function.returnValues["successMount"]
        assert not function.returnValues["successMount"]


def test_closePopup_1(function, mocked_sleepAndEvents):
    with mock.patch.object(function, "close"):
        function.closePopup(False)


def test_closePopup_2(function, mocked_sleepAndEvents):
    function.returnValues["successMount"] = True
    function.pollStatusRunState = True
    with mock.patch.object(function, "close"):
        function.closePopup(True)


def test_closePopup_3(function, mocked_sleepAndEvents):
    function.returnValues["successMount"] = False
    function.pollStatusRunState = False
    with mock.patch.object(function, "close"):
        function.closePopup(True)


def test_uploadFile_1(function):
    function.callBack = 1
    with mock.patch.object(function.threadPool, "start"):
        function.uploadFile()


def test_uploadFile_2(function):
    function.callBack = None
    with mock.patch.object(function.threadPool, "start"):
        function.uploadFile()
