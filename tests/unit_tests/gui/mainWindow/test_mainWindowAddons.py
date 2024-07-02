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
# GUI with PyQT5 for python
#
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
import astropy
import unittest.mock as mock

# external packages
from PySide6.QtWidgets import QWidget

# local import
from gui.mainWindow.mainWindowAddons import MainWindowAddons
from gui.widgets.main_ui import Ui_MainWindow
from base import packageConfig
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from resource import resources
resources.qInitResources()


@pytest.fixture(autouse=True, scope='module')
def window():
    packageConfig.isAvailable = True
    mainW = QWidget()

    mainW.app = App()
    mainW.ui = Ui_MainWindow()
    mainW.ui.setupUi(mainW)
    window = MainWindowAddons(mainW)
    yield window
    mainW.app.threadPool.waitForDone(1000)


def test_initConfig_1(window):
    with mock.patch.object(window.addons['ManageModel'],
                           'initConfig'):
        window.initConfig()


def test_storeConfig_1(window):
    with mock.patch.object(window.addons['ManageModel'],
                           'storeConfig'):
        window.storeConfig()


def test_setupIcons_1(window):
    with mock.patch.object(window.addons['ManageModel'],
                           'setupIcons'):
        window.setupIcons()


def test_updateColorSet_1(window):
    with mock.patch.object(window.addons['ManageModel'],
                           'updateColorSet'):
        window.updateColorSet()
