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
import pytest
from mw4.gui.mainWaddon.tabAlmanac import Almanac
from mw4.gui.mainWindow.mainWindowAddons import MainWindowAddons
from mw4.gui.utilities.qtMain import MWidget
from mw4.gui.widgets.main_ui import Ui_MainWindow
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from unittest import mock


class MockAddon:
    def initConfig(self):
        pass

    def storeConfig(self):
        pass

    def setupIcons(self):
        pass

    def updateColorSet(self):
        pass

    def shutdown(self):
        pass


@pytest.fixture(autouse=True, scope="module")
def window(qapp):
    mainW = MWidget()
    mainW.app = App()
    mainW.ui = Ui_MainWindow()
    mainW.ui.setupUi(mainW)
    # Avoid the heavy full-year twilight worker started by the Almanac addon
    # during construction; it is covered in the Almanac tests.
    with mock.patch.object(Almanac, "showTwilightDataPlot"):
        window = MainWindowAddons(mainW)
    window.addons = {"test": MockAddon()}
    yield window
    mainW.app.threadPool.waitForDone(10000)
    qapp.processEvents()


def test_initConfig_loads_addons_config(window):
    """Test initConfig loads configuration for all addons."""
    window.initConfig()


def test_storeConfig_saves_addons_config(window):
    """Test storeConfig saves configuration for all addons."""
    window.storeConfig()


def test_setupIcons_creates_addon_icons(window):
    """Test setupIcons creates icons for all addons."""
    window.setupIcons()


def test_updateColorSet_updates_addon_colors(window):
    """Test updateColorSet updates colors for all addons."""
    window.updateColorSet()


def test_shutdown_dispatchesToAllAddons(window):
    patches = [mock.patch.object(addon, "shutdown") for addon in window.addons.values()]
    mocks = [p.start() for p in patches]
    try:
        window.shutdown()
    finally:
        for p in patches:
            p.stop()
    for m in mocks:
        m.assert_called_once_with()
