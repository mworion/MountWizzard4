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
# GUI with PyQT5 for python
#
# written in python3, (c) 2019-2022 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import pickle
from io import BytesIO

# external packages
from PyQt5.QtCore import QObject, pyqtSignal, QFile, Qt
from PyQt5.QtWidgets import QApplication
import numpy as np
import matplotlib.path as mpath
from skyfield.api import wgs84
import pyqtgraph as pg

# local import
from gui.utilities import toolsQtWidget
from gui.widgets import satellite_ui


class SatelliteWindowSignals(QObject):
    """
    """
    __all__ = ['SatelliteWindowSignals']
    show = pyqtSignal(object, object, object, object, object)
    update = pyqtSignal(object, object)


class SatelliteWindow(toolsQtWidget.MWidget):
    """
    """
    __all__ = ['SatelliteWindow']

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.threadPool = app.threadPool
        self.ui = satellite_ui.Ui_SatelliteDialog()
        self.ui.setupUi(self)
        self.closing = False
        self.signals = SatelliteWindowSignals()
        self.satellite = None
        self.plotSatPosHorizon = None
        self.plotSatPosEarth = None
        self.pointerAltAz = None

        self.colors = [self.M_RED, self.M_YELLOW, self.M_GREEN]
        self.pens = []
        for color in self.colors:
            self.pens.append(pg.mkPen(color=color, width=4)
            self.pens.append(pg.mkPen(color=color, width=4, style=Qt.DotLine)
        self.penWhite = pg.mkPen(width=7, color=self.M_WHITE1)
        self.brushSat = pg.mkBrush(color=self.M_PINK1 + '80')
        self.brushPointer = pg.mkBrush(color=self.M_PINK + '80')
        self.penSat = pg.mkPen(color=self.M_PINK1)
        self.penPointer = pg.mkPen(color=self.M_PINK)
        self.penLocation = pg.mkPen(color=self.M_YELLOW)
        self.brushLocation = pg.mkBrush(color=self.M_YELLOW)
                             
        stream = QFile(':/data/worldmap.dat')
        stream.open(QFile.ReadOnly)
        pickleData = stream.readAll()
        stream.close()
        self.world = pickle.load(BytesIO(pickleData))
        self.signals.show.connect(self.drawSatellite)
        self.signals.update.connect(self.updatePositions)

    def initConfig(self):
        """
        :return: True for test purpose
        """
        if 'satelliteW' not in self.app.config:
            self.app.config['satelliteW'] = {}
        config = self.app.config['satelliteW']
        height = config.get('height', 600)
        width = config.get('width', 800)
        self.resize(width, height)
        x = config.get('winPosX', 0)
        y = config.get('winPosY', 0)
        if x > self.screenSizeX - width:
            x = 0
        if y > self.screenSizeY - height:
            y = 0
        if x != 0 and y != 0:
            self.move(x, y)

        return True

    def storeConfig(self):
        """
        :return: True for test purpose
        """
        if 'satelliteW' not in self.app.config:
            self.app.config['satelliteW'] = {}

        config = self.app.config['satelliteW']
        config['winPosX'] = max(self.pos().x(), 0)
        config['winPosY'] = max(self.pos().y(), 0)
        config['height'] = self.height()
        config['width'] = self.width()
        return True

    def closeEvent(self, closeEvent):
        """
        :param closeEvent:
        :return:
        """
        self.closing = True
        self.storeConfig()
        self.app.mount.signals.pointDone.disconnect(self.updatePointerAltAz)
        self.app.colorChange.disconnect(self.colorChange)
        super().closeEvent(closeEvent)

    def showWindow(self):
        """
        :return: True for test purpose
        """
        self.app.mount.signals.pointDone.connect(self.updatePointerAltAz)
        self.app.colorChange.connect(self.colorChange)
        self.app.sendSatelliteData.emit()
        self.show()
        return True

    def colorChange(self):
        """
        :return:
        """
        self.setStyleSheet(self.mw4Style)
        self.ui.satEarth.colorChange()
        self.ui.satHorizon.colorChange()
        self.colors = [self.M_RED, self.M_YELLOW, self.M_GREEN]
        self.app.sendSatelliteData.emit()
        return True

    def updatePointerAltAz(self, obsSite):
        """
        :return: success
        """
        if self.pointerAltAz is None:
            return False

        if obsSite.Alt is None or obsSite.Az is None:
            self.pointerAltAz.set_visible(False)
            return False
        else:
            self.pointerAltAz.setVisible(True)

        alt = obsSite.Alt.degrees
        az = obsSite.Az.degrees
        self.pointerAltAz.setData(x=[az], y=[alt])
        return True

    def updatePositions(self, now=None, location=None):
        """
        :return: success
        """
        if now is None:
            return False
        if location is None:
            return False
        if self.satellite is None:
            return False
        if self.plotSatPosEarth is None:
            return False
        if self.plotSatPosHorizon is None:
            return False

        observe = self.satellite.at(now)
        subpoint = wgs84.subpoint_of(observe)
        difference = self.satellite - location
        self.ui.satLatitude.setText(f'{subpoint.latitude.degrees:3.2f}')
        self.ui.satLongitude.setText(f'{subpoint.longitude.degrees:3.2f}')
        alt, az, _ = difference.at(now).altaz()
        self.ui.satAltitude.setText(f'{alt.degrees:3.2f}')
        self.ui.satAzimuth.setText(f'{az.degrees:3.2f}')
        lat = subpoint.latitude.degrees
        lon = subpoint.longitude.degrees
        self.plotSatPosEarth.setData(x=[lon], y=[lat])
        self.plotSatPosEarth.setVisible(True)
        alt = alt.degrees
        az = az.degrees
        self.plotSatPosHorizon.setData(x=[az], y=[alt])
        self.plotSatPosHorizon.setVisible(True)
        return True

    @staticmethod
    def unlinkWrap(dat, limits=(-180, 180), thresh=0.95):
        """
        Iterate over contiguous regions of `dat` (i.e. where it does not
        jump from near one limit to the other).
        This function returns an iterator object that yields slice
        objects, which index the contiguous portions of `dat`.
        This function implicitly assumes that all points in `dat` fall
        within `limits`.
        """
        jump = np.nonzero(np.abs(np.diff(dat)) > ((limits[1] - limits[0]) * thresh))[0]
        lastIndex = 0
        for ind in jump:
            yield slice(lastIndex, ind + 1)
            lastIndex = ind + 1
        yield slice(lastIndex, len(dat))

    @staticmethod
    def prepareEarth(plotItem):
        """
        :param plotItem:
        :return:
        """
        plotItem.getViewBox().setMouseMode(pg.ViewBox().PanMode)
        xTicks = [(x, f'{x:0.0f}') for x in np.arange(-135, 136, 45)]
        plotItem.getAxis('bottom').setTicks([xTicks])
        plotItem.getAxis('top').setTicks([xTicks])
        plotItem.setLabel('bottom', 'Longitude [deg]')
        plotItem.setLabel('left', 'Latitude [deg]')
        plotItem.setLimits(xMin=-180, xMax=180, yMin=-90, yMax=90,
                           minXRange=360 / 4, minYRange=180 / 4)
        plotItem.disableAutoRange()
        plotItem.setXRange(-180, 180)
        plotItem.setYRange(-90, 90)
        plotItem.setMouseEnabled(x=True, y=True)
        plotItem.clear()
        return True

    def drawShoreLine(self, plotItem):
        """
        :param plotItem:
        :return:
        """
        for key in self.world.keys():
            shape = self.world[key]
            pd = pg.PlotDataItem(
                x=shape['xDeg'], y=shape['yDeg'], pen=self.ui.satEarth.pen)
            plotItem.addItem(pd)

    def drawPosition(self, plotItem, obsSite):
        """
        :param plotItem:
        :param obsSite:
        :return:
        """
        lat = obsSite.location.latitude.degrees
        lon = obsSite.location.longitude.degrees
        pd = pg.PlotDataItem(
            x=[lon], y=[lat], symbol='o', symbolSize=5,
            symbolPen=self.penLocation, symbolBrush=self.brushLocation)
        plotItem.addItem(pd)
        return True

    def prepareEarthSatellite(self, plotItem, obsSite):
        """
        :param plotItem:
        :param obsSite:
        :return:
        """
        subpoint = wgs84.subpoint_of(self.satellite.at(obsSite.ts.now()))
        lat = subpoint.latitude.degrees
        lon = subpoint.longitude.degrees

        pd = pg.PlotDataItem(
            x=[lat], y=[lon], symbol='d', symbolSize=20,
            symbolPen=self.penSat, symbolBrush=self.brushSat)
        pd.setVisible(False)
        pd.setZValue(10)
        plotItem.addItem(pd)
        return pd

    def drawEarthTrajectory(self, plotItem, obsSite, satOrbits):
        """
        :param plotItem:
        :param obsSite:
        :param satOrbits:
        :return:
        """
        for i, satOrbit in enumerate(satOrbits):
            rise = satOrbit['rise'].tt
            settle = satOrbit['settle'].tt
            step = 0.005 * (settle - rise)
            if 'flip' not in satOrbit:
                satOrbit['flip'] = satOrbit['settle']

            flip = satOrbit['flip'].tt
            vector = np.arange(rise, flip, step)
            vecT = obsSite.ts.tt_jd(vector)
            subpoints = wgs84.subpoint_of(self.satellite.at(vecT))
            lat = subpoints.latitude.degrees
            lon = subpoints.longitude.degrees
            for slc in self.unlinkWrap(lon):
                pd = pg.PlotDataItem(x=lon[slc], y=lat[slc], pen=self.pens[2 * i])
                plotItem.addItem(pd)

            vector = np.arange(flip, settle, step)
            vecT = obsSite.ts.tt_jd(vector)
            subpoints = wgs84.subpoint_of(self.satellite.at(vecT))
            lat = subpoints.latitude.degrees
            lon = subpoints.longitude.degrees
            for slc in self.unlinkWrap(lon):
                pd = pg.PlotDataItem(x=lon[slc], y=lat[slc], pen=pen=self.pens[2 * i + 1])
                plotItem.addItem(pd)

        rise = satOrbits[0]['rise'].tt
        settle = satOrbits[-1]['settle'].tt
        step = 0.001 * (settle - rise)
        vector = np.arange(rise - 0.15, settle, step)
        vecT = obsSite.ts.tt_jd(vector)
        subpoints = wgs84.subpoint_of(self.satellite.at(vecT))
        lat = subpoints.latitude.degrees
        lon = subpoints.longitude.degrees
        for slc in self.unlinkWrap(lon):
            pd = pg.PlotDataItem(x=lon[slc], y=lat[slc], pen=self.penWhite)
            pd.setZValue(-10)
            plotItem.addItem(pd)
        return True

    def drawEarth(self, obsSite=None, satOrbits=None):
        """
        :param obsSite:
        :param satOrbits:
        :return: success
        """
        plotItem = self.ui.satEarth.p[0]
        self.prepareEarth(plotItem)
        self.drawShoreLine(plotItem)
        if obsSite is None:
            return False

        self.drawPosition(plotItem, obsSite)
        if not satOrbits:
            return False

        self.plotSatPosEarth = self.prepareEarthSatellite(plotItem, obsSite)
        self.drawEarthTrajectory(plotItem, obsSite, satOrbits)
        return True

    @staticmethod
    def prepareHorizon(plotItem):
        """
        :param plotItem:
        :return:
        """
        plotItem.getViewBox().setMouseMode(pg.ViewBox().PanMode)
        xTicks = [(x, f'{x:0.0f}') for x in np.arange(30, 360, 30)]
        plotItem.getAxis('bottom').setTicks([xTicks])
        plotItem.getAxis('top').setTicks([xTicks])
        plotItem.setLabel('bottom', 'Azimuth [deg]')
        plotItem.setLabel('left', 'Altitude [deg]')
        plotItem.setLimits(xMin=0, xMax=360, yMin=-0, yMax=90,
                           minXRange=360 / 4, minYRange=90 / 4)
        plotItem.disableAutoRange()
        plotItem.setXRange(0, 360)
        plotItem.setYRange(0, 90)
        plotItem.setMouseEnabled(x=True, y=True)
        plotItem.clear()
        return True

    def staticHorizon(self, axes=None):
        """
        :param axes: matplotlib axes object
        :return:
        """
        if not self.app.data.horizonP:
            return False

        alt, az = zip(*self.app.data.horizonP)
        alt = np.array(alt)
        az = np.array(az)
        altF = np.concatenate([[0], [alt[0]], alt, [alt[-1]], [0]])
        azF = np.concatenate([[0], [0], az, [360], [360]])

        axes.fill(azF, altF, color=self.M_GREY1, alpha=0.5, zorder=-10)
        axes.plot(az, alt, color=self.M_BLUE, marker='', alpha=0.7, lw=2)
        return True

    def prepareHorizonSatellite(self, plotItem, obsSite):
        """
        :param plotItem:
        :param obsSite:
        :return:
        """
        alt, az, _ = (self.satellite - obsSite.location).at(obsSite.ts.now()).altaz()
        pd = pg.PlotDataItem(
            x=[az.degrees], y=[alt.degrees], symbol='d', symbolSize=20,
            symbolPen=self.penSat, symbolBrush=self.brushSat)
        pd.setVisible(False)
        pd.setZValue(10)
        plotItem.addItem(pd)
        return pd

    def preparePointer(self, plotItem):
        """
        :param plotItem:
        :return:
        """
        pd = pg.PlotDataItem(
            x=[180], y=[45], symbol='o', symbolSize=20,
            symbolPen=self.penPointer, symbolBrush=self.brushPointer)
        pd.setVisible(False)
        pd.setZValue(10)
        plotItem.addItem(pd)
        return pd

    def drawHorizonTrajectory(self, plotItem, obsSite, satOrbits,
                              azimuth, altitude):
        """
        :param plotItem:
        :param obsSite:
        :param satOrbits:
        :param azimuth:
        :param altitude:
        :return:
        """
        ts = obsSite.ts
        for i, satOrbit in enumerate(satOrbits):
            rise = satOrbit['rise'].tt
            settle = satOrbit['settle'].tt
            step = 0.005 * (settle - rise)

            if 'flip' not in satOrbit:
                satOrbit['flip'] = satOrbit['settle']

            flip = satOrbit['flip'].tt
            vector = np.arange(rise, flip, step)
            vecT = ts.tt_jd(vector)
            alt, az, _ = (self.satellite - obsSite.location).at(vecT).altaz()

            for slc in self.unlinkWrap(az.degrees):
                pd = pg.PlotDataItem(
                    x=az.degrees[slc], y=alt.degrees[slc], pen=self.pens[2 * i])
                plotItem.addItem(pd)

            vector = np.arange(flip, settle, step)
            vecT = ts.tt_jd(vector)
            alt, az, _ = (self.satellite - obsSite.location).at(vecT).altaz()
            for slc in self.unlinkWrap(az.degrees):
                pd = pg.PlotDataItem(
                    x=az.degrees[slc], y=alt.degrees[slc], pen=self.pens[2 * i + 1])
                plotItem.addItem(pd)

        for slc in self.unlinkWrap(azimuth):
            pd = pg.PlotDataItem(
                x=azimuth[slc], y=altitude[slc], pen=self.penWhite)
            pd.setZValue(-5)
            plotItem.addItem(pd)

    def drawHorizonView(self, obsSite=None, satOrbits=None,
                        altitude=[], azimuth=[], isSunlit=[]):
        """
        drawHorizonView shows the horizon and enable the users to explore a
        satellite passing by

        :param obsSite:
        :param satOrbits:
        :param altitude:
        :param azimuth:
        :param isSunlit:
        :return: success
        """
        plotItem = self.ui.satHorizon.p[0]
        self.prepareHorizon(plotItem)
        # self.staticHorizon(axes=axe)

        if not satOrbits or obsSite is None:
            return False

        self.drawHorizonTrajectory(
            plotItem, obsSite, satOrbits, altitude, azimuth)
        self.plotSatPosHorizon = self.prepareHorizonSatellite(
            plotItem, obsSite)
        self.pointerAltAz = self.preparePointer(plotItem)
        return True

    def drawSatellite(self, satellite=None, satOrbits=None, altitude=[],
                      azimuth=[], name=''):
        """
        drawSatellite draws 2 different views of the actual satellite
        situation: a horizon view and an earth view.

        :param satellite:
        :param satOrbits:
        :param altitude:
        :param azimuth:
        :param name:
        :return: True for test purpose
        """
        if self.closing:
            return False

        self.setWindowTitle(f'Satellite {name}')
        self.satellite = satellite
        self.drawEarth(self.app.mount.obsSite, satOrbits=satOrbits)
        self.drawHorizonView(self.app.mount.obsSite, satOrbits=satOrbits,
                             altitude=altitude, azimuth=azimuth)
        return True
