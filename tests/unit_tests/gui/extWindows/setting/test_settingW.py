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
def settingWindow(qapp):
    """Setup SettingWindow fixture for testing."""
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


def test_initConfig_loads_config(settingWindow):
    """Test initConfig loads configuration."""
    settingWindow.initConfig()


def test_storeConfig_when_config_missing(settingWindow):
    """Test storeConfig when WindowSetting config missing."""
    if "WindowSetting" in settingWindow.app.config:
        del settingWindow.app.config["WindowSetting"]
    settingWindow.storeConfig()

    assert "WindowSetting" in settingWindow.app.config


def test_storeConfig_when_config_exists(settingWindow):
    """Test storeConfig when WindowSetting config exists."""
    settingWindow.app.config["WindowSetting"] = {}
    settingWindow.storeConfig()

    assert "WindowSetting" in settingWindow.app.config


def test_closeEvent_closes_properly(settingWindow):
    """Test closeEvent closes window properly."""
    with (
        mock.patch.object(settingWindow, "show"),
        mock.patch.object(MWidget, "closeEvent"),
        mock.patch.object(settingWindow.tabSettDevice, "closeEvent"),
    ):
        settingWindow.showWindow()
        settingWindow.closeEvent(QCloseEvent)


def test_showWindow_shows_window(settingWindow):
    """Test showWindow displays window."""
    with mock.patch.object(settingWindow, "show"):
        settingWindow.showWindow()


def test_colorChange_updates_style(settingWindow):
    """Test colorChange updates window style."""
    settingWindow.colorChange()


def test_setupIcons_creates_icons(settingWindow):
    """Test setupIcons initializes icons."""
    settingWindow.setupIcons()


def test_window_has_all_tabs(settingWindow):
    """Test window has all setting tabs."""
    assert hasattr(settingWindow, "tabSettDevice")
    assert hasattr(settingWindow, "tabSettMount")
    assert hasattr(settingWindow, "tabSettDome")
    assert hasattr(settingWindow, "tabSettMisc")
    assert hasattr(settingWindow, "tabSettParkPos")
    assert hasattr(settingWindow, "tabSettRelay")
    assert hasattr(settingWindow, "tabSettUpdate")

