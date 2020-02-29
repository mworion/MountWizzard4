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
import pytest
import sys
from queue import Queue

# external packages
import PyQt5.QtWidgets
from PyQt5.QtCore import QObject
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtCore import pyqtSignal
import PyQt5.QtCore
from indibase.indiBase import Device

# local import
from mw4.gui.messageW import MessageWindow


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    class Test(QObject):
        config = {'mainW': {}}
        update1s = pyqtSignal()
        messageQueue = Queue()

    global app
    with mock.patch.object(MessageWindow,
                           'show',
                           return_value=True):
        app = MessageWindow(app=Test())
    yield
    del app


def test_storeConfig_1():
    suc = app.storeConfig()
    assert suc


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
