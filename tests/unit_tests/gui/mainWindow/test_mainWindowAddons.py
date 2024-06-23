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
import unittest.mock as mock

# external packages

# local import
from gui.mainWindow.mainWindowAddons import MainWindowAddons
from gui.mainWindow.mainWindow import MainWindow
from gui.mainWaddon.astroObjects import AstroObjects
from base import packageConfig
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from resource import resources
resources.qInitResources()


@pytest.fixture(autouse=True, scope='module')
def window(qapp):
    packageConfig.isAvailable = True
    with mock.patch.object(MainWindow,
                           'show'):
        with mock.patch.object(AstroObjects,
                               'loadSourceUrl'):
            mainW = MainWindow(App())
            window = MainWindowAddons(mainW)
            yield window


def test_initConfig_1(window):
    window.initConfig()


def test_storeConfig_1(window):
    window.storeConfig()


def test_setupIcons_1(window):
    window.setupIcons()


def test_updateColorSet_1(window):
    window.updateColorSet()
