############################################################
# -*- coding: utf-8 -*-
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PySide for python
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
from pathlib import Path

# external packages
from skyfield.api import Angle

# local import
from mountcontrol.convert import convertToDMS, convertToHMS
from base.transform import J2000ToJNow
from gui.utilities.toolsQtWidget import MWidget
from gui.utilities.slewInterface import SlewInterface
from gui.widgets import image_ui
from logic.file.fileHandler import FileHandler
from logic.photometry.photometry import Photometry
from logic.fits.fitsFunction import getCoordinatesFromHeader, getImageHeader
from gui.extWindows.image.imageTabs import ImageTabs
from gui.extWindows.image.imageSignals import ImageWindowSignals
from gui.mainWaddon.tabModel import Model
from gui.utilities.toolsQtWidget import changeStyleDynamic


class ImageWindow(MWidget, SlewInterface):
    """ """

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.msg = app.msg
        self.threadPool = app.threadPool
        self.ui = image_ui.Ui_ImageDialog()
        self.ui.setupUi(self)
        self.signals = ImageWindowSignals()
        self.photometry = Photometry(app=app)
        self.fileHandler = FileHandler(app=app)
        self.barItem = None
        self.imageItem = None
        self.imageFileName: Path = Path("")
        self.imageFileNameOld: Path = Path("")
        self.exposureTime: float = 1
        self.binning: int = 1
        self.folder: Path = Path()
        self.result: dict
        self.imagingDeviceStat = {
            "expose": False,
            "exposeN": False,
            "solve": False,
        }
        self.tabs = ImageTabs(self)

    def initConfig(self) -> None:
        """ """
        config = self.app.config.get("imageW", {})

        self.positionWindow(config)
        self.setTabAndIndex(self.ui.tabImage, config, "orderMain")
        self.ui.color.setCurrentIndex(config.get("color", 0))
        self.ui.snTarget.setCurrentIndex(config.get("snTarget", 0))
        self.ui.tabImage.setCurrentIndex(config.get("tabImage", 0))
        self.imageFileName = Path(config.get("imageFileName", ""))
        self.folder = Path(self.app.mwGlob.get("imageDir", ""))
        self.ui.showCrosshair.setChecked(config.get("showCrosshair", False))
        self.ui.aspectLocked.setChecked(config.get("aspectLocked", False))
        self.ui.autoSolve.setChecked(config.get("autoSolve", False))
        self.ui.embedData.setChecked(config.get("embedData", False))
        self.ui.photometryGroup.setChecked(config.get("photometryGroup", False))
        self.ui.isoLayer.setChecked(config.get("isoLayer", False))
        self.ui.flipH.setChecked(config.get("flipH", False))
        self.ui.flipV.setChecked(config.get("flipV", False))
        self.ui.showValues.setChecked(config.get("showValues", False))
        self.ui.offsetTiltAngle.setValue(config.get("offsetTiltAngle", 0))
        self.ui.timeTagImage.setChecked(config.get("timeTagImage", True))
        isMovable = self.app.config["mainW"].get("tabsMovable", False)
        self.enableTabsMovable(isMovable)
        self.tabs.setCrosshair()

    def storeConfig(self) -> None:
        """ """
        configMain = self.app.config
        configMain["imageW"] = {}
        config = configMain["imageW"]

        config["winPosX"] = max(self.pos().x(), 0)
        config["winPosY"] = max(self.pos().y(), 0)
        config["height"] = self.height()
        config["width"] = self.width()
        self.getTabAndIndex(self.ui.tabImage, config, "tabMain")
        config["color"] = self.ui.color.currentIndex()
        config["snTarget"] = self.ui.snTarget.currentIndex()
        config["tabImage"] = self.ui.tabImage.currentIndex()
        config["imageFileName"] = str(self.imageFileName)
        config["showCrosshair"] = self.ui.showCrosshair.isChecked()
        config["aspectLocked"] = self.ui.aspectLocked.isChecked()
        config["autoSolve"] = self.ui.autoSolve.isChecked()
        config["embedData"] = self.ui.embedData.isChecked()
        config["photometryGroup"] = self.ui.photometryGroup.isChecked()
        config["isoLayer"] = self.ui.isoLayer.isChecked()
        config["flipH"] = self.ui.flipH.isChecked()
        config["flipV"] = self.ui.flipV.isChecked()
        config["showValues"] = self.ui.showValues.isChecked()
        config["offsetTiltAngle"] = self.ui.offsetTiltAngle.value()
        config["timeTagImage"] = self.ui.timeTagImage.isChecked()

    def enableTabsMovable(self, isMovable: bool) -> None:
        """ """
        self.ui.tabImage.setMovable(isMovable)

    def showWindow(self) -> None:
        """ """
        self.fileHandler.signals.imageLoaded.connect(self.processPhotometry)
        self.photometry.signals.sepFinished.connect(self.resultPhotometry)
        self.app.update1s.connect(self.updateWindowsStats)
        self.ui.load.clicked.connect(self.selectImage)
        self.ui.flipH.clicked.connect(self.showCurrent)
        self.ui.flipV.clicked.connect(self.showCurrent)
        self.ui.aspectLocked.clicked.connect(self.setAspectLocked)
        self.ui.photometryGroup.clicked.connect(self.processPhotometry)
        self.ui.snTarget.currentIndexChanged.connect(self.processPhotometry)
        self.ui.solve.clicked.connect(self.solveCurrent)
        self.ui.expose.clicked.connect(self.exposeImage)
        self.ui.exposeN.clicked.connect(self.exposeImageN)
        self.ui.abortExpose.clicked.connect(self.abortExpose)
        self.ui.abortSolve.clicked.connect(self.abortSolve)
        self.ui.slewCenter.clicked.connect(self.slewCenter)
        self.ui.syncModelToImage.clicked.connect(self.syncModelToImage)
        self.ui.image.barItem.sigLevelsChangeFinished.connect(self.copyLevels)
        self.signals.solveImage.connect(self.solveImage)
        self.app.colorChange.connect(self.colorChange)
        self.app.showImage.connect(self.showImage)
        self.app.operationRunning.connect(self.operationMode)
        self.app.tabsMovable.connect(self.enableTabsMovable)
        self.operationMode(self.app.statusOperationRunning)
        self.setAspectLocked()
        self.clearGui()
        self.setupIcons()
        self.colorChange()
        self.show()
        self.showCurrent()

    def closeEvent(self, closeEvent) -> None:
        """ """
        self.storeConfig()
        super().closeEvent(closeEvent)

    def setupIcons(self) -> None:
        """ """
        self.wIcon(self.ui.load, "load")

    def colorChange(self) -> None:
        """ """
        self.setStyleSheet(self.mw4Style)
        self.tabs.colorChange()
        self.setupIcons()
        self.showCurrent()

    def clearGui(self) -> None:
        """ """
        self.ui.medianHFR.setText("")
        self.ui.hfrPercentile.setText("")
        self.ui.numberStars.setText("")
        self.ui.aspectRatioPercentile.setText("")
        tab = self.ui.tabImage
        tabIndex = self.getTabIndex(tab, "Image")
        for i in range(0, self.ui.tabImage.count()):
            if i == tabIndex:
                continue
            self.ui.tabImage.setTabEnabled(i, False)

    def operationMode(self, status: int) -> None:
        """ """
        if status == 0:
            self.ui.groupImageActions.setEnabled(True)
        elif status != 6:
            self.ui.groupImageActions.setEnabled(False)

    def updateWindowsStats(self) -> None:
        """ """
        if self.imagingDeviceStat.get("expose", False):
            self.ui.exposeN.setEnabled(False)
            self.ui.load.setEnabled(False)
            self.ui.abortExpose.setEnabled(True)
        elif self.imagingDeviceStat.get("exposeN", False):
            self.ui.expose.setEnabled(False)
            self.ui.load.setEnabled(False)
            self.ui.abortExpose.setEnabled(True)
        else:
            self.ui.expose.setEnabled(True)
            self.ui.exposeN.setEnabled(True)
            self.ui.load.setEnabled(True)
            self.ui.abortExpose.setEnabled(False)

        isPlateSolve = bool(self.app.deviceStat.get("plateSolve", False))
        isSolving = bool(self.imagingDeviceStat.get("solve", False))
        isImage = self.imageFileName.is_file()

        self.ui.solve.setEnabled(isPlateSolve and isImage)
        self.ui.abortSolve.setEnabled(isPlateSolve and isImage and isSolving)

        if not self.app.deviceStat.get("camera", False):
            self.ui.expose.setEnabled(False)
            self.ui.exposeN.setEnabled(False)

        if self.imagingDeviceStat.get("expose", False):
            changeStyleDynamic(self.ui.expose, "running", True)
        elif self.imagingDeviceStat.get("exposeN", False):
            changeStyleDynamic(self.ui.exposeN, "running", True)
        else:
            changeStyleDynamic(self.ui.expose, "running", False)
            changeStyleDynamic(self.ui.exposeN, "running", False)

        if self.imagingDeviceStat.get("solve", False):
            changeStyleDynamic(self.ui.solve, "running", True)
        else:
            changeStyleDynamic(self.ui.solve, "running", False)

    def selectImage(self) -> None:
        """ """
        self.imageFileName = self.openFile(
            self,
            "Select image file",
            self.folder,
            "All (*.fit* *.xisf);; FITS files (*.fit*);;XISF files (*.xisf)",
            enableDir=True,
        )
        if not self.imageFileName.is_file():
            self.msg.emit(0, "Image", "Loading", "No image selected")
            return

        self.msg.emit(0, "Image", "Image selected", self.imageFileName.name)
        self.folder = self.imageFileName.parents[0]
        if self.ui.autoSolve.isChecked():
            self.signals.solveImage.emit(self.imageFileName)
        self.app.showImage.emit(self.imageFileName)

    def copyLevels(self) -> None:
        """ """
        level = self.ui.image.barItem.levels()
        self.ui.tiltSquare.barItem.setLevels(level)
        self.ui.tiltTriangle.barItem.setLevels(level)
        self.ui.aberration.barItem.setLevels(level)
        self.ui.imageSource.barItem.setLevels(level)

    def setAspectLocked(self) -> None:
        """ """
        isLocked = self.ui.aspectLocked.isChecked()
        self.ui.image.p[0].setAspectLocked(isLocked)
        self.ui.imageSource.p[0].setAspectLocked(isLocked)
        self.ui.tiltSquare.p[0].setAspectLocked(isLocked)
        self.ui.tiltTriangle.p[0].setAspectLocked(isLocked)
        self.ui.background.p[0].setAspectLocked(isLocked)
        self.ui.backgroundRMS.p[0].setAspectLocked(isLocked)
        self.ui.hfr.p[0].setAspectLocked(isLocked)
        self.ui.roundness.p[0].setAspectLocked(isLocked)

    def resultPhotometry(self) -> None:
        """ """
        changeStyleDynamic(self.ui.photometryGroup, "running", False)
        if self.photometry.objs is None:
            self.msg.emit(2, "Image", "Photometry error", "Too low pixel stack")
        else:
            self.msg.emit(0, "Image", "Photometry", "SEP done")

    def processPhotometry(self) -> None:
        """ """
        isPhotometry = self.ui.photometryGroup.isChecked()
        self.clearGui()
        if self.fileHandler.image is None or not isPhotometry:
            return

        changeStyleDynamic(self.ui.photometryGroup, "running", True)
        self.ui.showValues.setEnabled(isPhotometry)
        self.ui.isoLayer.setEnabled(isPhotometry)
        snTarget = self.ui.snTarget.currentIndex()
        self.photometry.processPhotometry(self.fileHandler.image, snTarget)

    def showImage(self, imagePath: Path) -> None:
        """ """
        if not imagePath.is_file():
            return

        changeStyleDynamic(self.ui.headerGroup, "running", True)
        self.setWindowTitle(f"Imaging:   {imagePath.name}")
        flipH = self.ui.flipH.isChecked()
        flipV = self.ui.flipV.isChecked()
        self.fileHandler.loadImage(imagePath, flipH, flipV)

    def showCurrent(self) -> None:
        """ """
        self.showImage(self.imageFileName)

    def exposeRaw(self, exposureTime: float, binning: int) -> None:
        """ """
        timeString = self.app.mount.obsSite.timeJD.utc_strftime("%Y-%m-%d-%H-%M-%S")
        if self.ui.timeTagImage.isChecked():
            self.imageFileName = self.app.mwGlob["imageDir"] / (timeString + "-exposure.fits")
        else:
            self.imageFileName = self.app.mwGlob["imageDir"] / "exposure.fits"

        if not self.app.camera.expose(self.imageFileName, exposureTime, binning):
            self.abortExpose()
            self.msg.emit(2, "Image", "Expose error", self.imageFileName.name)
            return
        self.msg.emit(0, "Image", "Exposing", self.imageFileName.name)

    def exposeImageDone(self, imagePath: Path) -> None:
        """ """
        self.app.camera.signals.saved.disconnect(self.exposeImageDone)
        self.msg.emit(0, "Image", "Exposed", imagePath.stem)
        self.imageFileName = imagePath

        if self.ui.autoSolve.isChecked():
            self.signals.solveImage.emit(imagePath)
        self.app.showImage.emit(imagePath)
        self.imagingDeviceStat["expose"] = False
        self.app.operationRunning.emit(Model.STATUS_IDLE)

    def exposeImage(self) -> None:
        """ """
        self.app.operationRunning.emit(Model.STATUS_EXPOSE_1)
        self.imagingDeviceStat["expose"] = True
        self.app.camera.signals.saved.connect(self.exposeImageDone)
        self.exposeRaw(self.app.camera.exposureTime1, self.app.camera.binning1)

    def exposeImageNDone(self, imagePath: Path) -> None:
        """ """
        self.msg.emit(0, "Image", "Exposed n", imagePath.stem)

        if self.ui.autoSolve.isChecked():
            self.signals.solveImage.emit(imagePath)
        self.app.showImage.emit(imagePath)
        self.exposeRaw(self.app.camera.exposureTimeN, self.app.camera.binningN)

    def exposeImageN(self) -> None:
        """ """
        self.app.operationRunning.emit(Model.STATUS_EXPOSE_N)
        self.imagingDeviceStat["exposeN"] = True
        self.app.camera.signals.saved.connect(self.exposeImageNDone)
        self.exposeRaw(self.app.camera.exposureTimeN, self.app.camera.binningN)

    def abortExpose(self) -> None:
        """ """
        self.app.camera.abort()
        if self.imagingDeviceStat["expose"]:
            self.app.camera.signals.saved.disconnect(self.exposeImageDone)
        if self.imagingDeviceStat["exposeN"]:
            self.app.camera.signals.saved.disconnect(self.exposeImageNDone)

        self.imageFileName = self.imageFileNameOld
        self.imagingDeviceStat["expose"] = False
        self.imagingDeviceStat["exposeN"] = False
        self.msg.emit(2, "Image", "Expose", "Exposing aborted")
        self.app.operationRunning.emit(Model.STATUS_IDLE)

    def solveDone(self, result: dict) -> None:
        """ """
        self.imagingDeviceStat["solve"] = False
        self.app.plateSolve.signals.result.disconnect(self.solveDone)

        if not result["success"]:
            self.msg.emit(2, "Image", "Solving error", result.get("message"))
            self.app.operationRunning.emit(Model.STATUS_IDLE)
            return

        text = f"RA: {convertToHMS(result['raJ2000S'])} "
        text += f"({result['raJ2000S'].hours:4.3f}), "
        self.msg.emit(0, "Image", "Solved", text)
        text = f"DEC: {convertToDMS(result['decJ2000S'])} "
        text += f"({result['decJ2000S'].degrees:4.3f}), "
        self.msg.emit(0, "", "", text)
        text = f"Angle: {result['angleS'].degrees:3.0f}, "
        self.msg.emit(0, "", "", text)
        text = f"Scale: {result['scaleS']:4.3f}, "
        self.msg.emit(0, "", "", text)
        text = f"Error: {result['errorRMS_S']:4.1f}"
        self.msg.emit(0, "", "", text)

        if self.ui.embedData.isChecked():
            self.showCurrent()
        self.app.operationRunning.emit(Model.STATUS_IDLE)

    def solveImage(self, imagePath: Path) -> None:
        """ """
        if not imagePath.is_file():
            return

        self.app.operationRunning.emit(Model.STATUS_SOLVE)
        self.app.plateSolve.signals.result.connect(self.solveDone)
        self.app.plateSolve.solve(imagePath, self.ui.embedData.isChecked())
        self.imagingDeviceStat["solve"] = True
        self.msg.emit(0, "Image", "Solving", imagePath.name)

    def solveCurrent(self) -> None:
        """ """
        self.signals.solveImage.emit(self.imageFileName)

    def abortSolve(self) -> None:
        """ """
        self.app.plateSolve.abort()
        self.app.operationRunning.emit(Model.STATUS_IDLE)

    def slewDirect(self, ra: Angle, dec: Angle) -> None:
        """ """
        if not self.app.deviceStat["mount"]:
            self.msg.emit(2, "Image", "Mount", "Mount is not connected")
            return
        question = "<b>Slewing to target</b>"
        question += "<br><br>Selected coordinates are:<br>"
        question += f"<font color={self.M_PRIM}> RA: {ra.hours:3.2f}h"
        question += f"   DEC: {dec.degrees:3.2f}°</font>"
        question += "<br><br>Would you like to start slewing?<br>"

        if not self.messageDialog(self, "Slewing mount", question):
            return
        self.slewTargetRaDec(ra, dec)

    def slewCenter(self) -> None:
        """ """
        ra, dec = getCoordinatesFromHeader(self.fileHandler.header)
        self.slewDirect(ra, dec)

    def syncModelToImage(self) -> None:
        """ """
        if not self.app.deviceStat["mount"]:
            self.msg.emit(2, "Image", "Mount", "Mount is not connected")
            return
        if not self.imageFileName.is_file():
            self.msg.emit(2, "Image", "Mount", "No image loaded")
            return

        ra, dec = getCoordinatesFromHeader(getImageHeader(self.imageFileName))

        if ra is None or dec is None:
            self.msg.emit(2, "Image", "Mount", "No coordinates found in image")
            return

        self.app.operationRunning.emit(Model.STATUS_MODEL_SYNC)
        obs = self.app.mount.obsSite
        raJNow, decJNow = J2000ToJNow(ra, dec, obs.timeJD)
        obs.setTargetRaDec(raJNow, decJNow)

        if obs.syncPositionToTarget():
            t = "Successfully synced model in mount to coordinates"
            self.msg.emit(1, "Model", "Run", t)
        else:
            t = "No sync, match failed because coordinates to far off for model"
            self.msg.emit(2, "Model", "Run error", t)
        self.app.operationRunning.emit(Model.STATUS_IDLE)
