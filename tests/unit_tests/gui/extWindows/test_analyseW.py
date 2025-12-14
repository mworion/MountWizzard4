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

import json
import numpy as np
import pytest
import unittest.mock as mock
from mw4.gui.extWindows.analyseW import AnalyseWindow
from mw4.gui.utilities.toolsQtWidget import MWidget
from pathlib import Path
from PySide6.QtGui import QCloseEvent, QResizeEvent
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    func = AnalyseWindow(app=App())
    yield func
    func.app.threadPool.waitForDone(10000)


def test_initConfig_1(function):
    function.initConfig()


def test_storeConfig_1(function):
    if "analyseW" in function.app.config:
        del function.app.config["analyseW"]

    function.storeConfig()


def test_storeConfig_2(function):
    function.app.config["analyseW"] = {}

    function.storeConfig()


def test_enableTabsMovable(function):
    function.enableTabsMovable(True)


def test_closeEvent_1(function):
    with mock.patch.object(function, "show"):
        with mock.patch.object(MWidget, "closeEvent"):
            function.showWindow()
            function.closeEvent(QCloseEvent)


def test_resizeEvent(function):
    with mock.patch.object(MWidget, "resizeEvent"):
        function.resizeEvent(QResizeEvent)


def test_showWindow(function):
    with mock.patch.object(function, "show"):
        function.showWindow()


def test_colorChange(function):
    with mock.patch.object(function, "drawAll"):
        function.colorChange()


def test_writeGui_1(function):
    function.writeGui([{"a": 1}], "test")


def test_list_to_array_replaces_none_and_nan(function):
    src = [1.5, None, 3, float("nan"), "4.2", "x"]
    arr = function.list2array(src, fill=0.0, dtype=np.float32)
    expected = np.array([1.5, 0.0, 3.0, 0.0, 4.2, 0.0], dtype=np.float32)
    for i, item in enumerate(src):
        assert expected[i] == arr[i]


def test_generateDataSets(function):
    with open("tests/testData/test.model") as infile:
        modelJSON = json.load(infile)

    function.generateDataSets(modelJSON)
    assert function.latitude == 48.1


def test_processModel_1(function):
    with mock.patch.object(function, "writeGui"):
        with mock.patch.object(function, "generateDataSets"):
            with mock.patch.object(function, "drawAll"):
                function.processModel(Path("tests/testData/test.model"))


def test_processModel_2(function):
    with mock.patch.object(json, "load", return_value={}, side_effect=Exception):
        function.processModel(Path("tests/testData/test.model"))


def test_loadModel_1(function):
    with mock.patch.object(function, "openFile", return_value=Path("test.test")):
        with mock.patch.object(Path, "is_file", return_value=True):
            with mock.patch.object(function, "processModel"):
                function.loadModel()


def test_loadModel_2(function):
    with mock.patch.object(function, "openFile", return_value=Path("test.test")):
        with mock.patch.object(Path, "is_file", return_value=True):
            with mock.patch.object(function, "processModel"):
                function.loadModel()


def test_showAnalyse_1(function):
    with mock.patch.object(function, "processModel"):
        with mock.patch.object(Path, "is_file", return_value=True):
            function.showAnalyse(Path("test.test"))


def test_draw_raRawErrors(function):
    function.errorRA_S = [0, 1, 2]
    function.errorDEC_S = [0, 1, 2]
    function.azimuth = [0, 1, 2]
    function.altitude = [0, 1, 2]
    function.drawRaRawErrors()


def test_draw_decRawErrors(function):
    function.errorRA_S = [0, 1, 2]
    function.errorDEC_S = [0, 1, 2]
    function.azimuth = [0, 1, 2]
    function.altitude = [0, 1, 2]
    function.drawDecRawErrors()


def test_draw_raErrors(function):
    function.errorRA = [0, 1, 2]
    function.errorDEC = [0, 1, 2]
    function.azimuth = [0, 1, 2]
    function.altitude = [0, 1, 2]
    function.drawRaErrors()


def test_draw_decErrors(function):
    function.errorRA = [0, 1, 2]
    function.errorDEC = [0, 1, 2]
    function.azimuth = [0, 1, 2]
    function.altitude = [0, 1, 2]
    function.drawDecError()


def test_draw_raErrorsRef(function):
    function.angularPosRA = [0, 1, 2]
    function.errorRA = [0, 0, 0]
    function.pierside = ["E", "W", "E"]
    function.drawRaErrorsRef()


def test_draw_decErrorsRef(function):
    function.angularPosDEC = [0, 0, 0]
    function.errorDEC = [0, 0, 0]
    function.pierside = ["E", "W", "E"]
    function.drawDecErrorsRef()


def test_draw_raRawErrorsRef(function):
    function.angularPosRA = [0, 1, 2]
    function.errorRA_S = [0, 0, 0]
    function.pierside = ["E", "W", "E"]
    function.drawRaRawErrorsRef()


def test_draw_decRawErrorsRef(function):
    function.errorDEC_S = [0, 0, 0]
    function.angularPosDEC = [0, 0, 0]
    function.pierside = ["E", "W", "E"]
    function.drawDecRawErrorsRef()


def test_draw_scaleImage(function):
    function.index = [0, 1, 2]
    function.scaleS = [0, 0, 0]
    function.pierside = ["E", "W", "E"]
    function.drawScaleImage()


def test_draw_errorAscending(function):
    function.errorRMS = [0, 1, 2]
    function.index = [0, 0, 0]
    function.pierside = ["E", "W", "E"]
    function.drawErrorAscending()


def test_draw_modelPositions_1(function):
    function.altitude = np.array([0, 1, 2])
    function.azimuth = np.array([0, 1, 2])
    function.errorRMS = np.array([0, 2, 4])
    function.errorAngle = np.array([0, 0, 0])
    function.latitude = 48
    function.drawModelPositions()


def test_draw_errorDistribution_1(function):
    function.errorRMS = np.array([0, 2, 4])
    function.errorAngle = np.array([0, 1, 2])
    function.pierside = ["E", "W", "E"]
    function.drawErrorDistribution()


def test_drawHorizon_1(function):
    function.ui.showHorizon.setChecked(False)
    function.drawHorizon()


def test_drawHorizon_2(function):
    function.ui.showHorizon.setChecked(True)
    function.drawHorizon()


def test_linkViewsAltAz_1(function):
    function.ui.linkViews.setChecked(True)
    function.linkViewsAltAz()


def test_linkViewsAltAz_2(function):
    function.ui.linkViews.setChecked(False)
    function.linkViewsAltAz()


def test_linkViewsRa_1(function):
    function.ui.linkViews.setChecked(True)
    function.linkViewsRa()


def test_linkViewsRa_2(function):
    function.ui.linkViews.setChecked(False)
    function.linkViewsRa()


def test_linkViewsDec_1(function):
    function.ui.linkViews.setChecked(True)
    function.linkViewsDec()


def test_linkViewsDec_2(function):
    function.ui.linkViews.setChecked(False)
    function.linkViewsDec()


def test_drawAll_1(function):
    def test():
        pass

    function.index = []
    function.charts = [test]
    with mock.patch.object(function, "linkViewsAltAz"):
        with mock.patch.object(function, "linkViewsRa"):
            with mock.patch.object(function, "linkViewsDec"):
                function.drawAll()


def test_drawAll_2(function):
    def test():
        pass

    function.index = None
    function.charts = [test]
    with mock.patch.object(function, "linkViewsAltAz"):
        with mock.patch.object(function, "linkViewsRa"):
            with mock.patch.object(function, "linkViewsDec"):
                function.drawAll()
