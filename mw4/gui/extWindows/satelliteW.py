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
import pickle
from io import BytesIO
from typing import Iterator

# external packages
from PySide6.QtCore import QFile, Qt
import numpy as np
from skyfield.api import wgs84, Timescale
import pyqtgraph as pg
from pyqtgraph import PlotWidget

# local import
from gui.utilities import toolsQtWidget
from gui.widgets import satellite_ui


class SatelliteWindow(toolsQtWidget.MWidget):
    """ """

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.obsSite = app.mount.obsSite
        self.threadPool = app.threadPool
        self.ui = satellite_ui.Ui_SatelliteDialog()
        self.ui.setupUi(self)
        self.satellite = None
        self.satOrbits = None
        self.plotSatPosHorizon = None
        self.plotSatPosEarth = None
        self.pointerAltAz = None

        self.colors = [self.M_RED, self.M_YELLOW, self.M_GREEN]
        self.pens = []
        for color in self.colors:
            self.pens.append(pg.mkPen(color=color, width=2))
            self.pens.append(pg.mkPen(color=color, width=2, style=Qt.PenStyle.DotLine))
        self.penLocation = pg.mkPen(color=self.M_RED)
        self.brushLocation = pg.mkBrush(color=self.M_YELLOW)
        stream = QFile(":/data/worldmap.dat")
        stream.open(QFile.OpenModeFlag.ReadOnly)
        pickleData = stream.readAll()
        stream.close()
        self.world = pickle.load(BytesIO(pickleData))
        self.app.showSatellite.connect(self.drawSatellite)
        self.app.updateSatellite.connect(self.updatePositions)
        self.app.redrawHorizon.connect(self.drawHorizon)

    def initConfig(self) -> None:
        """ """
        self.positionWindow(self.app.config.get("satelliteW", {}))

    def storeConfig(self) -> None:
        """ """
        configMain = self.app.config
        configMain["satelliteW"] = {}
        config = configMain["satelliteW"]

        config["winPosX"] = max(self.pos().x(), 0)
        config["winPosY"] = max(self.pos().y(), 0)
        config["height"] = self.height()
        config["width"] = self.width()

    def closeEvent(self, closeEvent) -> None:
        """ """
        self.storeConfig()
        super().closeEvent(closeEvent)

    def showWindow(self) -> None:
        """ """
        self.app.mount.signals.pointDone.connect(self.updatePointerAltAz)
        self.app.colorChange.connect(self.colorChange)
        self.app.sendSatelliteData.emit()
        self.show()

    def colorChange(self) -> None:
        """ """
        self.setStyleSheet(self.mw4Style)
        self.ui.satEarth.colorChange()
        self.ui.satHorizon.colorChange()
        self.app.sendSatelliteData.emit()

    def updatePointerAltAz(self) -> None:
        """ """
        if self.pointerAltAz is None:
            return
        if self.obsSite.Alt is None or self.obsSite.Az is None:
            self.pointerAltAz.setVisible(False)
            return

        self.pointerAltAz.setVisible(True)
        alt = self.obsSite.Alt.degrees
        az = self.obsSite.Az.degrees
        self.pointerAltAz.setData(x=[az], y=[alt])

    def updatePositions(self, now: Timescale, location: wgs84) -> None:
        """ """
        if (
            self.satellite is None
            or self.plotSatPosEarth is None
            or self.plotSatPosHorizon is None
        ):
            return

        observe = self.satellite.at(now)
        subPoint = wgs84.subpoint_of(observe)
        difference = self.satellite - location
        self.ui.satLatitude.setText(f"{subPoint.latitude.degrees:3.2f}")
        self.ui.satLongitude.setText(f"{subPoint.longitude.degrees:3.2f}")
        alt, az, _ = difference.at(now).altaz()
        self.ui.satAltitude.setText(f"{alt.degrees:3.2f}")
        self.ui.satAzimuth.setText(f"{az.degrees:3.2f}")
        lat = subPoint.latitude.degrees
        lon = subPoint.longitude.degrees
        self.plotSatPosEarth.setData(x=[lon], y=[lat])
        self.plotSatPosEarth.setVisible(True)
        alt = alt.degrees
        az = az.degrees
        self.plotSatPosHorizon.setData(x=[az], y=[alt])
        self.plotSatPosHorizon.setVisible(True)

    @staticmethod
    def unlinkWrap(dat) -> Iterator[slice]:
        """ """
        limits = (-180, 180)
        thresh = 0.97
        jump = np.nonzero(np.abs(np.diff(dat)) > ((limits[1] - limits[0]) * thresh))[0]
        lastIndex = 0
        for ind in jump:
            yield slice(lastIndex, ind + 1)
            lastIndex = ind + 1
        yield slice(lastIndex, len(dat))

    @staticmethod
    def prepareEarth(plotItem: PlotWidget) -> None:
        """ """
        plotItem.showAxes(True, showValues=True)
        plotItem.getViewBox().setMouseMode(pg.ViewBox().PanMode)
        xTicks = [(x, f"{x:0.0f}") for x in np.arange(-135, 136, 45)]
        plotItem.getAxis("bottom").setTicks([xTicks])
        plotItem.getAxis("top").setTicks([xTicks])
        plotItem.setLabel("bottom", "Longitude [deg]")
        plotItem.setLabel("left", "Latitude [deg]")
        plotItem.setLimits(
            xMin=-180, xMax=180, yMin=-90, yMax=90, minXRange=360 / 4, minYRange=180 / 4
        )
        plotItem.setXRange(-180, 180)
        plotItem.setYRange(-90, 90)
        plotItem.disableAutoRange()
        plotItem.setMouseEnabled(x=True, y=True)
        plotItem.clear()

    def drawShoreLine(self, plotItem: PlotWidget) -> None:
        """ """
        for key in self.world.keys():
            shape = self.world[key]
            x = np.array(shape["xDeg"])
            y = np.array(shape["yDeg"])
            path = pg.arrayToQPath(x, y)
            poly = pg.QtWidgets.QGraphicsPathItem(path)
            poly.setPen(self.ui.satEarth.penHorizon)
            poly.setBrush(self.ui.satEarth.brushHorizon)
            plotItem.addItem(poly)

    def drawPosition(self, plotItem: PlotWidget) -> None:
        """ """
        lat = self.obsSite.location.latitude.degrees
        lon = self.obsSite.location.longitude.degrees
        pd = pg.PlotDataItem(
            x=[lon],
            y=[lat],
            symbol="o",
            symbolSize=9,
            symbolPen=self.penLocation,
            symbolBrush=self.brushLocation,
        )
        plotItem.addItem(pd)

    def prepareSatellite(self, x, y) -> pg.PlotDataItem:
        """ """
        pd = pg.PlotDataItem(
            x=x,
            y=y,
            symbol=self.makeSat(),
            symbolSize=35,
            symbolPen=pg.mkPen(color=self.M_TER),
            symbolBrush=pg.mkBrush(color=self.M_PINK + "80"),
        )
        return pd

    def prepareEarthSatellite(
        self,
        plotItem: PlotWidget,
    ) -> pg.PlotDataItem:
        """ """
        subPoint = wgs84.subpoint_of(self.satellite.at(self.obsSite.ts.now()))
        lat = subPoint.latitude.degrees
        lon = subPoint.longitude.degrees
        pd = self.prepareSatellite([lat], [lon])
        pd.setVisible(False)
        pd.setZValue(10)
        plotItem.addItem(pd)
        return pd

    def drawEarthTrajectory(self, plotItem: PlotWidget) -> None:
        """ """
        for i, satOrbit in enumerate(self.satOrbits):
            rise = satOrbit["rise"].tt
            settle = satOrbit["settle"].tt
            step = 0.005 * (settle - rise)
            if "flip" not in satOrbit:
                satOrbit["flip"] = satOrbit["settle"]

            flip = satOrbit["flip"].tt
            vector = np.arange(rise, flip, step)
            vecT = self.obsSite.ts.tt_jd(vector)
            subPoints = wgs84.subpoint_of(self.satellite.at(vecT))
            lat = subPoints.latitude.degrees
            lon = subPoints.longitude.degrees
            for slc in self.unlinkWrap(lon):
                pd = pg.PlotDataItem(x=lon[slc], y=lat[slc], pen=self.pens[2 * i])
                plotItem.addItem(pd)

            vector = np.arange(flip, settle, step)
            vecT = self.obsSite.ts.tt_jd(vector)
            subPoints = wgs84.subpoint_of(self.satellite.at(vecT))
            lat = subPoints.latitude.degrees
            lon = subPoints.longitude.degrees
            for slc in self.unlinkWrap(lon):
                pd = pg.PlotDataItem(x=lon[slc], y=lat[slc], pen=self.pens[2 * i + 1])
                plotItem.addItem(pd)

        rise = self.satOrbits[0]["rise"].tt
        settle = self.satOrbits[-1]["settle"].tt
        step = 0.001 * (settle - rise)
        vector = np.arange(rise - 0.15, settle, step)
        vecT = self.obsSite.ts.tt_jd(vector)
        subPoints = wgs84.subpoint_of(self.satellite.at(vecT))
        lat = subPoints.latitude.degrees
        lon = subPoints.longitude.degrees
        for slc in self.unlinkWrap(lon):
            pd = pg.PlotDataItem(
                x=lon[slc], y=lat[slc], pen=pg.mkPen(width=1, color=self.M_TER1 + "80")
            )
            pd.setZValue(-10)
            plotItem.addItem(pd)

    def drawEarth(self) -> None:
        """ """
        plotItem = self.ui.satEarth.p[0]
        self.prepareEarth(plotItem)
        self.drawShoreLine(plotItem)
        self.drawPosition(plotItem)
        self.plotSatPosEarth = self.prepareEarthSatellite(plotItem)
        self.drawEarthTrajectory(plotItem)

    @staticmethod
    def prepareHorizon(plotItem: PlotWidget) -> None:
        """ """
        plotItem.getViewBox().setMouseMode(pg.ViewBox().PanMode)
        plotItem.showAxes(True, showValues=True)
        xTicks = [(x, f"{x:0.0f}") for x in np.arange(30, 360, 30)]
        yTicks = [(x, f"{x:0.0f}") for x in np.arange(10, 90, 10)]
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

    def prepareHorizonSatellite(self, plotItem: PlotWidget) -> pg.PlotDataItem:
        """ """
        alt, az, _ = (self.satellite - self.obsSite.location).at(self.obsSite.ts.now()).altaz()
        pd = self.prepareSatellite([az.degrees], [alt.degrees])
        pd.setVisible(False)
        pd.setZValue(10)
        plotItem.addItem(pd)
        return pd

    def preparePointer(self, plotItem: PlotWidget) -> pg.PlotDataItem:
        """ """
        pd = pg.PlotDataItem(
            x=[180],
            y=[45],
            symbol=self.makePointer(),
            symbolSize=40,
            symbolPen=pg.mkPen(color=self.M_PINK),
            symbolBrush=pg.mkBrush(color=self.M_PINK + "20"),
        )
        pd.setVisible(False)
        pd.setZValue(10)
        plotItem.addItem(pd)
        return pd

    def drawHorizonTrajectory(self, plotItem: PlotWidget, altitude, azimuth):
        """ """
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
        """ """
        self.ui.satHorizon.drawHorizon(self.app.data.horizonP)

    def drawHorizonView(self, altitude: list[float], azimuth: list[float]) -> None:
        """ """
        plotItem = self.ui.satHorizon.p[0]
        self.prepareHorizon(plotItem)
        self.drawHorizonTrajectory(plotItem, altitude, azimuth)
        self.plotSatPosHorizon = self.prepareHorizonSatellite(plotItem)
        self.pointerAltAz = self.preparePointer(plotItem)
        self.drawHorizon()

    def drawSatellite(
        self, satellite, satOrbits, altitude: float, azimuth: float, name: str
    ) -> None:
        """ """
        self.setWindowTitle(f"Satellite {name}")
        self.satellite = satellite
        self.satOrbits = satOrbits
        if satOrbits is None or self.obsSite is None:
            return
        self.drawEarth()
        self.drawHorizonView(altitude, azimuth)
