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
import unittest.mock as mock
import pytest
import os
from pathlib import Path

# external packages
from PySide6.QtWidgets import QMessageBox, QFileDialog, QWidget, QTabWidget
from PySide6.QtWidgets import QPushButton, QComboBox, QTableWidgetItem, QLineEdit
from PySide6.QtWidgets import QTableWidget
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QIcon, QPixmap, QPainterPath
from PySide6.QtTest import QTest
from skyfield.api import Angle, load
import numpy as np

# local import
from gui.utilities.toolsQtWidget import MWidget, sleepAndEvents, changeStyleDynamic
from gui.utilities.toolsQtWidget import findIndexValue, guiSetStyle
from gui.widgets.main_ui import Ui_MainWindow
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    window = MWidget()
    window.app = App()
    window.ui = Ui_MainWindow()
    window.ui.setupUi(window)
    yield window


def test_sleepAndEvents(function):
    suc = sleepAndEvents(1)
    assert suc


def test_changeStyleDynamic_1():
    changeStyleDynamic()


def test_findIndexValue_0():
    ui = QComboBox()
    ui.addItem("")
    val = findIndexValue(ui=ui, searchString="dome")
    assert val == 0


def test_findIndexValue_1():
    ui = QComboBox()
    ui.addItem("dome")
    ui.addItem("test")
    val = findIndexValue(ui=ui, searchString="dome")
    assert val == 0


def test_findIndexValue_2():
    ui = QComboBox()
    ui.addItem("dome")
    ui.addItem("indi")
    val = findIndexValue(ui=ui, searchString="indi")
    assert val == 1


def test_findIndexValue_3():
    ui = QComboBox()
    ui.addItem("dome")
    ui.addItem("test")
    ui.addItem("indi - test")
    val = findIndexValue(ui=ui, searchString="indi")
    assert val == 2


def test_findIndexValue_4():
    ui = QComboBox()
    ui.addItem("dome")
    ui.addItem("test")
    ui.addItem("indi - test")
    val = findIndexValue(ui=ui, searchString="indi", relaxed=True)
    assert val == 2


def test_findIndexValue_5():
    ui = QComboBox()
    val = findIndexValue(ui=ui, searchString="indi")
    assert val == 0


def test_guiSetStyle_1():
    pb = QPushButton()
    suc = guiSetStyle(pb)
    assert not suc


def test_guiSetStyle_2():
    pb = QPushButton()
    suc = guiSetStyle(pb, pStyle="color", value=None)
    assert suc


def test_guiSetStyle_3():
    pb = QPushButton()
    suc = guiSetStyle(pb, pStyle="color", value=True)
    assert suc


def test_guiSetStyle_4():
    pb = QPushButton()
    suc = guiSetStyle(pb, pStyle="color", value=False)
    assert suc


def test_saveWindowAsPNG(function):
    class Save:
        @staticmethod
        def save(a):
            return

    with mock.patch.object(QWidget, "grab", return_value=Save()):
        suc = function.saveWindowAsPNG(QWidget())
        assert suc


def test_saveAllWindowsAsPNG_1(function):
    function.app.uiWindows = {"test1": {"classObj": None}, "test2": {"classObj": 1}}
    function.app.mainW = QWidget()
    with mock.patch.object(function, "saveWindowAsPNG"):
        suc = function.saveAllWindowsAsPNG()
        assert suc


def test_keyPressEvent_1(function):
    class Key:
        @staticmethod
        def key():
            return 16777268

    with mock.patch.object(function, "saveWindowAsPNG"):
        function.keyPressEvent(Key())


def test_keyPressEvent_2(function):
    class Key:
        @staticmethod
        def key():
            return 16777269

    with mock.patch.object(function, "saveAllWindowsAsPNG"):
        function.keyPressEvent(Key())


def test_keyPressEvent_3(function):
    class Key:
        @staticmethod
        def key():
            return 1

    with mock.patch.object(QWidget, "keyPressEvent"):
        function.keyPressEvent(Key())


def test_img2pixmap_1(function):
    img = function.img2pixmap(os.getcwd() + "/tests/testData/altitude.png")
    assert isinstance(img, QPixmap)


def test_img2pixmap_2(function):
    img = function.img2pixmap(os.getcwd() + "/tests/testData/altitude.png", "#202020", "#303030")
    assert isinstance(img, QPixmap)


def test_svg2pixmap(function):
    img = function.svg2pixmap(os.getcwd() + "/tests/testData/choose.svg")
    assert isinstance(img, QPixmap)


def test_svg2icon_1(function):
    val = function.svg2icon(os.getcwd() + "/tests/testData/choose.svg")
    assert isinstance(val, QIcon)


def test_wIcon_1(function):
    suc = function.wIcon()
    assert not suc


def test_wIcon_2(function):
    ui = QPushButton()
    suc = function.wIcon(gui=ui)
    assert not suc


def test_wIcon_3(function):
    ui = QPushButton()
    suc = function.wIcon(gui=ui, name="load")
    assert suc


def test_renderStyle_1(function):
    inp = "12345$M_PRIM$12345"
    function.colorSet = 0
    val = function.renderStyle(inp).strip(" ")
    assert val == "12345#2090C012345\n"


def test_renderStyle_2(function):
    inp = "12345$M_TEST$12345"
    function.colorSet = 0
    val = function.renderStyle(inp).strip(" ")
    assert val == "12345$M_TEST$12345\n"


def test_initUI_1(function):
    suc = function.initUI()
    assert suc


def test_prepareFileDialog_1(function):
    suc = function.prepareFileDialog()
    assert not suc


def test_prepareFileDialog_2(function):
    window = QWidget()
    suc = function.prepareFileDialog(window=window)
    assert suc


def test_runDialog_1(function):
    dialog = QFileDialog()
    with mock.patch.object(QFileDialog, "exec", return_value=0):
        val = function.runDialog(dialog)
        assert val == 0


def test_messageDialog_1(function):
    widget = QWidget()
    with mock.patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.No):
        with mock.patch.object(QMessageBox, "show"):
            with mock.patch.object(
                function, "runDialog", return_value=QMessageBox.StandardButton.No
            ):
                suc = function.messageDialog(widget, "test", "test")
                assert not suc


def test_messageDialog_2(function):
    widget = QWidget()
    with mock.patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Yes):
        with mock.patch.object(QMessageBox, "show"):
            with mock.patch.object(
                function, "runDialog", return_value=QMessageBox.StandardButton.Yes
            ):
                suc = function.messageDialog(widget, "test", "test")
                assert suc


def test_messageDialog_3(function):
    widget = QWidget()
    with mock.patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Yes):
        with mock.patch.object(QMessageBox, "show"):
            with mock.patch.object(
                function, "runDialog", return_value=QMessageBox.StandardButton.Yes
            ):
                suc = function.messageDialog(widget, "test", "test", ["A", "B"])
                assert suc


def test_openFile_1(function):
    full = function.openFile()
    assert full == Path("")


def test_openFile_2(function):
    window = QWidget()
    full = function.openFile(window=window)
    assert full == Path("")


def test_openFile_3(function):
    window = QWidget()
    full = function.openFile(window=window, title="title")
    assert full == Path("")


def test_openFile_4(function):
    window = QWidget()
    full = function.openFile(window=window, title="title", folder=Path(".text"))
    assert full == Path("")


def test_openFile_5(function):
    window = QWidget()
    with mock.patch.object(function, "runDialog", return_value=0):
        full = function.openFile(window=window, title="title", folder=Path("."), filterSet="*.*")
        assert full == Path("")


def test_openFile_6(function):
    window = QWidget()
    with mock.patch.object(function, "runDialog", return_value=1):
        with mock.patch.object(QFileDialog, "selectedFiles", return_value=["test1", "test2"]):
            full = function.openFile(
                window=window,
                title="title",
                folder=Path("."),
                filterSet="*.*",
                multiple=True,
            )
            assert full == [Path("test1"), Path("test2")]


def test_openFile_7(function):
    window = QWidget()
    with mock.patch.object(function, "runDialog", return_value=1):
        with mock.patch.object(QFileDialog, "selectedFiles", return_value=["test1"]):
            full = function.openFile(
                window=window,
                title="title",
                folder=Path("."),
                filterSet="*.*",
                multiple=False,
            )
            assert full == Path("test1")


def test_saveFile_1(function):
    full = function.saveFile()
    assert full == Path("")


def test_saveFile_2(function):
    window = QWidget()
    full = function.saveFile(window=window)
    assert full == Path("")


def test_saveFile_3(function):
    window = QWidget()
    full = function.saveFile(window=window, title="title")
    assert full == Path("")


def test_saveFile_4(function):
    window = QWidget()
    full = function.saveFile(window=window, title="title", folder=Path("."))
    assert full == Path("")


def test_saveFile_5(function):
    window = QWidget()
    with mock.patch.object(function, "runDialog", return_value=0):
        full = function.saveFile(window=window, title="title", folder=Path("."), filterSet="*.*")
        assert full == Path("")


def test_saveFile_6(function):
    window = QWidget()
    with mock.patch.object(function, "runDialog", return_value=1):
        with mock.patch.object(QFileDialog, "selectedFiles", return_value=(["tests/test.txt"])):
            function.saveFile(window=window, title="title", folder=Path("."), filterSet="*.*")


def test_openDir_1(function):
    full = function.openDir()
    assert full == Path("")


def test_openDir_2(function):
    window = QWidget()
    full = function.openDir(window=window)
    assert full == Path("")


def test_openDir_3(function):
    window = QWidget()
    full = function.openDir(window=window, title="title")
    assert full == Path("")


def test_openDir_4(function):
    window = QWidget()
    with mock.patch.object(function, "runDialog", return_value=1):
        full = function.openDir(window=window, title="title", folder=Path("."))
        assert full == Path(os.getcwd())


def test_openDir_5(function):
    window = QWidget()
    with mock.patch.object(function, "runDialog", return_value=None):
        full = function.openDir(window=window, title="title", folder=Path("."))
        assert full == Path("")


def test_clickable_1(function):
    function.clickable()


def test_clickable_2(function):
    widget = QLineEdit()
    function.clickable(widget=widget)


def test_clickable_3(function):
    widget = QLineEdit()
    function.clickable(widget=widget)
    QTest.mouseRelease(widget, Qt.MouseButton.LeftButton)


def test_clickable_4(function):
    widget = QLineEdit()
    function.clickable(widget=widget)
    QTest.mouseRelease(widget, Qt.MouseButton.LeftButton, pos=QPoint(0, 0))


def test_clickable_5(function):
    widget = QLineEdit()
    function.clickable(widget=widget)
    QTest.mouseMove(widget, pos=QPoint(0, 0))


def test_guiSetText_1(function):
    suc = function.guiSetText(None, None)
    assert not suc


def test_guiSetText_2(function):
    pb = QPushButton()
    suc = function.guiSetText(pb, None)
    assert not suc


def test_guiSetText_3(function):
    pb = QPushButton()
    suc = function.guiSetText(pb, "3.5f")
    assert suc
    assert pb.text() == "-"


def test_guiSetText_3b(function):
    pb = QPushButton()
    suc = function.guiSetText(pb, "3.5f", [])
    assert suc


def test_guiSetText_3c(function):
    pb = QPushButton()
    suc = function.guiSetText(pb, "3.5f", np.array([]))
    assert suc


def test_guiSetText_4(function):
    pb = QPushButton()
    suc = function.guiSetText(pb, "3.0f", 100)
    assert suc
    assert pb.text() == "100"


def test_guiSetText_5(function):
    pb = QPushButton()
    suc = function.guiSetText(pb, "HSTR", Angle(hours=10))
    assert suc
    assert pb.text() == "10:00:00"


def test_guiSetText_6(function):
    pb = QPushButton()
    suc = function.guiSetText(pb, "DSTR", Angle(degrees=90))
    assert suc
    assert pb.text() == "+90:00:00"


def test_guiSetText_7(function):
    pb = QPushButton()
    suc = function.guiSetText(pb, "H2.2f", Angle(hours=12))
    assert suc
    assert pb.text() == "12.00"


def test_guiSetText_8(function):
    pb = QPushButton()
    suc = function.guiSetText(pb, "D+2.2f", Angle(degrees=90))
    assert suc
    assert pb.text() == "+90.00"


def test_guiSetText_9(function):
    pb = QPushButton()
    suc = function.guiSetText(pb, "s", "E")
    assert suc
    assert pb.text() == "EAST"


def test_guiSetText_10(function):
    pb = QPushButton()
    suc = function.guiSetText(pb, "s", "W")
    assert suc
    assert pb.text() == "WEST"


def test_guiSetText_11(function):
    pb = QPushButton()
    suc = function.guiSetText(pb, "s", True)
    assert suc
    assert pb.text() == "ON"


def test_guiSetText_12(function):
    pb = QPushButton()
    suc = function.guiSetText(pb, "s", False)
    assert suc
    assert pb.text() == "OFF"


def test_convertTime_1(function):
    ts = load.timescale()
    t = ts.tt(2000, 1, 1, 12, 0)
    function.ui.unitTimeUTC.setChecked(True)
    val = function.convertTime(t, "%H:%M")
    assert val


def test_convertTime_2(function):
    ts = load.timescale()
    t = ts.tt(2000, 1, 1, 12, 0)
    function.ui.unitTimeLocal.setChecked(True)
    val = function.convertTime(t, "%H:%M")
    assert val


def test_timeZoneString_1(function):
    function.ui.unitTimeUTC.setChecked(True)
    val = function.timeZoneString()
    assert val == "(time is UTC)"


def test_timeZoneString_2(function):
    function.ui.unitTimeLocal.setChecked(True)
    val = function.timeZoneString()
    assert val == "(time is local)"


def test_makePointer(function):
    val = function.makePointer()
    assert isinstance(val, QPainterPath)


def test_makeSat(function):
    val = function.makeSat()
    assert isinstance(val, QPainterPath)


def test_positionWindow_1(function):
    config = {"winPosX": 100, "winPosY": 100, "height": 400, "width": 600}
    function.screenSizeX = 1000
    function.screenSizeY = 1000
    suc = function.positionWindow(config)
    assert suc


def test_positionWindow_2(function):
    config = {"winPosX": 900, "winPosY": 900, "height": 400, "width": 600}
    function.screenSizeX = 1000
    function.screenSizeY = 1000
    suc = function.positionWindow(config)
    assert suc


def test_getTabAndIndex(function):
    widget = QTabWidget()
    w = QWidget()
    w.setObjectName("test")
    widget.addTab(w, "test")
    w = QWidget()
    w.setObjectName("test1")
    widget.addTab(w, "test1")

    config = {"test": 1}
    function.getTabAndIndex(widget, config, "test1")
    print(config)


def test_getTabIndex(function):
    widget = QTabWidget()
    w = QWidget()
    w.setObjectName("test")
    widget.addTab(w, "test")
    w = QWidget()
    w.setObjectName("test1")
    widget.addTab(w, "test1")
    index = function.getTabIndex(widget, "test1")
    assert index == 1


def test_setTabAndIndex_1(function):
    widget = QTabWidget()
    config = {"test": 0}
    function.setTabAndIndex(widget, config, "test")


def test_setTabAndIndex_2(function):
    widget = QTabWidget()
    widget.addTab(QWidget(), "test")
    widget.addTab(QWidget(), "tes1")
    config = {"test": {"00": "test"}}
    function.setTabAndIndex(widget, config, "test")


def test_positionCursorInTable_1(function):
    widget = QTableWidget()
    widget.setColumnCount(2)
    widget.setRowCount(2)
    widget.setItem(0, 0, QTableWidgetItem("test"))
    widget.setItem(1, 0, QTableWidgetItem("test1"))
    widget.setItem(0, 1, QTableWidgetItem("test2"))
    widget.setItem(1, 1, QTableWidgetItem("test3"))
    function.positionCursorInTable(widget, "test")
    assert widget.currentRow() == 0
    assert widget.currentColumn() == 0


def test_positionCursorInTable_2(function):
    widget = QTableWidget()
    widget.setColumnCount(2)
    widget.setRowCount(2)
    widget.setItem(0, 0, QTableWidgetItem("test"))
    widget.setItem(1, 0, QTableWidgetItem("test1"))
    widget.setItem(0, 1, QTableWidgetItem("test2"))
    widget.setItem(1, 1, QTableWidgetItem("test3"))
    function.positionCursorInTable(widget, "asdf")
    assert widget.currentRow() == -1
    assert widget.currentColumn() == -1
