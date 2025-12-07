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

import webbrowser
from unittest import mock

import pytest


from PySide6.QtWidgets import QWidget

from mw4.gui.mainWaddon.tabImage_Stats import ImageStats
from mw4.gui.widgets.main_ui import Ui_MainWindow


from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    mainW = QWidget()
    mainW.app = App()
    mainW.ui = Ui_MainWindow()
    mainW.ui.setupUi(mainW)
    window = ImageStats(mainW)
    yield window
    mainW.app.threadPool.waitForDone(1000)


def test_storeConfig(function):
    function.storeConfig()


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


def test_updateTelescopeParametersToGui_1(function):
    function.app.telescope.data["TELESCOPE_INFO.TELESCOPE_FOCAL_LENGTH"] = 1
    function.app.telescope.data["TELESCOPE_INFO.TELESCOPE_APERTURE"] = 1

    function.updateTelescopeParametersToGui()


def test_updateTelescopeParametersToGuiCyclic_1(function):
    function.ui.automaticTelescope.setChecked(False)
    function.updateTelescopeParametersToGuiCyclic()


def test_updateTelescopeParametersToGuiCyclic_2(function):
    function.ui.automaticTelescope.setChecked(True)
    with mock.patch.object(function, "updateTelescopeParametersToGui"):
        function.updateTelescopeParametersToGuiCyclic()
