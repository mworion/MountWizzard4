# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import json
import pytest
from dataclasses import replace
from mw4.logic.controllers.analyse.analyseController import AnalyseController
from mw4.logic.controllers.analyse.analyseModel import rebuildModel
from pathlib import Path
from PySide6.QtCore import QThreadPool
from typing import Any
from unittest import mock


@pytest.fixture(scope="module")
def controller() -> AnalyseController:
    return AnalyseController(QThreadPool.globalInstance())


def test_independentOfWindow(controller: AnalyseController) -> None:
    assert controller.parent() is None
    assert controller.threadPool is QThreadPool.globalInstance()
    assert not hasattr(controller, "app")
    assert not hasattr(controller, "ui")
    assert not hasattr(controller, "parentWindow")
    assert controller.runnerRebuildModel(7, []) == (7, rebuildModel([]))


def test_backgroundWithoutWindow(controller: AnalyseController, qtbot: Any) -> None:
    controller.startModelAnalysis([])
    qtbot.waitUntil(
        lambda: controller.analysisResult is not None and not controller.analysisWorkerActive
    )
    assert controller.analysisStatus == "ready"
    assert controller.analysisResult == rebuildModel([])
    controller.invalidateAnalysis()
    assert controller.analysisResult is None


def test_reusesWorker(controller: AnalyseController, qtbot: Any) -> None:
    controller.startModelAnalysis([])
    qtbot.waitUntil(lambda: not controller.analysisWorkerActive)
    worker = controller.workerRebuildModel
    assert worker is not None
    controller.startModelAnalysis([])
    qtbot.waitUntil(lambda: not controller.analysisWorkerActive)
    assert controller.workerRebuildModel is worker
    assert controller.analysisResult == rebuildModel([])
    controller.invalidateAnalysis()


def test_queuesLatestSnapshot(controller: AnalyseController) -> None:
    controller.analysisWorkerActive = True
    try:
        controller.startModelAnalysis([{"latitude": 48.1}])
        records = [{"latitude": 49.2}]
        controller.startModelAnalysis(records)
        assert controller.pendingAnalysis == (controller.analysisRevision, records)
        records[0]["latitude"] = 0
        assert controller.pendingAnalysis[1] == [{"latitude": 49.2}]
        assert controller.analysisResult is None
        with mock.patch.object(controller, "startPendingAnalysis") as start:
            controller.finishModelAnalysis()
        start.assert_called_once_with()
        assert not controller.analysisWorkerActive
    finally:
        controller.analysisWorkerActive = False
        controller.invalidateAnalysis()


def test_ignoresStaleResults(controller: AnalyseController) -> None:
    controller.invalidateAnalysis()
    result = rebuildModel([])
    controller.receiveModelAnalysis((controller.analysisRevision - 1, result))
    assert controller.analysisResult is None
    assert controller.analysisStatus == "idle"


def test_failureAndStaleError(controller: AnalyseController) -> None:
    controller.invalidateAnalysis()
    controller.activeAnalysisRevision = controller.analysisRevision
    with mock.patch.object(controller.log, "warning") as warning:
        controller.failModelAnalysis("current failure")
    warning.assert_called_once_with("Model analysis failed: %s", "current failure")
    assert controller.analysisStatus == "failed"
    assert controller.analysisError == "current failure"
    assert controller.analysisResult is None
    controller.invalidateAnalysis()
    with mock.patch.object(controller.log, "warning") as warning:
        controller.failModelAnalysis("stale failure")
    warning.assert_not_called()
    assert controller.analysisStatus == "idle"
    assert controller.analysisError is None


def test_publishesDiagnostics(controller: AnalyseController) -> None:
    records = json.loads(Path("tests/testData/test.model").read_text())
    result = rebuildModel(records)
    fit = replace(result.candidates[0], diagnostics=("fit diagnostic",))
    result = replace(
        result,
        diagnostics=("result diagnostic",),
        candidates=(fit,),
        setupComparison="disagreement",
        betterMatchingTerms=11,
    )
    controller.invalidateAnalysis()
    with mock.patch.object(controller.log, "warning") as warning:
        controller.receiveModelAnalysis((controller.analysisRevision, result))
    assert controller.analysisResult is result
    assert controller.analysisStatus == "ready"
    assert warning.call_args_list == [
        mock.call("Model analysis: %s", "result diagnostic"),
        mock.call("Model analysis (%s terms): %s", fit.termCount, "fit diagnostic"),
        mock.call(
            "Model analysis setup disagreement: recorded %s terms, closer RMS with %s terms",
            result.recordedTerms,
            11,
        ),
    ]
    controller.invalidateAnalysis()
