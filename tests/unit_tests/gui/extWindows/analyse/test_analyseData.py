# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import gc
import json
import numpy as np
import pytest
import threading
from copy import deepcopy
from dataclasses import replace
from mw4.gui.extWindows.analyse.analyseData import (
    RMS_TOLERANCE,
    TPOINT_TERMS,
    compareSetups,
    consistentMetadata,
    finiteNumber,
    fitCandidate,
    observationPoint,
    pointingBasis,
    programmedAngle,
    rebuildModel,
)
from mw4.gui.extWindows.analyse.analyseW import AnalyseWindow
from mw4.mountcontrol.convert import stringToAngle
from mw4.mountcontrol.model import Model
from pathlib import Path
from PySide6.QtWidgets import QApplication
from typing import Any
from unittest import mock


@pytest.fixture(autouse=True, scope="module")
def function(qapp, makeApp):
    func = AnalyseWindow(app=makeApp(), title="Analyse")
    yield func
    QApplication.processEvents()
    gc.collect()
    QApplication.processEvents()


def test_writeGui_1(function):
    function.writeGui([{"a": 1}], Path("test"))


def test_list_to_array_replaces_none_and_nan(function):
    src = [1.5, None, 3, float("nan"), "4.2", "x"]
    arr = function.list2array(src, fill=0.0, dtype=np.float32)
    expected = np.array([1.5, 0.0, 3.0, 0.0, 4.2, 0.0], dtype=np.float32)
    for i, _item in enumerate(src):
        assert expected[i] == arr[i]


def test_list2array_handlesUnconvertibleValues(function):
    arr = function.list2array([{}, 10**4000])
    assert arr.tolist() == [0.0, 0.0]


def test_generateDataSets(function):
    with open("tests/testData/test.model") as infile:
        modelJSON = json.load(infile)

    function.generateDataSets(modelJSON)
    assert function.latitude == 48.1


def test_validateModelData(function):
    with open("tests/testData/test.model") as infile:
        validModel = json.load(infile)

    assert function.validateModelData(validModel) is None
    assert function.validateModelData({}) is not None
    assert function.validateModelData([None]) is not None
    assert function.validateModelData([{"latitude": 48.1}]) is not None

    noLatitude = [record.copy() for record in validModel]
    del noLatitude[0]["latitude"]
    assert function.validateModelData(noLatitude) is not None

    invalidLatitude = [record.copy() for record in validModel]
    invalidLatitude[0]["latitude"] = "48.1"
    assert function.validateModelData(invalidLatitude) is not None

    booleanLatitude = [record.copy() for record in validModel]
    booleanLatitude[0]["latitude"] = True
    assert function.validateModelData(booleanLatitude) is not None


def test_processModel_1(function):
    with (
        mock.patch.object(function, "writeGui"),
        mock.patch.object(function, "generateDataSets"),
        mock.patch.object(function, "drawAll"),
    ):
        function.processModel(Path("tests/testData/test.model"))


def test_processModel_2(function):
    with mock.patch.object(
        json, "load", return_value={}, side_effect=json.JSONDecodeError("test", "test", 0)
    ):
        function.processModel(Path("tests/testData/test.model"))


@pytest.mark.parametrize("modelJSON", [[], [{"latitude": 48.1}]])
def test_processModel_invalidData(function, modelJSON):
    with (
        mock.patch.object(json, "load", return_value=modelJSON),
        mock.patch.object(function.log, "warning") as warning,
        mock.patch.object(function, "writeGui") as writeGui,
        mock.patch.object(function, "generateDataSets") as generateDataSets,
    ):
        function.processModel(Path("tests/testData/test.model"))

    warning.assert_called_once()
    writeGui.assert_not_called()
    generateDataSets.assert_not_called()


@pytest.fixture(scope="module")
def syntheticRecords() -> list[dict[str, Any]]:
    rng = np.random.default_rng(42)
    records = []
    for index in range(100):
        h, d = rng.uniform(-2.8, 2.8), rng.uniform(-1.1, 1.1)
        side = "W" if index % 2 else "E"
        # Independent observations: a pier-side-specific HA index and Dec offset.
        indexError = 30 if side == "W" else -21
        north = 4 if side == "W" else -3
        solvedRa = np.round((12 - np.degrees(h) / 15) * 36000) / 36000
        solvedDec = np.round(np.degrees(d) * 36000) / 36000
        east = -indexError * np.cos(np.radians(solvedDec))
        records.append(
            {
                "countSequence": index,
                "pierside": side,
                "success": True,
                "raJNowM": solvedRa - east / (54000 * np.cos(np.radians(solvedDec))),
                "raJNowS": solvedRa,
                "decJNowM": solvedDec - north / 3600,
                "decJNowS": solvedDec,
                "siderealTime": 12.0,
                "latitude": 48.0,
                "modelTerms": 22,
                "modelErrorRMS": 0.0,
                "modelPolarError": 0.1,
                "modelOrthoError": 0.02,
                "errorRA": 0.0,
                "errorDEC": 0.0,
                "firmware": "synthetic",
            }
        )
    return records


@pytest.mark.parametrize("value", [True, "1", None, float("nan"), float("inf"), 10**4000])
def test_finiteNumberRejectsInvalid(value: Any) -> None:
    assert finiteNumber(value) is None


def test_metadataConsistency() -> None:
    assert consistentMetadata([], "x") is None
    assert consistentMetadata([{"x": 1}, {"x": 2}], "x") is None
    assert consistentMetadata([{"x": 1}, {"x": 1}], "x") == 1


def test_basisCardinalDirections() -> None:
    expected = np.array(
        [
            [-1, 0, -1, 0, 0, 0, 0, 0, -1, 0, 0],
            [0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
        ]
    )
    np.testing.assert_allclose(pointingBasis(0, 0, 0, "W"), expected, atol=1e-14)
    west = pointingBasis(np.pi / 2, np.pi / 6, np.pi / 6, "W")
    east = pointingBasis(np.pi / 2, np.pi / 6, np.pi / 6, "E")
    np.testing.assert_allclose(west[:, 2:4], -east[:, 2:4])
    assert west[0, 3] == pytest.approx(-0.5)
    assert west[0, 5] == pytest.approx(-0.5)
    assert west[1, 4] == pytest.approx(1)
    assert west[1, 6] == pytest.approx(-np.sqrt(3) / 4)


@pytest.mark.parametrize(
    ("field", "value", "reason"),
    [
        ("raJNowM", None, "Missing"),
        ("raJNowS", float("inf"), "Missing"),
        ("raJNowM", 24, "outside"),
        ("raJNowS", -1, "outside"),
        ("decJNowM", -91, "outside"),
        ("decJNowS", 90, "outside"),
        ("siderealTime", 25, "outside"),
        ("latitude", 91, "outside"),
        ("pierside", "?", "Invalid"),
        ("success", False, "Unsuccessful"),
    ],
)
def test_observationExclusions(
    syntheticRecords: list[dict[str, Any]],
    field: str,
    value: Any,
    reason: str,
) -> None:
    point = observationPoint(syntheticRecords[0] | {field: value}, 0)
    assert point.observed is None
    assert reason in point.exclusion


def test_observationWrapping(syntheticRecords: list[dict[str, Any]]) -> None:
    record = syntheticRecords[0] | {
        "raJNowM": 23.999,
        "raJNowS": 0.001,
        "decJNowM": 0,
        "decJNowS": 0,
        "errorRA": None,
        "countSequence": 1.5,
    }
    point = observationPoint(record, 9)
    assert point.observed == pytest.approx((108, 0))
    assert point.recorded is None
    assert point.countSequence is None
    assert point.sourceIndex == 9


def test_splitRecoveryAndContributions(syntheticRecords: list[dict[str, Any]]) -> None:
    result = rebuildModel(syntheticRecords, "synthetic.model")
    fit = result.primary
    assert fit is not None
    assert fit.rank == fit.termCount == 22
    assert fit.condition > 1
    assert fit.rms < 1e-7
    assert fit.rmsComparison == "match"
    assert result.recordedTerms == 22
    assert result.betterMatchingTerms == 22
    assert result.setupComparison == "consistent"
    assert result.recordedPolar == 0.1
    assert result.recordedOrtho == 0.02
    assert [term.name for term in fit.terms[:11]] == list(TPOINT_TERMS)
    coefficients = {(term.pierside, term.name): term.coefficient for term in fit.terms}
    assert coefficients["W", "IH"] == pytest.approx(30, abs=1e-7)
    assert coefficients["E", "IH"] == pytest.approx(-21, abs=1e-7)
    assert coefficients["W", "ID"] == pytest.approx(4, abs=1e-7)
    assert coefficients["E", "ID"] == pytest.approx(-3, abs=1e-7)
    for point in fit.points:
        assert point.comparison == "match"
        np.testing.assert_allclose(np.sum(point.contributions, axis=0), point.correction)
        np.testing.assert_allclose(
            np.asarray(point.polar) + point.ortho + point.model,
            point.correction,
            atol=1e-10,
        )
        np.testing.assert_allclose(point.residual, (0, 0), atol=1e-7)
    assert result.candidates[0].rmsComparison == "mismatch"
    assert any(point.comparison == "mismatch" for point in result.candidates[0].points)


def test_sharedRecovery(syntheticRecords: list[dict[str, Any]]) -> None:
    records = deepcopy(syntheticRecords)
    for record in records:
        record["raJNowM"] = record["raJNowS"] + 7.5 / 54000
        record["decJNowM"] = record["decJNowS"] - 2 / 3600
        record["modelTerms"] = 11
    result = rebuildModel(records, "shared")
    assert result.primary.termCount == 11
    assert result.primary.rms < 1e-7
    assert result.setupComparison == "inconclusive"
    assert result.betterMatchingTerms is None
    assert result.primary.terms[0].coefficient == pytest.approx(7.5, abs=1e-7)


def test_mountTruthAndAlternativeDisagreement(syntheticRecords: list[dict[str, Any]]) -> None:
    first = rebuildModel(syntheticRecords, "split")
    sharedRms = first.candidates[0].rms
    records = [record | {"modelErrorRMS": sharedRms} for record in syntheticRecords]
    alternative = rebuildModel(records, "alternative")
    assert alternative.primary.termCount == alternative.recordedTerms == 22
    assert alternative.betterMatchingTerms == 11
    assert alternative.setupComparison == "disagreement"
    changed = rebuildModel([record | {"modelTerms": 11} for record in records], "changed")
    assert changed.primary.termCount == 11
    assert changed.setupComparison == "consistent"
    for old, new in zip(alternative.candidates, changed.candidates, strict=True):
        assert old.rms == new.rms
        assert old.terms == new.terms
    changedRms = replace(first.candidates[1], rmsDifference=sharedRms)
    assert compareSetups((alternative.candidates[0], changedRms), None) == (11, "inconclusive")


def test_comparisonBoundary(syntheticRecords: list[dict[str, Any]]) -> None:
    fit = rebuildModel(syntheticRecords, "boundary").candidates[0]
    candidates = (
        replace(fit, rmsDifference=0),
        replace(fit, termCount=22, rmsDifference=RMS_TOLERANCE),
    )
    assert compareSetups(candidates, 22) == (None, "inconclusive")
    candidates = (candidates[0], replace(candidates[1], rmsDifference=RMS_TOLERANCE + 1e-6))
    assert compareSetups(candidates, 22) == (11, "disagreement")


def test_rankDeficiency(syntheticRecords: list[dict[str, Any]]) -> None:
    records = [record for record in syntheticRecords if record["pierside"] == "W"]
    fit = rebuildModel(records, "one-side").primary
    assert fit.rms is None
    assert fit.rank == 11
    assert "Rank-deficient" in fit.diagnostics[0]
    empty = rebuildModel([], "empty")
    assert empty.primary is None
    assert all(fit.rms is None for fit in empty.candidates)


def test_solverFailure(syntheticRecords: list[dict[str, Any]]) -> None:
    with mock.patch("numpy.linalg.lstsq", side_effect=np.linalg.LinAlgError("failure")):
        result = rebuildModel(syntheticRecords, "solver")
    assert all("SVD failed" in fit.diagnostics[0] for fit in result.candidates)


@pytest.mark.parametrize("value", [None, -1, float("nan")])
def test_unavailableMetadata(syntheticRecords: list[dict[str, Any]], value: Any) -> None:
    records = [
        record | {"modelTerms": value, "modelErrorRMS": value} for record in syntheticRecords
    ]
    result = rebuildModel(records, "unavailable")
    assert result.primary is None
    assert result.recordedRms is None
    assert result.setupComparison == "inconclusive"
    assert all(fit.rmsComparison == "unavailable" for fit in result.candidates)


def test_exclusionsAndInconsistentMetadata(syntheticRecords: list[dict[str, Any]]) -> None:
    records = deepcopy(syntheticRecords)
    records[0]["firmware"] = "other"
    records[0]["errorRA"] = None
    records.append(records[1].copy())
    records.append(records[2] | {"success": False})
    result = rebuildModel(records, "duplicate")
    assert result.primary.points[-2].exclusion == "Duplicate observation"
    assert result.primary.points[-1].residual is None
    assert result.primary.points[0].comparison == "unavailable"
    assert result.primary.rmsComparison == "unavailable"
    assert result.setupComparison == "inconclusive"
    assert any("firmware" in diagnostic for diagnostic in result.diagnostics)


def test_savedMountFixture() -> None:
    records = json.loads(Path("tests/testData/test.model").read_text())
    result = rebuildModel(records, "test.model")
    assert result.primary.termCount == 22
    assert result.firmware == "2.16.11"
    assert result.primary.rank == 22
    assert result.primary.rms == pytest.approx(1.0966324212, abs=1e-8)
    assert result.recordedRms == 1.1
    assert result.primary.rmsComparison == "match"
    assert result.setupComparison == "consistent"
    assert sum(point.comparison == "match" for point in result.primary.points) == 57
    assert sum(point.comparison == "unavailable" for point in result.primary.points) == 1
    assert result.primary.points[0].recordedMagnitude == 1.2
    assert result.primary.points[0].recordedPositionAngle == 274
    np.testing.assert_allclose(
        np.asarray(result.primary.points[0].correction) - result.primary.points[0].observed,
        result.primary.points[0].residual,
    )
    assert any("unverified" in diagnostic for diagnostic in result.diagnostics)


def test_automaticRebuild(function: AnalyseWindow, qtbot: Any) -> None:
    with mock.patch.object(function, "drawAll"):
        function.processModel(Path("tests/testData/test.model"))
    qtbot.waitUntil(lambda: function.analysisResult is not None)
    assert function.analysisStatus == "ready"
    assert function.analysisResult.primary.termCount == 22
    firstWorker = function.workerRebuildModel
    function.app.threadPool.waitForDone()
    QApplication.processEvents()
    with mock.patch.object(function, "drawAll"):
        function.processModel(Path("tests/testData/test1.model"))
    qtbot.waitUntil(lambda: function.analysisResult is not None)
    assert function.workerRebuildModel is firstWorker
    assert function.analysisResult.source.endswith("test1.model")


def test_queuedLoadsAndStaleResults(
    function: AnalyseWindow,
    syntheticRecords: list[dict[str, Any]],
    qtbot: Any,
) -> None:
    entered, release = threading.Event(), threading.Event()

    def blockedRunner(records: list[dict[str, Any]], source: str) -> Any:
        entered.set()
        assert release.wait(5)
        return rebuildModel(records, source)

    function.app.threadPool.waitForDone()
    QApplication.processEvents()
    function.invalidateAnalysis()
    revision = function.analysisRevision
    with mock.patch(
        "mw4.gui.extWindows.analyse.analyseData.rebuildModel",
        side_effect=blockedRunner,
    ):
        function.pendingAnalysis = (revision, "old", syntheticRecords)
        function.startModelAnalysis()
        assert entered.wait(5)
        function.invalidateAnalysis()
        function.pendingAnalysis = (function.analysisRevision, "new", syntheticRecords)
        function.startModelAnalysis()
        assert function.pendingAnalysis is not None
        release.set()
        qtbot.waitUntil(lambda: function.analysisResult is not None)
    assert function.analysisResult.source == "new"
    function.invalidateAnalysis()
    function.receiveModelAnalysis((revision, rebuildModel(syntheticRecords, "stale")))
    assert function.analysisResult is None


def test_workerFailureAndInvalidation(function: AnalyseWindow, qtbot: Any) -> None:
    function.app.threadPool.waitForDone()
    QApplication.processEvents()
    function.invalidateAnalysis()
    with mock.patch(
        "mw4.gui.extWindows.analyse.analyseData.rebuildModel",
        side_effect=ValueError("test failure"),
    ):
        function.pendingAnalysis = (function.analysisRevision, "error", [])
        function.startModelAnalysis()
        qtbot.waitUntil(lambda: function.analysisStatus == "failed")
    assert function.analysisResult is None
    assert "test failure" in function.analysisError
    function.invalidateAnalysis()
    function.failModelAnalysis("stale error")
    assert function.analysisStatus == "idle"
    assert function.analysisError is None


def test_undeliveredFailureDoesNotFailNewLoad(
    function: AnalyseWindow,
    syntheticRecords: list[dict[str, Any]],
    qtbot: Any,
) -> None:
    function.app.threadPool.waitForDone()
    QApplication.processEvents()
    function.invalidateAnalysis()
    with mock.patch(
        "mw4.gui.extWindows.analyse.analyseData.rebuildModel",
        side_effect=ValueError("old failure"),
    ):
        function.pendingAnalysis = (function.analysisRevision, "old failure", syntheticRecords)
        function.startModelAnalysis()
        function.app.threadPool.waitForDone()
    assert function.analysisWorkerActive
    function.invalidateAnalysis()
    function.pendingAnalysis = (function.analysisRevision, "latest", syntheticRecords)
    function.startModelAnalysis()
    assert function.pendingAnalysis is not None
    qtbot.waitUntil(lambda: function.analysisResult is not None)
    assert function.analysisResult.source == "latest"
    assert function.analysisError is None
    assert function.analysisStatus == "ready"


def test_fileReadFailureClearsAnalysis(function: AnalyseWindow) -> None:
    function.analysisResult = rebuildModel([], "old")
    with mock.patch("builtins.open", side_effect=PermissionError("cannot read")):
        function.processModel(Path("unreadable.model"))
    assert function.analysisResult is None


def test_allCoefficients(syntheticRecords: list[dict[str, Any]]) -> None:
    records = deepcopy(syntheticRecords)
    expected = np.arange(1, 12, dtype=float)
    observations = []
    for record in records:
        h = np.radians((record["siderealTime"] - record["raJNowS"]) * 15)
        d, lat = np.radians(record["decJNowS"]), np.radians(record["latitude"])
        sign = 1 if record["pierside"] == "W" else -1
        # Expanded equations, independent of production matrix assembly/evaluation.
        east = (
            -np.cos(d)
            - 3 * sign
            - 4 * sign * np.sin(d)
            + 5 * np.cos(h) * np.sin(d)
            - 6 * np.sin(h) * np.sin(d)
            - 7 * np.cos(lat) * np.sin(h)
            - 8 * np.sin(h) * np.cos(d)
            - 9 * np.cos(h) * np.cos(d)
        )
        north = (
            2
            + 5 * np.sin(h)
            + 6 * np.cos(h)
            + 7 * (np.cos(lat) * np.cos(h) * np.sin(d) - np.sin(lat) * np.cos(d))
            + 10 * np.sin(d)
            + 11 * np.cos(d)
        )
        record["raJNowM"] = record["raJNowS"] - east / (54000 * np.cos(d))
        record["decJNowM"] = record["decJNowS"] - north / 3600
        record["modelTerms"] = 11
        observations.append((east, north))
    points = tuple(
        replace(observationPoint(record, i), observed=observations[i])
        for i, record in enumerate(records)
    )
    result = fitCandidate(records, points, 11, 0)
    np.testing.assert_allclose(
        [term.coefficient for term in result.terms],
        expected,
        atol=1e-7,
    )
    assert result.rms < 1e-7


@pytest.mark.parametrize("value", [0.0, -0.123456, 23.999999, 13.123456])
def test_programmedPrecision(value: float) -> None:
    assert abs(programmedAngle(value, 1)) == pytest.approx(
        abs(stringToAngle(Model.formatSexagesimalDec(value)).degrees),
        abs=1e-14,
    )
    assert np.sign(programmedAngle(value, 1)) == np.sign(value)
    assert programmedAngle(abs(value), 1) % 24 == pytest.approx(
        stringToAngle(Model.formatSexagesimalRA(abs(value)), "hours").hours,
        abs=1e-14,
    )
    assert programmedAngle(abs(value), 2) == pytest.approx(
        stringToAngle(Model.formatSexagesimalSidereal(abs(value)), "hours").hours,
        abs=1e-14,
    )


def test_receiveUnavailableAndDisagreement(
    function: AnalyseWindow,
    syntheticRecords: list[dict[str, Any]],
) -> None:
    unavailable = rebuildModel([], "empty")
    function.receiveModelAnalysis((function.analysisRevision, unavailable))
    assert function.analysisResult == unavailable
    result = rebuildModel(syntheticRecords, "disagreement")
    result = replace(result, setupComparison="disagreement", betterMatchingTerms=11)
    with mock.patch.object(function.log, "warning") as warning:
        function.receiveModelAnalysis((function.analysisRevision, result))
    assert any("setup disagreement" in call.args[0] for call in warning.call_args_list)
