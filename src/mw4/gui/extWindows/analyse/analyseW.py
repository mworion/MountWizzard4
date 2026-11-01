# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from collections.abc import Callable
from mw4.base.appProtocol import AppProtocol
from mw4.gui.extWindows.analyse.analyseData import AnalyseDataMixin
from mw4.gui.extWindows.analyse.analysePlots import AnalysePlotsMixin
from mw4.gui.utilities.nativeQt.qtFileDialog import MWFileDialog
from mw4.gui.utilities.qtMain import MWidget
from mw4.gui.widgets import analyse_ui
from pathlib import Path
from PySide6.QtGui import QCloseEvent


class AnalyseWindow(AnalyseDataMixin, AnalysePlotsMixin, MWidget):
    def __init__(self, app: AppProtocol, title: str) -> None:
        super().__init__()
        self.app = app
        self.ui = analyse_ui.Ui_AnalyseDialog()
        self.ui.setupUi(self.ws)
        self.setNoFocus(self)
        self.setWindowTitle("Analyse")
        self.setMinimumSize(self.FULL_WIDTH, self.FULL_HEIGHT)
        self.initData()

        self.wIcon(self.ui.load, "load")
        self.ui.load.clicked.connect(self.loadModel)
        self.app.signals.ui.colorChange.connect(self.colorChange)
        self.app.signals.ui.showAnalyse.connect(self.showAnalyse)
        self.app.signals.hemisphere.redrawHorizon.connect(self.drawHorizon)
        self.ui.showHorizon.clicked.connect(self.drawAll)
        self.ui.showISO.clicked.connect(self.drawAll)
        self.ui.linkViews.clicked.connect(self.drawAll)

        self.charts: list[Callable[[], None]] = [
            self.drawRaRawErrors,
            self.drawDecRawErrors,
            self.drawRaErrors,
            self.drawDecError,
            self.drawRaErrorsRef,
            self.drawDecErrorsRef,
            self.drawRaRawErrorsRef,
            self.drawDecRawErrorsRef,
            self.drawScaleImage,
            self.drawModelPositions,
            self.drawErrorAscending,
            self.drawErrorDistribution,
            self.drawHorizon,
        ]

    def initConfig(self) -> None:
        config = self.app.config.get("WindowAnalyse", {})
        self.setPositionWindow(config)
        self.ui.showHorizon.setChecked(config.get("showHorizon", False))
        self.ui.linkViews.setChecked(config.get("linkViews", False))

    def storeConfig(self) -> None:
        configMain = self.app.config
        configMain["WindowAnalyse"] = {}
        config = configMain["WindowAnalyse"]

        self.getPositionWindow(config)
        config["showHorizon"] = self.ui.showHorizon.isChecked()
        config["linkViews"] = self.ui.linkViews.isChecked()

    def closeEvent(self, event: QCloseEvent) -> None:
        self.storeConfig()
        self.ui.showISO.setChecked(False)
        super().closeEvent(event)

    def showWindow(self) -> None:
        self.show()

    def colorChange(self) -> None:
        self.wIcon(self.ui.load, "load")
        self.setStyleSheet(self.mw4Style)
        for plot in [
            self.ui.raRawErrors,
            self.ui.decRawErrors,
            self.ui.raErrors,
            self.ui.decErrors,
            self.ui.raRawErrorsRef,
            self.ui.decRawErrorsRef,
            self.ui.raErrorsRef,
            self.ui.decErrorsRef,
            self.ui.scaleImage,
            self.ui.modelPositions,
            self.ui.errorAscending,
            self.ui.errorDistribution,
        ]:
            plot.colorChange()
        self.drawAll()

    def loadModel(self) -> None:
        folder = self.app.mwGlob["modelDir"]
        loadFilePath = MWFileDialog.getOpenFileName(
            self, "Open model file", folder, "Model files (*.model)"
        )
        if loadFilePath.is_file():
            self.processModel(loadFilePath)

    def showAnalyse(self, path: Path) -> None:
        if path.is_file():
            self.processModel(path)

    def drawAll(self) -> None:
        for chart in self.charts:
            chart()
        self.linkViewsAltAz()
        self.linkViewsRa()
        self.linkViewsDec()
