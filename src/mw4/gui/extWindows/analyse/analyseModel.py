# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import numpy as np
from copy import deepcopy
from dataclasses import replace
from mw4.base.tpool import Worker, setupWorker, startWorker
from mw4.gui.extWindows.analyse.analyseTypes import (
    AlignmentComparison,
    AlignmentErrors,
    AnalysisFit,
    AnalysisPoint,
    AnalysisTerm,
    Comparison,
    ModelAnalysis,
    SkyVector,
)
from mw4.mountcontrol.convert import sexagesimalizeToInt
from PySide6.QtCore import QObject, Slot
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from mw4.gui.extWindows.analyse.analyseW import AnalyseWindow

TPOINT_TERMS = ("IH", "ID", "CH", "NP", "MA", "ME", "TF", "HCES", "HCEC", "DCES", "DCEC")
FIT_RCOND = 1e-10
RMS_TOLERANCE = 0.05 + 1e-9
POLAR_TOLERANCE = 0.00005 + 1e-12
ORTHO_TOLERANCE = 0.005 + 1e-12
COORDINATE_KEYS = ("raJNowM", "decJNowM", "raJNowS", "decJNowS", "siderealTime", "latitude")
ANALYSIS_LIMITATIONS = (
    "Local 11-term TPoint basis; firmware term subset, refinement and selection are unverified.",
    "Polar/ortho acquisition corrections are already applied; fitted terms are residuals only.",
    "Polar/ortho feedback is derived in the local linear basis; firmware mapping is unverified.",
    "Legacy producers convert unavailable alignment summaries to zero; recorded zero is ambiguous.",
)


class AnalyseModel(QObject):
    def __init__(self, parentWindow: "AnalyseWindow") -> None:
        super().__init__(parentWindow)
        self.app = parentWindow.app
        self.log = parentWindow.log
        self.analysisResult: ModelAnalysis | None = None
        self.analysisStatus = "idle"
        self.analysisError: str | None = None
        self.analysisWorkerActive = False
        self.analysisRevision = 0
        self.activeAnalysisRevision = 0
        self.workerRebuildModel: Worker | None = None
        self.pendingAnalysis: tuple[int, list[dict[str, Any]]] | None = None

    def invalidateAnalysis(self) -> None:
        self.analysisRevision += 1
        self.analysisResult = None
        self.analysisError = None
        self.pendingAnalysis = None
        self.analysisStatus = "idle"

    def startModelAnalysis(self, records: list[dict[str, Any]]) -> None:
        self.pendingAnalysis = (self.analysisRevision, deepcopy(records))
        self.startPendingAnalysis()

    @staticmethod
    def runnerRebuildModel(
        revision: int, records: list[dict[str, Any]]
    ) -> tuple[int, ModelAnalysis]:
        return revision, rebuildModel(records)

    @Slot()
    def startPendingAnalysis(self) -> None:
        if self.pendingAnalysis is None:
            return
        if self.analysisWorkerActive:
            return
        revision, records = self.pendingAnalysis
        self.pendingAnalysis = None
        self.activeAnalysisRevision = revision
        self.analysisStatus = "running"
        self.analysisWorkerActive = True
        if self.workerRebuildModel is None:
            self.workerRebuildModel = setupWorker(self.runnerRebuildModel)
            self.workerRebuildModel.signals.error.connect(self.failModelAnalysis)
        self.workerRebuildModel = startWorker(
            self.workerRebuildModel,
            self.app.threadPool,
            self.runnerRebuildModel,
            revision,
            records,
            resultMethod=self.receiveModelAnalysis,
            finishedMethod=self.finishModelAnalysis,
        )

    @Slot()
    def finishModelAnalysis(self) -> None:
        self.analysisWorkerActive = False
        self.startPendingAnalysis()

    @Slot(object)
    def receiveModelAnalysis(self, response: tuple[int, ModelAnalysis]) -> None:
        revision, result = response
        if revision != self.analysisRevision:
            return
        self.analysisResult = result
        self.analysisStatus = "ready"
        for diagnostic in result.diagnostics:
            self.log.warning("Model analysis: %s", diagnostic)
        for fit in result.candidates:
            for diagnostic in fit.diagnostics:
                self.log.warning("Model analysis (%s terms): %s", fit.termCount, diagnostic)
        if result.setupComparison == "disagreement":
            self.log.warning(
                "Model analysis setup disagreement: recorded %s terms, closer RMS with %s terms",
                result.recordedTerms,
                result.betterMatchingTerms,
            )

    @Slot(str)
    def failModelAnalysis(self, message: str) -> None:
        if self.activeAnalysisRevision == self.analysisRevision:
            self.analysisStatus = "failed"
            self.analysisError = message
            self.log.warning("Model analysis failed: %s", message)


def finiteNumber(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    try:
        number = float(value)
    except OverflowError:
        return None
    return number if np.isfinite(number) else None


def consistentMetadata(records: list[dict[str, Any]], key: str) -> float | None:
    values = [finiteNumber(record.get(key)) for record in records]
    return values[0] if values and all(value == values[0] for value in values) else None


def recordedVector(record: dict[str, Any]) -> SkyVector | None:
    east, north = finiteNumber(record.get("errorRA")), finiteNumber(record.get("errorDEC"))
    return (east, north) if east is not None and north is not None else None


def programmedAngle(value: float, decimals: int) -> float:
    """Reproduce Model.formatSexagesimal* rounding before reconstructing the fit."""
    sign, whole, minutes, seconds, fraction = sexagesimalizeToInt(value, decimals)
    return sign * (whole + minutes / 60 + (seconds + fraction / 10**decimals) / 3600)


def observationPoint(record: dict[str, Any], index: int) -> AnalysisPoint:
    side = str(record.get("pierside", ""))
    sequence = finiteNumber(record.get("countSequence"))
    count = int(sequence) if sequence is not None and sequence.is_integer() else None
    point = AnalysisPoint(
        index,
        count,
        side,
        None,
        None,
        recordedVector(record),
        recordedMagnitude=finiteNumber(record.get("errorRMS")),
        recordedPositionAngle=finiteNumber(record.get("errorAngle")),
    )
    values = [finiteNumber(record.get(key)) for key in COORDINATE_KEYS]
    if any(value is None for value in values):
        return replace(point, exclusion="Missing or nonfinite observation coordinates")
    if side not in ("E", "W"):
        return replace(point, exclusion="Invalid pier side")
    if record.get("success", True) is not True:
        return replace(point, exclusion="Unsuccessful observation")
    mountRa, mountDec, solvedRa, solvedDec, sidereal, latitude = (
        float(record[key]) for key in COORDINATE_KEYS
    )
    if not (
        0 <= mountRa < 24
        and 0 <= solvedRa < 24
        and 0 <= sidereal < 24
        and abs(mountDec) <= 90
        and abs(solvedDec) < 90
        and abs(latitude) <= 90
    ):
        return replace(point, exclusion="Observation coordinates outside supported ranges")
    mountRa, solvedRa = programmedAngle(mountRa, 1) % 24, programmedAngle(solvedRa, 1) % 24
    mountDec, solvedDec = programmedAngle(mountDec, 1), programmedAngle(solvedDec, 1)
    deltaRa = (solvedRa - mountRa + 12) % 24 - 12
    east = deltaRa * 54000 * np.cos(np.radians(solvedDec))
    north = (solvedDec - mountDec) * 3600
    return replace(point, observed=(float(east), north))


def observationPoints(records: list[dict[str, Any]]) -> tuple[AnalysisPoint, ...]:
    points = []
    seen = set()
    for index, record in enumerate(records):
        point = observationPoint(record, index)
        if point.observed is not None:
            identity = (*(record[key] for key in COORDINATE_KEYS), point.pierside)
            if identity in seen:
                point = replace(point, observed=None, exclusion="Duplicate observation")
            seen.add(identity)
        points.append(point)
    return tuple(points)


def pointingBasis(hourAngle: float, declination: float, latitude: float, side: str) -> np.ndarray:
    """Local linear basis in (east, north), per arcsecond coefficient; angles in radians."""
    h, d, lat = hourAngle, declination, latitude
    sh, ch, sd, cd = np.sin(h), np.cos(h), np.sin(d), np.cos(d)
    sl, cl = np.sin(lat), np.cos(lat)
    sign = 1 if side == "W" else -1
    return np.array(
        [
            [-cd, 0],
            [0, 1],
            [-sign, 0],
            [-sign * sd, 0],
            [ch * sd, sh],
            [-sh * sd, ch],
            [-cl * sh, cl * ch * sd - sl * cd],
            [-sh * cd, 0],
            [-ch * cd, 0],
            [0, sd],
            [0, cd],
        ],
        dtype=np.float64,
    ).T


def termGroup(name: str) -> Literal["polar", "ortho", "model"]:
    if name in ("MA", "ME"):
        return "polar"
    return "ortho" if name == "NP" else "model"


def designMatrix(
    records: list[dict[str, Any]], points: tuple[AnalysisPoint, ...], termCount: int
) -> tuple[np.ndarray, np.ndarray]:
    usable = [point for point in points if point.observed is not None]
    matrix = np.zeros((2 * len(usable), termCount), dtype=np.float64)
    observations = np.empty(2 * len(usable), dtype=np.float64)
    for row, point in enumerate(usable):
        record = records[point.sourceIndex]
        sidereal = programmedAngle(record["siderealTime"], 2)
        solvedRa = programmedAngle(record["raJNowS"], 1) % 24
        h = np.radians((sidereal - solvedRa) * 15)
        basis = pointingBasis(
            h,
            np.radians(programmedAngle(record["decJNowS"], 1)),
            np.radians(record["latitude"]),
            point.pierside,
        )
        offset = 11 if termCount == 22 and point.pierside == "E" else 0
        matrix[2 * row : 2 * row + 2, offset : offset + 11] = basis
        observations[2 * row : 2 * row + 2] = point.observed
    return matrix, observations


def vectorTuple(values: np.ndarray) -> SkyVector:
    return float(values[0]), float(values[1])


def evaluatePoint(
    point: AnalysisPoint,
    basis: np.ndarray,
    coefficients: np.ndarray,
    terms: tuple[AnalysisTerm, ...],
) -> AnalysisPoint:
    contributions = basis * coefficients
    correction = contributions.sum(axis=1)
    # Mount position-angle residuals point from the observed to the modelled position.
    residual = correction - np.asarray(point.observed)
    groups = {
        group: contributions[:, [i for i, term in enumerate(terms) if term.group == group]].sum(
            axis=1
        )
        for group in ("polar", "ortho", "model")
    }
    difference, tolerance = None, None
    comparison: Comparison = "unavailable"
    if point.recorded is not None:
        difference = vectorTuple(residual - point.recorded)
        # Protocol residuals have 0.1" magnitude and integer-degree position angle.
        tolerance = RMS_TOLERANCE + np.linalg.norm(point.recorded) * np.sin(np.radians(0.5))
        comparison = "match" if max(abs(value) for value in difference) <= tolerance else "mismatch"
    return replace(
        point,
        contributions=tuple(vectorTuple(values) for values in contributions.T),
        polar=vectorTuple(groups["polar"]),
        ortho=vectorTuple(groups["ortho"]),
        model=vectorTuple(groups["model"]),
        correction=vectorTuple(correction),
        residual=vectorTuple(residual),
        difference=difference,
        tolerance=None if tolerance is None else float(tolerance),
        comparison=comparison,
    )


def fitCandidate(
    records: list[dict[str, Any]],
    points: tuple[AnalysisPoint, ...],
    termCount: int,
    recordedRms: float | None,
) -> AnalysisFit:
    matrix, observations = designMatrix(records, points, termCount)
    unavailable = AnalysisFit(
        termCount, (), points, 0, None, None, recordedRms, None, "unavailable", ()
    )
    if matrix.shape[0] <= termCount:
        return replace(
            unavailable, diagnostics=("Insufficient observations for a constrained fit.",)
        )
    try:
        coefficients, _, rank, singular = np.linalg.lstsq(matrix, observations, rcond=FIT_RCOND)
    except np.linalg.LinAlgError as error:
        return replace(unavailable, diagnostics=(f"SVD failed: {error}",))
    if rank != termCount:
        return replace(
            unavailable,
            rank=int(rank),
            diagnostics=("Rank-deficient geometry or insufficient pier-side coverage.",),
        )
    scopes = ("shared",) if termCount == 11 else ("W", "E")
    terms = tuple(
        AnalysisTerm(name, float(coefficients[i]), termGroup(name), scope)
        for i, (scope, name) in enumerate((s, n) for s in scopes for n in TPOINT_TERMS)
    )
    evaluated, row = [], 0
    for point in points:
        if point.observed is None:
            evaluated.append(point)
            continue
        evaluated.append(evaluatePoint(point, matrix[2 * row : 2 * row + 2], coefficients, terms))
        row += 1
    residuals = observations - matrix @ coefficients
    rms = float(np.sqrt(np.sum(residuals**2) / row))
    difference = None if recordedRms is None else rms - recordedRms
    comparison: Comparison = (
        "unavailable"
        if difference is None
        else "match"
        if abs(difference) <= RMS_TOLERANCE
        else "mismatch"
    )
    return AnalysisFit(
        termCount,
        terms,
        tuple(evaluated),
        int(rank),
        float(singular[0] / singular[-1]),
        rms,
        recordedRms,
        difference,
        comparison,
        (),
    )


def compareSetups(
    candidates: tuple[AnalysisFit, ...], recordedTerms: int | None
) -> tuple[int | None, Literal["consistent", "disagreement", "inconclusive"]]:
    if any(fit.rmsDifference is None for fit in candidates):
        return None, "inconclusive"
    distances = [abs(fit.rmsDifference) for fit in candidates if fit.rmsDifference is not None]
    if abs(distances[0] - distances[1]) <= RMS_TOLERANCE:
        return None, "inconclusive"
    better = candidates[int(distances[1] < distances[0])].termCount
    if recordedTerms not in (11, 22):
        return better, "inconclusive"
    return better, "consistent" if better == recordedTerms else "disagreement"


def compareAlignmentError(
    calculated: float | None,
    recorded: float | None,
    tolerance: float,
    unresolved: str | None,
) -> AlignmentComparison:
    diagnostics = [] if unresolved is None else [unresolved]
    if recorded is None:
        diagnostics.append("Recorded alignment feedback is missing, nonfinite or inconsistent.")
    elif recorded == 0:
        diagnostics.append(
            "Recorded zero is ambiguous: legacy producers use zero for missing data."
        )
    diagnostic = " ".join(diagnostics) or None
    difference = None
    comparison: Comparison = "unavailable"
    if calculated is not None and recorded is not None and diagnostic is None:
        difference = calculated - recorded
        comparison = "match" if abs(difference) <= tolerance else "mismatch"
    return AlignmentComparison(calculated, recorded, difference, tolerance, comparison, diagnostic)


def deriveAlignmentFeedback(
    fit: AnalysisFit,
    recordedPolar: float | None,
    recordedOrtho: float | None,
    sameSample: bool = True,
) -> AnalysisFit:
    errors = []
    for scope in dict.fromkeys(term.pierside for term in fit.terms):
        coefficients = {term.name: term.coefficient for term in fit.terms if term.pierside == scope}
        errors.append(
            AlignmentErrors(
                scope,
                float(np.hypot(coefficients["MA"], coefficients["ME"])) / 3600,
                coefficients["NP"] / 3600,
            )
        )
    unresolved = None
    polar, ortho = None, None
    if not errors:
        unresolved = "Alignment feedback cannot be derived: the candidate fit is unavailable."
    elif fit.termCount == 22:
        unresolved = (
            "Per-side errors are derived; the firmware's pier-side combination rule is unresolved."
        )
    else:
        polar, ortho = errors[0].polarError, errors[0].orthoError
    if not sameSample:
        unresolved = "Excluded observations: fitted samples differ from the mount's."
    polarComparison = compareAlignmentError(polar, recordedPolar, POLAR_TOLERANCE, unresolved)
    if recordedPolar is not None and recordedPolar < 0:
        polarComparison = replace(
            polarComparison,
            difference=None,
            comparison="unavailable",
            diagnostic="Recorded polar error must be a nonnegative magnitude.",
        )
    orthoComparison = compareAlignmentError(ortho, recordedOrtho, ORTHO_TOLERANCE, unresolved)
    diagnostics = tuple(
        dict.fromkeys(
            comparison.diagnostic
            for comparison in (polarComparison, orthoComparison)
            if comparison.diagnostic is not None
        )
    )
    return replace(
        fit,
        alignmentErrors=tuple(errors),
        polarComparison=polarComparison,
        orthoComparison=orthoComparison,
        diagnostics=fit.diagnostics + diagnostics,
    )


def rebuildModel(records: list[dict[str, Any]]) -> ModelAnalysis:
    points = observationPoints(records)
    recordedTerms = consistentMetadata(records, "modelTerms")
    terms = int(recordedTerms) if recordedTerms in (11, 22) else None
    recordedRms = consistentMetadata(records, "modelErrorRMS")
    if recordedRms is not None and recordedRms < 0:
        recordedRms = None
    candidates = tuple(fitCandidate(records, points, size, recordedRms) for size in (11, 22))
    recordedPolar = consistentMetadata(records, "modelPolarError")
    recordedOrtho = consistentMetadata(records, "modelOrthoError")
    better, comparison = compareSetups(candidates, terms)
    diagnostics = list(ANALYSIS_LIMITATIONS)
    if terms is None:
        diagnostics.append("Missing, inconsistent or unsupported recorded modelTerms.")
    if recordedRms is None:
        diagnostics.append("Missing, inconsistent or invalid recorded modelErrorRMS.")
    sameSample = not any(point.exclusion for point in points)
    if not sameSample:
        diagnostics.append(
            "Excluded observations: RMS may not represent the mount's fitted sample."
        )
        candidates = tuple(replace(fit, rmsComparison="unavailable") for fit in candidates)
        better, comparison = None, "inconclusive"
    candidates = tuple(
        deriveAlignmentFeedback(fit, recordedPolar, recordedOrtho, sameSample) for fit in candidates
    )
    if len({str(record.get("firmware", "")) for record in records}) > 1:
        diagnostics.append("Inconsistent firmware metadata.")
    return ModelAnalysis(
        str(records[0].get("firmware", "")) if records else "",
        terms,
        recordedRms,
        recordedPolar,
        recordedOrtho,
        candidates,
        better,
        comparison,
        tuple(diagnostics),
        RMS_TOLERANCE,
    )
