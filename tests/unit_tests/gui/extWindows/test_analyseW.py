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
# written in python3, (c) 2019-2021 by mworion
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
from tests.baseTestSetupExtWindows import App
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
    function.app.config['analyseW'] = {'winPosX': 100,
                                       'winPosY': 100}
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


def test_writeGui_1(function):
    suc = function.writeGui([{'a': 1}], 'test')
    assert suc
    assert function.ui.filename.text() == 'test'
    assert function.ui.mirrored.text() == ''


def test_generateDataSets(function):
    with open('tests/testData/test.model', 'r') as infile:
        modelJSON = json.load(infile)

    suc = function.generateDataSets(modelJSON)
    assert suc
    assert function.latitude == 48.1


def test_processModel_1(function):
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


def test_plotFigureFlat_1(function):
    axe, _ = function.generateFlat(widget=function.raPointErrorsRaw)

    with mock.patch.object(axe.figure.canvas,
                           'draw'):
        suc = function.plotFigureFlat(axe, [0, 1], [0, 1], ['E', 'E'], 'X', 'Y')
        assert suc


def test_plotFigureFlat_2(function):
    axe, _ = function.generateFlat(widget=function.raPointErrorsRaw)

    function.ui.winsorizedLimit.setChecked(True)
    with mock.patch.object(axe.figure.canvas,
                           'draw'):
        suc = function.plotFigureFlat(axe, [0, 1], [0, 1], ['E', 'E'], 'X', 'Y', sort=True)
        assert suc


def test_plotFigureFlat_3(function):
    axe, _ = function.generateFlat(widget=function.raPointErrorsRaw)

    function.ui.winsorizedLimit.setChecked(True)
    with mock.patch.object(axe.figure.canvas,
                           'draw'):
        suc = function.plotFigureFlat(axe, [0, 1], [0, 1], ['W', 'W'], 'X', 'Y',
                                      poly=1)
        assert suc


def test_plotFigureFlat_4(function):
    axe, _ = function.generateFlat(widget=function.raPointErrorsRaw)

    function.ui.winsorizedLimit.setChecked(True)
    with mock.patch.object(axe.figure.canvas,
                           'draw'):
        suc = function.plotFigureFlat(axe, [0, 1], [0, 1], ['E', 'E'], 'X', 'Y',
                                      poly=1)
        assert suc


def test_plotFigureFlat_5(function):
    axe, _ = function.generateFlat(widget=function.raPointErrorsRaw)

    function.ui.winsorizedLimit.setChecked(True)
    with mock.patch.object(axe.figure.canvas,
                           'draw'):
        suc = function.plotFigureFlat(axe, [0, 1, 2], [0, 1, 2], ['W', 'W', 'W'], 'X', 'Y',
                                      poly=1)
        assert suc


def test_plotFigureFlat_6(function):
    axe, _ = function.generateFlat(widget=function.raPointErrorsRaw)

    function.ui.winsorizedLimit.setChecked(True)
    with mock.patch.object(axe.figure.canvas,
                           'draw'):
        suc = function.plotFigureFlat(axe, [0, 1, 2], [0, 1, 2], ['E', 'E', 'E'], 'X', 'Y',
                                      poly=1)
        assert suc


def test_draw_raPointErrorsRaw(function):
    function.index = [0, 1, 2]
    function.errorRA_S = [0, 0, 0]
    function.pierside = ['E', 'W', 'E']

    with mock.patch.object(function,
                           'plotFigureFlat'):
        suc = function.draw_raPointErrorsRaw()
        assert suc


def test_draw_decPointErrorsRaw(function):
    function.index = [0, 1, 2]
    function.errorDEC_S = [0, 0, 0]
    function.pierside = ['E', 'W', 'E']

    with mock.patch.object(function,
                           'plotFigureFlat'):
        suc = function.draw_decPointErrorsRaw()
        assert suc


def test_draw_raModelErrors(function):
    function.index = [0, 1, 2]
    function.errorRA = [0, 0, 0]
    function.pierside = ['E', 'W', 'E']

    with mock.patch.object(function,
                           'plotFigureFlat'):
        suc = function.draw_raModelErrors()
        assert suc


def test_draw_decModelErrors(function):
    function.index = [0, 1, 2]
    function.errorDEC = [0, 0, 0]
    function.pierside = ['E', 'W', 'E']

    with mock.patch.object(function,
                           'plotFigureFlat'):
        suc = function.draw_decModelErrors()
        assert suc


def test_draw_raModelErrorsRef(function):
    function.errorRA = [0, 1, 2]
    function.angularPosRA = [0, 0, 0]
    function.pierside = ['E', 'W', 'E']

    with mock.patch.object(function,
                           'plotFigureFlat'):
        suc = function.draw_raModelErrorsRef()
        assert suc


def test_draw_decModelErrorsRef(function):
    function.errorDEC = [0, 1, 2]
    function.angularPosDEC = [0, 0, 0]
    function.pierside = ['E', 'W', 'E']

    with mock.patch.object(function,
                           'plotFigureFlat'):
        suc = function.draw_decModelErrorsRef()
        assert suc


def test_draw_raPointErrorsRawRef(function):
    function.angularPosRA = [0, 1, 2]
    function.errorRA_S = [0, 0, 0]
    function.pierside = ['E', 'W', 'E']

    with mock.patch.object(function,
                           'plotFigureFlat'):
        suc = function.draw_raPointErrorsRawRef()
        assert suc


def test_draw_decPointErrorsRawRef(function):
    function.angularPosDEC = [0, 1, 2]
    function.errorDEC_S = [0, 0, 0]
    function.pierside = ['E', 'W', 'E']

    with mock.patch.object(function,
                           'plotFigureFlat'):
        suc = function.draw_decPointErrorsRawRef()
        assert suc


def test_draw_scaleImage(function):
    function.index = [0, 1, 2]
    function.scaleS = [0, 0, 0]
    function.pierside = ['E', 'W', 'E']

    with mock.patch.object(function,
                           'plotFigureFlat'):
        suc = function.draw_scaleImage()
        assert suc


def test_draw_errorAscending(function):
    function.errorRMS = [0, 1, 2]
    function.index = [0, 0, 0]
    function.pierside = ['E', 'W', 'E']

    with mock.patch.object(function,
                           'plotFigureFlat'):
        suc = function.draw_errorAscending()
        assert suc


def test_draw_modelPositions_1(function):
    function.altitude = np.array([0, 1, 2])
    function.azimuth = np.array([0, 1, 2])
    function.errorRMS = np.array([0, 2, 4])
    function.errorAngle = np.array([0, 0, 0])
    function.latitude = None

    axe, fig = function.generatePolar(widget=function.modelPositions)
    with mock.patch.object(MWidget,
                           'generatePolar',
                           return_value=(axe, fig)):
        with mock.patch.object(axe.figure.canvas,
                               'draw'):
            suc = function.draw_modelPositions()
            assert suc


def test_draw_modelPositions_2(function):
    function.altitude = np.array([0, 1, 2])
    function.azimuth = np.array([0, 1, 2])
    function.errorRMS = np.array([0, 2, 4])
    function.errorAngle = np.array([0, 0, 0])
    function.latitude = 48

    axe, fig = function.generatePolar(widget=function.modelPositions)
    with mock.patch.object(MWidget,
                           'generatePolar',
                           return_value=(axe, fig)):
        with mock.patch.object(axe.figure.canvas,
                               'draw'):
            suc = function.draw_modelPositions()
            assert suc


def test_draw_errorDistribution_1(function):
    function.errorRMS = np.array([0, 2, 4])
    function.errorAngle = np.array([0, 0, 0])
    function.pierside = ['E', 'W', 'E']

    axe, fig = function.generatePolar(widget=function.errorDistribution)
    with mock.patch.object(MWidget,
                           'generatePolar',
                           return_value=(axe, fig)):
        with mock.patch.object(axe.figure.canvas,
                               'draw'):
            suc = function.draw_errorDistribution()
            assert suc


def test_drawAll_1(function):
    def test():
        pass

    function.charts = [test]
    suc = function.drawAll()
    assert suc


def test_drawAll_2(function):
    def test():
        pass

    function.closing = True
    function.charts = [test]
    suc = function.drawAll()
    assert suc
