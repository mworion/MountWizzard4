# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import pytest
from mw4.logic.controllers.analyse.analyseController import AnalyseController
from mw4.logic.controllers.analyse.analyseModel import rebuildModel
from PySide6.QtCore import QThreadPool
from typing import Any


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
