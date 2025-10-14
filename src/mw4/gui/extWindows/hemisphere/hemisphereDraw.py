############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages
import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QFont

from mw4.base.transform import diffModulusAbs

# local import
from mw4.gui.utilities.slewInterface import SlewInterface
from mw4.gui.utilities.toolsQtWidget import MWidget
from mw4.mountcontrol.setting import Setting


class HemisphereDraw(MWidget, SlewInterface):
    """ """

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.ui = parent.ui
        self.app = parent.app
        self.msg = parent.msg

        self.pointerDome = None
        self.modelPointsText = []
        self.alignmentStars = None
        self.alignmentStarsText = None
        self.horizonLimitHigh = None
        self.horizonLimitLow = None
        self.meridianSlew = None
        self.meridianTrack = None
        self.hemMouse = None

    def initConfig(self) -> None:
        """ """
        self.app.update3s.connect(self.drawAlignmentStars)

        self.app.mount.signals.pointDone.connect(self.drawPointer)
        self.app.dome.signals.azimuth.connect(self.drawDome)
        self.app.dome.signals.deviceDisconnected.connect(self.drawDome)
        self.app.dome.signals.serverDisconnected.connect(self.drawDome)
        self.ui.showSlewPath.clicked.connect(self.drawTab)
        self.ui.showHorizon.clicked.connect(self.drawTab)
        self.ui.showAlignStar.clicked.connect(self.drawTab)
        self.ui.showMountLimits.clicked.connect(self.drawTab)
        self.ui.showCelestial.clicked.connect(self.drawTab)
        self.ui.showPolar.clicked.connect(self.drawTab)
        self.ui.showTerrain.clicked.connect(self.drawTab)
        self.ui.showIsoModel.clicked.connect(self.drawTab)
        self.app.mount.signals.getModelDone.connect(self.drawTab)
        self.ui.showTerrain.clicked.connect(self.drawTab)
        self.ui.azimuthShift.valueChanged.connect(self.drawTab)
        self.ui.altitudeShift.valueChanged.connect(self.drawTab)
        self.ui.terrainAlpha.valueChanged.connect(self.drawTab)
        self.app.mount.signals.settingDone.connect(self.updateOnChangedParams)
        self.ui.normalModeHem.clicked.connect(self.setOperationMode)
        self.ui.editModeHem.clicked.connect(self.setOperationMode)
        self.ui.alignmentModeHem.clicked.connect(self.setOperationMode)
        self.app.updatePointMarker.connect(self.setupModel)
        self.app.redrawHemisphere.connect(self.drawTab)
        self.app.redrawHorizon.connect(self.drawHorizon)
        self.app.operationRunning.connect(self.enableOperationModeChange)
        self.ui.hemisphere.p[0].scene().sigMouseMoved.connect(self.mouseMovedHemisphere)

        sett = self.app.mount.setting
        self.meridianSlew = sett.meridianLimitSlew
        self.meridianTrack = sett.meridianLimitTrack
        self.horizonLimitHigh = sett.horizonLimitHigh
        self.horizonLimitLow = sett.horizonLimitLow

    def close(self) -> None:
        """ """
        self.app.update3s.disconnect(self.drawAlignmentStars)

    def mouseMovedHemisphere(self, pos: QPointF) -> None:
        """ """
        self.parent.mouseMoved(pos)

    def enableOperationModeChange(self, status: int) -> None:
        """ """
        isRunning = status != 0
        if isRunning:
            self.ui.normalModeHem.setChecked(True)
        self.ui.operationModeGroup.setEnabled(not isRunning)

    def setOperationMode(self) -> None:
        """ """
        if self.ui.editModeHem.isChecked():
            self.drawModelPoints()
        elif self.ui.alignmentModeHem.isChecked():
            self.ui.showAlignStar.setChecked(True)
            self.app.data.clearBuildP()
        self.drawTab()

    def updateOnChangedParams(self, sett: Setting) -> bool:
        """ """
        needRedraw = False
        if self.meridianSlew != sett.meridianLimitSlew:
            self.meridianSlew = sett.meridianLimitSlew
            needRedraw = True
        if self.meridianTrack != sett.meridianLimitTrack:
            self.meridianTrack = sett.meridianLimitTrack
            needRedraw = True
        if self.horizonLimitHigh != sett.horizonLimitHigh:
            self.horizonLimitHigh = sett.horizonLimitHigh
            needRedraw = True
        if self.horizonLimitLow != sett.horizonLimitLow:
            self.horizonLimitLow = sett.horizonLimitLow
            needRedraw = True
        if needRedraw:
            self.drawTab()
        return needRedraw

    def prepareView(self) -> None:
        """ """
        plotItem = self.ui.hemisphere.p[0]
        self.parent.preparePlotItem(plotItem)
        polarItem = self.ui.hemisphere.p[1]
        self.parent.preparePolarItem(polarItem)
        self.pointerDome = None
        self.modelPointsText = []
        self.alignmentStars = None
        self.alignmentStarsText = None
        plotItem.getViewBox().callbackMDC = self.mouseDoubleClick

    def drawCelestialEquator(self) -> None:
        """ """
        celestial = self.app.data.generateCelestialEquator()
        if not celestial:
            return

        for i, plotItem in enumerate(self.ui.hemisphere.p):
            alt, az = zip(*celestial)
            alt = np.array(alt)
            az = np.array(az)
            pd = pg.ScatterPlotItem()
            if i == 1:
                az, alt = self.ui.hemisphere.toPolar(az, alt)
            pd.setData(
                x=az,
                y=alt,
                symbol="o",
                pen=pg.mkPen(color=self.M_TER1, size=0.9),
                brush=pg.mkBrush(color=self.M_TER),
                size=0.9,
            )
            plotItem.addItem(pd)

    def drawHorizon(self) -> None:
        """ """
        p0 = self.ui.hemisphere.p[0]
        p1 = self.ui.hemisphere.p[1]
        self.ui.hemisphere.drawHorizon(self.app.data.horizonP, plotItem=p0)
        self.ui.hemisphere.drawHorizon(self.app.data.horizonP, plotItem=p1, polar=True)

    def drawMeridianLimits(self) -> None:
        """ """
        slew = self.app.mount.setting.meridianLimitSlew
        track = self.app.mount.setting.meridianLimitTrack
        if slew is None or track is None:
            return

        plotItem = self.ui.hemisphere.p[0]

        mSlew = pg.QtWidgets.QGraphicsRectItem(180 - slew, 0, 2 * slew, 90)
        mSlew.setPen(pg.mkPen(color=self.M_YELLOW1 + "40"))
        mSlew.setBrush(pg.mkBrush(color=self.M_YELLOW + "40"))
        mSlew.setZValue(10)
        plotItem.addItem(mSlew)

        mTrack = pg.QtWidgets.QGraphicsRectItem(180 - track, 0, 2 * track, 90)
        mTrack.setPen(pg.mkPen(color=self.M_YELLOW1 + "40"))
        mTrack.setBrush(pg.mkBrush(color=self.M_YELLOW + "40"))
        mTrack.setZValue(20)
        plotItem.addItem(mTrack)

    def drawHorizonLimits(self) -> None:
        """ """
        plotItem = self.ui.hemisphere.p[0]
        val = self.app.mount.setting.horizonLimitHigh
        high = val if val is not None else 90

        val = self.app.mount.setting.horizonLimitLow
        low = val if val is not None else 0

        hLow = pg.QtWidgets.QGraphicsRectItem(0, high, 360, 90 - high)
        hLow.setPen(pg.mkPen(color=self.M_RED1 + "40"))
        hLow.setBrush(pg.mkBrush(color=self.M_RED + "40"))
        hLow.setZValue(0)
        plotItem.addItem(hLow)

        hHigh = pg.QtWidgets.QGraphicsRectItem(0, 0, 360, low)
        hHigh.setPen(pg.mkPen(color=self.M_RED1 + "40"))
        hHigh.setBrush(pg.mkBrush(color=self.M_RED + "40"))
        hHigh.setZValue(0)
        plotItem.addItem(hHigh)

    def setupAlignmentStars(self) -> None:
        """ """
        plotItem = self.ui.hemisphere.p[0]
        hip = self.app.hipparcos
        self.alignmentStarsText = []
        pd = pg.ScatterPlotItem(symbol="star", size=6, pen=pg.mkPen(color=self.M_YELLOW1))
        pd.setZValue(30)
        self.alignmentStars = pd
        plotItem.addItem(pd)
        for i in range(len(hip.name)):
            textItem = pg.TextItem(anchor=(0.5, 1.1))
            self.alignmentStarsText.append(textItem)
            plotItem.addItem(textItem)

    def calculateRelevance(self, alt: float, az: float) -> float:
        """ """
        if self.app.mount.obsSite.location is None:
            isNorth = True
        else:
            isNorth = self.app.mount.obsSite.location.latitude.degrees > 0
        altFak = 1 - np.minimum(np.abs(alt - 30), 35) / 35
        if isNorth:
            azFak = 1 - np.minimum(diffModulusAbs(0, az - 180, 360), 75) / 75
        else:
            azFak = 1 - np.minimum(diffModulusAbs(0, az, 360), 75) / 75
        sumFak = np.sqrt(altFak * azFak)
        return sumFak

    def selectFontParam(self, relevance: float) -> tuple:
        """ """
        cMap = pg.ColorMap([0, 0.6, 1.0], [self.M_RED, self.M_YELLOW, self.M_GREEN])
        color = cMap[float(relevance)]
        size = 8 + int(relevance * 5)
        return color, size

    def drawAlignmentStars(self) -> None:
        """ """
        if not self.ui.showAlignStar.isChecked():
            return
        if self.alignmentStars is None:
            return

        hip = self.app.hipparcos
        hip.calculateAlignStarPositionsAltAz()
        isAlignMode = self.ui.alignmentModeHem.isChecked()
        self.alignmentStars.setData(x=hip.az, y=hip.alt)
        for i, val in enumerate(zip(hip.alt, hip.az, hip.name)):
            alt, az, name = val
            color = self.M_YELLOW if isAlignMode else self.M_YELLOW1

            size = 10 if isAlignMode else 6
            if isAlignMode:
                rel = self.calculateRelevance(alt=alt, az=az)
                fontColor, fontSize = self.selectFontParam(rel)
            else:
                fontSize = 8
                fontColor = self.M_TER1

            item = self.alignmentStars.points()[i]
            item.setPen(pg.mkPen(color=color))
            item.setBrush(pg.mkBrush(color=color))
            item.setSize(size)
            font = QFont(
                self.window().font().family(),
                int(self.window().font().pointSize() * fontSize / 9),
            )
            self.alignmentStarsText[i].setText(name)
            self.alignmentStarsText[i].setFont(font)
            self.alignmentStarsText[i].setColor(fontColor)
            self.alignmentStarsText[i].setPos(az, alt)
            self.alignmentStarsText[i].setZValue(30)

    def drawModelPoints(self) -> None:
        """ """
        points = self.app.data.buildP
        if not points:
            return

        x = [x[1] for x in points]
        y = [x[0] for x in points]
        act = [x[2] for x in points]

        for index, plotItem in enumerate(self.ui.hemisphere.p):
            item = self.ui.hemisphere.findItemByName(plotItem, "model")
            if not item:
                continue
            if index == 1:
                x, y = self.ui.hemisphere.toPolar(x, y)
            item.setData(x=x, y=y)

            isEdit = self.ui.editModeHem.isChecked()
            for i in range(len(x)):
                active = act[i]
                col = [self.M_TER, self.M_GREEN, self.M_RED]
                colActive = col[active]
                color = self.M_PINK if isEdit else colActive
                sym = ["d", "o", "x"]
                symbol = sym[active]

                spot = item.scatter.points()[i]
                spot.setPen(pg.mkPen(color=color, width=1.5))
                spot.setBrush(pg.mkBrush(color=color + "40"))
                spot.setSymbol(symbol)

    def drawModelText(self) -> None:
        """ """
        plotItem = self.ui.hemisphere.p[0]
        points = self.app.data.buildP
        if not points:
            return
        x = [x[1] for x in points]
        y = [x[0] for x in points]
        act = [x[2] for x in points]

        for textItem in self.modelPointsText:
            self.ui.hemisphere.p[0].removeItem(textItem)
        self.modelPointsText = []
        isEdit = self.ui.editModeHem.isChecked()
        facFont = 1 if isEdit else 0.85
        font = QFont(
            self.window().font().family(),
            int(self.window().font().pointSize() * facFont),
        )
        for i in range(len(x)):
            az = x[i]
            alt = y[i]
            active = act[i]
            col = [self.M_TER, self.M_GREEN, self.M_RED]
            colActive = col[active]
            color = self.M_PINK if isEdit else colActive

            text = f"{i + 1}"
            textItem = pg.TextItem(anchor=(0.5, 1.1))
            textItem.setText(text)
            textItem.setFont(font)
            textItem.setColor(color)
            textItem.setPos(az, alt)
            textItem.setZValue(40)
            self.modelPointsText.append(textItem)
            plotItem.addItem(textItem)

    def updateDataModel(self, x: float, y: float) -> None:
        """ """
        bp = [(y, x, True) for y, x in zip(y, x)]
        self.app.data.buildP = bp
        self.drawModelPoints()
        self.drawModelText()
        self.app.buildPointsChanged.emit()

    def setupModel(self) -> None:
        """ """
        for i, plotItem in enumerate(self.ui.hemisphere.p):
            if self.ui.showSlewPath.isChecked():
                pen = pg.mkPen(color=self.M_GREEN, style=Qt.PenStyle.DashLine)
            else:
                pen = None

            if self.ui.editModeHem.isChecked():
                pd = pg.PlotDataItem(
                    symbolBrush=pg.mkBrush(color=self.M_PINK + "40"),
                    symbolPen=pg.mkPen(color=self.M_PINK1, width=2),
                    symbolSize=10,
                    symbol="o",
                    connect="all",
                    pen=pen,
                )
                pd.nameStr = "model"
                vb = plotItem.getViewBox()
                vb.setPlotDataItem(pd)
                if i == 0:
                    vb.updateData = self.updateDataModel
            else:
                pd = pg.PlotDataItem(
                    symbolBrush=pg.mkBrush(color=self.M_GREEN + "40"),
                    symbolPen=pg.mkPen(color=self.M_GREEN1, width=2),
                    symbolSize=8,
                    symbol="o",
                    connect="all",
                    pen=pen,
                )
                pd.nameStr = "model"
                vb = plotItem.getViewBox()
                if i == 0:
                    vb.setPlotDataItem(None)
            pd.setZValue(40)
            plotItem.addItem(pd)

        self.drawModelPoints()
        self.drawModelText()

    def setupPointer(self) -> None:
        """ """
        for plotItem in self.ui.hemisphere.p:
            symbol = self.makePointer()
            pd = pg.ScatterPlotItem(symbol=symbol, size=40)
            pd.setData(x=[0], y=[0])
            pd.setPen(pg.mkPen(color=self.M_PINK))
            pd.setBrush(pg.mkBrush(color=self.M_PINK + "20"))
            pd.setZValue(60)
            pd.nameStr = "pointer"
            plotItem.addItem(pd)

    def drawPointer(self) -> None:
        """ """
        items = []
        for plotItem in self.ui.hemisphere.p:
            item = self.ui.hemisphere.findItemByName(plotItem, "pointer")
            if item:
                items.append(item)

        obsSite = self.app.mount.obsSite
        isVisible = not (obsSite.Alt is None or obsSite.Az is None)
        for item in items:
            item.setVisible(isVisible)

        if not isVisible or not items:
            return

        alt = obsSite.Alt.degrees
        az = obsSite.Az.degrees
        items[0].setData(x=[az], y=[alt])
        x, y = self.ui.hemisphere.toPolar([az], [alt])
        items[1].setData(x=x, y=y)

    def setupDome(self) -> None:
        """ """
        plotItem = self.ui.hemisphere.p[0]
        self.pointerDome = pg.QtWidgets.QGraphicsRectItem(165, 1, 30, 88)
        self.pointerDome.setPen(pg.mkPen(color=self.M_SEC))
        self.pointerDome.setBrush(pg.mkBrush(color=self.M_SEC + "80"))
        self.pointerDome.setVisible(False)
        plotItem.addItem(self.pointerDome)

    def drawDome(self, azimuth: float = None) -> None:
        """ """
        if not isinstance(azimuth, int | float):
            self.pointerDome.setVisible(False)
            return

        visible = self.app.deviceStat.get("dome", False)
        self.pointerDome.setRect(azimuth - 15, 1, 30, 88)
        self.pointerDome.setVisible(visible)

    def getMountModelData(self) -> tuple:
        """ """
        model = self.app.mount.model
        if len(model.starList) == 0:
            return None, None, None
        alt = np.array([x.alt.degrees for x in model.starList])
        az = np.array([x.az.degrees for x in model.starList])
        err = np.array([x.errorRMS for x in model.starList])
        return az, alt, err

    def drawModelIsoCurve(self) -> None:
        """ """
        az, alt, err = self.getMountModelData()
        if az is None or alt is None or err is None:
            return

        self.ui.hemisphere.addIsoItemHorizon(az, alt, err)

    def slewDirect(self, posView: QPointF) -> None:
        """ """
        azimuth = int(posView.x() + 0.5)
        altitude = int(posView.y() + 0.5)

        question = "<b>Manual slewing to coordinate</b>"
        question += "<br><br>Selected coordinates are:<br>"
        question += f"<font color={self.M_PRIM}> Altitude: {altitude:3.1f}°"
        question += f"   Azimuth: {azimuth:3.1f}°</font>"
        question += "<br><br>Would you like to start slewing?<br>"

        suc = self.messageDialog(self, "Slewing mount", question)
        if not suc:
            return
        self.slewTargetAltAz(altitude, azimuth)

    def slewStar(self, posView: QPointF) -> None:
        """ """
        spot = self.alignmentStars.pointsAt(posView)
        if len(spot) == 0:
            return

        index = spot[0].index()
        hip = self.app.hipparcos
        name = hip.name[index]
        ra, dec = hip.getAlignStarRaDecFromName(hip.name[index])

        question = "<b>Polar / Ortho Alignment procedure</b>"
        question += "<br>Selected alignment star: "
        question += f"<font color={self.M_PRIM}>{name}.</font>"
        question += "<br>Would you like to start alignment?<br>"

        isDAT = self.app.mount.setting.statusDualAxisTracking
        warning = f"<br><i><font color={self.M_YELLOW}>"
        warning += "Dual Axis Tracking is actually enabled!<br>"
        warning += "It should be off during alignment process.</font></i>"

        buttons = ["Cancel", "Ortho Align", "Polar Align"]
        question = question + warning if isDAT else question
        reply = self.messageDialog(self, "Slewing mount", question, buttons)
        if reply == 0:
            return
        elif reply == 1:
            alignType = "ortho"
        else:
            alignType = "polar"

        t = f"Align [{alignType}] to [{name}]"
        self.msg.emit(1, "Hemisphere", "Align", t)
        self.slewTargetRaDec(ra, dec, slewType=alignType, epoch="JNow")

    def mouseDoubleClick(self, ev, posView: QPointF) -> None:
        """ """
        if self.ui.alignmentModeHem.isChecked():
            self.slewStar(posView)
        elif self.ui.normalModeHem.isChecked():
            self.slewDirect(posView)

    def drawTab(self) -> None:
        """ """
        hasModel = bool(self.app.mount.model.numberStars)
        self.ui.alignmentModeHem.setEnabled(hasModel)
        self.ui.showIsoModel.setEnabled(hasModel)
        isMount = bool(self.app.deviceStat["mount"])
        self.ui.showMountLimits.setEnabled(isMount)

        self.prepareView()
        if self.ui.showCelestial.isChecked():
            self.drawCelestialEquator()
        if self.ui.showTerrain.isChecked():
            self.parent.horizonDraw.drawTerrainImage(self.ui.hemisphere.p[0])
        if self.ui.showMountLimits.isChecked():
            self.drawMeridianLimits()
            self.drawHorizonLimits()
        if self.ui.showIsoModel.isChecked():
            self.drawModelIsoCurve()
        self.setupAlignmentStars()
        self.drawAlignmentStars()
        self.setupModel()
        self.setupPointer()
        self.drawPointer()
        self.setupDome()
        self.drawDome()
        self.ui.hemisphere.p[1].getViewBox().rightMouseRange()
        if self.ui.showHorizon.isChecked():
            self.drawHorizon()
