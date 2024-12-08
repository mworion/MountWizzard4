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
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import os
from pathlib import Path

# external packages
import pyqtgraph as pg
from PySide6.QtCore import Signal, QObject, Qt
from PySide6.QtGui import QFont, QGuiApplication, QCursor
from skyfield.api import Angle
from astropy.io import fits

# local import
from mountcontrol.convert import convertToDMS, convertToHMS
from base.transform import J2000ToJNow
from logic.fits.fitsFunction import getCoordinatesFromHeader, getSQMFromHeader
from logic.fits.fitsFunction import getExposureFromHeader, getScaleFromHeader
from gui.utilities import toolsQtWidget
from gui.utilities.slewInterface import SlewInterface
from gui.widgets import image_ui
from logic.file.fileHandler import FileHandler
from logic.photometry.photometry import Photometry
from gui.extWindows.image.imageTabs import ImageTabs


class ImageWindowSignals(QObject):
    """ """

    solveImage = Signal(object)


class ImageWindow(toolsQtWidget.MWidget, ImageTabs, SlewInterface):
    """ """

    TILT = {
        "none": 5,
        "almost none": 10,
        "mild": 15,
        "moderate": 20,
        "severe": 30,
        "extreme": 1000,
    }

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
        self.imageSourceRange = None
        self.imageFileName: Path = Path("")
        self.imageFileNameOld: Path = Path("")
        self.exposureTime = 1
        self.binning = 1
        self.folder = ""
        self.result = None
        self.pen = pg.mkPen(color=self.M_PRIM, width=2)
        self.penPink = pg.mkPen(color=self.M_PINK + "80", width=5)
        self.fontText = QFont(self.window().font().family(), 16)
        self.fontAnno = QFont(self.window().font().family(), 10, italic=True)
        self.fontText.setBold(True)

        self.imagingDeviceStat = {
            "expose": False,
            "exposeN": False,
            "solve": False,
        }

    def initConfig(self) -> None:
        """ """
        if "imageW" not in self.app.config:
            self.app.config["imageW"] = {}
        config = self.app.config["imageW"]

        self.positionWindow(config)
        self.setTabAndIndex(self.ui.tabImage, config, "orderMain")
        self.ui.color.setCurrentIndex(config.get("color", 0))
        self.ui.snTarget.setCurrentIndex(config.get("snTarget", 0))
        self.ui.tabImage.setCurrentIndex(config.get("tabImage", 0))
        self.imageFileName = Path(config.get("imageFileName", ""))
        self.folder = self.app.mwGlob.get("imageDir", "")
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
        self.setCrosshair()

    def storeConfig(self) -> None:
        """ """
        config = self.app.config
        if "imageW" not in config:
            config["imageW"] = {}
        else:
            config["imageW"].clear()
        config = config["imageW"]

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
        self.fileHandler.signals.imageLoaded.connect(self.showTabImage)
        self.fileHandler.signals.imageLoaded.connect(self.processPhotometry)
        self.photometry.signals.sepFinished.connect(self.resultPhotometry)
        self.photometry.signals.hfr.connect(self.showTabHFR)
        self.photometry.signals.hfrSquare.connect(self.showTabTiltSquare)
        self.photometry.signals.hfrTriangle.connect(self.showTabTiltTriangle)
        self.photometry.signals.roundness.connect(self.showTabRoundness)
        self.photometry.signals.aberration.connect(self.showTabAberrationInspect)
        self.photometry.signals.aberration.connect(self.showTabImageSources)
        self.photometry.signals.background.connect(self.showTabBackground)
        self.photometry.signals.backgroundRMS.connect(self.showTabBackgroundRMS)
        self.app.update1s.connect(self.updateWindowsStats)
        self.ui.load.clicked.connect(self.selectImage)
        self.ui.color.currentIndexChanged.connect(self.setBarColor)
        self.ui.showCrosshair.clicked.connect(self.setCrosshair)
        self.ui.flipH.clicked.connect(self.showCurrent)
        self.ui.flipV.clicked.connect(self.showCurrent)
        self.ui.aspectLocked.clicked.connect(self.setAspectLocked)
        self.ui.photometryGroup.clicked.connect(self.processPhotometry)
        self.ui.isoLayer.clicked.connect(self.showTabHFR)
        self.ui.isoLayer.clicked.connect(self.showTabRoundness)
        self.ui.showValues.clicked.connect(self.showTabImageSources)
        self.ui.snTarget.currentIndexChanged.connect(self.processPhotometry)
        self.ui.solve.clicked.connect(self.solveCurrent)
        self.ui.expose.clicked.connect(self.exposeImage)
        self.ui.exposeN.clicked.connect(self.exposeImageN)
        self.ui.abortExpose.clicked.connect(self.abortExpose)
        self.ui.abortSolve.clicked.connect(self.abortSolve)
        self.ui.slewCenter.clicked.connect(self.slewCenter)
        self.ui.image.barItem.sigLevelsChangeFinished.connect(self.copyLevels)
        self.ui.offsetTiltAngle.valueChanged.connect(self.showTabTiltTriangle)
        self.signals.solveImage.connect(self.solveImage)
        self.app.colorChange.connect(self.colorChange)
        self.app.showImage.connect(self.showImage)
        self.app.operationRunning.connect(self.operationMode)
        self.app.tabsMovable.connect(self.enableTabsMovable)
        self.wIcon(self.ui.load, "load")
        self.operationMode(self.app.statusOperationRunning)
        self.ui.image.p[0].getViewBox().callbackMDC = self.mouseDoubleClick
        self.ui.image.p[0].scene().sigMouseMoved.connect(self.mouseMoved)
        self.showCurrent()
        self.setAspectLocked()
        self.clearGui()
        self.show()

    def closeEvent(self, closeEvent) -> None:
        """ """
        self.storeConfig()
        super().closeEvent(closeEvent)

    def colorChange(self) -> None:
        """ """
        self.setStyleSheet(self.mw4Style)
        self.ui.image.colorChange()
        self.pen = pg.mkPen(color=self.M_PRIM)
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
            self.changeStyleDynamic(self.ui.expose, "running", True)
        elif self.imagingDeviceStat.get("exposeN", False):
            self.changeStyleDynamic(self.ui.exposeN, "running", True)
        else:
            self.changeStyleDynamic(self.ui.expose, "running", False)
            self.changeStyleDynamic(self.ui.exposeN, "running", False)

        if self.imagingDeviceStat.get("solve", False):
            self.changeStyleDynamic(self.ui.solve, "running", True)
        else:
            self.changeStyleDynamic(self.ui.solve, "running", False)

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

    def setBarColor(self) -> None:
        """ """
        cMap = ["CET-L2", "plasma", "cividis", "magma", "CET-D1A"]
        colorMap = cMap[self.ui.color.currentIndex()]
        self.ui.image.setColorMap(colorMap)
        self.ui.imageSource.setColorMap(colorMap)
        self.ui.background.setColorMap(colorMap)
        self.ui.backgroundRMS.setColorMap(colorMap)
        self.ui.hfr.setColorMap(colorMap)
        self.ui.tiltSquare.setColorMap(colorMap)
        self.ui.tiltTriangle.setColorMap(colorMap)
        self.ui.roundness.setColorMap(colorMap)
        self.ui.aberration.setColorMap(colorMap)

    def copyLevels(self) -> None:
        """ """
        level = self.ui.image.barItem.levels()
        self.ui.tiltSquare.barItem.setLevels(level)
        self.ui.tiltTriangle.barItem.setLevels(level)
        self.ui.aberration.barItem.setLevels(level)
        self.ui.imageSource.barItem.setLevels(level)

    def setCrosshair(self) -> None:
        """ """
        self.ui.image.showCrosshair(self.ui.showCrosshair.isChecked())

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

    def getImageSourceRange(self) -> None:
        """ """
        vb = self.ui.imageSource.p[0].getViewBox()
        self.imageSourceRange = vb.viewRect()

    def writeHeaderDataToGUI(self, header: fits.Header) -> None:
        """ """
        self.guiSetText(self.ui.object, "s", header.get("OBJECT", "").upper())
        ra, dec = getCoordinatesFromHeader(header=header)
        self.guiSetText(self.ui.ra, "HSTR", ra)
        self.guiSetText(self.ui.raFloat, "2.5f", ra.hours)
        self.guiSetText(self.ui.dec, "DSTR", dec)
        self.guiSetText(self.ui.decFloat, "2.5f", dec.degrees)
        self.guiSetText(self.ui.scale, "5.3f", getScaleFromHeader(header=header))
        self.guiSetText(self.ui.rotation, "6.2f", header.get("ANGLE"))
        self.guiSetText(self.ui.ccdTemp, "4.1f", header.get("CCD-TEMP"))
        self.guiSetText(
            self.ui.exposureTime, "5.1f", getExposureFromHeader(header=header)
        )
        self.guiSetText(self.ui.filter, "s", header.get("FILTER"))
        self.guiSetText(self.ui.binX, "1.0f", header.get("XBINNING"))
        self.guiSetText(self.ui.binY, "1.0f", header.get("YBINNING"))
        self.guiSetText(self.ui.sqm, "5.2f", getSQMFromHeader(header=header))

    def resultPhotometry(self) -> None:
        """ """
        if self.photometry.objs is None:
            self.msg.emit(2, "Image", "Photometry error", "Too low pixel stack")
        else:
            self.msg.emit(0, "Image", "Photometry", "SEP done")

    def processPhotometry(self) -> None:
        """ """
        isPhotometry = self.ui.photometryGroup.isChecked()
        if self.fileHandler.image is None or not isPhotometry:
            self.clearGui()
            return

        self.ui.showValues.setEnabled(isPhotometry)
        self.ui.isoLayer.setEnabled(isPhotometry)
        snTarget = self.ui.snTarget.currentIndex()

        self.photometry.processPhotometry(
            image=self.fileHandler.image, snTarget=snTarget
        )

    def showImage(self, imagePath: Path) -> None:
        """ """
        if self.imagingDeviceStat["expose"]:
            self.ui.image.setImage(None)
            self.clearGui()
        if not imagePath.is_file():
            return

        self.changeStyleDynamic(self.ui.headerGroup, "running", True)
        self.setWindowTitle(f"Imaging:   {os.path.basename(imagePath)}")
        flipH = self.ui.flipH.isChecked()
        flipV = self.ui.flipV.isChecked()
        self.fileHandler.loadImage(imagePath=imagePath, flipH=flipH, flipV=flipV)

    def showCurrent(self) -> None:
        """ """
        self.showImage(self.imageFileName)

    def exposeRaw(self, exposureTime: float, binning: int) -> None:
        """ """
        timeString = self.app.mount.obsSite.timeJD.utc_strftime("%Y-%m-%d-%H-%M-%S")

        if self.ui.timeTagImage.isChecked():
            fileName = timeString + "-exposure.fits"
        else:
            fileName = "exposure.fits"

        self.imageFileName = self.app.mwGlob["imageDir"] / fileName

        suc = self.app.camera.expose(
            imagePath=self.imageFileName, exposureTime=exposureTime, binning=binning
        )
        if not suc:
            self.abortExpose()
            text = f"{os.path.basename(self.imageFileName)}"
            self.msg.emit(2, "Image", "Expose error", text)
            return

        text = f"{os.path.basename(self.imageFileName)}"
        self.msg.emit(0, "Image", "Exposing", text)

    def exposeImageDone(self, imagePath: Path) -> None:
        """ """
        self.app.camera.signals.saved.disconnect(self.exposeImageDone)
        text = f"{os.path.basename(imagePath)}"
        self.msg.emit(0, "Image", "Exposed", text)
        self.imageFileName = imagePath

        if self.ui.autoSolve.isChecked():
            self.signals.solveImage.emit(imagePath)
        self.app.showImage.emit(imagePath)
        self.app.operationRunning.emit(0)
        self.imagingDeviceStat["expose"] = False

    def exposeImage(self) -> None:
        """ """
        self.imagingDeviceStat["expose"] = True
        self.app.camera.signals.saved.connect(self.exposeImageDone)
        self.app.operationRunning.emit(6)
        self.exposeRaw(
            exposureTime=self.app.camera.exposureTime1, binning=self.app.camera.binning1
        )

    def exposeImageNDone(self, imagePath: Path) -> None:
        """ """
        text = f"{os.path.basename(imagePath)}"
        self.msg.emit(0, "Image", "Exposed n", text)

        if self.ui.autoSolve.isChecked():
            self.signals.solveImage.emit(imagePath)
        self.app.showImage.emit(imagePath)
        self.exposeRaw(
            exposureTime=self.app.camera.exposureTimeN, binning=self.app.camera.binningN
        )

    def exposeImageN(self) -> None:
        """ """
        self.imagingDeviceStat["exposeN"] = True
        self.app.camera.signals.saved.connect(self.exposeImageNDone)
        self.app.operationRunning.emit(6)
        self.exposeRaw(
            exposureTime=self.app.camera.exposureTimeN, binning=self.app.camera.binningN
        )

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
        self.app.operationRunning.emit(0)

    def solveDone(self, result: dict) -> None:
        """ """
        self.imagingDeviceStat["solve"] = False
        self.app.plateSolve.signals.result.disconnect(self.solveDone)

        if not result:
            self.msg.emit(2, "Image", "Solving", "Solving error, result missing")
            self.app.operationRunning.emit(0)
            return
        if not result["success"]:
            self.msg.emit(2, "Image", "Solving error", f'{result.get("message")}')
            self.app.operationRunning.emit(0)
            return

        text = f'RA: {convertToHMS(result["raJ2000S"])} '
        text += f'({result["raJ2000S"].hours:4.3f}), '
        self.msg.emit(0, "Image", "Solved", text)
        text = f'DEC: {convertToDMS(result["decJ2000S"])} '
        text += f'({result["decJ2000S"].degrees:4.3f}), '
        self.msg.emit(0, "", "", text)
        text = f'Angle: {result["angleS"].degrees:3.0f}, '
        self.msg.emit(0, "", "", text)
        text = f'Scale: {result["scaleS"]:4.3f}, '
        self.msg.emit(0, "", "", text)
        text = f'Error: {result["errorRMS_S"]:4.1f}'
        self.msg.emit(0, "", "", text)

        if self.ui.embedData.isChecked():
            self.showCurrent()
        self.app.operationRunning.emit(0)

    def solveImage(self, imagePath: Path) -> None:
        """ """
        if not os.path.isfile(imagePath):
            self.app.operationRunning.emit(0)
            return

        updateHeader = self.ui.embedData.isChecked()
        self.app.plateSolve.signals.result.connect(self.solveDone)
        self.app.operationRunning.emit(6)
        self.app.plateSolve.solve(imagePath=imagePath, updateHeader=updateHeader)
        self.imagingDeviceStat["solve"] = True
        self.msg.emit(0, "Image", "Solving", imagePath)

    def solveCurrent(self) -> None:
        """ """
        self.signals.solveImage.emit(self.imageFileName)

    def abortSolve(self) -> None:
        """ """
        self.app.plateSolve.abort()
        self.app.operationRunning.emit(0)

    def mouseToWorld(self, mousePoint):
        """ """
        if self.fileHandler.wcs is None:
            return Angle(hours=0), Angle(degrees=0)
        x = mousePoint.x()
        y = mousePoint.y()
        if self.fileHandler.flipH:
            x = self.fileHandler.sizeX - x
        if not self.fileHandler.flipV:
            y = self.fileHandler.sizeY - y

        ra, dec = self.fileHandler.wcs.wcs_pix2world(x, y, 0)
        ra = Angle(hours=float(ra / 360 * 24))
        dec = Angle(degrees=float(dec))
        return ra, dec

    def slewDirect(self, ra: Angle, dec: Angle) -> None:
        """ """
        if not self.app.deviceStat["mount"]:
            self.msg.emit(2, "Image", "Mount", "Mount is not connected")
            return False
        question = "<b>Slewing to target</b>"
        question += "<br><br>Selected coordinates are:<br>"
        question += f"<font color={self.M_PRIM}> RA: {ra.hours:3.2f}h"
        question += f"   DEC: {dec.degrees:3.2f}°</font>"
        question += "<br><br>Would you like to start slewing?<br>"

        if not self.messageDialog(self, "Slewing mount", question):
            return
        self.slewTargetRaDec(ra, dec)

    def mouseMoved(self, pos) -> None:
        """ """
        viewBox = self.ui.image.p[0].getViewBox()
        mousePoint = viewBox.mapSceneToView(pos)
        ra, dec = self.mouseToWorld(mousePoint)

        if viewBox.posInViewRange(mousePoint):
            self.guiSetText(self.ui.raMouse, "HSTR", ra)
            self.guiSetText(self.ui.raMouseFloat, "2.5f", ra.hours)
            self.guiSetText(self.ui.decMouse, "DSTR", dec)
            self.guiSetText(self.ui.decMouseFloat, "2.5f", dec.degrees)
            QGuiApplication.setOverrideCursor(QCursor(Qt.CursorShape.CrossCursor))
        else:
            self.ui.raMouse.setText("")
            self.ui.raMouseFloat.setText("")
            self.ui.decMouse.setText("")
            self.ui.decMouseFloat.setText("")
            QGuiApplication.setOverrideCursor(QCursor(Qt.CursorShape.ArrowCursor))

    def mouseDoubleClick(self, ev, mousePoint) -> None:
        """ """
        if not self.fileHandler.hasCelestial:
            return

        ra, dec = self.mouseToWorld(mousePoint)
        self.slewDirect(ra, dec)

    def slewCenter(self) -> None:
        """ """
        if not self.fileHandler.hasCelestial:
            return

        ra, dec = getCoordinatesFromHeader(self.fileHandler.header)
        self.slewDirect(ra, dec)

    def syncMountToImage(self) -> None:
        """ """
        # todo: implement result
        result = {"raJ2000S": Angle(hours=0), "decJ2000S": Angle(degrees=0)}
        obs = self.app.mount.obsSite
        timeJD = obs.timeJD
        raJNow, decJNow = J2000ToJNow(result["raJ2000S"], result["decJ2000S"], timeJD)
        obs.setTargetRaDec(raJNow, decJNow)
        suc = obs.syncPositionToTarget()
        if suc:
            t = "Successfully synced model in mount to coordinates"
            self.msg.emit(1, "Model", "Run", t)
        else:
            t = "No sync, match failed because coordinates to far off for model"
            self.msg.emit(2, "Model", "Run error", t)
