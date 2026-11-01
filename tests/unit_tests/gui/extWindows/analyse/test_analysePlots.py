# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import gc
import numpy as np
import pytest
from mw4.gui.extWindows.analyse.analyseW import AnalyseWindow
from PySide6.QtWidgets import QApplication
from unittest import mock


@pytest.fixture(autouse=True, scope="module")
def function(qapp, makeApp):
    func = AnalyseWindow(app=makeApp(), title="Analyse")
    yield func
    QApplication.processEvents()
    gc.collect()
    QApplication.processEvents()


def test_draw_raRawErrors(function):
    function.errorRA_S = np.array([0, 1, 2])
    function.errorDEC_S = np.array([0, 1, 2])
    function.azimuth = np.array([0, 1, 2])
    function.altitude = np.array([0, 1, 2])
    function.drawRaRawErrors()


def test_draw_decRawErrors(function):
    function.errorRA_S = np.array([0, 1, 2])
    function.errorDEC_S = np.array([0, 1, 2])
    function.azimuth = np.array([0, 1, 2])
    function.altitude = np.array([0, 1, 2])
    function.drawDecRawErrors()


def test_draw_raErrors(function):
    function.errorRA = np.array([0, 1, 2])
    function.errorDEC = np.array([0, 1, 2])
    function.azimuth = np.array([0, 1, 2])
    function.altitude = np.array([0, 1, 2])
    function.drawRaErrors()


def test_draw_decErrors(function):
    function.errorRA = np.array([0, 1, 2])
    function.errorDEC = np.array([0, 1, 2])
    function.azimuth = np.array([0, 1, 2])
    function.altitude = np.array([0, 1, 2])
    function.drawDecError()


def test_draw_raErrorsRef(function):
    function.angularPosRA = np.array([0, 1, 2])
    function.errorRA = np.array([0, 0, 0])
    function.pierside = ["E", "W", "E"]
    function.drawRaErrorsRef()


def test_draw_decErrorsRef(function):
    function.angularPosDEC = np.array([0, 0, 0])
    function.errorDEC = np.array([0, 0, 0])
    function.pierside = ["E", "W", "E"]
    function.drawDecErrorsRef()


def test_draw_raRawErrorsRef(function):
    function.angularPosRA = np.array([0, 1, 2])
    function.errorRA_S = np.array([0, 0, 0])
    function.pierside = ["E", "W", "E"]
    function.drawRaRawErrorsRef()


def test_draw_decRawErrorsRef(function):
    function.errorDEC_S = np.array([0, 0, 0])
    function.angularPosDEC = np.array([0, 0, 0])
    function.pierside = ["E", "W", "E"]
    function.drawDecRawErrorsRef()


def test_drawDecRef_flipsEastPierErrors(function):
    function.angularPosDEC = np.array([1, 2])
    function.pierside = ["W", "E"]
    with mock.patch.object(function.ui.decErrorsRef, "plot") as plot:
        function.drawDecRef(function.ui.decErrorsRef, np.array([3, 4]))

    assert plot.call_args.args[1] == [3, -4]


def test_draw_scaleImage(function):
    function.errorIndex = np.array([0, 1, 2])
    function.scaleS = np.array([0, 0, 0])
    function.pierside = ["E", "W", "E"]
    function.drawScaleImage()


def test_draw_errorAscending(function):
    function.errorRMS = np.array([0, 1, 2])
    function.errorIndex = np.array([0, 0, 0])
    function.pierside = ["E", "W", "E"]
    function.drawErrorAscending()


def test_draw_errorAscendingKeepsPointsAligned(function):
    function.errorRMS = np.array([0.3, 0.1, 0.2])
    function.errorIndex = np.array([4, 1, 7])
    function.pierside = ["E", "W", "E"]
    with mock.patch.object(function.ui.errorAscending, "plot") as plot:
        function.drawErrorAscending()

    args = plot.call_args.args
    kwargs = plot.call_args.kwargs
    assert args[0] == [1, 7, 4]
    assert args[1] == [0.1, 0.2, 0.3]
    assert kwargs["data"] == ["W", "E", "E"]
    assert kwargs["color"] == [
        function.M_GREEN,
        function.M_YELLOW,
        function.M_YELLOW,
    ]


def test_drawAltAzErrorChart(function):
    function.ui.showISO.setChecked(True)
    with mock.patch.object(function.ui.raRawErrors, "plot") as plot:
        function.drawAltAzErrorChart(function.ui.raRawErrors, np.array([1, 2]))

    assert plot.call_args.kwargs["isoLevels"] == 20


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
