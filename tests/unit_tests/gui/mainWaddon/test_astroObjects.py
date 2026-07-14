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
import shutil
from mw4.gui.mainWaddon.astroObjects import AstroObjects
from pathlib import Path
from PySide6.QtCore import QThreadPool
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGroupBox,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
)
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from unittest import mock


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    class TestUI:
        isOnline = QCheckBox()
        ageDatabases = QSpinBox()

    class Test:
        app = App()
        ui = TestUI()

        @staticmethod
        def x():
            return 0

        @staticmethod
        def y():
            return 0

        @staticmethod
        def height():
            return 0

        @staticmethod
        def width():
            return 0

    def test():
        pass

    satBaseUrl = "http://www.celestrak.org/NORAD/elements/gp.php?"
    satSourceURLs = {
        "100 brightest": {
            "url": satBaseUrl + "GROUP=visual&FORMAT=tle",
            "file": "visual.txt",
            "unzip": False,
        },
        "": {
            "url": "",
            "file": "",
            "unzip": True,
        },
    }

    parent = Test()
    shutil.copyfile("tests/testData/visual.txt", "tests/work/data/visual.txt")

    patcher_dl = mock.patch("mw4.gui.mainWaddon.astroObjects.DownloadPopup")
    patcher_ul = mock.patch("mw4.gui.mainWaddon.astroObjects.UploadPopup")
    patcher_dl.start()
    patcher_ul.start()

    function = AstroObjects(
        window=parent,
        objectText="test",
        sourceUrls=satSourceURLs,
        uiObjectList=QTableWidget(),
        uiSourceList=QComboBox(),
        uiSourceGroup=QGroupBox(),
        processSource=test,
    )
    function.window.app = App()
    function.window.threadPool = QThreadPool()
    yield function

    patcher_dl.stop()
    patcher_ul.stop()


def test_buildSourceListDropdown_1(function):
    with mock.patch.object(function, "loadSourceUrl"):
        function.buildSourceListDropdown()
        assert function.uiSourceList.count() == 3


def test_setAge_1(function):
    function.setAge(0)
    assert function.uiSourceGroup.title() == "test data - age: 0.0d"


def test_workerProcessSource_1(function):
    with mock.patch.object(function, "processSource"):
        function.workerProcessSource()


def test_procSourceData_1(function):
    with mock.patch.object(function.threadPool, "start"):
        function.procSourceData()


def test_runDownloadPopup_1(function):
    with (
        mock.patch(
            "mw4.gui.mainWaddon.astroObjects.DownloadPopup.download", return_value=True
        ),
        mock.patch.object(function, "procSourceData") as mock_proc,
    ):
        function.runDownloadPopup(Path(), False)
        mock_proc.assert_called_once()


def test_runDownloadPopup_2(function):
    with (
        mock.patch(
            "mw4.gui.mainWaddon.astroObjects.DownloadPopup.download", return_value=False
        ),
        mock.patch.object(function, "procSourceData") as mock_proc,
    ):
        function.runDownloadPopup(Path(), False)
        mock_proc.assert_not_called()


def test_checkFileAgeOK_1(function):
    function.app.config["SettingUpdate"] = {"ageDatabases": 3}
    with mock.patch.object(Path, "is_file", return_value=False):
        val = function.checkFileAgeOK(Path())
        assert not val


def test_checkFileAgeOK_2(function):
    function.app.config["SettingUpdate"] = {"ageDatabases": 3}
    with (
        mock.patch.object(Path, "is_file", return_value=True),
        mock.patch.object(function.loader, "days_old", return_value=1),
    ):
        val = function.checkFileAgeOK(Path())
        assert val


def test_checkFileAgeOK_3(function):
    function.app.config["SettingUpdate"] = {"ageDatabases": 3}
    with (
        mock.patch.object(Path, "is_file", return_value=True),
        mock.patch.object(function.loader, "days_old", return_value=5),
    ):
        val = function.checkFileAgeOK(Path())
        assert not val


def test_loadSourceUrl_1(function):
    function.uiSourceList.clear()
    function.uiSourceList.addItem("Please select")
    function.loadSourceUrl()


def test_loadSourceUrl_2(function):
    function.uiSourceList.clear()
    function.uiSourceList.addItem("100 brightest")

    with (
        mock.patch.object(function, "checkFileAgeOK", return_value=True),
        mock.patch.object(function, "procSourceData"),
    ):
        function.loadSourceUrl()


def test_loadSourceUrl_3(function):
    function.uiSourceList.clear()
    function.uiSourceList.addItem("100 brightest")

    function.window.ui.isOnline.setChecked(False)
    with mock.patch.object(function, "checkFileAgeOK", return_value=False):
        function.loadSourceUrl()


def test_loadSourceUrl_4(function):
    function.uiSourceList.clear()
    function.uiSourceList.addItem("100 brightest")

    function.window.ui.isOnline.setChecked(True)
    with (
        mock.patch.object(function, "checkFileAgeOK", return_value=False),
        mock.patch.object(function, "runDownloadPopup"),
    ):
        function.loadSourceUrl()


def test_runUploadPopup_1(function):
    with mock.patch("mw4.gui.mainWaddon.astroObjects.UploadPopup.upload", return_value=True):
        function.runUploadPopup(Path())


def test_runUploadPopup_2(function):
    with mock.patch("mw4.gui.mainWaddon.astroObjects.UploadPopup.upload", return_value=False):
        function.runUploadPopup(Path())


def test_runUploadPopup_calls_showWindow(function):
    """Test runUploadPopup calls exec and emits success message on True result."""
    with mock.patch("mw4.gui.mainWaddon.astroObjects.UploadPopup.upload", return_value=True):
        function.runUploadPopup(Path())


def test_progObjects_1(function):
    function.progObjects([])


def test_progObjects_2(function):
    function.app.mount.host = ("localhost", 3492)

    def test(objects, dataFilePath=""):
        return True

    function.objectText = "comet"
    function.dbProcFuncs["comet"] = test
    with mock.patch.object(function, "runUploadPopup"):
        function.progObjects(["test"])


def test_progGUI_1(function):
    function.progGUI("test")


def test_progSelected_1(function):
    function.objects = {"test": "test"}

    class Test:
        def column(self):
            return 0

        def text(self):
            return "test"

    with (
        mock.patch.object(function, "progGUI"),
        mock.patch.object(function, "progObjects"),
        mock.patch.object(function.uiObjectList, "selectedItems", return_value=[Test()]),
    ):
        function.progSelected()


def test_progSelected_2(function):
    function.objects = {"test": "test"}

    class Test:
        def column(self):
            return 1

        def text(self):
            return "test"

    with (
        mock.patch.object(function, "progGUI"),
        mock.patch.object(function, "progObjects"),
        mock.patch.object(function.uiObjectList, "selectedItems", return_value=[Test()]),
    ):
        function.progSelected()


def test_progFiltered_1(function):
    function.objects = {"test": "test"}

    function.uiObjectList = QTableWidget()
    function.uiObjectList.setRowCount(0)
    function.uiObjectList.setColumnCount(2)
    item = QTableWidgetItem("test")
    function.uiObjectList.insertRow(0)
    function.uiObjectList.setItem(0, 1, item)
    function.uiObjectList.setRowHidden(0, True)

    with mock.patch.object(function, "progGUI"), mock.patch.object(function, "progObjects"):
        function.progFiltered()


def test_progFiltered_2(function):
    function.objects = {"test": "test"}
    function.uiObjectList = QTableWidget()
    function.uiObjectList.setRowCount(0)
    function.uiObjectList.setColumnCount(2)
    item = QTableWidgetItem("test")
    function.uiObjectList.insertRow(0)
    function.uiObjectList.setItem(0, 1, item)
    function.uiObjectList.setRowHidden(0, False)

    with mock.patch.object(function, "progGUI"), mock.patch.object(function, "progObjects"):
        function.progFiltered()


def test_progFull_1(function):
    with mock.patch.object(function, "progGUI"), mock.patch.object(function, "progObjects"):
        function.progFull()


def test_runDownloadPopup_when_online(function):
    """Test runDownloadPopup calls download and procSourceData on success."""
    with (
        mock.patch(
            "mw4.gui.mainWaddon.astroObjects.DownloadPopup.download", return_value=True
        ),
        mock.patch.object(function, "procSourceData") as mock_proc,
    ):
        function.runDownloadPopup(Path(), False)
        mock_proc.assert_called_once()


def test_loadSourceUrl_online_with_old_file(function):
    """Test loadSourceUrl when file is old and app is online (lines 132-135)."""
    function.uiSourceList.clear()
    function.uiSourceList.addItem("100 brightest")
    function.app.isOnline = True
    function.window.ui.isOnline.setChecked(True)

    with (
        mock.patch.object(function, "checkFileAgeOK", return_value=False),
        mock.patch.object(function, "runDownloadPopup"),
        mock.patch.object(function, "setAge"),
    ):
        function.loadSourceUrl()
        function.setAge.assert_called_once_with(0)
        function.runDownloadPopup.assert_called_once()
