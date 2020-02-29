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
import pytest
import unittest.mock as mock
from queue import Queue

# external packages
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal

# local import
from mw4.gui.messageW import MessageWindow
from mw4.gui.widget import MWidget


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    class Test(QObject):
        config = {'mainW': {}}
        update1s = pyqtSignal()
        messageQueue = Queue()

    global app
    app = MessageWindow(app=Test())
    yield
    del app


def test_initConfig_1():
    suc = app.initConfig()
    assert suc


def test_storeConfig_1():
    suc = app.storeConfig()
    assert suc


def test_closeEvent_1():
    with mock.patch.object(MWidget,
                           'closeEvent',
                           return_value=True):
        app.closeEvent(QCloseEvent())


def test_clearWindow_1():
    suc = app.clearWindow()
    assert suc


def test_writeMessage_1():
    suc = app.writeMessage()
    assert suc


def test_writeMessage_2():
    app.app.messageQueue.put(('test', 0))
    suc = app.writeMessage()
    assert suc
