# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from mw4.base.appProtocol import AppProtocol
from mw4.gui.extWindows.analyse.altAzPlots import AltAzPlots
from mw4.gui.extWindows.analyse.analyseData import AnalyseData
from mw4.gui.extWindows.analyse.analyseModel import AnalyseModel
from mw4.gui.extWindows.analyse.generalPlots import GeneralPlots
from mw4.gui.extWindows.analyse.raDecPlots import RaDecPlots
from mw4.gui.utilities.nativeQt.qtFileDialog import MWFileDialog
from mw4.gui.utilities.qtMain import MWidget
from mw4.gui.widgets import analyse_ui
from pathlib import Path
from PySide6.QtGui import QCloseEvent
from typing import Any


class AnalyseWindow(MWidget):
    def __init__(self, app: AppProtocol, title: str) -> None:
        super().__init__()
        self.app = app
        self.ui = analyse_ui.Ui_AnalyseDialog()
        self.ui.setupUi(self.ws)
        self.setNoFocus(self)
        self.setWindowTitle("Analyse")
        self.setMinimumSize(self.FULL_WIDTH, self.FULL_HEIGHT)
        self.analyseData = AnalyseData()
        self.analyseModel = AnalyseModel(self)
        self.generalPlots = GeneralPlots(self)
        self.altAzPlots = AltAzPlots(self)
        self.raDecPlots = RaDecPlots(self)
        self.tabs = (self.generalPlots, self.altAzPlots, self.raDecPlots)

        self.wIcon(self.ui.load, "load")
        self.ui.load.clicked.connect(self.loadModel)
        self.app.signals.ui.colorChange.connect(self.colorChange)
        self.app.signals.ui.showAnalyse.connect(self.showAnalyse)
        self.app.signals.hemisphere.redrawHorizon.connect(self.altAzPlots.drawHorizon)
        self.ui.showHorizon.clicked.connect(self.drawAll)
        self.ui.showISO.clicked.connect(self.drawAll)
        self.ui.linkViews.clicked.connect(self.drawAll)

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
        self.analyseModel.invalidateAnalysis()
        self.storeConfig()
        self.ui.showISO.setChecked(False)
        super().closeEvent(event)

    def showWindow(self) -> None:
        self.show()

    def colorChange(self) -> None:
        self.wIcon(self.ui.load, "load")
        self.setStyleSheet(self.mw4Style)
        for tab in self.tabs:
            tab.colorChange()
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
        for tab in self.tabs:
            tab.drawTab()

    def writeGui(self, data: list[dict[str, Any]], loadFilePath: Path) -> None:
        d = data[0]
        de = data[-1]

        title = f"Analyse Model     {loadFilePath.stem}"
        self.setWindowTitle(title)
        self.ui.exposureTime.setText(f"{d.get('exposureTime', '')}")
        self.ui.solver.setText(d.get("plateSolveApp", ""))
        self.ui.binning.setText(f"{d.get('binning', 0):1.0f}")
        self.ui.time.setText(d.get("julianDate", "").replace("T", "  ").replace("Z", ""))
        self.ui.subframe.setText(f"{d.get('subFrame', 0):3.0f}")
        self.ui.modelTerms.setText(f"{d.get('modelTerms', 0):02.0f}")
        self.ui.modelErrorRMS.setText(f"{d.get('modelErrorRMS', 0):5.1f}")
        self.ui.modelOrthoError.setText(f"{d.get('modelOrthoError', 0):5.0f}")
        self.ui.modelPolarError.setText(f"{d.get('modelPolarError', 0):5.0f}")
        self.ui.focalLength.setText(f"{d.get('focalLength', 0):4.0f}")
        self.ui.profile.setText(f"{d.get('profile', '')}")
        self.ui.firmware.setText(f"{d.get('firmware', '')}")
        self.ui.totalPoints.setText(f"{d.get('lenSequence', 0)}")
        self.ui.goodPoints.setText(f"{de.get('errorIndex', 0)}")
        app = de.get("astrometryApp", "").split("-")[0].strip()
        self.ui.solver.setText(f"{app}")
        version = d.get("version", "").removeprefix("MountWizzard4 - v")
        self.ui.version.setText(f"{version}")

    def processModel(self, loadFilePath: Path) -> None:
        self.analyseModel.invalidateAnalysis()
        modelJSON = self.analyseData.loadModel(loadFilePath)
        if modelJSON is None:
            return

        self.writeGui(modelJSON, loadFilePath)
        self.drawAll()
        self.analyseModel.startModelAnalysis(modelJSON, str(loadFilePath))
