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
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock
import pytest
import astropy

# external packages
from PySide6.QtWidgets import QWidget

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.mainWaddon.tabAnalysis import Analysis
from gui.widgets.main_ui import Ui_MainWindow
from gui.mainWaddon.runBasic import RunBasic


@pytest.fixture(autouse=True, scope='module')
def function(qapp):

    mainW = QWidget()
    mainW.app = App()
    mainW.threadPool = mainW.app.threadPool
    mainW.ui = Ui_MainWindow()
    mainW.ui.setupUi(mainW)

    window = Analysis(mainW)
    yield window


def test_initConfig_1(function):
    function.app.config['mainW'] = {}
    function.initConfig()


def test_storeConfig_1(function):
    function.storeConfig()


def test_setupIcons_1(function):
    function.setupIcons()


def test_setAnalysisOperationMode_1(function):
    function.setAnalysisOperationMode(0)


def test_setAnalysisOperationMode_2(function):
    function.setAnalysisOperationMode(4)


def test_setAnalysisOperationMode_3(function):
    function.setAnalysisOperationMode(5)


def test_setAnalysisOperationMode_4(function):
    function.setAnalysisOperationMode(6)


def test_checkAnalysisConditions_1(function):
    with mock.patch.object(function.ui.plateSolveDevice,
                           'currentText',
                           return_value='No device'):
        suc = function.checkAnalysisConditions()
        assert not suc


def test_checkAnalysisConditions_2(function):
    with mock.patch.object(function.app.plateSolve,
                           'checkAvailability',
                           return_value=(False, False)):
        suc = function.checkAnalysisConditions()
        assert not suc


def test_checkAnalysisConditions_3(function):
    with mock.patch.object(function.app.plateSolve,
                           'checkAvailability',
                           return_value=(True, True)):
        suc = function.checkAnalysisConditions()
        assert suc


def test_setupFlexurePoints(function):
    v, t = function.setupFlexurePoints()
    assert len(v) == 120
    assert t == 30


def test_restoreAnalysisDefaultContextAndGuiStatus(function):
    function.restoreAnalysisDefaultContextAndGuiStatus()


def test_cancelAnalysis(function):
    function.cancelAnalysis()


def test_processAnalysisData(function):
    with mock.patch.object(function,
                           'restoreAnalysisDefaultContextAndGuiStatus'):
        function.processAnalysisData()


def test_updateAnalysisProgress_1(function):
    mPoint = {}
    suc = function.updateAnalysisProgress(mPoint)
    assert not suc


def test_updateAnalysisProgress_2(function):
    mPoint = {'lenSequence': 3,
              'countSequence': 2}
    suc = function.updateAnalysisProgress(mPoint)
    assert suc


def test_updateAnalysisProgress_3(function):
    mPoint = {'lenSequence': 2,
              'countSequence': 3}
    suc = function.updateAnalysisProgress(mPoint)
    assert not suc


def test_updateAnalysisProgress_4(function):
    mPoint = {'lenSequence': 0,
              'countSequence': -1}
    suc = function.updateAnalysisProgress(mPoint)
    assert not suc


def test_runFlexure_1(function):
    with mock.patch.object(function,
                           'checkAnalysisConditions',
                           return_value=False):
        suc = function.runFlexure()
        assert not suc


def test_runFlexure_2(function):
    def test(modelPoints=None,
             retryCounter=None,
             runType=None,
             processData=None,
             progress=None,
             imgDir=None,
             keepImages=None):
        return

    function.cycleThroughPoints = test
    with mock.patch.object(function,
                           'checkAnalysisConditions',
                           return_value=True):
        with mock.patch.object(RunBasic,
                               'setupFilenamesAndDirectories',
                               return_value=('', '')):
            with mock.patch.object(RunBasic,
                                   'setupRunPoints',
                                   return_value=[1, 2]):
                suc = function.runFlexure()
                assert suc
