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
# written in python3, (c) 2019-2023 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock
import glob
import os

# external packages
import pytest
import PyQt5
from PyQt5.QtCore import QEvent, QPoint, Qt
from PyQt5.QtGui import QMouseEvent
from PyQt5 import QtWidgets

# local import
from  mw4.loader import MyApp


@pytest.fixture(scope="session")
def qapp():
    yield MyApp([])


@pytest.fixture(autouse=True, scope="function")
def setup_teardown(qapp):
    global app

    app = qapp

    files = glob.glob('tests/workDir/config/*.cfg')
    for f in files:
        os.remove(f)

    yield


def test_handleButtons_1():
    ui = QtWidgets.QTabBar()
    val = app.handleButtons(obj=ui, returnValue=10)
    assert val == 10


def test_handleButtons_2():
    ui = QtWidgets.QComboBox()
    val = app.handleButtons(obj=ui, returnValue=10)
    assert val == 10


def test_handleButtons_3():
    ui = QtWidgets.QPushButton()
    val = app.handleButtons(obj=ui, returnValue=10)
    assert val == 10


def test_handleButtons_3b():
    ui = QtWidgets.QPushButton()
    ui.setObjectName('test')
    val = app.handleButtons(obj=ui, returnValue=10)
    assert val == 10


def test_handleButtons_4():
    ui = QtWidgets.QRadioButton()
    val = app.handleButtons(obj=ui, returnValue=10)
    assert val == 10


def test_handleButtons_5():
    ui = QtWidgets.QGroupBox()
    val = app.handleButtons(obj=ui, returnValue=10)
    assert val == 10


def test_handleButtons_6():
    ui = QtWidgets.QCheckBox()
    val = app.handleButtons(obj=ui, returnValue=10)
    assert val == 10


def test_handleButtons_7():
    ui = QtWidgets.QLineEdit()
    val = app.handleButtons(obj=ui, returnValue=10)
    assert val == 10


def test_handleButtons_8():
    ui = QtWidgets.QLCDNumber()
    val = app.handleButtons(obj=ui, returnValue=10)
    assert val == 10


def test_handleButtons_8a():
    ui = QtWidgets.QLCDNumber()
    ui.setObjectName('qt_scrollarea_viewport')
    val = app.handleButtons(obj=ui, returnValue=10)
    assert val == 10


def test_handleButtons_8b():
    ui = QtWidgets.QLCDNumber()
    ui.setObjectName('test')
    val = app.handleButtons(obj=ui, returnValue=10)
    assert val == 10


def test_handleButtons_9():
    ui = QtWidgets.QLineEdit()
    app.last = ui
    val = app.handleButtons(obj=ui, returnValue=10)
    assert val == 10


def test_handleButtons_10():
    ui = QtWidgets.QLineEdit()
    ui.setObjectName('MainWindowWindow')
    val = app.handleButtons(obj=ui, returnValue=10)
    assert val == 10


def test_notify_1():
    ui = QtWidgets.QLineEdit()
    event = QEvent(QEvent.ToolTipChange)
    suc = app.notify(obj=ui, event=event)
    assert not suc


def test_notify_2():
    ui = QtWidgets.QLineEdit()
    event = QEvent(QEvent.MouseButtonPress)
    with mock.patch.object(PyQt5.QtWidgets.QApplication,
                           'notify',
                           return_value=True,
                           side_effect=Exception()):
        suc = app.notify(obj=ui, event=event)
        assert not suc


def test_notify_3():
    ui = QtWidgets.QLineEdit()
    event = QMouseEvent(QEvent.MouseButtonRelease,
                        QPoint(100, 100),
                        Qt.NoButton,
                        Qt.NoButton,
                        Qt.NoModifier,
                        )
    with mock.patch.object(PyQt5.QtWidgets.QApplication,
                           'notify',
                           return_value=True):
        suc = app.notify(obj=ui, event=event)
        assert suc


def test_notify_4():
    ui = QtWidgets.QLineEdit()
    event = QMouseEvent(QEvent.MouseButtonRelease,
                        QPoint(100, 100),
                        Qt.LeftButton,
                        Qt.LeftButton,
                        Qt.NoModifier,
                        )
    with mock.patch.object(PyQt5.QtWidgets.QApplication,
                           'notify',
                           return_value=True):
        with mock.patch.object(app,
                               'handleButtons',
                               return_value=True):
            suc = app.notify(obj=ui, event=event)
            assert suc


def test_notify_5():
    ui = QtWidgets.QLineEdit()
    event = QMouseEvent(QEvent.MouseButtonPress,
                        QPoint(100, 100),
                        Qt.LeftButton,
                        Qt.LeftButton,
                        Qt.NoModifier,
                        )
    with mock.patch.object(PyQt5.QtWidgets.QApplication,
                           'notify',
                           return_value=True):
        with mock.patch.object(app,
                               'handleButtons',
                               return_value=True):
            suc = app.notify(obj=ui, event=event)
            assert suc
