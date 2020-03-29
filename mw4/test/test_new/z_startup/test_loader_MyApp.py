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
# Python  v3.7.5
#
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock

# external packages
import pytest
import PyQt5
from PyQt5.QtCore import QEvent
from PyQt5 import QtWidgets

# local import
from mw4.loader import MyApp


@pytest.fixture(scope="session")
def qapp():
    yield MyApp([])


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


def test_notify_1(qapp):
    ui = QtWidgets.QLineEdit()
    event = QEvent(QEvent.ToolTipChange)
    suc = qapp.notify(obj=ui, event=event)
    assert not suc


def test_notify_2(qapp):
    ui = QtWidgets.QLineEdit()
    event = QEvent(QEvent.MouseButtonPress)
    with mock.patch.object(PyQt5.QtWidgets.QApplication,
                           'beep',
                           return_value=False):
        suc = qapp.notify(obj=ui, event=event)
        assert suc


def test_notify_3(qapp):
    ui = QtWidgets.QLineEdit()
    event = QEvent(QEvent.MouseMove)
    with mock.patch.object(PyQt5.QtWidgets.QApplication,
                           'notify',
                           return_value=False,
                           side_effect=Exception()):
        suc = qapp.notify(obj=ui, event=event)
        assert not suc
