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
# written in python3, (c) 2019-2022 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest

# external packages

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.mainWmixin.tabSettImageStats import SettImageStats
from gui.widgets.main_ui import Ui_MainWindow
from gui.utilities.toolsQtWidget import MWidget


@pytest.fixture(autouse=True, scope='function')
def function(qapp):
    class Mixin(MWidget, SettImageStats):
        def __init__(self):
            super().__init__()
            self.app = App()
            self.deviceStat = {}
            self.threadPool = self.app.threadPool
            self.ui = Ui_MainWindow()
            self.ui.setupUi(self)
            SettImageStats.__init__(self)

    window = Mixin()
    yield window


def test_updateImageStats_1(function):
    suc = function.updateImageStats()
    assert suc


def test_updateImageStats_2(function):
    function.app.camera.data['CCD_INFO.CCD_PIXEL_SIZE_X'] = 1
    function.app.camera.data['CCD_INFO.CCD_PIXEL_SIZE_Y'] = 1
    function.app.camera.data['CCD_INFO.CCD_MAX_X'] = 1
    function.app.camera.data['CCD_INFO.CCD_MAX_Y'] = 1
    suc = function.updateImageStats()
    assert suc


def test_updateImageStats_3(function):
    function.app.camera.data['CCD_INFO.CCD_PIXEL_SIZE_X'] = 1
    function.app.camera.data['CCD_INFO.CCD_PIXEL_SIZE_Y'] = 1
    function.app.camera.data['CCD_INFO.CCD_MAX_X'] = 1
    function.app.camera.data['CCD_INFO.CCD_MAX_Y'] = 1
    function.ui.aperture.setValue(0)
    function.ui.focalLength.setValue(0)
    suc = function.updateImageStats()
    assert suc
