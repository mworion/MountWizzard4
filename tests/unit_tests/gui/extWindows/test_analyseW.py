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
import unittest.mock as mock
import json

# external packages
from PyQt5.QtGui import QCloseEvent, QResizeEvent
import numpy as np

# local import
from tests.unit_tests.unitTestAddOns.baseTestSetupExtWindows import App
from gui.utilities.toolsQtWidget import MWidget
from gui.extWindows.analyseW import AnalyseWindow


@pytest.fixture(autouse=True, scope='module')
def module(qapp):
    yield


@pytest.fixture(autouse=True, scope='function')
def function(module):

    window = AnalyseWindow(app=App())
    yield window


def test_initConfig_1(function):
    suc = function.initConfig()
    assert suc


def test_initConfig_2(function):
    suc = function.initConfig()
    assert suc

    function.app.config['analyseW'] = {'winPosX': 10000}
    suc = function.initConfig()
    assert suc


def test_initConfig_3(function):
    suc = function.initConfig()
    assert suc

    function.app.config['analyseW'] = {'winPosY': 10000}
    suc = function.initConfig()
    assert suc


def test_initConfig_4(function):
    function.screenSizeX = 1000
    function.screenSizeY = 1000
    function.app.config['analyseW'] = {'winPosX': 100,
                                       'winPosY': 100,
                                       'height': 10,
                                       'width': 10}
    suc = function.initConfig()
    assert suc


def test_storeConfig_1(function):
    if 'analyseW' in function.app.config:
        del function.app.config['analyseW']

    suc = function.storeConfig()
    assert suc


def test_storeConfig_2(function):
    function.app.config['analyseW'] = {}

    suc = function.storeConfig()
    assert suc


def test_closeEvent_1(function):
    with mock.patch.object(function,
                           'show'):
        with mock.patch.object(MWidget,
                               'closeEvent'):
            function.showWindow()
            function.closeEvent(QCloseEvent)


def test_resizeEvent(function):
    with mock.patch.object(MWidget,
                           'resizeEvent'):
        function.resizeEvent(QResizeEvent)


def test_showWindow(function):
    with mock.patch.object(function,
                           'show'):
        suc = function.showWindow()
        assert suc


def test_colorChange(function):
    with mock.patch.object(function,
                           'drawAll'):
        suc = function.colorChange()
        assert suc


def test_writeGui_1(function):
    suc = function.writeGui([{'a': 1}], 'test')
    assert suc
    assert function.ui.mirrored.text() == ''


def test_generateDataSets(function):
    with open('tests/testData/test.model', 'r') as infile:
        modelJSON = json.load(infile)

    suc = function.generateDataSets(modelJSON)
    assert suc
    assert function.latitude == 48.1


def test_processModel_1(function):
    with mock.patch.object(function,
                           'writeGui'):
        with mock.patch.object(function,
                               'generateDataSets'):
            with mock.patch.object(function,
                                   'drawAll'):
                suc = function.processModel('tests/testData/test.model')
                assert suc


def test_loadModel_1(function):
    with mock.patch.object(function,
                           'openFile',
                           return_value=('', '', '')):
        with mock.patch.object(function,
                               'processModel'):
            suc = function.loadModel()
            assert suc


def test_loadModel_2(function):
    with mock.patch.object(function,
                           'openFile',
                           return_value=('test', 'test', 'test')):
        with mock.patch.object(function,
                               'processModel'):
            suc = function.loadModel()
            assert suc


def test_showAnalyse_1(function):
    with mock.patch.object(function,
                           'processModel'):
        suc = function.showAnalyse('test')
        assert suc


def test_draw_raRawErrors(function):
    function.errorRA_S = [0, 1, 2]
    function.errorDEC_S = [0, 1, 2]
    function.azimuth = [0, 1, 2]
    function.altitude = [0, 1, 2]
    suc = function.drawRaRawErrors()
    assert suc


def test_draw_decRawErrors(function):
    function.errorRA_S = [0, 1, 2]
    function.errorDEC_S = [0, 1, 2]
    function.azimuth = [0, 1, 2]
    function.altitude = [0, 1, 2]
    suc = function.drawDecRawErrors()
    assert suc


def test_draw_raErrors(function):
    function.errorRA = [0, 1, 2]
    function.errorDEC = [0, 1, 2]
    function.azimuth = [0, 1, 2]
    function.altitude = [0, 1, 2]
    suc = function.drawRaErrors()
    assert suc


def test_draw_decErrors(function):
    function.errorRA = [0, 1, 2]
    function.errorDEC = [0, 1, 2]
    function.azimuth = [0, 1, 2]
    function.altitude = [0, 1, 2]
    suc = function.drawDecError()
    assert suc


def test_draw_raErrorsRef(function):
    function.angularPosRA = [0, 1, 2]
    function.errorRA = [0, 0, 0]
    function.pierside = ['E', 'W', 'E']
    suc = function.drawRaErrorsRef()
    assert suc


def test_draw_decErrorsRef(function):
    function.angularPosDEC = [0, 0, 0]
    function.errorDEC = [0, 0, 0]
    function.pierside = ['E', 'W', 'E']
    suc = function.drawDecErrorsRef()
    assert suc


def test_draw_raRawErrorsRef(function):
    function.angularPosRA = [0, 1, 2]
    function.errorRA_S = [0, 0, 0]
    function.pierside = ['E', 'W', 'E']
    suc = function.drawRaRawErrorsRef()
    assert suc


def test_draw_decRawErrorsRef(function):
    function.errorDEC_S = [0, 0, 0]
    function.angularPosDEC = [0, 0, 0]
    function.pierside = ['E', 'W', 'E']
    suc = function.drawDecRawErrorsRef()
    assert suc


def test_draw_scaleImage(function):
    function.index = [0, 1, 2]
    function.scaleS = [0, 0, 0]
    function.pierside = ['E', 'W', 'E']
    suc = function.drawScaleImage()
    assert suc


def test_draw_errorAscending(function):
    function.errorRMS = [0, 1, 2]
    function.index = [0, 0, 0]
    function.pierside = ['E', 'W', 'E']
    suc = function.drawErrorAscending()
    assert suc


def test_draw_modelPositions_1(function):
    function.altitude = np.array([0, 1, 2])
    function.azimuth = np.array([0, 1, 2])
    function.errorRMS = np.array([0, 2, 4])
    function.errorAngle = np.array([0, 0, 0])
    function.latitude = 48
    suc = function.drawModelPositions()
    assert suc


def test_draw_errorDistribution_1(function):
    function.errorRMS = np.array([0, 2, 4])
    function.errorAngle = np.array([0, 1, 2])
    function.pierside = ['E', 'W', 'E']
    suc = function.drawErrorDistribution()
    assert suc


def test_drawAll(function):
    def test():
        pass

    function.index = []
    function.charts = [test]
    suc = function.drawAll()
    assert suc
