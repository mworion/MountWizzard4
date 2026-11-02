# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from dataclasses import dataclass
from typing import Literal

type SkyVector = tuple[float, float]
type Comparison = Literal["match", "mismatch", "unavailable"]


@dataclass(frozen=True)
class AnalysisTerm:
    name: str
    coefficient: float
    group: Literal["polar", "ortho", "model"]
    pierside: str
    unit: str = "arcsec"


@dataclass(frozen=True)
class AnalysisPoint:
    sourceIndex: int
    countSequence: int | None
    pierside: str
    exclusion: str | None
    observed: SkyVector | None
    recorded: SkyVector | None
    recordedMagnitude: float | None = None
    recordedPositionAngle: float | None = None
    contributions: tuple[SkyVector, ...] = ()
    polar: SkyVector | None = None
    ortho: SkyVector | None = None
    model: SkyVector | None = None
    correction: SkyVector | None = None
    residual: SkyVector | None = None
    difference: SkyVector | None = None
    tolerance: float | None = None
    comparison: Comparison = "unavailable"


@dataclass(frozen=True)
class AnalysisFit:
    termCount: int
    terms: tuple[AnalysisTerm, ...]
    points: tuple[AnalysisPoint, ...]
    rank: int
    condition: float | None
    rms: float | None
    recordedRms: float | None
    rmsDifference: float | None
    rmsComparison: Comparison
    diagnostics: tuple[str, ...]


@dataclass(frozen=True)
class ModelAnalysis:
    source: str
    firmware: str
    recordedTerms: int | None
    recordedRms: float | None
    recordedPolar: float | None
    recordedOrtho: float | None
    candidates: tuple[AnalysisFit, ...]
    betterMatchingTerms: int | None
    setupComparison: Literal["consistent", "disagreement", "inconclusive"]
    diagnostics: tuple[str, ...]
    rmsTolerance: float = 0.05
    vectorUnit: str = "arcsec (east, north)"
    alignmentUnit: str = "degrees"

    @property
    def primary(self) -> AnalysisFit | None:
        return next((fit for fit in self.candidates if fit.termCount == self.recordedTerms), None)
