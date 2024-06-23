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
from unittest import mock
import webbrowser

# external packages

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.mainWaddon.tabImage_Stats import ImagsStats
from gui.widgets.main_ui import Ui_MainWindow
from gui.utilities.toolsQtWidget import MWidget


@pytest.fixture(autouse=True, scope='function')
def function(qapp):
    class Mixin(MWidget, ImagsStats):
        def __init__(self):
            super().__init__()
            self.app = App()
            self.msg = self.app.msg
            self.deviceStat = {}
            self.threadPool = self.app.threadPool
            self.ui = Ui_MainWindow()
            self.ui.setupUi(self)
            ImagsStats.__init__(self)

    window = Mixin()
    yield window
    window.threadPool.waitForDone(1000)


def test_updateImageStats_1(function):
    suc = function.updateImageStats()
    assert suc


def test_updateImageStats_2(function):
    function.app.camera.data['CCD_INFO.CCD_PIXEL_SIZE_X'] = 1
    function.app.camera.data['CCD_INFO.CCD_PIXEL_SIZE_Y'] = 1
    function.app.camera.data['CCD_INFO.CCD_MAX_X'] = 100
    function.app.camera.data['CCD_INFO.CCD_MAX_Y'] = 100
    function.ui.focalLength.setValue(0)
    function.ui.aperture.setValue(0)
    suc = function.updateImageStats()
    assert suc


def test_updateImageStats_3(function):
    function.app.camera.data['CCD_INFO.CCD_PIXEL_SIZE_X'] = 1
    function.app.camera.data['CCD_INFO.CCD_PIXEL_SIZE_Y'] = 1
    function.app.camera.data['CCD_INFO.CCD_MAX_X'] = 100
    function.app.camera.data['CCD_INFO.CCD_MAX_Y'] = 100
    function.ui.aperture.setValue(100)
    function.ui.focalLength.setValue(100)
    suc = function.updateImageStats()
    assert suc


def test_openWatneyCatalog_1(function):
    with mock.patch.object(webbrowser,
                           'open',
                           return_value=True):
        suc = function.openWatneyCatalog()
        assert suc


def test_openWatneyCatalog_2(function):
    with mock.patch.object(webbrowser,
                           'open',
                           return_value=False):
        suc = function.openWatneyCatalog()
        assert suc


def test_openASTAPCatalog_1(function):
    with mock.patch.object(webbrowser,
                           'open',
                           return_value=True):
        suc = function.openASTAPCatalog()
        assert suc


def test_openASTAPCatalog_2(function):
    with mock.patch.object(webbrowser,
                           'open',
                           return_value=False):
        suc = function.openASTAPCatalog()
        assert suc


def test_openAstrometryCatalog_1(function):
    with mock.patch.object(webbrowser,
                           'open',
                           return_value=True):
        suc = function.openAstrometryCatalog()
        assert suc


def test_openAstrometryCatalog_2(function):
    with mock.patch.object(webbrowser,
                           'open',
                           return_value=False):
        suc = function.openAstrometryCatalog()
        assert suc
