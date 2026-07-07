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
import os
import pytest
from mw4.gui.utilities.qtHelpers import (
    addAlpha,
    changeStyleDynamic,
    clickable,
    findIndexValue,
    getTabAndIndex,
    getTabIndex,
    guiSetText,
    img2pixmap,
    positionCursorInTable,
    setPixmapAlpha,
    setTabAndIndex,
    svg2icon,
    svg2pixmap,
)
from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QColor, QIcon, QPixmap
from PySide6.QtTest import QTest
from PySide6.QtWidgets import (
    QComboBox,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QWidget,
)
from skyfield.api import Angle


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    yield


def test_changeStyleDynamic_1():
    changeStyleDynamic(QLineEdit(), "color", "red")


def test_changeStyleDynamic_2():
    butt = QLineEdit()
    changeStyleDynamic(butt, "color", "red")
    changeStyleDynamic(butt, "color", "red")


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


def test_guiSetText_1():
    pb = QLineEdit()
    guiSetText(pb, "3.0f", None)
    assert pb.text() == ""


def test_guiSetText_4():
    pb = QLineEdit()
    guiSetText(pb, "3.0f", 100)
    assert pb.text() == "100"


def test_guiSetText_5():
    pb = QLineEdit()
    guiSetText(pb, "HSTR", Angle(hours=10))
    assert pb.text() == "10:00:00"


def test_guiSetText_6():
    pb = QLineEdit()
    guiSetText(pb, "DSTR", Angle(degrees=90))
    assert pb.text() == "+90:00:00"


def test_guiSetText_7():
    pb = QLineEdit()
    guiSetText(pb, "H2.2f", Angle(hours=12))
    assert pb.text() == "12.00"


def test_guiSetText_8():
    pb = QLineEdit()
    guiSetText(pb, "D+2.2f", Angle(degrees=90))
    assert pb.text() == "+90.00"


def test_guiSetText_9():
    pb = QLineEdit()
    guiSetText(pb, "s", "E")
    assert pb.text() == "EAST"


def test_guiSetText_10():
    pb = QLineEdit()
    guiSetText(pb, "s", "W")
    assert pb.text() == "WEST"


def test_guiSetText_11():
    pb = QLineEdit()
    guiSetText(pb, "s", True)
    assert pb.text() == "ON"


def test_guiSetText_12():
    pb = QLineEdit()
    guiSetText(pb, "s", False)
    assert pb.text() == "OFF"


def test_clickable_2():
    widget = QLineEdit()
    clickable(widget=widget)


def test_clickable_3():
    widget = QLineEdit()
    clickable(widget=widget)
    QTest.mouseRelease(widget, Qt.MouseButton.LeftButton)


def test_clickable_4():
    widget = QLineEdit()
    clickable(widget=widget)
    QTest.mouseRelease(widget, Qt.MouseButton.LeftButton, pos=QPoint(0, 0))


def test_clickable_5():
    widget = QLineEdit()
    clickable(widget=widget)
    QTest.mouseMove(widget, pos=QPoint(0, 0))


def test_img2pixmap_1(function):
    img = img2pixmap(os.getcwd() + "/tests/testData/altitude.png")
    assert isinstance(img, QPixmap)


def test_img2pixmap_2(function):
    img = img2pixmap(os.getcwd() + "/tests/testData/altitude.png")
    assert isinstance(img, QPixmap)


def test_svg2pixmap(function):
    img = svg2pixmap(os.getcwd() + "/tests/testData/choose.svg")
    assert isinstance(img, QPixmap)


def test_svg2icon_1(function):
    val = svg2icon(os.getcwd() + "/tests/testData/choose.svg")
    assert isinstance(val, QIcon)


def test_getTabAndIndex(function):
    widget = QTabWidget()
    w = QWidget()
    w.setObjectName("test")
    widget.addTab(w, "test")
    w = QWidget()
    w.setObjectName("test1")
    widget.addTab(w, "test1")

    config = {"test": 1}
    getTabAndIndex(widget, config, "test1")


def test_getTabIndex(function):
    widget = QTabWidget()
    w = QWidget()
    w.setObjectName("test")
    widget.addTab(w, "test")
    w = QWidget()
    w.setObjectName("test1")
    widget.addTab(w, "test1")
    index = getTabIndex(widget, "test1")
    assert index == 1


def test_setTabAndIndex_1(function):
    widget = QTabWidget()
    config = {"test": 0}
    setTabAndIndex(widget, config, "test")


def test_setTabAndIndex_2(function):
    widget = QTabWidget()
    widget.addTab(QWidget(), "test")
    widget.addTab(QWidget(), "tes1")
    config = {"test": {"00": "test", "01": None}}
    setTabAndIndex(widget, config, "test")


def test_positionCursorInTable_1(function):
    widget = QTableWidget()
    widget.setColumnCount(2)
    widget.setRowCount(2)
    widget.setItem(0, 0, QTableWidgetItem("test"))
    widget.setItem(1, 0, QTableWidgetItem("test1"))
    widget.setItem(0, 1, QTableWidgetItem("test2"))
    widget.setItem(1, 1, QTableWidgetItem("test3"))
    positionCursorInTable(widget, "test")
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
    positionCursorInTable(widget, "asdf")
    assert widget.currentRow() == -1
    assert widget.currentColumn() == -1


def test_addAlpha_1():
    color = addAlpha("red")
    assert isinstance(color, QColor)
    assert color.alphaF() == pytest.approx(0.5, abs=1e-5)


def test_addAlpha_2():
    color = addAlpha("#FF0000")
    assert isinstance(color, QColor)
    assert color.alphaF() == pytest.approx(0.5, abs=1e-5)


def test_addAlpha_3():
    color = addAlpha("blue")
    assert isinstance(color, QColor)
    assert color.alphaF() == pytest.approx(0.5, abs=1e-5)


def test_addAlpha_4():
    original = QColor("green")
    original.setAlphaF(1.0)
    color = addAlpha("green")
    assert isinstance(color, QColor)
    assert color.alphaF() == pytest.approx(0.5, abs=1e-5)


def test_addAlpha_5():
    original = QColor("rgba(255, 255, 0, 1.0)")
    original_alpha = original.alphaF()
    color = addAlpha("rgba(255, 255, 0, 1.0)")
    assert isinstance(color, QColor)
    assert color.alphaF() == pytest.approx(original_alpha * 0.5, abs=1e-5)


def test_setPixmapAlpha_1():
    pixmap = QPixmap(100, 100)
    pixmap.fill(QColor("red"))
    result = setPixmapAlpha(pixmap, 0.5)
    assert isinstance(result, QPixmap)
    assert result.width() == 100
    assert result.height() == 100


def test_setPixmapAlpha_2():
    pixmap = QPixmap(50, 75)
    pixmap.fill(QColor("blue"))
    result = setPixmapAlpha(pixmap, 0.75)
    assert isinstance(result, QPixmap)
    assert result.width() == 50
    assert result.height() == 75


def test_setPixmapAlpha_3():
    pixmap = QPixmap(100, 100)
    pixmap.fill(QColor("green"))
    result = setPixmapAlpha(pixmap, 0.0)
    assert isinstance(result, QPixmap)
    assert result.width() == 100
    assert result.height() == 100


def test_setPixmapAlpha_4():
    pixmap = QPixmap(100, 100)
    pixmap.fill(QColor("yellow"))
    result = setPixmapAlpha(pixmap, 1.0)
    assert isinstance(result, QPixmap)
    assert result.width() == 100
    assert result.height() == 100


def test_setPixmapAlpha_5():
    pixmap = QPixmap(200, 150)
    pixmap.fill(QColor("black"))
    result = setPixmapAlpha(pixmap, 0.5)
    assert isinstance(result, QPixmap)
    assert result.size() == pixmap.size()

