# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import pytest
from dataclasses import FrozenInstanceError, replace
from mw4.gui.extWindows.analyse.analyseTypes import (
    AlignmentComparison,
    AlignmentErrors,
    AnalysisFit,
    AnalysisPoint,
    AnalysisTerm,
    ModelAnalysis,
)


@pytest.fixture(scope="module")
def analysisResult() -> ModelAnalysis:
    shared = AnalysisFit(11, (), (), 11, 1, 0.1, 0.2, -0.1, "mismatch", ())
    split = replace(shared, termCount=22, rank=22)
    return ModelAnalysis(
        "test",
        22,
        0.2,
        None,
        None,
        (shared, split),
        11,
        "disagreement",
        (),
    )


def test_primaryIsAuthoritative(analysisResult: ModelAnalysis) -> None:
    assert analysisResult.primary is analysisResult.candidates[1]
    assert analysisResult.betterMatchingTerms == 11
    assert replace(analysisResult, recordedTerms=11).primary is analysisResult.candidates[0]
    assert replace(analysisResult, recordedTerms=None).primary is None


def test_immutableResult(analysisResult: ModelAnalysis) -> None:
    with pytest.raises(FrozenInstanceError):
        analysisResult.recordedTerms = 11


def test_resultUnitsAndUnavailablePoint(analysisResult: ModelAnalysis) -> None:
    assert analysisResult.vectorUnit == "arcsec (east, north)"
    assert analysisResult.alignmentUnit == "degrees"
    term = AnalysisTerm("MA", 1.2, "polar", "W")
    assert term.unit == "arcsec"
    point = AnalysisPoint(0, None, "W", "Missing coordinates", None, None)
    assert point.comparison == "unavailable"
    assert point.residual is None
    assert point.contributions == ()
    errors = AlignmentErrors("W", 0.1, -0.02)
    assert errors.unit == "degrees"
    assert "signed NP" in errors.mapping
    comparison = AlignmentComparison(0.1, 0.1, 0, 0.00005, "match", None)
    assert comparison.unit == "degrees"
    assert analysisResult.primary.alignmentErrors == ()
    assert analysisResult.primary.polarComparison is None
    assert analysisResult.primary.orthoComparison is None
