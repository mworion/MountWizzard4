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
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
from unittest import mock
from pathlib import Path

# external packages
from PySide6.QtWidgets import QWidget, QComboBox, QTableWidget, QGroupBox
from PySide6.QtWidgets import QTableWidgetItem
from PySide6.QtCore import QThreadPool

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.mainWaddon.astroObjects import AstroObjects
import gui
from gui.widgets.main_ui import Ui_MainWindow

satBaseUrl = "http://www.celestrak.org/NORAD/elements/gp.php?"
satSourceURLs = {
    "100 brightest": {
        "url": satBaseUrl + "GROUP=visual&FORMAT=tle",
        "file": "visual.txt",
        "unzip": False,
    },
}


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    def test():
        pass

    with mock.patch.object(App().mount.obsSite.loader, "days_old", return_value=0):
        parent = QWidget()
        parent.ui = Ui_MainWindow()
        parent.ui.setupUi(parent)
        parent.app = App()

        function = AstroObjects(
            window=parent,
            objectText="test",
            sourceUrls=satSourceURLs,
            uiObjectList=QTableWidget(),
            uiSourceList=QComboBox(),
            uiSourceGroup=QGroupBox(),
            prepareTable=test,
            processSource=test,
        )
        function.window.app = App()
        function.window.threadPool = QThreadPool()
        yield function


def test_buildSourceListDropdown_1(function):
    with mock.patch.object(function, "loadSourceUrl"):
        function.buildSourceListDropdown()
        assert function.uiSourceList.count() == 1


def test_setAge_1(function):
    function.setAge(0)
    assert function.uiSourceGroup.title() == "test data - age: 0.0d"


def test_procSourceData_1(function):
    class Test:
        returnValues = {"success": False}

    function.downloadPopup = Test()
    function.procSourceData(direct=False)


def test_procSourceData_2(function):
    class Test:
        returnValues = {"success": True}

    function.downloadPopup = Test()
    with mock.patch.object(function, "processSource"):
        function.procSourceData(direct=True)


def test_runDownloadPopup_1(function):
    function.window.ui.isOnline.setChecked(True)
    with mock.patch.object(gui.extWindows.downloadPopupW.DownloadPopup, "show"):
        with mock.patch.object(function.window.app.threadPool, "start"):
            function.runDownloadPopup("", False)


def test_runDownloadPopup_2(function):
    function.window.ui.isOnline.setChecked(False)
    with mock.patch.object(gui.extWindows.downloadPopupW.DownloadPopup, "show"):
        with mock.patch.object(function.window.app.threadPool, "start"):
            function.runDownloadPopup("", False)


def test_loadSourceUrl_1(function):
    function.uiSourceList.clear()

    function.loadSourceUrl()


def test_loadSourceUrl_2(function):
    function.uiSourceList.clear()
    function.uiSourceList.addItem("100 brightest")

    with mock.patch.object(Path, "is_file", return_value=True):
        with mock.patch.object(function, "procSourceData"):
            function.loadSourceUrl()


def test_loadSourceUrl_3(function):
    function.uiSourceList.clear()
    function.uiSourceList.addItem("100 brightest")

    function.window.ui.isOnline.setChecked(False)
    with mock.patch.object(Path, "is_file", return_value=False):
        with mock.patch.object(function, "runDownloadPopup"):
            function.loadSourceUrl()


def test_loadSourceUrl_4(function):
    function.uiSourceList.clear()
    function.uiSourceList.addItem("100 brightest")

    function.window.ui.isOnline.setChecked(True)
    with mock.patch.object(Path, "is_file", return_value=False):
        with mock.patch.object(function, "runDownloadPopup"):
            function.loadSourceUrl()


def test_finishProgObjects_1(function):
    class Test:
        returnValues = {"success": False}

    function.uploadPopup = Test()
    function.finishProgObjects()


def test_finishProgObjects_2(function):
    class Test:
        returnValues = {"success": True}

    function.uploadPopup = Test()
    function.finishProgObjects()


def test_runUploadPopup_1(function):
    with mock.patch.object(gui.extWindows.uploadPopupW.UploadPopup, "show"):
        with mock.patch.object(function.window.app.threadPool, "start"):
            function.runUploadPopup("")


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

    with mock.patch.object(function, "progGUI"):
        with mock.patch.object(function, "progObjects"):
            with mock.patch.object(
                function.uiObjectList, "selectedItems", return_value=[Test()]
            ):
                function.progSelected()


def test_progSelected_2(function):
    function.objects = {"test": "test"}

    class Test:
        def column(self):
            return 1

        def text(self):
            return "test"

    with mock.patch.object(function, "progGUI"):
        with mock.patch.object(function, "progObjects"):
            with mock.patch.object(
                function.uiObjectList, "selectedItems", return_value=[Test()]
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

    with mock.patch.object(function, "progGUI"):
        with mock.patch.object(function, "progObjects"):
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

    with mock.patch.object(function, "progGUI"):
        with mock.patch.object(function, "progObjects"):
            function.progFiltered()


def test_progFull_1(function):
    with mock.patch.object(function, "progGUI"):
        with mock.patch.object(function, "progObjects"):
            function.progFull()
