# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import gc
import json
import pytest
import threading
from dataclasses import replace
from mw4.gui.extWindows.analyse.analyseW import AnalyseWindow
from mw4.logic.controllers.analyse.analyseModel import rebuildModel
from pathlib import Path
from PySide6.QtWidgets import QApplication
from typing import Any
from unittest import mock


@pytest.fixture(scope="module")
def modelRecords() -> list[dict[str, Any]]:
    return json.loads(Path("tests/testData/test.model").read_text())


@pytest.fixture(autouse=True, scope="module")
def function(qapp, makeApp):
    func = AnalyseWindow(app=makeApp(), title="Analyse")
    yield func
    QApplication.processEvents()
    gc.collect()
    QApplication.processEvents()


def test_modelComposition(function: AnalyseWindow) -> None:
    model = function.analyseController
    assert model.parent() is function
    assert model.thread() == function.thread()
    assert not hasattr(function, "pendingAnalysis")
    assert not hasattr(function, "runnerRebuildModel")
    assert not hasattr(function, "analyseModel")
    assert type(model).__name__ == "AnalyseController"
    assert type(function.analyseData).__module__ == "mw4.logic.controllers.analyse.analyseData"


def test_startSnapshotsRecords(function: AnalyseWindow) -> None:
    model = function.analyseController
    revisionBefore = model.analysisRevision
    model.analysisResult = rebuildModel([])
    model.analysisError = "previous failure"
    records = [{"latitude": 48.1}]
    with mock.patch.object(model, "startPendingAnalysis") as start:
        model.startModelAnalysis(records)
    start.assert_called_once()
    revision, snapshot = model.pendingAnalysis
    assert revision == revisionBefore + 1
    assert revision == model.analysisRevision
    assert model.analysisResult is None
    assert model.analysisError is None
    assert snapshot == records
    records[0]["latitude"] = 0
    assert snapshot[0]["latitude"] == 48.1
    model.invalidateAnalysis()


def test_automaticRebuild(function: AnalyseWindow, qtbot: Any) -> None:
    with mock.patch.object(function, "drawAll"):
        function.processModel(Path("tests/testData/test.model"))
    qtbot.waitUntil(lambda: function.analyseController.analysisResult is not None)
    assert function.analyseController.analysisStatus == "ready"
    assert function.analyseController.analysisResult.primary.termCount == 22
    firstWorker = function.analyseController.workerRebuildModel
    function.app.threadPool.waitForDone()
    QApplication.processEvents()
    with mock.patch.object(function, "drawAll"):
        function.processModel(Path("tests/testData/test1.model"))
    qtbot.waitUntil(lambda: function.analyseController.analysisResult is not None)
    assert function.analyseController.workerRebuildModel is firstWorker
    assert (
        function.analyseController.activeAnalysisRevision
        == function.analyseController.analysisRevision
    )
    assert function.analyseController.analysisResult.primary.termCount == 22


def test_queuedLoadsAndStaleResults(
    function: AnalyseWindow,
    modelRecords: list[dict[str, Any]],
    qtbot: Any,
) -> None:
    entered, release = threading.Event(), threading.Event()

    def blockedRunner(records: list[dict[str, Any]]) -> Any:
        entered.set()
        assert release.wait(5)
        return rebuildModel(records)

    function.app.threadPool.waitForDone()
    QApplication.processEvents()
    function.analyseController.invalidateAnalysis()
    revision = function.analyseController.analysisRevision
    with mock.patch(
        "mw4.gui.extWindows.analyse.analyseController.rebuildModel",
        side_effect=blockedRunner,
    ):
        function.analyseController.startModelAnalysis(modelRecords)
        assert entered.wait(5)
        function.analyseController.startModelAnalysis(modelRecords)
        latestRecords = [record | {"firmware": "latest"} for record in modelRecords]
        function.analyseController.startModelAnalysis(latestRecords)
        assert function.analyseController.pendingAnalysis is not None
        release.set()
        qtbot.waitUntil(lambda: function.analyseController.analysisResult is not None)
    assert function.analyseController.analysisResult.firmware == "latest"
    assert (
        function.analyseController.activeAnalysisRevision
        == function.analyseController.analysisRevision
    )
    function.analyseController.invalidateAnalysis()
    function.analyseController.receiveModelAnalysis((revision, rebuildModel(modelRecords)))
    assert function.analyseController.analysisResult is None


def test_workerFailureAndInvalidation(function: AnalyseWindow, qtbot: Any) -> None:
    function.app.threadPool.waitForDone()
    QApplication.processEvents()
    function.analyseController.invalidateAnalysis()
    with mock.patch(
        "mw4.gui.extWindows.analyse.analyseController.rebuildModel",
        side_effect=ValueError("test failure"),
    ):
        function.analyseController.startModelAnalysis([])
        qtbot.waitUntil(lambda: function.analyseController.analysisStatus == "failed")
    assert function.analyseController.analysisResult is None
    assert "test failure" in function.analyseController.analysisError
    function.analyseController.invalidateAnalysis()
    function.analyseController.failModelAnalysis("stale error")
    assert function.analyseController.analysisStatus == "idle"
    assert function.analyseController.analysisError is None


def test_undeliveredFailureDoesNotFailNewLoad(
    function: AnalyseWindow,
    modelRecords: list[dict[str, Any]],
    qtbot: Any,
) -> None:
    function.app.threadPool.waitForDone()
    QApplication.processEvents()
    function.analyseController.invalidateAnalysis()
    with mock.patch(
        "mw4.gui.extWindows.analyse.analyseController.rebuildModel",
        side_effect=ValueError("old failure"),
    ):
        function.analyseController.startModelAnalysis(modelRecords)
        function.app.threadPool.waitForDone()
    assert function.analyseController.analysisWorkerActive
    function.analyseController.invalidateAnalysis()
    function.analyseController.startModelAnalysis(modelRecords)
    assert function.analyseController.pendingAnalysis is not None
    qtbot.waitUntil(lambda: function.analyseController.analysisResult is not None)
    assert (
        function.analyseController.activeAnalysisRevision
        == function.analyseController.analysisRevision
    )
    assert function.analyseController.analysisError is None
    assert function.analyseController.analysisStatus == "ready"


def test_receiveUnavailableAndDisagreement(
    function: AnalyseWindow,
    modelRecords: list[dict[str, Any]],
) -> None:
    unavailable = rebuildModel([])
    function.analyseController.receiveModelAnalysis(
        (function.analyseController.analysisRevision, unavailable)
    )
    assert function.analyseController.analysisResult == unavailable
    result = rebuildModel(modelRecords)
    result = replace(result, setupComparison="disagreement", betterMatchingTerms=11)
    with mock.patch.object(function.log, "warning") as warning:
        function.analyseController.receiveModelAnalysis(
            (function.analyseController.analysisRevision, result)
        )
    assert any("setup disagreement" in call.args[0] for call in warning.call_args_list)
