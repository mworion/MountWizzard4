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
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock

import pytest

# external packages
from PySide6.QtGui import QCloseEvent

from mw4.gui.extWindows.bigPopupW import BigPopup
from mw4.gui.utilities.toolsQtWidget import MWidget

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    window = BigPopup(App())
    yield window
    window.app.threadPool.waitForDone(10000)


def test_initConfig_1(function):
    function.initConfig()


def test_storeConfig_1(function):
    if "bigPopupW" in function.app.config:
        del function.app.config["bigPopupW"]

    function.storeConfig()


def test_storeConfig_2(function):
    function.app.config["bigPopupW"] = {}

    function.storeConfig()


def test_closeEvent_1(function):
    with mock.patch.object(function, "show"):
        with mock.patch.object(MWidget, "closeEvent"):
            function.showWindow()
            function.closeEvent(QCloseEvent)


def test_showWindow(function):
    with mock.patch.object(function, "show"):
        function.showWindow()


def test_colorChange(function):
    function.colorChange()


def test_updateDeviceStats(function):
    function.updateDeviceStats()


def test_updateStatus_1(function):
    function.app.mount.obsSite.status = 0
    function.updateStatus()


def test_updateStatus_2(function):
    function.app.mount.obsSite.status = 1
    function.updateStatus()
