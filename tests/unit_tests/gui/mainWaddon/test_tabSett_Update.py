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
import logging
import os
import platform
import sys
import webbrowser
from unittest import mock

import importlib_metadata
import pytest

# external packages
import requests

from mw4.base.loggerMW import setupLogging
from mw4.gui.mainWaddon.tabSett_Update import SettUpdate
from mw4.gui.utilities.toolsQtWidget import MWidget
from mw4.gui.widgets.main_ui import Ui_MainWindow

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App

setupLogging()


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    mainW = MWidget()
    mainW.app = App()
    mainW.ui = Ui_MainWindow()
    mainW.ui.setupUi(mainW)
    window = SettUpdate(mainW)
    yield window
    mainW.app.threadPool.waitForDone(1000)


def test_initConfig_1(function):
    function.app.config["mainW"] = {}
    function.initConfig()


def test_storeConfig_1(function):
    function.storeConfig()


def test_setWeatherOnline_1(function):
    temp = function.app.onlineWeather
    function.app.onlineWeather = None
    suc = function.setWeatherOnline()
    assert not suc
    function.app.onlineWeather = temp


def test_setWeatherOnline_2(function):
    suc = function.setWeatherOnline()
    assert suc


def test_setSeeingOnline_1(function):
    temp = function.app.seeingWeather
    function.app.seeingWeather = None
    suc = function.setSeeingOnline()
    assert not suc
    function.app.seeingWeather = temp


def test_setSeeingOnline_2(function):
    suc = function.setSeeingOnline()
    assert suc


def test_setupIERS_1(function):
    function.ui.isOnline.setChecked(False)
    function.setupIERS()


def test_setupIERS_2(function):
    function.ui.isOnline.setChecked(True)
    function.setupIERS()


def test_setLoggingLevel1(function):
    function.ui.loglevelDebug.setChecked(True)
    function.setLoggingLevel()
    val = logging.getLogger("MW4").getEffectiveLevel()
    assert val == 10


def test_setLoggingLevel2(function):
    function.ui.loglevelStandard.setChecked(True)
    function.setLoggingLevel()
    val = logging.getLogger("MW4").getEffectiveLevel()
    assert val == 20


def test_setLoggingLevel3(function):
    function.ui.loglevelTrace.setChecked(True)
    function.setLoggingLevel()
    val = logging.getLogger("MW4").getEffectiveLevel()
    assert val == 5
