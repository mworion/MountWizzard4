# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from copy import deepcopy
from logging import getLogger
from mw4.base.tpool import Worker, setupWorker, startWorker
from mw4.logic.controllers.analyse.analyseModel import rebuildModel
from mw4.logic.controllers.analyse.analyseTypes import ModelAnalysis
from PySide6.QtCore import QObject, QThreadPool, Slot
from typing import Any, Literal


class AnalyseController(QObject):
    def __init__(self, threadPool: QThreadPool, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.threadPool = threadPool
        self.log = getLogger("MW4")
        self.analysisResult: ModelAnalysis | None = None
        self.analysisStatus: Literal["idle", "running", "ready", "failed"] = "idle"
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
        self.invalidateAnalysis()
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
            self.threadPool,
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
        self.log.debug("Model analysis result: %s", self.analysisResult)

    @Slot(str)
    def failModelAnalysis(self, message: str) -> None:
        if self.activeAnalysisRevision == self.analysisRevision:
            self.analysisStatus = "failed"
            self.analysisError = message
            self.log.warning("Model analysis failed: %s", message)
