############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock

# external packages
import pytest

# local import
from loader import MyApp
from PySide6 import QtWidgets
from PySide6.QtCore import QEvent, QPointF, Qt
from PySide6.QtGui import QMouseEvent


@pytest.fixture(scope="module", autouse=True)
def qapp():
    myapp = MyApp([])
    yield myapp
    myapp.shutdown()
    del myapp


def test_logUserInterface_1(qapp):
    ui = QtWidgets.QTabBar()
    qapp.logUserInterface(obj=ui)


def test_logUserInterface_2(qapp):
    ui = QtWidgets.QComboBox()
    qapp.logUserInterface(obj=ui)


def test_logUserInterface_3(qapp):
    ui = QtWidgets.QPushButton()
    qapp.logUserInterface(obj=ui)


def test_logUserInterface_3b(qapp):
    ui = QtWidgets.QPushButton()
    ui.setObjectName("test")
    qapp.logUserInterface(obj=ui)


def test_logUserInterface_4(qapp):
    ui = QtWidgets.QRadioButton()
    qapp.logUserInterface(obj=ui)


def test_logUserInterface_5(qapp):
    ui = QtWidgets.QGroupBox()
    qapp.logUserInterface(obj=ui)


def test_logUserInterface_6(qapp):
    ui = QtWidgets.QCheckBox()
    qapp.logUserInterface(obj=ui)


def test_logUserInterface_7(qapp):
    ui = QtWidgets.QLineEdit()
    qapp.logUserInterface(obj=ui)


def test_logUserInterface_8(qapp):
    ui = QtWidgets.QLCDNumber()
    qapp.logUserInterface(obj=ui)


def test_logUserInterface_8a(qapp):
    ui = QtWidgets.QLCDNumber()
    ui.setObjectName("qt_scrollarea_viewport")
    qapp.logUserInterface(obj=ui)


def test_logUserInterface_8b(qapp):
    ui = QtWidgets.QLCDNumber()
    ui.setObjectName("test")
    qapp.logUserInterface(obj=ui)


def test_logUserInterface_9(qapp):
    ui = QtWidgets.QLineEdit()
    qapp.last = ui
    qapp.logUserInterface(obj=ui)


def test_handleButtons_1(qapp):
    ui = QtWidgets.QLineEdit()
    ui.setObjectName("Test")
    retValue = qapp.handleButtons(obj=ui, returnValue=True)
    assert retValue


def test_notify_1(qapp):
    ui = QtWidgets.QPushButton()
    event = QEvent(QEvent.Type.ToolTipChange)
    suc = qapp.notify(obj=ui, event=event)
    assert not suc


def test_notify_3(qapp):
    ui = QtWidgets.QPushButton()
    event = QMouseEvent(
        QEvent.Type.MouseButtonRelease,
        QPointF(100, 100),
        Qt.MouseButton.NoButton,
        Qt.MouseButton.NoButton,
        Qt.KeyboardModifier.NoModifier,
    )
    with mock.patch.object(QtWidgets.QApplication, "notify", return_value=True):
        suc = qapp.notify(obj=ui, event=event)
        assert suc


def test_notify_4(qapp):
    ui = QtWidgets.QPushButton()
    event = QMouseEvent(
        QEvent.Type.MouseButtonRelease,
        QPointF(100, 100),
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
    )
    with mock.patch.object(QtWidgets.QApplication, "notify", return_value=True):
        with mock.patch.object(qapp, "handleButtons", return_value=True):
            suc = qapp.notify(obj=ui, event=event)
            assert suc


def test_notify_5(qapp):
    ui = QtWidgets.QPushButton()
    event = QMouseEvent(
        QEvent.Type.MouseButtonPress,
        QPointF(100, 100),
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
    )
    with mock.patch.object(QtWidgets.QApplication, "notify", return_value=True):
        with mock.patch.object(qapp, "handleButtons", return_value=True):
            suc = qapp.notify(obj=ui, event=event)
            assert suc
