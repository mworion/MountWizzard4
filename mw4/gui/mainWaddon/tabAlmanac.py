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
from dateutil.tz import tzlocal

# external packages
from PySide6.QtGui import QPixmap, QPainter, QPen, QColor
from PySide6.QtCore import Qt, QPointF, QObject
import pyqtgraph as pg
from skyfield import almanac
from skyfield.toposlib import GeographicPosition
from skyfield.trigonometry import position_angle_of
import numpy as np
from range_key_dict import RangeKeyDict

# local import
from base.tpool import Worker
from gui.utilities.toolsQtWidget import changeStyleDynamic


class Almanac(QObject):
    """ """

    phasesText = RangeKeyDict(
        {
            (0, 1): "New moon",
            (1, 23): "Waxing crescent",
            (23, 27): "First quarter",
            (27, 48): "Waxing gibbous",
            (48, 52): "Full moon",
            (52, 73): "Waning gibbous",
            (73, 77): "Third quarter",
            (77, 99): "Waning crescent",
            (99, 100): "New moon ",
        }
    )
    Y_TICKS = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24]
    Y_LABELS = ["", "14", "16", "18", "20", "22", "24", "02", "04", "06", "08", "10", ""]

    def __init__(self, mainW):
        super().__init__()
        self.mainW = mainW
        self.app = mainW.app
        self.ui = mainW.ui

        self.civil = None
        self.nautical = None
        self.astronomical = None
        self.twilightTime = None
        self.twilightEvents = None
        self.colors = None
        self.worker: Worker = None
        self.setColors()
        self.app.update1h.connect(self.showMoonPhase)
        self.app.colorChange.connect(self.updateColorSet)
        self.ui.unitTimeUTC.toggled.connect(self.showTwilightDataList)
        self.ui.unitTimeUTC.toggled.connect(self.showTwilightDataPlot)
        self.ui.unitTimeUTC.toggled.connect(self.showMoonPhase)

    def initConfig(self) -> None:
        """ """
        config = self.app.config["mainW"]
        self.ui.almanacPrediction.currentIndexChanged.connect(self.showTwilightDataPlot)
        self.ui.almanacPrediction.setCurrentIndex(config.get("almanacPrediction", 0))

    def storeConfig(self) -> None:
        """ """
        config = self.app.config["mainW"]
        config["almanacPrediction"] = self.ui.almanacPrediction.currentIndex()

    def setColors(self) -> None:
        """ """
        self.ui.almanacCivil.setStyleSheet(f"background-color: {self.mainW.M_PRIM1};")
        self.ui.almanacNautical.setStyleSheet(f"background-color: {self.mainW.M_PRIM2};")
        self.ui.almanacAstronomical.setStyleSheet(f"background-color: {self.mainW.M_PRIM3};")
        self.ui.almanacDark.setStyleSheet(f"background-color: {self.mainW.M_PRIM4};")
        self.colors = [
            self.mainW.M_PRIM4,
            self.mainW.M_PRIM3,
            self.mainW.M_PRIM2,
            self.mainW.M_PRIM1,
            self.mainW.M_BACK,
        ]

    def updateColorSet(self) -> None:
        """ """
        self.setColors()
        self.ui.twilight.colorChange()
        self.showTwilightDataList()
        self.showTwilightDataPlot()
        self.showMoonPhase()

    def plotTwilightData(self, result) -> None:
        """ """
        ts, t, e = result
        xMin = int(t[0].tt) + 1
        xMax = int(t[-1].tt) - 1
        xNow = (xMax - xMin) / 2 + xMin

        xTicks = np.arange(xMin, xMax, (xMax - xMin) / 9)
        xLabels = ts.tt_jd(xTicks).utc_strftime("%d%b")
        xLabels[0] = ""
        xTicks = [(x, y) for x, y in zip(xTicks, xLabels)]
        yTicks = [(x, y) for x, y in zip(self.Y_TICKS, self.Y_LABELS)]
        penLine = pg.mkPen(color=self.mainW.M_PINK + "80", width=2)
        plotItem = self.ui.twilight.p[0]
        plotItem.getViewBox().setMouseMode(pg.ViewBox().RectMode)
        plotItem.getViewBox().xRange = (0, 360)
        plotItem.getViewBox().yRange = (0, 90)
        plotItem.showAxes(True, showValues=True)
        plotItem.getAxis("bottom").setTicks([xTicks])
        plotItem.getAxis("left").setTicks([yTicks])
        plotItem.getAxis("top").setTicks([xTicks])
        plotItem.getAxis("right").setTicks([yTicks])
        plotItem.setLimits(xMin=xMin, xMax=xMax, yMin=0, yMax=24)
        plotItem.setYRange(0, 24)
        plotItem.setXRange(xMin, xMax)

        pens = []
        brushes = []
        for i in range(5):
            pens.append(pg.mkPen(color=self.colors[i]))
            brushes.append(pg.mkBrush(color=self.colors[i]))
        penBar = [pens[x] for x in e]
        brushBar = [brushes[x] for x in e]

        tLoc = t.astimezone(tzlocal())
        refDay = [x.replace(hour=0, minute=0, second=0, microsecond=0) for x in tLoc]
        dayLoc = tLoc - refDay
        yH = [x.total_seconds() / 3600 for x in dayLoc]
        xD = np.array([int(x) for x in t.tt])

        plotItem.clear()
        for i in range(len(t)):
            if yH[i] > 12:
                rect = pg.QtWidgets.QGraphicsRectItem(xD[i], yH[i] - 12, 1, 24 - (yH[i] - 12))
            else:
                rect = pg.QtWidgets.QGraphicsRectItem(xD[i], 12 + yH[i], 1, 24 - (12 + yH[i]))
            rect.setPen(penBar[i])
            rect.setBrush(brushBar[i])
            plotItem.addItem(rect)
        plotItem.addLine(x=xNow, pen=penLine)

        changeStyleDynamic(self.ui.almanacGroup, "running", False)

    def listTwilightData(self, timeEvents, events):
        """ """
        text = ""
        self.ui.twilightEvents.clear()
        self.ui.twilightEvents.setTextColor(QColor(self.mainW.M_PRIM))

        for timeEvent, event in zip(timeEvents, events):
            text += f"{self.mainW.convertTime(timeEvent, '%H:%M:%S')} "
            text += f"{almanac.TWILIGHTS[event]}"
            self.ui.twilightEvents.insertPlainText(text)
            text = "\n"
        title = "Sun " + self.mainW.timeZoneString()
        self.ui.sunAlmanacGroup.setTitle(title)

    def calcTwilightData(
        self, ts, location: GeographicPosition, tWinL: int, tWinH: int
    ) -> (list, list):
        """ """
        timeJD = self.app.mount.obsSite.timeJD
        t0 = ts.tt_jd(int(timeJD.tt) - tWinL)
        t1 = ts.tt_jd(int(timeJD.tt) + tWinH + 1)

        f = almanac.dark_twilight_day(self.app.ephemeris, location)
        twilightTime, twilightEvents = almanac.find_discrete(t0, t1, f)
        return twilightTime, twilightEvents

    def workerCalcTwilightDataPlot(
        self, ts, location: GeographicPosition, timeWindow
    ) -> (list, list, list):
        """ """
        t, e = self.calcTwilightData(ts, location, timeWindow, timeWindow)
        return ts, t, e

    def showTwilightDataPlot(self) -> None:
        """ """
        timeWindowParam = [17, 32, 47, 92, 182]
        location = self.app.mount.obsSite.location
        if location is None:
            return

        index = self.ui.almanacPrediction.currentIndex()
        text = self.ui.almanacPrediction.currentText()
        timeWindow = timeWindowParam[index]

        t = f"Twilight passes for: {text} {self.mainW.timeZoneString()}"
        self.ui.almanacGroup.setTitle(t)

        ts = self.app.mount.obsSite.ts
        changeStyleDynamic(self.ui.almanacGroup, "running", True)
        self.worker = Worker(self.workerCalcTwilightDataPlot, ts, location, timeWindow)
        self.worker.signals.result.connect(self.plotTwilightData)
        self.app.threadPool.start(self.worker)

    def showTwilightDataList(self) -> None:
        """ """
        location = self.app.mount.obsSite.location
        if location is None:
            return

        ts = self.app.mount.obsSite.ts
        result = self.calcTwilightData(ts, location, 0, 1)
        self.twilightTime, self.twilightEvents = result
        self.listTwilightData(self.twilightTime[:8], self.twilightEvents[:8])

    def calcMoonPhase(self) -> list:
        """ """
        ephemeris = self.app.ephemeris
        sun = ephemeris["sun"]
        moon = ephemeris["moon"]
        earth = ephemeris["earth"]
        now = self.app.mount.obsSite.ts.now()
        loc = self.app.mount.obsSite.location
        ts = self.app.mount.obsSite.ts
        timeJD = self.app.mount.obsSite.timeJD
        e = earth.at(timeJD)

        # calc phases for obstruction
        _, sunLon, _ = e.observe(sun).apparent().ecliptic_latlon()
        _, moonLon, _ = e.observe(moon).apparent().ecliptic_latlon()

        mpIllumination = almanac.fraction_illuminated(ephemeris, "moon", now)
        mpDegree = (moonLon.degrees - sunLon.degrees) % 360.0
        mpPercent = mpDegree / 360 * 100
        retVal = [mpIllumination, mpDegree, mpPercent]

        locObserver = (loc + earth).at(timeJD)
        moonApparent = locObserver.observe(moon).apparent()
        sunApparent = locObserver.observe(sun).apparent()
        moonAngle = position_angle_of(moonApparent.altaz(), sunApparent.altaz())
        retVal.append(moonAngle)

        # calc rise and set times
        t0 = ts.tt_jd(int(timeJD.tt))
        t1 = ts.tt_jd(int(timeJD.tt) + 2)

        f = almanac.risings_and_settings(ephemeris, ephemeris["moon"], loc)
        moonTimes, moonEvents = almanac.find_discrete(t0, t1, f)
        moonTimes = moonTimes[0:3]
        moonEvents = moonEvents[0:3]
        retVal.append(moonTimes)
        retVal.append(moonEvents)

        # calc nodes
        t0 = ts.tt_jd(int(timeJD.tt))
        t1 = ts.tt_jd(int(timeJD.tt) + 29)
        f = almanac.moon_nodes(ephemeris)
        nodeTimes, nodeEvents = almanac.find_discrete(t0, t1, f)
        nodeTimes = nodeTimes[0:2]
        nodeEvents = nodeEvents[0:2]
        retVal.append(nodeTimes)
        retVal.append(nodeEvents)

        return retVal

    def generateMoonMask(self, pixmap: QPixmap, mpDegree: float) -> QPixmap:
        """ """
        colCover = QColor(self.mainW.M_BACK)
        colFree = QColor("transparent")
        colFrame = QColor(self.mainW.M_SEC1)

        penCov = QPen(colCover, 0)
        penFree = QPen(colFree, 0)
        penFrame = QPen(colFrame, 3)

        height = pixmap.height()
        width = pixmap.width()
        h2 = height / 2
        w2 = width / 2

        moonMask = QPixmap(width, height)
        moonMask.fill(QColor("transparent"))

        maskPainter = QPainter(moonMask)
        maskPainter.setBrush(Qt.BrushStyle.SolidPattern)
        maskPainter.setBrush(colFree)
        maskPainter.setPen(penFrame)

        if 0 <= mpDegree <= 90:
            maskPainter.setBrush(colCover)
            maskPainter.drawPie(0, 0, width, height, 90 * 16, 180 * 16)

            r = np.cos(np.radians(mpDegree)) * w2
            maskPainter.setBrush(colCover)
            maskPainter.setPen(penCov)
            maskPainter.drawEllipse(QPointF(w2, h2), r, h2)

        elif 90 < mpDegree <= 180:
            maskPainter.setBrush(colCover)
            maskPainter.drawPie(0, 0, width, height, 90 * 16, 180 * 16)

            maskPainter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
            r = np.cos(np.radians(mpDegree)) * w2
            maskPainter.setBrush(colFree)
            maskPainter.setPen(colFree)
            maskPainter.drawEllipse(QPointF(w2, h2), r, h2)

        elif 180 < mpDegree <= 270:
            maskPainter.setBrush(colCover)
            maskPainter.drawPie(0, 0, width, height, -90 * 16, 180 * 16)

            maskPainter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
            r = np.cos(np.radians(mpDegree)) * w2
            maskPainter.setBrush(colFree)
            maskPainter.setPen(penFree)
            maskPainter.drawEllipse(QPointF(w2, h2), r, h2)

        else:
            maskPainter.setBrush(colCover)
            maskPainter.drawPie(0, 0, width, height, -90 * 16, 180 * 16)

            r = np.cos(np.radians(mpDegree)) * w2
            maskPainter.setPen(penCov)
            maskPainter.setBrush(colCover)
            maskPainter.drawEllipse(QPointF(w2, h2), r, h2)

        maskPainter.end()
        return moonMask

    def showMoonPhase(self) -> None:
        """ """
        calcMoon = self.calcMoonPhase()

        mpIllumination, mpDegree, mpPercent, moonAngle = calcMoon[0:4]
        self.ui.moonPhaseIllumination.setText(f"{mpIllumination * 100:3.1f}")
        self.ui.moonPhasePercent.setText(f"{mpPercent:3.0f}")
        self.ui.moonPhaseDegree.setText(f"{mpDegree:3.0f}")

        moonTimes, moonEvents = calcMoon[4:6]
        text = ""
        self.ui.riseSetEventsMoon.clear()
        self.ui.riseSetEventsMoon.setTextColor(QColor(self.mainW.M_PRIM))
        moon = ["set", "rise"]
        for moonTime, moonEvent in zip(moonTimes, moonEvents):
            textTime = self.mainW.convertTime(moonTime, "%d.%m. %H:%M")
            text += f"{textTime} {moon[moonEvent]}"
            self.ui.riseSetEventsMoon.insertPlainText(text)
            text = "\n"
        title = "Moon " + self.mainW.timeZoneString()
        self.ui.moonAlmanacGroup.setTitle(title)

        self.ui.moonPhaseText.setText(self.phasesText[mpPercent])

        nodeTimes, nodeEvents = calcMoon[6:8]
        text = ""
        self.ui.nodeEvents.clear()
        self.ui.nodeEvents.setTextColor(QColor(self.mainW.M_PRIM))
        node = ["ascending", "descending"]
        for nodeTime, nodeEvent in zip(nodeTimes, nodeEvents):
            textTime = self.mainW.convertTime(nodeTime, "%d.%m. %H:%M")
            text += f"{textTime} {node[nodeEvent]}"
            self.ui.nodeEvents.insertPlainText(text)
            text = "\n"

        moon = QPixmap(":/pics/moon.png")
        moonMask = self.generateMoonMask(moon, mpDegree)

        m = QPainter(moon)
        m.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
        m.drawPixmap(0, 0, moonMask)
        m.end()

        width = self.ui.moonPic.width()
        height = self.ui.moonPic.height()
        self.ui.moonPic.setPixmap(moon.scaled(width, height))
