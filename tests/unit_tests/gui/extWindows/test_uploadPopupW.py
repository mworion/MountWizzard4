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
import gc
import pytest
import requests
import unittest.mock as mock
from mw4.gui.extWindows.uploadPopupW import UploadPopup
from mw4.gui.utilities.qtMain import MWidget
from pathlib import Path
from PySide6.QtCore import QEventLoop
from PySide6.QtWidgets import QApplication
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    widget = MWidget()
    widget.app = App()
    window = UploadPopup(widget, Path(), [], Path())
    yield window
    QApplication.processEvents()
    gc.collect()
    QApplication.processEvents()


@pytest.fixture
def mocked_sleepAndEvents(monkeypatch, function):
    def test(a):
        function.pollStatusRunState = False

    monkeypatch.setattr("mw4.gui.extWindows.uploadPopupW.mainThreadSleep", test)


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


def test_sendProgressValue(function):
    function.sendProgressValue("12")


def test_pollDispatcherHelper(function):
    text = "Processing"
    function.pollDispatcherHelper(text)
    assert not function.pollStatusRunState


def test_sendProgressStatus_0(function):
    text = [""]
    function.sendProgressStatus(text)


def test_sendProgressStatus_1(function):
    text = ["Uploading"]
    function.sendProgressStatus(text)


def test_sendProgressStatus_2(function):
    text = ["Processing"]
    function.sendProgressStatus(text)


def test_sendProgressStatus_3(function):
    text = ["Processing", "elements file."]
    with mock.patch.object(function, "sendProgressValue"):
        function.sendProgressStatus(text)
        assert not function.returnValues["successMount"]


def test_sendProgressStatus_4(function):
    text = ["Processing", "file failed"]
    with mock.patch.object(function, "sendProgressValue"):
        function.sendProgressStatus(text)
        assert not function.returnValues["successMount"]


def test_sendProgressStatus_5(function):
    text = ["Processing", "elements saved."]
    with mock.patch.object(function, "sendProgressValue"):
        function.sendProgressStatus(text)
        assert function.returnValues["successMount"]
        assert not function.pollStatusRunState


def test_sendProgressStatus_6(function):
    text = ["Processing", "data updated."]
    with mock.patch.object(function, "sendProgressValue"):
        function.sendProgressStatus(text)
        assert function.returnValues["successMount"]
        assert not function.pollStatusRunState


def test_sendProgressStatus_7(function):
    text = ["Processing", "90"]
    with mock.patch.object(function, "sendProgressValue"):
        function.sendProgressStatus(text)


def test_sendProgressStatus_8(function):
    text = ["test"]
    function.sendProgressStatus(text)


def test_generateURLStatus_1(function):
    val = function.generateURLStatus()
    assert "http://" in val
    assert "/bin/uploadst" in val


def test_getStatus_1(function):
    class Test:
        status_code = 202
        text = "test"

    function.pollStatusRunState = True
    with mock.patch.object(requests, "get", return_value=Test()):
        function.getStatus()
        assert not function.pollStatusRunState
        assert not function.returnValues["successMount"]


def test_getStatus_2(function):
    class Test:
        status_code = 200
        text = "test"

    function.pollStatusRunState = True
    with mock.patch.object(requests, "get", return_value=Test()):
        function.getStatus()
        assert function.pollStatusRunState
        assert function.returnValues["successMount"]


def test_pollStatus_1(function):
    def getStatus():
        function.pollStatusRunState = False

    function.pollStatusRunState = True
    temp = function.getStatus
    function.getStatus = getStatus

    with mock.patch.object(function, "sendProgressStatus"):
        function.pollStatus()

    function.getStatus = temp


def test_prepareFiles_1(function):
    function.dataTypes = ["comet"]
    with mock.patch("builtins.open", mock.mock_open(read_data=b"")):
        val = function.prepareFiles()
        assert val


def test_prepareFiles_2(function):
    function.dataTypes = ["test"]
    with mock.patch("builtins.open", mock.mock_open(read_data=b"")):
        val = function.prepareFiles()
        assert not val


def test_generateURL(function):
    val = function.generateURL()
    assert "http://" in val
    assert "/bin/upload" in val


def test_deleteHostData_1(function):
    class Test:
        status_code = 200

    with mock.patch.object(requests, "delete", return_value=Test()) as m:
        val = function.deleteHostData()
        assert val
        _, kwargs = m.call_args
        assert kwargs.get("timeout") == 10  # SEC-4


def test_deleteHostData_2(function):
    class Test:
        status_code = 400

    with mock.patch.object(requests, "delete", return_value=Test()) as m:
        val = function.deleteHostData()
        assert not val
        _, kwargs = m.call_args
        assert kwargs.get("timeout") == 10  # SEC-4


def test_postHostData_1(function):
    class Test:
        status_code = 202

    with mock.patch.object(requests, "post", return_value=Test()) as m:
        val = function.postHostData({})
        assert val
        _, kwargs = m.call_args
        assert kwargs.get("timeout") == 10  # SEC-4


def test_postHostData_2(function):
    class Test:
        status_code = 400

    with mock.patch.object(requests, "post", return_value=Test()) as m:
        val = function.postHostData({})
        assert not val
        _, kwargs = m.call_args
        assert kwargs.get("timeout") == 10  # SEC-4


def test_uploadFileWorker_1(function):
    with (
        mock.patch.object(function, "deleteHostData", return_value=False),
        mock.patch.object(function, "prepareFiles"),
        mock.patch.object(function.threadPool, "start"),
        mock.patch.object(function, "postHostData"),
    ):
        assert not function.uploadFileWorker()


def test_uploadFileWorker_2(function):
    with (
        mock.patch.object(function, "deleteHostData", return_value=True),
        mock.patch.object(function, "prepareFiles"),
        mock.patch.object(function.threadPool, "start"),
        mock.patch.object(function, "postHostData", return_value=False),
    ):
        assert not function.uploadFileWorker()


def test_uploadFileWorker_3(function):
    with (
        mock.patch.object(function, "deleteHostData", return_value=True),
        mock.patch.object(function, "prepareFiles"),
        mock.patch.object(function.threadPool, "start"),
        mock.patch.object(function, "postHostData", return_value=True),
    ):
        assert function.uploadFileWorker()


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


def test_exec_1(function):
    with (
        mock.patch.object(function, "showWindow"),
        mock.patch.object(function.threadPool, "start"),
        mock.patch("mw4.gui.extWindows.uploadPopupW.QEventLoop") as mock_loop_cls,
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
        mock.patch("mw4.gui.extWindows.uploadPopupW.QEventLoop") as mock_loop_cls,
    ):
        mock_loop = mock.MagicMock(spec=QEventLoop)
        mock_loop_cls.return_value = mock_loop
        function.returnValues["success"] = False
        result = function.exec()
        assert not result
        mock_loop.exec.assert_called_once()


def test_upload_1(function):
    with mock.patch.object(UploadPopup, "exec", return_value=True):
        result = UploadPopup.upload(function.parentWidget, Path(), [], Path())
        assert result


def test_upload_2(function):
    with mock.patch.object(UploadPopup, "exec", return_value=False):
        result = UploadPopup.upload(function.parentWidget, Path(), [], Path())
        assert not result
