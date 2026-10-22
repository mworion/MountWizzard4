# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import pyqtgraph as pg
from astropy.io import fits
from mw4.gui.utilities.qtHelpers import changeStyleDynamic, getTabIndex, guiSetText
from mw4.logic.controllers.imageWindow.photometry_analysis import (
    computeTiltSquareView,
    computeTiltTriangleView,
    tiltHint,
)
from mw4.logic.controllers.imageWindow.tiltGeometry import (
    TRIANGLE_LINKS,
    TriangleGeometry,
    calcTriangleGeometry,
)
from mw4.logic.fits.fitsFunction import (
    getCoordinatesFromHeader,
    getExposureFromHeader,
    getScaleFromHeader,
    getSQMFromHeader,
)
from PySide6.QtCore import QRectF
from PySide6.QtGui import QFont
from typing import Any, ClassVar


class ImageTabs:
    TILT: ClassVar = {
        "none": 5,
        "almost none": 10,
        "mild": 15,
        "moderate": 20,
        "severe": 30,
        "extreme": 1000,
    }

    def __init__(self, parent: Any) -> None:
        super().__init__()
        self.parent = parent
        self.ui = parent.ui
        self.msg = parent.msg
        self.fileHandler = parent.fileHandler
        self.photometry = parent.photometry
        self.threadPool = parent.threadPool
        self.pen = pg.mkPen(color=self.parent.M_PRIM, width=2)
        self.penPink = pg.mkPen(color=self.parent.M_PINK, width=5)
        self.fontText = QFont(self.parent.window().font().family(), 16)
        self.fontAnno = QFont(self.parent.window().font().family(), 10, italic=True)
        self.fontText.setBold(True)
        self.imageSourceRange: QRectF = QRectF()
        self.fileHandler.signals.imageLoaded.connect(self.showImage)
        self.photometry.signals.hfr.connect(self.showHFR)
        self.photometry.signals.hfrSquare.connect(self.showTiltSquare)
        self.photometry.signals.hfrTriangle.connect(self.showTiltTriangle)
        self.photometry.signals.roundness.connect(self.showRoundness)
        self.photometry.signals.aberration.connect(self.showAberrationInspect)
        self.photometry.signals.sources.connect(self.showImageSources)
        self.photometry.signals.background.connect(self.showBackground)
        self.photometry.signals.backgroundRMS.connect(self.showBackgroundRMS)
        self.ui.isoLayer.clicked.connect(self.showHFR)
        self.ui.isoLayer.clicked.connect(self.showRoundness)
        self.ui.showValues.clicked.connect(self.showImageSources)
        self.ui.offsetTiltAngle.valueChanged.connect(self.showTiltTriangle)
        self.ui.color.currentIndexChanged.connect(self.setBarColor)
        self.ui.showCrosshair.clicked.connect(self.setCrosshair)

    def colorChange(self) -> None:
        self.ui.image.colorChange()
        self.ui.imageSource.colorChange()
        self.ui.background.colorChange()
        self.ui.backgroundRMS.colorChange()
        self.ui.hfr.colorChange()
        self.ui.tiltSquare.colorChange()
        self.ui.tiltTriangle.colorChange()
        self.ui.roundness.colorChange()
        self.ui.aberration.colorChange()
        self.pen = pg.mkPen(color=self.parent.M_PRIM)

    def getImageSourceRange(self) -> None:
        vb = self.ui.imageSource.p[0].getViewBox()
        self.imageSourceRange = vb.viewRect()

    def setBarColor(self) -> None:
        colorMapIndex = self.ui.color.currentIndex() + 1
        self.ui.image.setImageColorMap(colorMapIndex)
        self.ui.imageSource.setImageColorMap(colorMapIndex)
        self.ui.background.setImageColorMap(colorMapIndex)
        self.ui.backgroundRMS.setImageColorMap(colorMapIndex)
        self.ui.hfr.setImageColorMap(colorMapIndex)
        self.ui.tiltSquare.setImageColorMap(colorMapIndex)
        self.ui.tiltTriangle.setImageColorMap(colorMapIndex)
        self.ui.roundness.setImageColorMap(colorMapIndex)
        self.ui.aberration.setImageColorMap(colorMapIndex)

    def setCrosshair(self) -> None:
        self.ui.image.showCrosshair(self.ui.showCrosshair.isChecked())

    def writeHeaderDataToGUI(self, header: fits.Header) -> None:
        guiSetText(self.ui.object, "s", str(header.get("OBJECT", "")).upper())
        ra, dec = getCoordinatesFromHeader(header=header)
        guiSetText(self.ui.ra, "HSTR", ra)
        # pyrefly: ignore[bad-argument-type]
        guiSetText(self.ui.raFloat, "2.5f", ra.hours)
        guiSetText(self.ui.dec, "DSTR", dec)
        # pyrefly: ignore[bad-argument-type]
        guiSetText(self.ui.decFloat, "2.5f", dec.degrees)
        guiSetText(self.ui.scale, "5.3f", getScaleFromHeader(header=header))
        guiSetText(self.ui.rotation, "6.2f", header.get("ANGLE", 0))
        guiSetText(self.ui.ccdTemp, "4.1f", header.get("CCD-TEMP", 0))
        guiSetText(self.ui.exposureTime, "5.1f", getExposureFromHeader(header=header))
        guiSetText(self.ui.filter, "s", header.get("FILTER", ""))
        guiSetText(self.ui.binX, "1.0f", header.get("XBINNING", 0))
        guiSetText(self.ui.binY, "1.0f", header.get("YBINNING", 0))
        guiSetText(self.ui.sqm, "5.2f", getSQMFromHeader(header=header))

    @staticmethod
    def clearImageTab(imageWidget) -> None:
        imageWidget.p[0].clear()
        imageWidget.p[0].showAxes(False, showValues=False)
        imageWidget.p[0].setMouseEnabled(x=False, y=False)
        imageWidget.barItem.setVisible(False)

    def showImage(self) -> None:
        changeStyleDynamic(self.ui.headerGroup, "run", "false")
        tab = self.ui.tabImage
        tabIndex = getTabIndex(tab, "Image")
        tab.setTabEnabled(tabIndex, True)

        if self.fileHandler.image is None:
            self.msg.emit(0, "Image", "Rendering error", "Incompatible image format")
            return

        self.ui.slewCenter.setEnabled(self.fileHandler.hasCelestial)
        self.imageSourceRange = QRectF()
        self.ui.image.setImage(
            imageDisp=self.fileHandler.image,
            updateGeometry=not self.ui.continous.isChecked(),
        )
        self.setBarColor()
        self.setCrosshair()
        self.writeHeaderDataToGUI(self.fileHandler.header)

    def showHFR(self) -> None:
        self.ui.hfr.setImage(imageDisp=self.photometry.hfrGrid)
        self.ui.hfr.barItem.setLevels((self.photometry.hfrMin, self.photometry.hfrMax))
        self.ui.hfrPercentile.setText(f"{self.photometry.hfrPercentile:1.1f}")
        self.ui.medianHFR.setText(f"{self.photometry.hfrMedian:1.2f}")
        self.ui.numberStars.setText(f"{len(self.photometry.hfr):1.0f}")
        if self.ui.isoLayer.isChecked():
            self.ui.hfr.addIsoBasic(self.ui.hfr.p[0], self.photometry.hfrGrid, levels=20)
        tab = self.ui.tabImage
        tab.setTabEnabled(getTabIndex(tab, "HFR"), True)

    def drawTiltGrid(self, plotItem: Any, w: float, h: float) -> None:
        for i in range(1, 3):
            posX = i * w / 3
            lineItem = pg.QtWidgets.QGraphicsLineItem()
            lineItem.setPen(self.pen)
            lineItem.setLine(posX, 0, posX, h)
            plotItem.addItem(lineItem)

            posY = i * h / 3
            lineItem = pg.QtWidgets.QGraphicsLineItem()
            lineItem.setPen(self.pen)
            lineItem.setLine(0, posY, w, posY)
            plotItem.addItem(lineItem)

    def writeTiltValues(self, plotItem: Any, segHFR: Any, w: float, h: float) -> None:
        for ix in range(3):
            for iy in range(3):
                textItem = pg.TextItem(anchor=(0.5, 0.5), color=self.parent.M_PRIM)
                textItem.setText(f"{segHFR[ix][iy]:1.2f}")
                textItem.setFont(self.fontText)
                textItem.setPos(ix * w / 3 + w / 6, iy * h / 3 + h / 6)
                textItem.setZValue(10)
                plotItem.addItem(textItem)

    def drawTiltVectors(self, plotItem: Any, points: Any) -> None:
        links = [[0, 1], [1, 2], [2, 4], [4, 7], [7, 6], [6, 5], [5, 3], [3, 0], [0, 7], [2, 5]]
        for start, end in links:
            lineItem = pg.QtWidgets.QGraphicsLineItem()
            lineItem.setPen(self.penPink)
            lineItem.setLine(points[start][0], points[start][1], points[end][0], points[end][1])
            plotItem.addItem(lineItem)

    def showTiltSquare(self) -> bool:
        segHFR = self.photometry.hfrSegSquare
        w = self.photometry.w
        h = self.photometry.h
        plotItem = self.ui.tiltSquare.p[0]
        self.clearImageTab(self.ui.tiltSquare)
        self.ui.tiltSquare.setImage(self.photometry.image)
        self.ui.tiltSquare.barItem.setLevels(self.ui.image.barItem.levels())

        self.drawTiltGrid(plotItem, w, h)
        self.writeTiltValues(plotItem, segHFR, w, h)

        # calc extreme hfr values
        # arrays upper left to lower right
        view = computeTiltSquareView(
            segHFR, w, h, self.photometry.hfrMedian, self.photometry.hfrOuter
        )
        points = view.points

        self.drawTiltVectors(plotItem, points)

        hint = tiltHint(view.tiltPercent, self.TILT)
        self.ui.textSquareTiltHFR.setText(f"{view.tiltDiff:1.2f} ({view.tiltPercent:1.0f}%) {hint}")
        t = f"{view.offAxisDiff:1.2f} ({view.offAxisPercent:1.0f}%)"
        self.ui.textSquareTiltOffAxis.setText(t)
        self.ui.squareMedianHFR.setText(f"{self.photometry.hfrMedian:1.2f}")
        self.ui.squareNumberStars.setText(f"{len(self.photometry.hfr):1.0f}")
        tab = self.ui.tabImage
        tab.setTabEnabled(getTabIndex(tab, "TiltSquare"), True)
        return True

    def addTextItem(self, plotItem: Any, text: str, x: float, y: float) -> None:
        textItem = pg.TextItem(anchor=(0.5, 0.5), color=self.parent.M_PRIM)
        textItem.setText(text)
        textItem.setFont(self.fontText)
        textItem.setZValue(10)
        textItem.setPos(x, y)
        plotItem.addItem(textItem)

    def addLineItem(self, plotItem: Any, line: tuple[float, ...], pen: Any) -> None:
        lineItem = pg.QtWidgets.QGraphicsLineItem()
        lineItem.setLine(*line)
        lineItem.setPen(pen)
        plotItem.addItem(lineItem)

    def drawTriangleGeometry(self, plotItem: Any, geometry: TriangleGeometry, view: Any) -> None:
        for ring in geometry.rings:
            ellipseItem = pg.QtWidgets.QGraphicsEllipseItem()
            ellipseItem.setRect(*ring)
            ellipseItem.setPen(self.pen)
            plotItem.addItem(ellipseItem)

        self.addTextItem(plotItem, f"{self.photometry.hfrInner:1.2f}", geometry.cx, geometry.cy)
        for i, separator in enumerate(geometry.separators):
            self.addLineItem(plotItem, separator, self.pen)
            posX, posY = geometry.textPositions[i]
            self.addTextItem(plotItem, f"{view.segData[i]:1.2f}", posX, posY)

        points = view.points
        for a, b in TRIANGLE_LINKS:
            line = (points[a][0], points[a][1], points[b][0], points[b][1])
            self.addLineItem(plotItem, line, self.penPink)

    def showTiltTriangle(self) -> None:
        w = self.photometry.w
        h = self.photometry.h
        plotItem = self.ui.tiltTriangle.p[0]
        self.clearImageTab(self.ui.tiltTriangle)
        self.ui.tiltTriangle.setImage(self.photometry.image)
        self.ui.tiltTriangle.barItem.setLevels(self.ui.image.barItem.levels())

        offsetTiltAngle = self.ui.offsetTiltAngle.value()
        view = computeTiltTriangleView(
            self.photometry.hfrSegTriangle,
            offsetTiltAngle,
            w,
            h,
            self.photometry.hfrMedian,
            self.photometry.hfrInner,
            self.photometry.hfrOuter,
        )
        geometry = calcTriangleGeometry(w, h, offsetTiltAngle)
        self.drawTriangleGeometry(plotItem, geometry, view)

        hint = tiltHint(view.tiltPercent, self.TILT)
        self.ui.textTriangleTiltHFR.setText(
            f"{view.tiltDiff:1.2f} ({view.tiltPercent:1.0f}%) {hint}"
        )
        t = f"{view.offAxisDiff:1.2f} ({view.offAxisPercent:1.0f}%)"
        self.ui.textTriangleTiltOffAxis.setText(t)
        self.ui.triangleMedianHFR.setText(f"{self.photometry.hfrMedian:1.2f}")
        self.ui.triangleNumberStars.setText(f"{len(self.photometry.hfr):1.0f}")
        tab = self.ui.tabImage
        tab.setTabEnabled(getTabIndex(tab, "TiltTriangle"), True)

    def showRoundness(self) -> None:
        self.ui.roundness.setImage(imageDisp=self.photometry.roundnessGrid)
        self.ui.roundness.p[0].showAxes(False, showValues=False)
        self.ui.roundness.p[0].setMouseEnabled(x=False, y=False)
        self.ui.roundness.barItem.setLevels(
            (self.photometry.roundnessMin, self.photometry.roundnessMax)
        )
        self.ui.aspectRatioPercentile.setText(f"{self.photometry.roundnessPercentile:1.1f}")
        if self.ui.isoLayer.isChecked():
            self.ui.roundness.addIsoBasic(
                self.ui.roundness.p[0], self.photometry.roundnessGrid, levels=20
            )
        tab = self.ui.tabImage
        tab.setTabEnabled(getTabIndex(tab, "Roundness"), True)

    def showAberrationInspect(self) -> None:
        self.ui.aberration.barItem.setVisible(False)
        self.ui.aberration.p[0].clear()
        self.ui.aberration.p[0].setAspectLocked(True)
        self.ui.aberration.p[0].showAxes(False, showValues=False)
        self.ui.aberration.p[0].setMouseEnabled(x=False, y=False)
        self.ui.aberration.setImage(self.photometry.aberrationImage)
        for i in range(1, 3):
            posX = i * self.photometry.ABERRATION_SIZE
            lineItem = pg.QtWidgets.QGraphicsLineItem()
            lineItem.setPen(self.pen)
            lineItem.setLine(posX, 0, posX, 3 * self.photometry.ABERRATION_SIZE)
            self.ui.aberration.p[0].addItem(lineItem)

            posY = i * self.photometry.ABERRATION_SIZE
            lineItem = pg.QtWidgets.QGraphicsLineItem()
            lineItem.setPen(self.pen)
            lineItem.setLine(0, posY, 3 * self.photometry.ABERRATION_SIZE, posY)
            self.ui.aberration.p[0].addItem(lineItem)

        tab = self.ui.tabImage
        tab.setTabEnabled(getTabIndex(tab, "Aberration"), True)
        self.ui.aberration.p[0].getViewBox().rightMouseRange()

    def showImageSources(self) -> None:
        temp = self.imageSourceRange
        self.ui.imageSource.setImage(imageDisp=self.photometry.image)
        self.ui.imageSource.p[0].getViewBox().sigRangeChanged.connect(self.getImageSourceRange)
        if temp:
            self.ui.imageSource.p[0].getViewBox().setRange(rect=temp)

        photometry = self.photometry
        for i in range(len(photometry.hfr)):
            eItem = self.ui.imageSource.addEllipse(
                photometry.xCoord[i],
                photometry.yCoord[i],
                photometry.aAxis[i] * 4,
                photometry.bAxis[i] * 4,
                photometry.theta[i],
            )
            if self.ui.showValues.isChecked():
                t = f"{photometry.hfr[i]:2.1f}"
                item = pg.TextItem(text=t, color=self.parent.M_PRIM, anchor=(1, 1))
                item.setFont(self.fontAnno)
                item.setParentItem(eItem)
        tab = self.ui.tabImage
        tab.setTabEnabled(getTabIndex(tab, "Sources"), True)

    def showBackground(self) -> None:
        self.ui.background.setImage(imageDisp=self.photometry.background)
        self.ui.background.barItem.setLevels(
            (self.photometry.backgroundMin, self.photometry.backgroundMax)
        )
        tab = self.ui.tabImage
        tab.setTabEnabled(getTabIndex(tab, "Back"), True)

    def showBackgroundRMS(self) -> None:
        self.ui.backgroundRMS.setImage(imageDisp=self.photometry.backgroundRMS)
        tab = self.ui.tabImage
        tab.setTabEnabled(getTabIndex(tab, "BackRMS"), True)
