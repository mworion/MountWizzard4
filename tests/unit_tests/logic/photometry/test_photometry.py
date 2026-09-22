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
# written in python3, (c) 2019-2026 by mworion
# License APL2.0
#
###########################################################

import mw4.logic.photometry.photometry
import numpy as np
import pytest
from mw4.logic.photometry.photometry import Photometry, PhotometrySignals
from mw4.logic.photometry.photometry_analysis import GridGeometry
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from unittest import mock


class Parent:
    try:
        app = App()
    except (RuntimeError, ImportError, AttributeError, ConnectionError, OSError, ValueError):
        app = mock.MagicMock()


def makeGeom(h=200, w=200, fc=3):
    rangeX = np.linspace(0, w, 20)
    rangeY = np.linspace(0, h, 20)
    xm, ym = np.meshgrid(rangeX, rangeY)
    return GridGeometry(h, w, fc, fc, xm, ym)


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    func = Photometry(Parent(), np.zeros((1, 1)))
    yield func


def test_signals(function):
    PhotometrySignals()


def test_workerGetHFR(function):
    function.geom = makeGeom()
    function.xCoord = np.linspace(0, 200, 20)
    function.yCoord = np.linspace(0, 200, 20)
    function.hfr = np.linspace(1, 2, 20)
    function.runnerGetHFR()
    assert function.hfrGrid.shape == (20, 20)


def test_workerGetRoundness(function):
    function.geom = makeGeom()
    rng = np.random.default_rng(1)
    function.xCoord = rng.uniform(0, 200, 20)
    function.yCoord = rng.uniform(0, 200, 20)
    function.elongation = rng.random(20) + 1
    function.runnerGetRoundness()
    assert function.roundnessGrid.shape == (20, 20)


def test_workerCalcTiltValuesSquare(function):
    function.geom = makeGeom(1000, 1000)
    function.xCoord = np.linspace(0, 1000, 20)
    function.yCoord = np.linspace(0, 1000, 20)
    function.hfr = np.linspace(20, 30, 20)
    function.runnerCalcTiltValuesSquare()
    assert function.hfrSegSquare.shape == (3, 3)


def test_workerCalcTiltValuesTriangle(function):
    function.geom = makeGeom(10, 10)
    function.xCoord = np.linspace(0, 100, 20)
    function.yCoord = np.linspace(0, 100, 20)
    function.hfr = np.linspace(20, 30, 20)
    function.runnerCalcTiltValuesTriangle()
    assert function.hfrSegTriangle.size == 72


def test_calcAberrationInspectView_1(function):
    function.image = np.array(np.random.rand(1000, 1000) + 1)
    function.calcAberrationInspectView()
    h, w = function.aberrationImage.shape
    assert w == function.ABERRATION_SIZE * 3
    assert h == function.ABERRATION_SIZE * 3


def test_calcAberrationInspectView_2(function):
    function.image = np.array(np.random.rand(100, 100) + 1)
    function.calcAberrationInspectView()
    h, w = function.aberrationImage.shape
    assert w == function.image.shape[0]
    assert h == function.image.shape[1]


def test_showTabBackground(function):
    function.geom = makeGeom()
    function.bkg = mock.Mock(globalback=2.0)
    function.backSignal = np.random.rand(100, 100) + 1
    function.calcBackground()


def test_showTabBackgroundRMS(function):
    function.geom = makeGeom()
    function.backRMS = np.random.rand(100, 100) + 1
    function.calcBackgroundRMS()


def test_baseCalcs(function):
    function.image = np.array(np.random.rand(1000, 1000) + 1)
    function.baseCalcs()
    assert function.geom is not None
    assert function.w == 1000
    assert function.h == 1000


def test_runCalcs_1(function):
    function.hfr = np.array([1, 2, 3])
    with (
        mock.patch.object(function, "baseCalcs"),
        mock.patch.object(function, "runnerGetHFR"),
        mock.patch.object(function, "runnerCalcTiltValuesSquare"),
        mock.patch.object(function, "runnerCalcTiltValuesTriangle"),
        mock.patch.object(function, "runnerGetRoundness"),
        mock.patch.object(function, "calcAberrationInspectView"),
        mock.patch.object(function, "calcBackground"),
        mock.patch.object(function, "calcBackgroundRMS"),
    ):
        function.runCalcs()


def test_runCalcs_2(function):
    function.hfr = np.array([1] * 20)
    with (
        mock.patch.object(function, "baseCalcs"),
        mock.patch.object(function, "runnerGetHFR"),
        mock.patch.object(function, "runnerCalcTiltValuesSquare"),
        mock.patch.object(function, "runnerCalcTiltValuesTriangle"),
        mock.patch.object(function, "runnerGetRoundness"),
        mock.patch.object(function, "calcAberrationInspectView"),
        mock.patch.object(function, "calcBackground"),
        mock.patch.object(function, "calcBackgroundRMS"),
    ):
        function.runCalcs()


def test_emptyResult(function):
    function.emptyResult()
    assert function.xCoord.size == 0
    assert function.hfr.size == 0
    assert function.elongation.size == 0


def test_runnerCalcPhotometry_success(function):
    function.image = np.array(np.random.rand(100, 100) + 1).astype(np.float32)
    sources = mock.Mock(
        xCoord=np.linspace(0, 100, 20),
        yCoord=np.linspace(0, 100, 20),
        aAxis=np.ones(20),
        bAxis=np.ones(20),
        theta=np.zeros(20),
        hfr=np.ones(20),
        elongation=np.ones(20),
    )
    counts = mock.Mock(raw=30, select=25, signalNoise=22, hfr=20)
    with (
        mock.patch.object(function, "runCalcs"),
        mock.patch.object(
            mw4.logic.photometry.photometry,
            "extractSources",
            return_value=(sources, counts),
        ),
    ):
        function.runnerCalcPhotometry()
        assert function.bkg is not None
        assert len(function.xCoord) == 20
        assert len(function.elongation) == len(function.hfr)


def test_runnerCalcPhotometry_noSources(function):
    function.image = np.array(np.random.rand(100, 100) + 1).astype(np.float32)
    with mock.patch.object(
        mw4.logic.photometry.photometry, "extractSources", return_value=None
    ):
        function.runnerCalcPhotometry()
        assert function.hfr.size == 0


def test_runnerCalcPhotometry_error(function):
    function.image = np.array(np.random.rand(100, 100) + 1).astype(np.float32)
    with mock.patch.object(
        mw4.logic.photometry.photometry, "extractSources", side_effect=ValueError
    ):
        function.runnerCalcPhotometry()
        assert function.hfr.size == 0


def test_processPhotometry_1(function):
    function.image = np.array(np.random.rand(100, 100) + 1)
    with mock.patch.object(function.threadPool, "start"):
        function.processPhotometry(np.array(np.random.rand(100, 100) + 1), 0)


def test_processPhotometry_createsWorkerOnFirstCall(function):
    """Test that processPhotometry creates a worker on first call."""
    function.workerCalcPhotometry = None
    function.image = np.array(np.random.rand(100, 100) + 1)
    with mock.patch("mw4.logic.photometry.photometry.startWorker") as mock_start_worker:
        mock_worker = mock.Mock()
        mock_start_worker.return_value = mock_worker
        function.processPhotometry(np.array(np.random.rand(100, 100) + 1), 0)
        mock_start_worker.assert_called_once_with(
            None,
            function.threadPool,
            function.runnerCalcPhotometry,
            resultMethod=function.signals.photometryFinished.emit,
        )
        assert function.workerCalcPhotometry == mock_worker


def test_processPhotometry_reusesWorker(function):
    """Test that processPhotometry reuses worker on subsequent calls."""
    existing_worker = mock.Mock()
    function.workerCalcPhotometry = existing_worker
    function.image = np.array(np.random.rand(100, 100) + 1)
    with mock.patch("mw4.logic.photometry.photometry.startWorker") as mock_start_worker:
        mock_start_worker.return_value = existing_worker
        function.processPhotometry(np.array(np.random.rand(100, 100) + 1), 0)
        mock_start_worker.assert_called_once_with(
            existing_worker,
            function.threadPool,
            function.runnerCalcPhotometry,
            resultMethod=function.signals.photometryFinished.emit,
        )
        assert function.workerCalcPhotometry == existing_worker
