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
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
from unittest import mock
import webbrowser

# external packages
from PySide6.QtWidgets import QWidget

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.mainWaddon.tabImage_Stats import ImageStats
from gui.widgets.main_ui import Ui_MainWindow


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    mainW = QWidget()
    mainW.app = App()
    mainW.ui = Ui_MainWindow()
    mainW.ui.setupUi(mainW)
    window = ImageStats(mainW)
    yield window
    mainW.app.threadPool.waitForDone(1000)


def test_updateImageStats_1(function):
    function.updateImageStats()


def test_updateImageStats_2(function):
    function.app.camera.data["CCD_INFO.CCD_PIXEL_SIZE_X"] = 1
    function.app.camera.data["CCD_INFO.CCD_PIXEL_SIZE_Y"] = 1
    function.app.camera.data["CCD_INFO.CCD_MAX_X"] = 100
    function.app.camera.data["CCD_INFO.CCD_MAX_Y"] = 100
    function.ui.focalLength.setValue(0)
    function.ui.aperture.setValue(0)
    function.updateImageStats()


def test_updateImageStats_3(function):
    function.app.camera.data["CCD_INFO.CCD_PIXEL_SIZE_X"] = 1
    function.app.camera.data["CCD_INFO.CCD_PIXEL_SIZE_Y"] = 1
    function.app.camera.data["CCD_INFO.CCD_MAX_X"] = 100
    function.app.camera.data["CCD_INFO.CCD_MAX_Y"] = 100
    function.ui.aperture.setValue(100)
    function.ui.focalLength.setValue(100)
    function.updateImageStats()


def test_openWatneyCatalog_1(function):
    with mock.patch.object(webbrowser, "open", return_value=True):
        function.openWatneyCatalog()


def test_openWatneyCatalog_2(function):
    with mock.patch.object(webbrowser, "open", return_value=False):
        function.openWatneyCatalog()


def test_openASTAPCatalog_1(function):
    with mock.patch.object(webbrowser, "open", return_value=True):
        function.openASTAPCatalog()


def test_openASTAPCatalog_2(function):
    with mock.patch.object(webbrowser, "open", return_value=False):
        function.openASTAPCatalog()


def test_openAstrometryCatalog_1(function):
    with mock.patch.object(webbrowser, "open", return_value=True):
        function.openAstrometryCatalog()


def test_openAstrometryCatalog_2(function):
    with mock.patch.object(webbrowser, "open", return_value=False):
        function.openAstrometryCatalog()
