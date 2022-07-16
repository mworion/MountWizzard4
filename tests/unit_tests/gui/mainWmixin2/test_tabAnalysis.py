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
# GUI with PyQT5 for python !

#
# written in python3, (c) 2019-2022 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock
import pytest
import glob
import shutil
import os

# external packages

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.mainWmixin.tabAnalysis import Analysis
import gui.mainWmixin.tabAnalysis
from gui.widgets.main_ui import Ui_MainWindow
from gui.utilities.toolsQtWidget import MWidget
from base.loggerMW import setupLogging
setupLogging()


@pytest.fixture(autouse=True, scope='function')
def function(qapp):
    class Mixin(MWidget, Analysis):
        def __init__(self):
            super().__init__()
            self.app = App()
            self.msg = self.app.msg
            self.deviceStat = {}
            self.scaleHint = None
            self.fovHint = None
            self.playSound = None
            self.ui = Ui_MainWindow()
            self.ui.setupUi(self)
            Analysis.__init__(self)

    window = Mixin()
    yield window

    files = glob.glob('tests/workDir/model/a-*.analysis')
    for f in files:
        os.remove(f)
    for path in glob.glob('tests/workDir/image/a-*'):
        shutil.rmtree(path)


def test_initConfig_1(function):
    function.app.config['mainW'] = {}
    suc = function.initConfig()
    assert suc


def test_storeConfig_1(function):
    suc = function.storeConfig()
    assert suc


def test_setAnalysisOperationMode_1(function):
    suc = function.setAnalysisOperationMode(0)
    assert suc


def test_setAnalysisOperationMode_2(function):
    suc = function.setAnalysisOperationMode(4)
    assert suc


def test_setAnalysisOperationMode_3(function):
    suc = function.setAnalysisOperationMode(5)
    assert suc


def test_setAnalysisOperationMode_4(function):
    suc = function.setAnalysisOperationMode(6)
    assert suc
