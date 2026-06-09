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
# written in python3, (c) 2019-2026 by mworion
# License APL2.0
#
###########################################################
import gc
import pytest
import unittest.mock as mock
from mw4.gui.extWindows.setting.settingW import SettingWindow
from mw4.gui.utilities.qtMain import MWidget
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QApplication
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    app = App()
    # Only return devices that have UI elements in setupUiDriver
    validDevices = [
        "camera",
        "cover",
        "directWeather",
        "dome",
        "filter",
        "focuser",
        "lightPanel",
        "power",
        "sensor1Weather",
        "sensor2Weather",
        "sensor3Weather",
        "sensor4Weather",
        "telescope",
    ]

    def mockConfigurable():
        for entry in app.dReg.d.values():
            if (
                entry.name in validDevices
                and entry.isConfigurable
                and entry.instance is not None
            ):
                yield entry

    with mock.patch.object(app.dReg, "configurable", mockConfigurable):
        func = SettingWindow(app=app, title="Setting")
    yield func
    QApplication.processEvents()
    gc.collect()
    QApplication.processEvents()


def test_initConfig_1(function):
    function.initConfig()


def test_storeConfig_1(function):
    if "WindowSetting" in function.app.config:
        del function.app.config["WindowSetting"]
    function.storeConfig()


def test_storeConfig_2(function):
    function.app.config["WindowSetting"] = {}
    function.storeConfig()


def test_closeEvent_1(function):
    with (
        mock.patch.object(function, "show"),
        mock.patch.object(MWidget, "closeEvent"),
        mock.patch.object(function.tabSettDevice, "closeEvent"),
    ):
        function.showWindow()
        function.closeEvent(QCloseEvent)


def test_showWindow(function):
    with mock.patch.object(function, "show"):
        function.showWindow()


def test_colorChange(function):
    function.colorChange()
