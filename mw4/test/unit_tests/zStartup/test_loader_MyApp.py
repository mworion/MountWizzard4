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
import glob
import os
import faulthandler
faulthandler.enable()

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


@pytest.fixture(autouse=True, scope="function")
def setup_teardown(qapp):
    global app

    app = qapp

    files = glob.glob('mw4/test/config/*.cfg')
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


def test_notify_1():
    ui = QtWidgets.QLineEdit()
    event = QEvent(QEvent.ToolTipChange)
    suc = app.notify(obj=ui, event=event)
    assert not suc


def test_notify_2():
    ui = QtWidgets.QLineEdit()
    event = QEvent(QEvent.MouseButtonPress)
    with mock.patch.object(PyQt5.QtWidgets.QApplication,
                           'beep',
                           return_value=False):
        suc = app.notify(obj=ui, event=event)
        assert suc


def test_notify_3():
    ui = QtWidgets.QLineEdit()
    event = QEvent(QEvent.MouseMove)
    with mock.patch.object(PyQt5.QtWidgets.QApplication,
                           'notify',
                           return_value=False,
                           side_effect=Exception()):
        suc = app.notify(obj=ui, event=event)
        assert not suc
