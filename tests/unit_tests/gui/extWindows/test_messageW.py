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
import unittest.mock as mock

# external packages
from PySide6.QtGui import QCloseEvent

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.utilities.toolsQtWidget import MWidget
from gui.extWindows.messageW import MessageWindow
from base.loggerMW import setupLogging

setupLogging()


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    func = MessageWindow(app=App())
    yield func
    func.app.threadPool.waitForDone(10000)


def test_initConfig_1(function):
    function.initConfig()


def test_storeConfig_1(function):
    if "messageW" in function.app.config:
        del function.app.config["messageW"]

    function.storeConfig()


def test_storeConfig_2(function):
    function.app.config["messageW"] = {}

    function.storeConfig()


def test_closeEvent_1(function):
    with mock.patch.object(function, "show"):
        with mock.patch.object(MWidget, "closeEvent"):
            function.showWindow()
            function.closeEvent(QCloseEvent)


def test_updateListColors(function):
    function.app.messageQueue.put((0, "test", "test", "test"))
    function.writeMessage()
    function.updateListColors()


def test_colorChange(function):
    with mock.patch.object(function, "setupMessage"):
        with mock.patch.object(function, "clearMessageTable"):
            function.colorChange()


def test_clearMessageTable_1(function):
    function.clearMessageTable()


def test_writeMessageQueue(function):
    function.writeMessageQueue(1, "test", "test", "test")


def test_writeMessage_1(function):
    function.writeMessage()


def test_writeMessage_2(function):
    function.app.messageQueue.put((0, "test", "test", "test"))
    function.writeMessage()
