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
from mw4.gui.extWindows.analyse.analyseModel import (
    ORTHO_TOLERANCE,
    POLAR_TOLERANCE,
    RMS_TOLERANCE,
    TPOINT_TERMS,
    compareAlignmentError,
    compareSetups,
    consistentMetadata,
    deriveAlignmentFeedback,
    finiteNumber,
    fitCandidate,
    observationPoint,
    pointingBasis,
    programmedAngle,
    rebuildModel,
)
from mw4.gui.extWindows.analyse.analyseTypes import AnalysisFit, AnalysisTerm
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


def test_modelComposition(function: AnalyseWindow) -> None:
    model = function.analyseModel
    assert model.parent() is function
    assert model.thread() == function.thread()
    assert not hasattr(function, "pendingAnalysis")
    assert not hasattr(function, "runnerRebuildModel")


def test_startSnapshotsRecords(function: AnalyseWindow) -> None:
    model = function.analyseModel
    model.invalidateAnalysis()
    records = [{"latitude": 48.1}]
    with mock.patch.object(model, "startPendingAnalysis") as start:
        model.startModelAnalysis(records)
    start.assert_called_once()
    revision, snapshot = model.pendingAnalysis
    assert revision == model.analysisRevision
    assert snapshot == records
    records[0]["latitude"] = 0
    assert snapshot[0]["latitude"] == 48.1
    model.invalidateAnalysis()


def test_processModel_1(function):
    with (
        mock.patch.object(function, "writeGui"),
        mock.patch.object(function.analyseData, "generateDataSets"),
        mock.patch.object(function, "drawAll"),
    ):
        function.processModel(Path("tests/testData/test.model"))


def test_processModel_2(function):
    with mock.patch.object(
        json, "load", return_value={}, side_effect=json.JSONDecodeError("test", "test", 0)
    ):
        function.processModel(Path("tests/testData/test.model"))


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
    result = rebuildModel(syntheticRecords)
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
    result = rebuildModel(records)
    assert result.primary.termCount == 11
    assert result.primary.rms < 1e-7
    assert result.setupComparison == "inconclusive"
    assert result.betterMatchingTerms is None
    assert result.primary.terms[0].coefficient == pytest.approx(7.5, abs=1e-7)


def test_mountTruthAndAlternativeDisagreement(syntheticRecords: list[dict[str, Any]]) -> None:
    first = rebuildModel(syntheticRecords)
    sharedRms = first.candidates[0].rms
    records = [record | {"modelErrorRMS": sharedRms} for record in syntheticRecords]
    alternative = rebuildModel(records)
    assert alternative.primary.termCount == alternative.recordedTerms == 22
    assert alternative.betterMatchingTerms == 11
    assert alternative.setupComparison == "disagreement"
    changed = rebuildModel([record | {"modelTerms": 11} for record in records])
    assert changed.primary.termCount == 11
    assert changed.setupComparison == "consistent"
    for old, new in zip(alternative.candidates, changed.candidates, strict=True):
        assert old.rms == new.rms
        assert old.terms == new.terms
    changedRms = replace(first.candidates[1], rmsDifference=sharedRms)
    assert compareSetups((alternative.candidates[0], changedRms), None) == (11, "inconclusive")


def test_comparisonBoundary(syntheticRecords: list[dict[str, Any]]) -> None:
    fit = rebuildModel(syntheticRecords).candidates[0]
    candidates = (
        replace(fit, rmsDifference=0),
        replace(fit, termCount=22, rmsDifference=RMS_TOLERANCE),
    )
    assert compareSetups(candidates, 22) == (None, "inconclusive")
    candidates = (candidates[0], replace(candidates[1], rmsDifference=RMS_TOLERANCE + 1e-6))
    assert compareSetups(candidates, 22) == (11, "disagreement")


def test_rankDeficiency(syntheticRecords: list[dict[str, Any]]) -> None:
    records = [record for record in syntheticRecords if record["pierside"] == "W"]
    fit = rebuildModel(records).primary
    assert fit.rms is None
    assert fit.rank == 11
    assert "Rank-deficient" in fit.diagnostics[0]
    empty = rebuildModel([])
    assert empty.primary is None
    assert all(fit.rms is None for fit in empty.candidates)


def test_solverFailure(syntheticRecords: list[dict[str, Any]]) -> None:
    with mock.patch("numpy.linalg.lstsq", side_effect=np.linalg.LinAlgError("failure")):
        result = rebuildModel(syntheticRecords)
    assert all("SVD failed" in fit.diagnostics[0] for fit in result.candidates)


@pytest.mark.parametrize("value", [None, -1, float("nan")])
def test_unavailableMetadata(syntheticRecords: list[dict[str, Any]], value: Any) -> None:
    records = [
        record | {"modelTerms": value, "modelErrorRMS": value} for record in syntheticRecords
    ]
    result = rebuildModel(records)
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
    result = rebuildModel(records)
    assert result.primary.points[-2].exclusion == "Duplicate observation"
    assert result.primary.points[-1].residual is None
    assert result.primary.points[0].comparison == "unavailable"
    assert result.primary.rmsComparison == "unavailable"
    assert result.setupComparison == "inconclusive"
    assert any("firmware" in diagnostic for diagnostic in result.diagnostics)


def test_savedMountFixture() -> None:
    records = json.loads(Path("tests/testData/test.model").read_text())
    result = rebuildModel(records)
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
    assert [errors.pierside for errors in result.primary.alignmentErrors] == ["W", "E"]
    assert result.primary.polarComparison.comparison == "unavailable"
    assert "combination rule is unresolved" in result.primary.polarComparison.diagnostic
    assert result.primary.orthoComparison.recorded == 0
    assert "Recorded zero is ambiguous" in result.primary.orthoComparison.diagnostic
    assert result.candidates[0].polarComparison.comparison == "mismatch"
    assert not any("cannot be reconstructed" in diagnostic for diagnostic in result.diagnostics)
    np.testing.assert_allclose(
        np.asarray(result.primary.points[0].correction) - result.primary.points[0].observed,
        result.primary.points[0].residual,
    )
    assert any("unverified" in diagnostic for diagnostic in result.diagnostics)


def test_automaticRebuild(function: AnalyseWindow, qtbot: Any) -> None:
    with mock.patch.object(function, "drawAll"):
        function.processModel(Path("tests/testData/test.model"))
    qtbot.waitUntil(lambda: function.analyseModel.analysisResult is not None)
    assert function.analyseModel.analysisStatus == "ready"
    assert function.analyseModel.analysisResult.primary.termCount == 22
    firstWorker = function.analyseModel.workerRebuildModel
    function.app.threadPool.waitForDone()
    QApplication.processEvents()
    with mock.patch.object(function, "drawAll"):
        function.processModel(Path("tests/testData/test1.model"))
    qtbot.waitUntil(lambda: function.analyseModel.analysisResult is not None)
    assert function.analyseModel.workerRebuildModel is firstWorker
    assert function.analyseModel.activeAnalysisRevision == function.analyseModel.analysisRevision
    assert function.analyseModel.analysisResult.primary.termCount == 22


def test_queuedLoadsAndStaleResults(
    function: AnalyseWindow,
    syntheticRecords: list[dict[str, Any]],
    qtbot: Any,
) -> None:
    entered, release = threading.Event(), threading.Event()

    def blockedRunner(records: list[dict[str, Any]]) -> Any:
        entered.set()
        assert release.wait(5)
        return rebuildModel(records)

    function.app.threadPool.waitForDone()
    QApplication.processEvents()
    function.analyseModel.invalidateAnalysis()
    revision = function.analyseModel.analysisRevision
    with mock.patch(
        "mw4.gui.extWindows.analyse.analyseModel.rebuildModel",
        side_effect=blockedRunner,
    ):
        function.analyseModel.startModelAnalysis(syntheticRecords)
        assert entered.wait(5)
        function.analyseModel.invalidateAnalysis()
        function.analyseModel.startModelAnalysis(syntheticRecords)
        function.analyseModel.invalidateAnalysis()
        latestRecords = [record | {"firmware": "latest"} for record in syntheticRecords]
        function.analyseModel.startModelAnalysis(latestRecords)
        assert function.analyseModel.pendingAnalysis is not None
        release.set()
        qtbot.waitUntil(lambda: function.analyseModel.analysisResult is not None)
    assert function.analyseModel.analysisResult.firmware == "latest"
    assert function.analyseModel.activeAnalysisRevision == function.analyseModel.analysisRevision
    function.analyseModel.invalidateAnalysis()
    function.analyseModel.receiveModelAnalysis((revision, rebuildModel(syntheticRecords)))
    assert function.analyseModel.analysisResult is None


def test_workerFailureAndInvalidation(function: AnalyseWindow, qtbot: Any) -> None:
    function.app.threadPool.waitForDone()
    QApplication.processEvents()
    function.analyseModel.invalidateAnalysis()
    with mock.patch(
        "mw4.gui.extWindows.analyse.analyseModel.rebuildModel",
        side_effect=ValueError("test failure"),
    ):
        function.analyseModel.startModelAnalysis([])
        qtbot.waitUntil(lambda: function.analyseModel.analysisStatus == "failed")
    assert function.analyseModel.analysisResult is None
    assert "test failure" in function.analyseModel.analysisError
    function.analyseModel.invalidateAnalysis()
    function.analyseModel.failModelAnalysis("stale error")
    assert function.analyseModel.analysisStatus == "idle"
    assert function.analyseModel.analysisError is None


def test_undeliveredFailureDoesNotFailNewLoad(
    function: AnalyseWindow,
    syntheticRecords: list[dict[str, Any]],
    qtbot: Any,
) -> None:
    function.app.threadPool.waitForDone()
    QApplication.processEvents()
    function.analyseModel.invalidateAnalysis()
    with mock.patch(
        "mw4.gui.extWindows.analyse.analyseModel.rebuildModel",
        side_effect=ValueError("old failure"),
    ):
        function.analyseModel.startModelAnalysis(syntheticRecords)
        function.app.threadPool.waitForDone()
    assert function.analyseModel.analysisWorkerActive
    function.analyseModel.invalidateAnalysis()
    function.analyseModel.startModelAnalysis(syntheticRecords)
    assert function.analyseModel.pendingAnalysis is not None
    qtbot.waitUntil(lambda: function.analyseModel.analysisResult is not None)
    assert function.analyseModel.activeAnalysisRevision == function.analyseModel.analysisRevision
    assert function.analyseModel.analysisError is None
    assert function.analyseModel.analysisStatus == "ready"


def test_fileReadFailureClearsAnalysis(function: AnalyseWindow) -> None:
    function.analyseModel.analysisResult = rebuildModel([])
    with mock.patch("builtins.open", side_effect=PermissionError("cannot read")):
        function.processModel(Path("unreadable.model"))
    assert function.analyseModel.analysisResult is None


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
    unavailable = rebuildModel([])
    function.analyseModel.receiveModelAnalysis(
        (function.analyseModel.analysisRevision, unavailable)
    )
    assert function.analyseModel.analysisResult == unavailable
    result = rebuildModel(syntheticRecords)
    result = replace(result, setupComparison="disagreement", betterMatchingTerms=11)
    with mock.patch.object(function.log, "warning") as warning:
        function.analyseModel.receiveModelAnalysis((function.analyseModel.analysisRevision, result))
    assert any("setup disagreement" in call.args[0] for call in warning.call_args_list)


@pytest.fixture(scope="module")
def alignmentFit() -> AnalysisFit:
    terms = (
        AnalysisTerm("MA", -10800, "polar", "shared"),
        AnalysisTerm("ME", 14400, "polar", "shared"),
        AnalysisTerm("NP", -7200, "ortho", "shared"),
    )
    return AnalysisFit(11, terms, (), 11, 1, 0, 0, 0, "match", ())


def test_sharedAlignmentFeedback(alignmentFit: AnalysisFit) -> None:
    result = deriveAlignmentFeedback(alignmentFit, 5, -2)
    assert result.alignmentErrors[0].pierside == "shared"
    assert result.alignmentErrors[0].polarError == 5
    assert result.alignmentErrors[0].orthoError == -2
    assert result.polarComparison.calculated == result.polarComparison.recorded == 5
    assert result.orthoComparison.calculated == result.orthoComparison.recorded == -2
    assert result.polarComparison.comparison == result.orthoComparison.comparison == "match"
    assert result.polarComparison.difference == result.orthoComparison.difference == 0
    assert result.polarComparison.tolerance == POLAR_TOLERANCE
    assert result.orthoComparison.tolerance == ORTHO_TOLERANCE
    assert not result.diagnostics
    changed = deriveAlignmentFeedback(alignmentFit, 6, 2)
    assert changed.alignmentErrors == result.alignmentErrors
    assert changed.polarComparison.difference == -1
    assert changed.orthoComparison.difference == -4
    assert changed.polarComparison.comparison == changed.orthoComparison.comparison == "mismatch"


def test_splitAlignmentFeedbackPreservesSides(alignmentFit: AnalysisFit) -> None:
    west = tuple(replace(term, pierside="W") for term in alignmentFit.terms)
    east = tuple(
        replace(term, pierside="E", coefficient=-2 * term.coefficient)
        for term in alignmentFit.terms
    )
    result = deriveAlignmentFeedback(replace(alignmentFit, termCount=22, terms=west + east), 5, -2)
    assert [
        (error.pierside, error.polarError, error.orthoError) for error in result.alignmentErrors
    ] == [("W", 5, -2), ("E", 10, 4)]
    for comparison in (result.polarComparison, result.orthoComparison):
        assert comparison.calculated is None
        assert comparison.difference is None
        assert comparison.comparison == "unavailable"
        assert "combination rule is unresolved" in comparison.diagnostic
    assert len(result.diagnostics) == 1
    assert result.polarComparison.recorded == 5
    assert result.orthoComparison.recorded == -2


@pytest.mark.parametrize("recorded", [None, 0])
def test_unavailableRecordedAlignment(alignmentFit: AnalysisFit, recorded: float | None) -> None:
    result = deriveAlignmentFeedback(alignmentFit, recorded, recorded)
    for comparison in (result.polarComparison, result.orthoComparison):
        assert comparison.calculated is not None
        assert comparison.recorded == recorded
        assert comparison.comparison == "unavailable"
        assert comparison.difference is None
        assert comparison.diagnostic is not None


def test_zeroDerivedAlignment(alignmentFit: AnalysisFit) -> None:
    result = deriveAlignmentFeedback(
        replace(
            alignmentFit, terms=tuple(replace(term, coefficient=0) for term in alignmentFit.terms)
        ),
        0.00001,
        -0.001,
    )
    assert result.alignmentErrors[0].polarError == result.alignmentErrors[0].orthoError == 0
    assert result.polarComparison.comparison == result.orthoComparison.comparison == "match"


def test_invalidPolarFeedback(alignmentFit: AnalysisFit) -> None:
    result = deriveAlignmentFeedback(alignmentFit, -5, -2)
    assert result.polarComparison.comparison == "unavailable"
    assert result.polarComparison.recorded == -5
    assert result.polarComparison.difference is None
    assert "nonnegative" in result.polarComparison.diagnostic
    assert result.orthoComparison.comparison == "match"


def test_unavailableFitAlignment(alignmentFit: AnalysisFit) -> None:
    result = deriveAlignmentFeedback(replace(alignmentFit, terms=(), rms=None), 5, -2)
    assert result.alignmentErrors == ()
    assert result.polarComparison.comparison == result.orthoComparison.comparison == "unavailable"
    assert "candidate fit is unavailable" in result.polarComparison.diagnostic


def test_excludedSampleAlignment(alignmentFit: AnalysisFit) -> None:
    result = deriveAlignmentFeedback(alignmentFit, 5, -2, sameSample=False)
    assert len(result.alignmentErrors) == 1
    assert result.polarComparison.comparison == result.orthoComparison.comparison == "unavailable"
    assert "Excluded observations" in result.polarComparison.diagnostic


@pytest.mark.parametrize("tolerance", [POLAR_TOLERANCE, ORTHO_TOLERANCE])
@pytest.mark.parametrize("sign", [-1, 1])
def test_alignmentToleranceBoundary(tolerance: float, sign: int) -> None:
    inside = compareAlignmentError(0.25 + sign * (tolerance - 1e-13), 0.25, tolerance, None)
    outside = compareAlignmentError(0.25 + sign * (tolerance + 1e-13), 0.25, tolerance, None)
    assert inside.comparison == "match"
    assert outside.comparison == "mismatch"
    assert inside.difference == pytest.approx(sign * tolerance)


def test_rebuildAlignmentMetadataIndependence(syntheticRecords: list[dict[str, Any]]) -> None:
    first = rebuildModel(syntheticRecords)
    changed = rebuildModel(
        [
            record | {"modelPolarError": 1.0, "modelOrthoError": -0.01}
            for record in syntheticRecords
        ],
    )
    for originalFit, changedFit in zip(first.candidates, changed.candidates, strict=True):
        assert changedFit.terms == originalFit.terms
        assert changedFit.alignmentErrors == originalFit.alignmentErrors
        assert changedFit.polarComparison.recorded == 1
        assert changedFit.orthoComparison.recorded == -0.01
    assert changed.primary.termCount == 22
    assert changed.primary.polarComparison.comparison == "unavailable"
    assert changed.primary.polarComparison.calculated is None
    assert changed.recordedPolar == 1
    assert changed.recordedOrtho == -0.01
    inconsistent = deepcopy(syntheticRecords)
    inconsistent[0]["modelPolarError"] = float("nan")
    inconsistent[0]["modelOrthoError"] = None
    result = rebuildModel(inconsistent)
    assert result.recordedPolar is None
    assert result.recordedOrtho is None
    assert result.candidates[0].polarComparison.comparison == "unavailable"
    assert result.candidates[0].orthoComparison.comparison == "unavailable"
