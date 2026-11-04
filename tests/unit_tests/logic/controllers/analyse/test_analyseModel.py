# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import json
import numpy as np
import pytest
from copy import deepcopy
from dataclasses import replace
from mw4.logic.controllers.analyse.analyseModel import (
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
from mw4.logic.controllers.analyse.analyseTypes import AnalysisFit, AnalysisTerm
from mw4.mountcontrol.convert import stringToAngle
from mw4.mountcontrol.model import Model
from pathlib import Path
from typing import Any
from unittest import mock


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
    assert compareSetups(alternative.candidates[0], changedRms, None) == (11, "inconclusive")


def test_comparisonBoundary(syntheticRecords: list[dict[str, Any]]) -> None:
    fit = rebuildModel(syntheticRecords).candidates[0]
    candidates = (
        replace(fit, rmsDifference=0),
        replace(fit, termCount=22, rmsDifference=RMS_TOLERANCE),
    )
    assert compareSetups(*candidates, 22) == (None, "inconclusive")
    candidates = (candidates[0], replace(candidates[1], rmsDifference=RMS_TOLERANCE + 1e-6))
    assert compareSetups(*candidates, 22) == (11, "disagreement")


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
    assert [item.pierside for item in result.primary.residualAlignment] == ["W", "E"]
    assert result.primary.polarComparison.comparison == "unavailable"
    assert "no W/E aggregation" in result.primary.polarComparison.diagnostic
    assert result.primary.orthoComparison.recorded == 0
    assert "Recorded zero is ambiguous" in result.primary.orthoComparison.diagnostic
    assert result.candidates[0].polarComparison.comparison == "unavailable"
    assert not any("cannot be reconstructed" in diagnostic for diagnostic in result.diagnostics)
    np.testing.assert_allclose(
        np.asarray(result.primary.points[0].correction) - result.primary.points[0].observed,
        result.primary.points[0].residual,
    )
    assert any("unverified" in diagnostic for diagnostic in result.diagnostics)


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
    assert result.residualAlignment[0].pierside == "shared"
    assert result.residualAlignment[0].maMeMagnitude == 5
    assert result.residualAlignment[0].npCoefficient == -2
    assert result.polarComparison.recorded == 5
    assert result.orthoComparison.recorded == -2
    for comparison in (result.polarComparison, result.orthoComparison):
        assert comparison.calculated is None
        assert comparison.difference is None
        assert comparison.comparison == "unavailable"
    assert result.polarComparison.tolerance == POLAR_TOLERANCE
    assert result.orthoComparison.tolerance == ORTHO_TOLERANCE
    assert len(result.diagnostics) == 2
    assert result.polarComparison.source == "Polar-axis rotation third column"
    assert result.orthoComparison.source == "Orthogonality angle (radians converted to degrees)"
    assert "correction direction" in result.polarComparison.diagnostic
    assert "NP/CH" in result.orthoComparison.diagnostic
    changed = deriveAlignmentFeedback(alignmentFit, 6, 2)
    assert changed.residualAlignment == result.residualAlignment
    assert changed.polarComparison.recorded == 6
    assert changed.orthoComparison.recorded == 2
    assert changed.polarComparison.difference is None
    assert changed.orthoComparison.difference is None
    assert changed.polarComparison.comparison == changed.orthoComparison.comparison == "unavailable"


def test_splitAlignmentFeedbackPreservesSides(alignmentFit: AnalysisFit) -> None:
    west = tuple(replace(term, pierside="W") for term in alignmentFit.terms)
    east = tuple(
        replace(term, pierside="E", coefficient=-2 * term.coefficient)
        for term in alignmentFit.terms
    )
    result = deriveAlignmentFeedback(replace(alignmentFit, termCount=22, terms=west + east), 5, -2)
    assert [
        (item.pierside, item.maMeMagnitude, item.npCoefficient) for item in result.residualAlignment
    ] == [("W", 5, -2), ("E", 10, 4)]
    for comparison in (result.polarComparison, result.orthoComparison):
        assert comparison.calculated is None
        assert comparison.difference is None
        assert comparison.comparison == "unavailable"
        assert "no W/E aggregation" in comparison.diagnostic
    assert len(result.diagnostics) == 2
    assert result.polarComparison.recorded == 5
    assert result.orthoComparison.recorded == -2


@pytest.mark.parametrize("hourAngle,declination", [(0, 0), (0.7, -0.4), (-2.1, 0.9)])
def test_polarBasisDuplicatesRigidRotation(hourAngle: float, declination: float) -> None:
    h, d = hourAngle, declination
    direction = np.array([np.cos(d) * np.cos(h), np.cos(d) * np.sin(h), np.sin(d)])
    east = np.array([np.sin(h), -np.cos(h), 0])
    north = np.array([-np.sin(d) * np.cos(h), -np.sin(d) * np.sin(h), np.cos(d)])
    tangent = np.array([east, north])
    basis = pointingBasis(h, d, 0.5, "W")
    # Infinitesimal rotations about x and -y reproduce the local MA and ME modes.
    for axis, name in (([1, 0, 0], "MA"), ([0, -1, 0], "ME")):
        rotationMode = tangent @ np.cross(axis, direction)
        np.testing.assert_allclose(basis[:, TPOINT_TERMS.index(name)], rotationMode, atol=1e-15)
    augmented = np.column_stack(
        (basis[:, TPOINT_TERMS.index("MA")], tangent @ np.cross([1, 0, 0], direction))
    )
    assert np.linalg.matrix_rank(augmented) < augmented.shape[1]


@pytest.mark.parametrize("termCount", [11, 22])
def test_feedbackDoesNotChooseNpOrCh(alignmentFit: AnalysisFit, termCount: int) -> None:
    terms = (*alignmentFit.terms, AnalysisTerm("CH", 3600, "model", "shared"))
    if termCount == 22:
        terms = tuple(replace(term, pierside=side) for side in ("W", "E") for term in terms)
    fit = replace(alignmentFit, terms=terms, termCount=termCount)
    for recorded in (-2, 1):
        result = deriveAlignmentFeedback(fit, 5, recorded)
        assert result.terms == terms
        assert all(item.npCoefficient == -2 for item in result.residualAlignment)
        assert result.orthoComparison.recorded == recorded
        assert result.orthoComparison.calculated is None
        assert result.orthoComparison.comparison == "unavailable"
        assert "constrained state recovery" in result.orthoComparison.diagnostic


@pytest.mark.parametrize("recorded", [None, 0])
def test_unavailableRecordedAlignment(alignmentFit: AnalysisFit, recorded: float | None) -> None:
    result = deriveAlignmentFeedback(alignmentFit, recorded, recorded)
    for comparison in (result.polarComparison, result.orthoComparison):
        assert comparison.calculated is None
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
    assert result.residualAlignment[0].maMeMagnitude == 0
    assert result.residualAlignment[0].npCoefficient == 0
    assert result.polarComparison.comparison == result.orthoComparison.comparison == "unavailable"


def test_invalidPolarFeedback(alignmentFit: AnalysisFit) -> None:
    result = deriveAlignmentFeedback(alignmentFit, -5, -2)
    assert result.polarComparison.comparison == "unavailable"
    assert result.polarComparison.recorded == -5
    assert result.polarComparison.difference is None
    assert "nonnegative" in result.polarComparison.diagnostic
    assert result.orthoComparison.comparison == "unavailable"
    assert "polar-axis rotation" in result.polarComparison.diagnostic


def test_unavailableFitAlignment(alignmentFit: AnalysisFit) -> None:
    result = deriveAlignmentFeedback(replace(alignmentFit, terms=(), rms=None), 5, -2)
    assert result.residualAlignment == ()
    assert result.polarComparison.comparison == result.orthoComparison.comparison == "unavailable"
    assert "candidate fit is unavailable" in result.polarComparison.diagnostic


def test_excludedSampleAlignment(alignmentFit: AnalysisFit) -> None:
    result = deriveAlignmentFeedback(alignmentFit, 5, -2, sameSample=False)
    assert len(result.residualAlignment) == 1
    assert result.polarComparison.comparison == result.orthoComparison.comparison == "unavailable"
    assert "Excluded observations" in result.polarComparison.diagnostic


@pytest.mark.parametrize("unavailable", [True, False])
def test_alignmentRetainsIndependentReasons(alignmentFit: AnalysisFit, unavailable: bool) -> None:
    terms = (
        ()
        if unavailable
        else tuple(
            replace(term, pierside=side) for side in ("W", "E") for term in alignmentFit.terms
        )
    )
    result = deriveAlignmentFeedback(
        replace(alignmentFit, terms=terms, termCount=22), -5, None, sameSample=False
    )
    reason = "candidate fit is unavailable" if unavailable else "no W/E aggregation"
    assert reason in result.polarComparison.diagnostic
    assert "Excluded observations" in result.polarComparison.diagnostic
    assert "nonnegative" in result.polarComparison.diagnostic
    assert reason in result.orthoComparison.diagnostic
    assert "Excluded observations" in result.orthoComparison.diagnostic
    assert "missing, nonfinite or inconsistent" in result.orthoComparison.diagnostic


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
        assert changedFit.residualAlignment == originalFit.residualAlignment
        assert changedFit.alignmentState == originalFit.alignmentState
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
