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
# GUI with PyQT5 for python
#
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock

# external packages
import pytest
import astropy
import PySide6
from PySide6.QtCore import QEvent, QPointF, Qt
from PySide6.QtGui import QMouseEvent
from PySide6 import QtWidgets

# local import
from loader import MyApp


@pytest.fixture(scope="module")
def qapp():
    myapp = MyApp([])
    yield myapp
    myapp.shutdown()
    del myapp


def test_handleButtons_1(qapp):
    ui = QtWidgets.QTabBar()
    val = qapp.handleButtons(obj=ui, returnValue=10)
    assert val == 10


def test_handleButtons_2(qapp):
    ui = QtWidgets.QComboBox()
    val = qapp.handleButtons(obj=ui, returnValue=10)
    assert val == 10


def test_handleButtons_3(qapp):
    ui = QtWidgets.QPushButton()
    val = qapp.handleButtons(obj=ui, returnValue=10)
    assert val == 10


def test_handleButtons_3b(qapp):
    ui = QtWidgets.QPushButton()
    ui.setObjectName('test')
    val = qapp.handleButtons(obj=ui, returnValue=10)
    assert val == 10


def test_handleButtons_4(qapp):
    ui = QtWidgets.QRadioButton()
    val = qapp.handleButtons(obj=ui, returnValue=10)
    assert val == 10


def test_handleButtons_5(qapp):
    ui = QtWidgets.QGroupBox()
    val = qapp.handleButtons(obj=ui, returnValue=10)
    assert val == 10


def test_handleButtons_6(qapp):
    ui = QtWidgets.QCheckBox()
    val = qapp.handleButtons(obj=ui, returnValue=10)
    assert val == 10


def test_handleButtons_7(qapp):
    ui = QtWidgets.QLineEdit()
    val = qapp.handleButtons(obj=ui, returnValue=10)
    assert val == 10


def test_handleButtons_8(qapp):
    ui = QtWidgets.QLCDNumber()
    val = qapp.handleButtons(obj=ui, returnValue=10)
    assert val == 10


def test_handleButtons_8a(qapp):
    ui = QtWidgets.QLCDNumber()
    ui.setObjectName('qt_scrollarea_viewport')
    val = qapp.handleButtons(obj=ui, returnValue=10)
    assert val == 10


def test_handleButtons_8b(qapp):
    ui = QtWidgets.QLCDNumber()
    ui.setObjectName('test')
    val = qapp.handleButtons(obj=ui, returnValue=10)
    assert val == 10


def test_handleButtons_9(qapp):
    ui = QtWidgets.QLineEdit()
    qapp.last = ui
    val = qapp.handleButtons(obj=ui, returnValue=10)
    assert val == 10


def test_handleButtons_10(qapp):
    ui = QtWidgets.QLineEdit()
    ui.setObjectName('MainWindowWindow')
    val = qapp.handleButtons(obj=ui, returnValue=10)
    assert val == 10


def test_notify_1(qapp):
    ui = QtWidgets.QLineEdit()
    event = QEvent(QEvent.Type.ToolTipChange)
    suc = qapp.notify(obj=ui, event=event)
    assert not suc


def test_notify_2(qapp):
    ui = QtWidgets.QLineEdit()
    event = QEvent(QEvent.Type.MouseButtonPress)
    with mock.patch.object(MyApp,
                           'notify',
                           return_value=True,
                           side_effect=Exception()):
        suc = qapp.notify(obj=ui, event=event)
        assert not suc


def test_notify_3(qapp):
    ui = QtWidgets.QLineEdit()
    event = QMouseEvent(QEvent.Type.MouseButtonRelease,
                        QPointF(100, 100),
                        Qt.MouseButton.NoButton,
                        Qt.MouseButton.NoButton,
                        Qt.KeyboardModifier.NoModifier,
                        )
    with mock.patch.object(MyApp,
                           'notify',
                           return_value=True):
        suc = qapp.notify(obj=ui, event=event)
        assert suc


def test_notify_4(qapp):
    ui = QtWidgets.QLineEdit()
    event = QMouseEvent(QEvent.Type.MouseButtonRelease,
                        QPointF(100, 100),
                        Qt.MouseButton.LeftButton,
                        Qt.MouseButton.LeftButton,
                        Qt.KeyboardModifier.NoModifier,
                        )
    with mock.patch.object(MyApp,
                           'notify',
                           return_value=True):
        with mock.patch.object(qapp,
                               'handleButtons',
                               return_value=True):
            suc = qapp.notify(obj=ui, event=event)
            assert suc


def test_notify_5(qapp):
    ui = QtWidgets.QLineEdit()
    event = QMouseEvent(QEvent.Type.MouseButtonPress,
                        QPointF(100, 100),
                        Qt.MouseButton.LeftButton,
                        Qt.MouseButton.LeftButton,
                        Qt.KeyboardModifier.NoModifier,
                        )
    with mock.patch.object(MyApp,
                           'notify',
                           return_value=True):
        with mock.patch.object(qapp,
                               'handleButtons',
                               return_value=True):
            suc = qapp.notify(obj=ui, event=event)
            assert suc
