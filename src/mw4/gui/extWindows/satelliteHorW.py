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
# Licence APL2.0
#
###########################################################
import numpy as np
import pyqtgraph as pg
from collections.abc import Iterator
from mw4.gui.utilities.generateSprites import makePointer, makeSat
from mw4.gui.utilities.qtMain import MWidget
from mw4.gui.widgets import satelliteHor_ui
from PySide6.QtCore import Qt
from skyfield.api import EarthSatellite, Timescale
from skyfield.toposlib import GeographicPosition
from typing import Any


class SatelliteHorizonWindow(MWidget):
    def __init__(self, app: Any) -> None:
        super().__init__()
        self.app = app
        self.obsSite = app.mount.obsSite
        self.threadPool = app.threadPool
        self.ui = satelliteHor_ui.Ui_SatelliteHorizonDialog()
        self.ui.setupUi(self)
        self.satellite: EarthSatellite = EarthSatellite("", "", "")
        self.satOrbits: dict = {}
        self.plotSatPosHorizon: pg.PlotDataItem = pg.PlotDataItem()
        self.pointerAltAz: pg.PlotDataItem = pg.PlotDataItem()
        self.colors = [self.M_RED, self.M_YELLOW, self.M_GREEN]
        self.pens = []
        for color in self.colors:
            self.pens.append(pg.mkPen(color=color, width=2))
            self.pens.append(pg.mkPen(color=color, width=2, style=Qt.PenStyle.DotLine))
        self.penLocation = pg.mkPen(color=self.M_RED)
        self.brushLocation = pg.mkBrush(color=self.M_YELLOW)
        self.app.showSatellite.connect(self.drawSatellite)
        self.app.updateSatellite.connect(self.updatePositions)
        self.app.redrawHorizon.connect(self.drawHorizon)
        self.app.mount.signals.mountIsUp.connect(self.setPointerVisibility)

    def initConfig(self) -> None:
        self.positionWindow(self.app.config.get("satelliteHorW", {}))

    def storeConfig(self) -> None:
        configMain = self.app.config
        configMain["satelliteHorW"] = {}
        config = configMain["satelliteHorW"]

        config["winPosX"] = max(self.pos().x(), 0)
        config["winPosY"] = max(self.pos().y(), 0)
        config["height"] = self.height()
        config["width"] = self.width()

    def closeEvent(self, closeEvent) -> None:
        self.storeConfig()
        self.app.showSatellite.disconnect(self.drawSatellite)
        self.app.updateSatellite.disconnect(self.updatePositions)
        self.app.redrawHorizon.disconnect(self.drawHorizon)
        self.app.mount.signals.mountIsUp.disconnect(self.setPointerVisibility)
        self.app.mount.signals.pointDone.disconnect(self.updatePointerAltAz)
        self.app.colorChange.disconnect(self.colorChange)
        super().closeEvent(closeEvent)

    def showWindow(self) -> None:
        self.app.mount.signals.pointDone.connect(self.updatePointerAltAz)
        self.app.colorChange.connect(self.colorChange)
        self.app.sendSatelliteData.emit([], [])
        self.show()

    def colorChange(self) -> None:
        self.setStyleSheet(self.mw4Style)
        self.ui.satHorizon.colorChange()
        self.app.sendSatelliteData.emit([], [])

    def setPointerVisibility(self, status) -> None:
        self.pointerAltAz.setVisible(status)

    def updatePointerAltAz(self) -> None:
        alt = self.obsSite.Alt.degrees
        az = self.obsSite.Az.degrees
        self.pointerAltAz.setData(x=[az], y=[alt])

    def updatePositions(self, now: Timescale, location: GeographicPosition) -> None:
        difference = self.satellite - location
        alt, az, _ = difference.at(now).altaz()
        self.ui.satAltitude.setText(f"{alt.degrees:3.2f}")
        self.ui.satAzimuth.setText(f"{az.degrees:3.2f}")
        alt = alt.degrees
        az = az.degrees
        self.plotSatPosHorizon.setData(x=[az], y=[alt])
        self.plotSatPosHorizon.setVisible(True)

    @staticmethod
    def unlinkWrap(dat) -> Iterator[slice]:
        limits = (-180, 180)
        thresh = 0.97
        jump = np.nonzero(np.abs(np.diff(dat)) > ((limits[1] - limits[0]) * thresh))[0]
        lastIndex = 0
        for ind in jump:
            yield slice(lastIndex, ind + 1)
            lastIndex = ind + 1
        yield slice(lastIndex, len(dat))

    def prepareSatellite(self, x, y) -> pg.PlotDataItem:
        pd = pg.PlotDataItem(
            x=x,
            y=y,
            symbol=makeSat(),
            symbolSize=40,
            symbolPen=pg.mkPen(color=self.M_TER, width=1),
            symbolBrush=pg.mkBrush(color=self.M_TER2 + "80"),
        )
        return pd

    @staticmethod
    def prepareHorizon(plotItem: pg.PlotItem) -> None:
        plotItem.getViewBox().setMouseMode(pg.ViewBox.PanMode)
        plotItem.showAxes(True, showValues=True)
        xTicks = [(float(x), f"{x:0.0f}") for x in np.arange(30, 360, 30)]
        yTicks = [(float(x), f"{x:0.0f}") for x in np.arange(10, 90, 10)]
        plotItem.getAxis("bottom").setTicks([xTicks])
        plotItem.getAxis("top").setTicks([xTicks])
        plotItem.getAxis("left").setTicks([yTicks])
        plotItem.setLabel("bottom", "Azimuth [deg]")
        plotItem.setLabel("left", "Altitude [deg]")
        plotItem.setLimits(
            xMin=0, xMax=360, yMin=-0, yMax=90, minXRange=360 / 4, minYRange=90 / 4
        )
        plotItem.setXRange(0, 360)
        plotItem.setYRange(0, 90)
        plotItem.disableAutoRange()
        plotItem.setMouseEnabled(x=True, y=True)
        plotItem.clear()

    def prepareHorizonSatellite(self, plotItem: pg.PlotItem) -> pg.PlotDataItem:
        alt, az, _ = (self.satellite - self.obsSite.location).at(self.obsSite.ts.now()).altaz()
        pd = self.prepareSatellite([az.degrees], [alt.degrees])
        pd.setVisible(False)
        pd.setZValue(10)
        plotItem.addItem(pd)
        return pd

    def preparePointer(self, plotItem: pg.PlotItem) -> pg.PlotDataItem:
        pd = pg.PlotDataItem(
            x=[180],
            y=[45],
            symbol=makePointer(),
            symbolSize=40,
            symbolPen=pg.mkPen(color=self.M_PINK),
            symbolBrush=pg.mkBrush(color=self.M_PINK + "20"),
        )
        pd.setVisible(False)
        pd.setZValue(10)
        plotItem.addItem(pd)
        return pd

    def drawHorizonTrajectory(self, plotItem: pg.PlotItem, altitude, azimuth):
        ts = self.obsSite.ts
        for i, satOrbit in enumerate(self.satOrbits):
            rise = satOrbit["rise"].tt
            settle = satOrbit["settle"].tt
            step = 0.005 * (settle - rise)

            if "flip" not in satOrbit:
                satOrbit["flip"] = satOrbit["settle"]

            flip = satOrbit["flip"].tt
            vector = np.arange(rise, flip, step)
            vecT = ts.tt_jd(vector)
            alt, az, _ = (self.satellite - self.obsSite.location).at(vecT).altaz()

            for slc in self.unlinkWrap(az.degrees):
                pd = pg.PlotDataItem(
                    x=az.degrees[slc], y=alt.degrees[slc], pen=self.pens[2 * i]
                )
                plotItem.addItem(pd)

            vector = np.arange(flip, settle, step)
            vecT = ts.tt_jd(vector)
            alt, az, _ = (self.satellite - self.obsSite.location).at(vecT).altaz()
            for slc in self.unlinkWrap(az.degrees):
                pd = pg.PlotDataItem(
                    x=az.degrees[slc], y=alt.degrees[slc], pen=self.pens[2 * i + 1]
                )
                plotItem.addItem(pd)

        for slc in self.unlinkWrap(azimuth):
            pd = pg.PlotDataItem(
                x=azimuth[slc], y=altitude[slc], pen=pg.mkPen(width=5, color=self.M_TER)
            )
            pd.setZValue(-5)
            plotItem.addItem(pd)

    def drawHorizon(self) -> None:
        self.ui.satHorizon.drawHorizon(self.app.data.horizonP)

    def drawHorizonView(self, altitude: list[float], azimuth: list[float]) -> None:
        plotItem = self.ui.satHorizon.p[0]
        self.prepareHorizon(plotItem)
        self.drawHorizonTrajectory(plotItem, altitude, azimuth)
        self.plotSatPosHorizon = self.prepareHorizonSatellite(plotItem)
        self.pointerAltAz = self.preparePointer(plotItem)
        self.drawHorizon()

    def drawSatellite(
        self,
        satellite: EarthSatellite,
        satOrbits: dict,
        altitude: list[float],
        azimuth: list[float],
        name: str,
    ) -> None:
        self.setWindowTitle(f"Satellite {name}")
        self.satellite = satellite
        self.satOrbits = satOrbits
        self.drawHorizonView(altitude, azimuth)
