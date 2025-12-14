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


import pytest
from mw4.assets import assetsData
from mw4.gui.mainWindow.mainWindowAddons import MainWindowAddons
from mw4.gui.utilities.toolsQtWidget import MWidget
from mw4.gui.widgets.main_ui import Ui_MainWindow
from tests.unit_tests.unitTestAddOns.baseTestApp import App

assetsData.qInitResources()


class Test:
    def initConfig(self):
        pass

    def storeConfig(self):
        pass

    def setupIcons(self):
        pass

    def updateColorSet(self):
        pass


@pytest.fixture(autouse=True, scope="module")
def window(qapp):
    mainW = MWidget()
    mainW.app = App()
    mainW.ui = Ui_MainWindow()
    mainW.ui.setupUi(mainW)
    window = MainWindowAddons(mainW)
    window.addons = {"test": Test()}
    yield window
    mainW.app.threadPool.waitForDone(10000)


def test_initConfig_1(window):
    window.initConfig()


def test_storeConfig_1(window):
    window.storeConfig()


def test_setupIcons_1(window):
    window.setupIcons()


def test_updateColorSet_1(window):
    window.updateColorSet()
