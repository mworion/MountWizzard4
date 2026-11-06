# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from mw4.base.appProtocol import AppProtocol
from mw4.gui.extWindows.analyse.altAzPlots import AltAzPlots
from mw4.gui.extWindows.analyse.generalPlots import GeneralPlots
from mw4.gui.extWindows.analyse.raDecPlots import RaDecPlots
from mw4.gui.utilities.nativeQt.qtFileDialog import MWFileDialog
from mw4.gui.utilities.qtMain import MWidget
from mw4.gui.widgets import analyse_ui
from mw4.logic.controllers.analyse.analyseData import AnalyseData
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
        if not self.analyseData.errorIndex.size:
            return
        for tab in self.tabs:
            tab.drawTab()

    def writeGui(self, data: list[dict[str, Any]], loadFilePath: Path) -> None:
        firstRecord = data[0]
        lastRecord = data[-1]

        title = f"Analyse Model     {loadFilePath.stem}"
        self.setWindowTitle(title)
        self.ui.exposureTime.setText(f"{firstRecord.get('exposureTime', '')}")
        self.ui.binning.setText(f"{firstRecord.get('binning', 0):1.0f}")
        self.ui.time.setText(firstRecord.get("julianDate", "").replace("T", "  ").replace("Z", ""))
        self.ui.subframe.setText(f"{firstRecord.get('subFrame', 0):3.0f}")
        self.ui.modelTerms.setText(f"{firstRecord.get('modelTerms', 0):02.0f}")
        self.ui.modelErrorRMS.setText(f"{firstRecord.get('modelErrorRMS', 0):5.1f}")
        self.ui.modelOrthoError.setText(f"{firstRecord.get('modelOrthoError', 0):5.0f}")
        self.ui.modelPolarError.setText(f"{firstRecord.get('modelPolarError', 0):5.0f}")
        self.ui.focalLength.setText(f"{firstRecord.get('focalLength', 0):4.0f}")
        self.ui.profile.setText(f"{firstRecord.get('profile', '')}")
        self.ui.firmware.setText(f"{firstRecord.get('firmware', '')}")
        self.ui.totalPoints.setText(f"{firstRecord.get('lenSequence', 0)}")
        self.ui.goodPoints.setText(f"{lastRecord.get('errorIndex', 0)}")
        app = lastRecord.get("astrometryApp", "").split("-")[0].strip()
        self.ui.solver.setText(f"{app}")
        version = firstRecord.get("version", "").removeprefix("MountWizzard4 - v")
        self.ui.version.setText(f"{version}")

    def processModel(self, loadFilePath: Path) -> None:
        modelJSON = self.analyseData.loadModel(loadFilePath)
        if modelJSON is None:
            return
        self.writeGui(modelJSON, loadFilePath)
        self.drawAll()
