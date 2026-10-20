# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import webbrowser
from mw4.gui.mainWaddon.tabAddon import TabAddon
from mw4.gui.utilities.qtHelpers import guiSetText
from mw4.logic.photometry.imageStats import calcImageStats
from range_key_dict import RangeKeyDict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mw4.gui.mainWindow.mainWindow import MainWindow


class ImageStats(TabAddon):
    WATNEY = RangeKeyDict(
        {
            (0.001, 0.2): "Passes 14 (watneyqdb-14-20)",
            (0.2, 0.3): "Passes 12-13 (watneyqdb-12-13)",
            (0.3, 0.5): "Passes 10-11 (watneyqdb-10-11)",
            (0.5, 0.8): "Passes 8-9 (watneyqdb-08-09)",
            (0.8, 360): "Passes 0-7 (watneyqdb-00-07)",
        }
    )
    ASTAP = RangeKeyDict(
        {
            (0.001, 0.25): "D50, H18 (exp. 10s - 20s)",
            (0.25, 0.5): "D20, H18 (exp. 10s - 20s)",
            (0.5, 1): "D05, H18 (exp. 10s - 20s)",
            (1, 10): "D05, H18, H17 (exp. 3s - 10s)",
            (10, 20): "D05, V17 (exp. 1s - 3s)",
            (20, 360): "W08 (epx. 1s - 3s)",
        }
    )
    ASTROMETRY = RangeKeyDict(
        {
            (0.033, 0.047): "index-4200-*.fits",
            (0.047, 0.067): "index-4201-*.fits",
            (0.067, 0.093): "index-4202-*.fits",
            (0.093, 0.13): "index-4203-*.fits",
            (0.13, 0.183): "index-4204-*.fits",
            (0.183, 0.27): "index-4205-*.fits",
            (0.27, 0.37): "index-4206-*.fits",
            (0.37, 0.5): "index-4207-*.fits",
            (0.5, 0.7): "index-4208.fits",
            (0.7, 1.0): "index-4209.fits",
            (1.0, 1.4): "index-4210.fits",
            (1.4, 2.0): "index-4211.fits",
            (2.0, 2.8): "index-4212.fits",
            (2.8, 4): "index-4213.fits",
            (4.0, 5.7): "index-4214.fits",
            (5.7, 8.0): "index-4215.fits",
            (8.0, 11.3): "index-4216.fits",
            (11.3, 16.7): "index-4217.fits",
            (16.7, 23.3): "index-4218.fits",
            (23.3, 360): "index-4219.fits",
        }
    )

    def __init__(self, mainW: "MainWindow") -> None:
        self.mainW = mainW
        self.app = mainW.app
        self.msg = mainW.app.signals.ui.msg
        self.ui = mainW.ui
        imageStatsWidgets = [self.ui.aperture, self.ui.focalLength]
        for widget in imageStatsWidgets:
            widget.valueChanged.connect(self.updateImageStats)
        self.ui.openWatneyCatalog.clicked.connect(self.openWatneyCatalog)
        self.ui.openASTAPCatalog.clicked.connect(self.openASTAPCatalog)
        self.ui.openAstrometryCatalog.clicked.connect(self.openAstrometryCatalog)
        self.ui.copyFromTelescopeDriver.clicked.connect(self.updateTelescopeParametersToGui)
        self.app.timeMgr.update1s.connect(self.updateImageStats)
        self.app.timeMgr.update3s.connect(self.updateTelescopeParametersToGuiCyclic)
        self.fovHint: float = 0

    def initConfig(self) -> None:
        config = self.app.config["WindowMain"]
        self.ui.automaticTelescope.setChecked(config.get("automaticTelescope", False))

    def storeConfig(self) -> None:
        config = self.app.config["WindowMain"]
        config["automaticTelescope"] = self.ui.automaticTelescope.isChecked()

    def updateImageStats(self) -> None:
        focalLength = self.ui.focalLength.value()
        aperture = self.ui.aperture.value()
        data = self.app.dReg.camera.instance.data
        pixelSizeX = data.get("CCD_INFO.CCD_PIXEL_SIZE_X", 0)
        pixelSizeY = data.get("CCD_INFO.CCD_PIXEL_SIZE_Y", 0)
        pixelX = data.get("CCD_INFO.CCD_MAX_X", 0)
        pixelY = data.get("CCD_INFO.CCD_MAX_Y", 0)
        rotation = data.get("CCD_ROTATION.CCD_ROTATION_VALUE", 0)
        stats = calcImageStats(focalLength, aperture, pixelSizeX, pixelSizeY, pixelX, pixelY)
        self.fovHint = stats.fovHint

        guiSetText(self.ui.speed, "2.1f", stats.speed)
        guiSetText(self.ui.pixelSizeX, "2.2f", pixelSizeX)
        guiSetText(self.ui.pixelSizeY, "2.2f", pixelSizeY)
        guiSetText(self.ui.pixelX, "5.0f", pixelX)
        guiSetText(self.ui.pixelY, "5.0f", pixelY)
        guiSetText(self.ui.rotation, "3.1f", rotation)
        guiSetText(self.ui.resolutionX, "2.2f", stats.resolutionX)
        guiSetText(self.ui.resolutionY, "2.2f", stats.resolutionY)
        guiSetText(self.ui.dawes, "2.2f", stats.dawes)
        guiSetText(self.ui.rayleigh, "2.2f", stats.rayleigh)
        guiSetText(self.ui.magLimit, "2.2f", stats.magLimit)
        guiSetText(self.ui.FOVX, "2.2f", stats.fovX)
        guiSetText(self.ui.FOVY, "2.2f", stats.fovY)
        guiSetText(self.ui.focalLengthStats, "3.0f", focalLength)
        guiSetText(self.ui.apertureStats, "3.0f", aperture)
        guiSetText(self.ui.focusRed, "3.0f", stats.focusRed)
        guiSetText(self.ui.focusGreen, "3.0f", stats.focusGreen)
        guiSetText(self.ui.focusBlue, "3.0f", stats.focusBlue)
        guiSetText(self.ui.focusCCD, "3.0f", stats.focusCCD)

        watneyText = self.WATNEY.get(self.fovHint, "Out of Range")
        astapText = self.ASTAP.get(self.fovHint, "Out of Range")
        astrometryText = self.ASTROMETRY.get(self.fovHint, "Out of Range")
        self.ui.openWatneyCatalog.setEnabled(watneyText != "Out of Range")
        self.ui.openASTAPCatalog.setEnabled(astapText != "Out of Range")
        self.ui.openAstrometryCatalog.setEnabled(astrometryText != "Out of Range")
        guiSetText(self.ui.watneyIndex, "s", watneyText)
        guiSetText(self.ui.astapIndex, "s", astapText)
        guiSetText(self.ui.astrometryIndex, "s", astrometryText)

    def openWatneyCatalog(self) -> None:
        url = "https://github.com/Jusas/WatneyAstrometry/releases/tag/watneyqdb3"
        if not webbrowser.open(url, new=0):
            self.msg.emit(2, "System", "ImageStats", "Browser failed")

    def openASTAPCatalog(self) -> None:
        url = "https://www.hnsky.org/astap.htm"
        if not webbrowser.open(url, new=0):
            self.msg.emit(2, "System", "ImageStats", "Browser failed")

    def openAstrometryCatalog(self) -> None:
        url = "https://data.astrometry.net/4200/"  # SEC-5: changed http → https
        if not webbrowser.open(url, new=0):
            self.msg.emit(2, "System", "ImageStats", "Browser failed")

    def updateTelescopeParametersToGui(self) -> None:
        data = self.app.dReg.telescope.instance.data
        value = data.get("TELESCOPE_INFO.TELESCOPE_FOCAL_LENGTH", 0)
        if value is not None:
            value = float(value)
            self.ui.focalLength.setValue(value)

        value = data.get("TELESCOPE_INFO.TELESCOPE_APERTURE", 0)
        if value is not None:
            value = float(value)
            self.ui.aperture.setValue(value)

    def updateTelescopeParametersToGuiCyclic(self) -> None:
        if self.ui.automaticTelescope.isChecked():
            self.updateTelescopeParametersToGui()
