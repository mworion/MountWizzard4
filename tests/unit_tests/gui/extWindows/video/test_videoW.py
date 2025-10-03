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

import pytest
from gui.extWindows.video.videoW import VideoWindow
from gui.utilities.toolsQtWidget import MWidget

# external packages
from PySide6.QtGui import QCloseEvent

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    func = VideoWindow(app=App())
    with mock.patch.object(func, "show"):
        yield func
        func.app.threadPool.waitForDone(10000)


def test_initConfig_1(function):
    function.initConfig()


def test_storeConfig_1(function):
    if "videoW1" in function.app.config:
        del function.app.config["videoW1"]

    function.storeConfig()


def test_storeConfig_2(function):
    function.app.config["videoW1"] = {}

    function.storeConfig()


def test_closeEvent_1(function):
    with mock.patch.object(function, "stopVideo"):
        with mock.patch.object(MWidget, "closeEvent"):
            function.showWindow()
            function.closeEvent(QCloseEvent)
