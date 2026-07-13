############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10_micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2026 by mworion
# License APL2.0
#
###########################################################
import numpy as np
import pyqtgraph as pg
from dataclasses import dataclass
from dateutil.tz import tzlocal
from importlib.resources import as_file, files
from mw4.base.tpool import Worker
from mw4.gui.mainWaddon.tabAddon import TabAddon
from mw4.gui.utilities.qtHelpers import changeStyleDynamic, setPixmapAlpha
from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QBrush, QColor, QPainter, QPen, QPixmap
from pytestqt.qtbot import QWidget
from range_key_dict import RangeKeyDict
from skyfield import almanac
from skyfield.timelib import Timescale
from skyfield.toposlib import GeographicPosition
from skyfield.trigonometry import position_angle_of
from typing import Any

TWILIGHT_PLOT_DAYS: int = 91
MAX_TWILIGHT_ROWS: int = 8
MOON_RISE_DAYS: int = 2
MOON_RISE_MAX: int = 3
MOON_NODE_DAYS: int = 29
MOON_NODE_MAX: int = 2


@dataclass
class MoonPhaseData:
    illumination: float
    degree: float
    percent: float
    angle: Any
    moonTimes: Any
    moonEvents: Any
    nodeTimes: Any
    nodeEvents: Any


class Almanac(TabAddon):
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

    def __init__(self, mainW: Any) -> None:
        self.mainW = mainW
        self.app = mainW.app
        self.ui = mainW.ui

        self.civil = None
        self.nautical = None
        self.astronomical = None
        self.twilightTime = None
        self.twilightEvents = None
        self.colors: dict[QWidget, list[int]] = {}
        self.workerCalcTwilightDataPlot: Worker | None = None
        self.app.timeMgr.update30m.connect(self.showMoonPhase)
        self.app.colorChange.connect(self.updateColorSet)
        self.app.timebaseChanged.connect(self.showTwilightDataList)
        self.app.timebaseChanged.connect(self.showTwilightDataPlot)
        self.app.timebaseChanged.connect(self.showMoonPhase)

    def initConfig(self) -> None:
        self.updateColorSet()

    def setColors(self) -> None:
        self.colors = {
            self.ui.almanacDark: self.mainW.M_PRIM4a,
            self.ui.almanacAstronomical: self.mainW.M_PRIM3a,
            self.ui.almanacNautical: self.mainW.M_PRIM2a,
            self.ui.almanacCivil: self.mainW.M_PRIM1a,
        }
        for widget, c in self.colors.items():
            val = f"background-color: rgba({c[0]}, {c[1]}, {c[2]}, {c[3]});"
            val += f"border-color: rgba({c[0]}, {c[1]}, {c[2]}, {c[3]});"
            widget.setStyleSheet(val)

    def plotAll(self) -> None:
        self.showTwilightDataList()
        self.showTwilightDataPlot()
        self.showMoonPhase()

    def updateColorSet(self) -> None:
        self.setColors()
        self.ui.twilight.colorChange()
        self.plotAll()

    def plotTwilightData(self, result: tuple) -> None:
        ts, t, e = result
        xMin = int(t[0].tt) + 1
        xMax = int(t[-1].tt) - 1
        xNow = (xMax - xMin) / 2 + xMin

        xTicks = np.arange(xMin, xMax, (xMax - xMin) / 9)
        xLabels = ts.tt_jd(xTicks).utc_strftime("%d%b")
        xLabels[0] = ""
        xTicks = [(x, y) for x, y in zip(xTicks, xLabels)]
        yTicks = [(x, y) for x, y in zip(self.Y_TICKS, self.Y_LABELS)]
        pen = pg.mkPen(color="transparent")
        penLine = pg.mkPen(color=self.mainW.rgb2hex(self.mainW.M_PINK), width=2)
        plotItem = self.ui.twilight.p[0]
        plotItem.getViewBox().setMouseMode(pg.ViewBox.RectMode)
        plotItem.setXRange(0, 360)
        plotItem.setYRange(0, 90)
        plotItem.showAxes(True, showValues=True)
        plotItem.getAxis("bottom").setTicks([xTicks])
        plotItem.getAxis("left").setTicks([yTicks])
        plotItem.getAxis("top").setTicks([xTicks])
        plotItem.getAxis("right").setTicks([yTicks])
        plotItem.setLimits(xMin=xMin, xMax=xMax, yMin=0, yMax=24)
        plotItem.setYRange(0, 24)
        plotItem.setXRange(xMin, xMax)
        brushes: list[QBrush] = []
        for widget, color in self.colors.items():
            colorHex = self.mainW.rgb2hex(color)
            brushes.append(pg.mkBrush(color=colorHex, style=Qt.BrushStyle.SolidPattern))

        tLoc = t.utc_datetime() if self.app.timeMgr.unitTimeUTC else t.astimezone(tzlocal())
        refDay = [x.replace(hour=0, minute=0, second=0, microsecond=0) for x in tLoc]
        dayLoc = tLoc - refDay
        yH = [x.total_seconds() / 3600 for x in dayLoc]
        xD = np.array([int(x) for x in t.tt])

        plotItem.clear()
        for i in range(len(t) - 1):
            x = xD[i]
            if x != xD[i + 1]:
                continue
            ti = yH[i] - 12 if yH[i] > 12 else yH[i] + 12
            ti1 = yH[i + 1] - 12 if yH[i + 1] > 12 else yH[i + 1] + 12
            width = 1
            y = ti
            height = ti1 - ti
            rect = pg.QtWidgets.QGraphicsRectItem(x, y, width, height)
            rect.setPen(pen)
            rect.setBrush(brushes[e[i]])
            plotItem.addItem(rect)
        plotItem.addLine(x=xNow, pen=penLine)
        changeStyleDynamic(self.ui.almanacGroup, "run", False)

    def renderEventList(
        self,
        widget: Any,
        times: list,
        events: list,
        labels: Any,
        timeFormat: str,
    ) -> None:
        widget.clear()
        text = ""
        for eventTime, event in zip(times, events):
            text += f"{self.app.timeMgr.convertTime(eventTime, timeFormat)} "
            text += f"{labels[event]}"
            widget.insertPlainText(text)
            text = "\n"

    def listTwilightData(self, timeEvents: list, events: list) -> None:
        self.renderEventList(
            self.ui.twilightEvents,
            timeEvents,
            events,
            almanac.TWILIGHTS,
            "%H:%M:%S",
        )
        title = "Sun " + self.app.timeMgr.timeZoneString()
        self.ui.sunAlmanacGroup.setTitle(title)

    def calcTwilightData(
        self, ts: Timescale, location: GeographicPosition, tWinL: int, tWinH: int
    ) -> tuple[list, list]:
        timeJD = self.app.dReg["mount"].obsSite.timeJD
        t0 = ts.tt_jd(int(timeJD.tt) - tWinL)
        t1 = ts.tt_jd(int(timeJD.tt) + tWinH + 1)

        f = almanac.dark_twilight_day(self.app.ephemeris, location)
        twilightTime, twilightEvents = almanac.find_discrete(t0, t1, f)
        return twilightTime, twilightEvents

    def runnerCalcTwilightDataPlot(
        self, ts: Timescale, location: GeographicPosition, timeWindow: int
    ) -> tuple[Timescale, list, list]:
        t, e = self.calcTwilightData(ts, location, timeWindow, timeWindow)
        return ts, t, e

    def showTwilightDataPlot(self) -> None:
        location = self.app.dReg["mount"].obsSite.location
        if location is None:
            return
        timeWindow = TWILIGHT_PLOT_DAYS
        t = f"Twilight passes for: 1 year {self.app.timeMgr.timeZoneString()}"
        self.ui.almanacGroup.setTitle(t)
        ts = self.app.dReg["mount"].obsSite.ts
        changeStyleDynamic(self.ui.almanacGroup, "run", True)
        self.workerCalcTwilightDataPlot = Worker(
            self.runnerCalcTwilightDataPlot, ts, location, timeWindow
        )
        self.workerCalcTwilightDataPlot.signals.result.connect(self.plotTwilightData)
        self.app.threadPool.start(self.workerCalcTwilightDataPlot)

    def showTwilightDataList(self) -> None:
        location = self.app.dReg["mount"].obsSite.location
        if location is None:
            return

        ts = self.app.dReg["mount"].obsSite.ts
        result = self.calcTwilightData(ts, location, 0, 1)
        self.twilightTime, self.twilightEvents = result
        self.listTwilightData(
            self.twilightTime[:MAX_TWILIGHT_ROWS],
            self.twilightEvents[:MAX_TWILIGHT_ROWS],
        )

    def calcMoonPhase(self) -> MoonPhaseData:
        ephemeris = self.app.ephemeris
        sun = ephemeris["sun"]
        moon = ephemeris["moon"]
        earth = ephemeris["earth"]
        now = self.app.dReg["mount"].obsSite.ts.now()
        loc = self.app.dReg["mount"].obsSite.location
        ts = self.app.dReg["mount"].obsSite.ts
        timeJD = self.app.dReg["mount"].obsSite.timeJD
        e = earth.at(timeJD)

        # calc phases for obstruction
        _, sunLon, _ = e.observe(sun).apparent().ecliptic_latlon()
        _, moonLon, _ = e.observe(moon).apparent().ecliptic_latlon()

        mpIllumination = almanac.fraction_illuminated(ephemeris, "moon", now)
        mpDegree = (moonLon.degrees - sunLon.degrees) % 360.0
        mpPercent = mpDegree / 360 * 100

        locObserver = (loc + earth).at(timeJD)
        moonApparent = locObserver.observe(moon).apparent()
        sunApparent = locObserver.observe(sun).apparent()
        moonAngle = position_angle_of(moonApparent.altaz(), sunApparent.altaz())

        # calc rise and set times
        t0 = ts.tt_jd(int(timeJD.tt))
        t1 = ts.tt_jd(int(timeJD.tt) + MOON_RISE_DAYS)

        f = almanac.risings_and_settings(ephemeris, ephemeris["moon"], loc)
        moonTimes, moonEvents = almanac.find_discrete(t0, t1, f)
        moonTimes = moonTimes[0:MOON_RISE_MAX]
        moonEvents = moonEvents[0:MOON_RISE_MAX]

        # calc nodes
        t0 = ts.tt_jd(int(timeJD.tt))
        t1 = ts.tt_jd(int(timeJD.tt) + MOON_NODE_DAYS)
        f = almanac.moon_nodes(ephemeris)
        nodeTimes, nodeEvents = almanac.find_discrete(t0, t1, f)
        nodeTimes = nodeTimes[0:MOON_NODE_MAX]
        nodeEvents = nodeEvents[0:MOON_NODE_MAX]

        return MoonPhaseData(
            illumination=mpIllumination,
            degree=mpDegree,
            percent=mpPercent,
            angle=moonAngle,
            moonTimes=moonTimes,
            moonEvents=moonEvents,
            nodeTimes=nodeTimes,
            nodeEvents=nodeEvents,
        )

    def generateMoonMask(self, pixmap: QPixmap, mpDegree: float) -> QPixmap:
        colCover = QColor(*self.mainW.M_BACK)
        colFree = QColor("transparent")
        colFrame = QColor(*self.mainW.M_SEC1)

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
        maskPainter.setBrush(colCover)
        maskPainter.setPen(penFrame)

        # Cover the shaded half-disc: left half up to full moon, right half after.
        pieStart = 90 * 16 if mpDegree <= 180 else -90 * 16
        maskPainter.drawPie(0, 0, width, height, pieStart, 180 * 16)

        # Terminator ellipse: add cover while cos >= 0, clear it otherwise.
        r = float(np.cos(np.radians(mpDegree)) * w2)
        if r >= 0:
            maskPainter.setBrush(colCover)
            maskPainter.setPen(penCov)
        else:
            maskPainter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
            maskPainter.setBrush(colFree)
            maskPainter.setPen(penFree)
        maskPainter.drawEllipse(QPointF(w2, h2), r, h2)

        maskPainter.end()
        return moonMask

    def showMoonNumbers(self, data: MoonPhaseData) -> None:
        self.ui.moonPhaseIllumination.setText(f"{data.illumination * 100:3.1f}")
        self.ui.moonPhasePercent.setText(f"{data.percent:3.0f}")
        self.ui.moonPhaseDegree.setText(f"{data.degree:3.0f}")
        self.ui.moonPhaseText.setText(self.phasesText[data.percent])

    def showMoonRiseSet(self, data: MoonPhaseData) -> None:
        self.renderEventList(
            self.ui.riseSetEventsMoon,
            data.moonTimes,
            data.moonEvents,
            ["set", "rise"],
            "%d.%m. %H:%M",
        )
        title = "Moon " + self.app.timeMgr.timeZoneString()
        self.ui.moonAlmanacGroup.setTitle(title)

    def showMoonNodes(self, data: MoonPhaseData) -> None:
        self.renderEventList(
            self.ui.nodeEvents,
            data.nodeTimes,
            data.nodeEvents,
            ["ascending", "descending"],
            "%d.%m. %H:%M",
        )

    def renderMoonImage(self, mpDegree: float) -> None:
        with as_file(files("mw4").joinpath("assets/pics/moon.png")) as imageFile:
            moon = QPixmap(str(imageFile))
        moonMask = self.generateMoonMask(moon, mpDegree)

        m = QPainter(moon)
        m.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
        m.drawPixmap(0, 0, moonMask)
        m.end()

        width = self.ui.moonPic.width()
        height = self.ui.moonPic.height()

        pm = moon.scaled(width, height)
        pm = setPixmapAlpha(pm, self.mainW.transparency)
        self.ui.moonPic.setPixmap(pm)

    def showMoonPhase(self) -> None:
        data = self.calcMoonPhase()
        self.showMoonNumbers(data)
        self.showMoonRiseSet(data)
        self.showMoonNodes(data)
        self.renderMoonImage(data.degree)
