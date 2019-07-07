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
# Python  v3.7.3
#
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
import pickle
from io import BytesIO
# external packages
import PyQt5.QtCore
import PyQt5.QtWidgets
import PyQt5.uic
# This import registers the 3D projection, but is otherwise unused.
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.pyplot as plt
import numpy as np
from skyfield.api import EarthSatellite
# local import
from mw4.gui import widget
from mw4.gui.widgets import satellite_ui
from mw4.base import transform
from mw4.base.tpool import Worker


class SatelliteWindowSignals(PyQt5.QtCore.QObject):
    """
    The CameraSignals class offers a list of signals to be used and instantiated by
    the Mount class to get signals for triggers for finished tasks to
    enable a gui to update their values transferred to the caller back.

    This has to be done in a separate class as the signals have to be subclassed from
    QObject and the Mount class itself is subclassed from object
    """

    __all__ = ['SatelliteWindowSignals']
    version = '0.1'

    show = PyQt5.QtCore.pyqtSignal(object)
    update = PyQt5.QtCore.pyqtSignal(object, object, object)


class SatelliteWindow(widget.MWidget):
    """
    the satellite window class handles

    """

    __all__ = ['SatelliteWindow',
               ]
    version = '0.9'
    logger = logging.getLogger(__name__)

    # length of forecast time in hours
    FORECAST_TIME = 3
    # earth radius
    EARTH_RADIUS = 6378.0

    def __init__(self, app, threadPool):
        super().__init__()
        self.app = app
        self.threadPool = threadPool

        self.ui = satellite_ui.Ui_SatelliteDialog()
        self.ui.setupUi(self)
        self.initUI()
        self.signals = SatelliteWindowSignals()
        self.satellite = None
        self.plotSatPosSphere1 = None
        self.plotSatPosSphere2 = None
        self.plotSatPosHorizon = None
        self.plotSatPosEarth = None

        self.satSphereMat1 = self.embedMatplot(self.ui.satSphere1)
        self.satSphereMat1.parentWidget().setStyleSheet(self.BACK_BG)
        self.satSphereMat2 = self.embedMatplot(self.ui.satSphere2)
        self.satSphereMat2.parentWidget().setStyleSheet(self.BACK_BG)
        self.satHorizonMat = self.embedMatplot(self.ui.satHorizon)
        self.satHorizonMat.parentWidget().setStyleSheet(self.BACK_BG)
        self.satEarthMat = self.embedMatplot(self.ui.satEarth)
        self.satEarthMat.parentWidget().setStyleSheet(self.BACK_BG)

        self.signals.show.connect(self.receiveSatelliteAndShow)
        self.signals.update.connect(self.updatePositions)

        stream = PyQt5.QtCore.QFile(':/worldmap.dat')
        stream.open(PyQt5.QtCore.QFile.ReadOnly)
        pickleData = stream.readAll()
        stream.close()
        # loading the world image from nasa as PNG as matplotlib only loads png.
        self.world = pickle.load(BytesIO(pickleData))

        self.initConfig()
        self.showWindow()

    def initConfig(self):
        """
        initConfig read the key out of the configuration dict and stores it to the gui
        elements. if some initialisations have to be proceeded with the loaded persistent
        data, they will be launched as well in this method.

        :return: True for test purpose
        """

        if 'satelliteW' not in self.app.config:
            self.app.config['satelliteW'] = {}
        config = self.app.config['satelliteW']
        x = config.get('winPosX', 100)
        y = config.get('winPosY', 100)
        if x > self.screenSizeX:
            x = 0
        if y > self.screenSizeY:
            y = 0
        self.move(x, y)
        height = config.get('height', 600)
        width = config.get('width', 800)
        self.resize(width, height)

    def storeConfig(self):
        """
        storeConfig writes the keys to the configuration dict and stores. if some
        saving has to be proceeded to persistent data, they will be launched as
        well in this method.

        :return: True for test purpose
        """
        if 'satelliteW' not in self.app.config:
            self.app.config['satelliteW'] = {}
        config = self.app.config['satelliteW']
        config['winPosX'] = self.pos().x()
        config['winPosY'] = self.pos().y()
        config['height'] = self.height()
        config['width'] = self.width()

    def closeEvent(self, closeEvent):
        self.storeConfig()

        # gui signals
        super().closeEvent(closeEvent)

    def showWindow(self):
        self.receiveSatelliteAndShow(self.app.mainW.satellite)
        self.show()

    def receiveSatelliteAndShow(self, satellite):
        """
        receiveSatelliteAndShow receives a signal with the content of the selected satellite.
        it locally sets it an draws the the complete view

        :param satellite:
        :return: true for test purpose
        """

        if satellite is None:
            self.drawSatellite()
            return False
        self.satellite = satellite
        if satellite.model.no < 0.02:
            self.FORECAST_TIME = 24
        else:
            self.FORECAST_TIME = 3
        self.drawSatellite()
        return True

    def updatePositions(self, observe, subpoint, altaz):
        """
        updatePositions is triggered once a second and update the satellite position in each
        view.

        :return: success
        """

        if self.satellite is None:
            return False
        if self.plotSatPosEarth is None:
            return False
        if self.plotSatPosHorizon is None:
            return False
        if self.plotSatPosSphere1 is None:
            return False
        if self.plotSatPosSphere2 is None:
            return False

        # sphere1
        x, y, z = observe.position.km
        self.plotSatPosSphere1.set_data_3d((x, y, z))

        # sphere2
        lat = subpoint.latitude.radians
        lon = subpoint.longitude.radians
        elev = subpoint.elevation.m / 1000 + self.EARTH_RADIUS
        x, y, z = transform.sphericalToCartesian(azimuth=lon,
                                                 altitude=lat,
                                                 radius=elev)
        self.plotSatPosSphere2.set_data_3d((x, y, z))

        # earth
        lat = subpoint.latitude.degrees
        lon = subpoint.longitude.degrees
        self.plotSatPosEarth.set_data((lon, lat))

        # horizon
        alt, az, _ = altaz
        alt = alt.degrees
        az = az.degrees
        self.plotSatPosHorizon.set_data((az, alt))

        # update the plot and redraw
        self.satSphereMat1.figure.canvas.draw()
        self.satEarthMat.figure.canvas.draw()
        self.satHorizonMat.figure.canvas.draw()

        return True

    @staticmethod
    def makeCubeLimits(axe, centers=None, hw=None):
        """

        :param axe:
        :param centers:
        :param hw:
        :return:
        """

        limits = axe.get_xlim(), axe.get_ylim(), axe.get_zlim()
        if centers is None:
            centers = [0.5 * sum(pair) for pair in limits]

        if hw is None:
            widths = [pair[1] - pair[0] for pair in limits]
            hw = 0.5 * max(widths)
            axe.set_xlim(centers[0] - hw, centers[0] + hw)
            axe.set_ylim(centers[1] - hw, centers[1] + hw)
            axe.set_zlim(centers[2] - hw, centers[2] + hw)

        else:
            try:
                hwx, hwy, hwz = hw
                axe.set_xlim(centers[0] - hwx, centers[0] + hwx)
                axe.set_ylim(centers[1] - hwy, centers[1] + hwy)
                axe.set_zlim(centers[2] - hwz, centers[2] + hwz)
            except Exception:
                axe.set_xlim(centers[0] - hw, centers[0] + hw)
                axe.set_ylim(centers[1] - hw, centers[1] + hw)
                axe.set_zlim(centers[2] - hw, centers[2] + hw)

        return centers, hw

    def drawSphere1(self, observe=None):
        """
        draw sphere and put face color als image overlay:

        https://stackoverflow.com/questions/53074908/
        map-an-image-onto-a-sphere-and-plot-3d-trajectories

        but performance problems

        see also:

        https://space.stackexchange.com/questions/25958/
        how-can-i-plot-a-satellites-orbit-in-3d-from-a-tle-using-python-and-skyfield

        :param observe:
        :return: success
        """

        figure = self.satSphereMat1.figure
        figure.clf()
        figure.subplots_adjust(left=-0.15, right=1.1, bottom=-0.3, top=1.3)
        axe = figure.add_subplot(111, projection='3d')

        # switching all visual grids and planes off
        axe.set_facecolor((0, 0, 0, 0))
        axe.tick_params(colors=self.M_GREY,
                        labelsize=12)
        axe.set_axis_off()
        axe.w_xaxis.set_pane_color((0.0, 0.0, 0.0, 0.0))
        axe.w_yaxis.set_pane_color((0.0, 0.0, 0.0, 0.0))
        axe.w_zaxis.set_pane_color((0.0, 0.0, 0.0, 0.0))

        # calculating sphere
        theta = np.linspace(0, 2 * np.pi, 51)
        cth, sth, zth = [f(theta) for f in [np.cos, np.sin, np.zeros_like]]
        lon0 = self.EARTH_RADIUS * np.vstack((cth, zth, sth))
        longitudes = []
        lonBase = np.arange(-180, 180, 15)
        for phi in np.radians(lonBase):
            cph, sph = [f(phi) for f in [np.cos, np.sin]]
            lon = np.vstack((lon0[0] * cph - lon0[1] * sph,
                             lon0[1] * cph + lon0[0] * sph,
                             lon0[2]))
            longitudes.append(lon)
        lats = []
        latBase = np.arange(-75, 90, 15)
        for phi in np.radians(latBase):
            cph, sph = [f(phi) for f in [np.cos, np.sin]]
            lat = self.EARTH_RADIUS * np.vstack((cth * cph, sth * cph, zth + sph))
            lats.append(lat)

        # plotting sphere and labels
        for i, longitude in enumerate(longitudes):
            x, y, z = longitude
            axe.plot(x, y, z, '-k', lw=1,
                     color=self.M_GREY)
        for i, lat in enumerate(lats):
            x, y, z = lat
            axe.plot(x, y, z, '-k', lw=1,
                     color=self.M_GREY)

        axe.plot([0, 0],
                 [0, 0],
                 [- self.EARTH_RADIUS * 1.1, self.EARTH_RADIUS * 1.1],
                 lw=3,
                 color=self.M_BLUE)
        axe.text(0, 0, self.EARTH_RADIUS * 1.2, 'N',
                 fontsize=14,
                 color=self.M_BLUE)
        axe.text(0, 0, - self.EARTH_RADIUS * 1.2 - 200, 'S',
                 fontsize=14,
                 color=self.M_BLUE)

        # empty chart if no satellite is chosen
        if observe is None:
            axe.figure.canvas.draw()
            return False

        # drawing satellite
        x, y, z = observe.position.km
        axe.plot(x, y, z, color=self.M_GREEN)

        self.plotSatPosSphere1, = axe.plot([x[0]], [y[0]], [z[0]],
                                           marker='o',
                                           markersize=10,
                                           color=self.M_PINK)
        self.makeCubeLimits(axe)
        axe.figure.canvas.draw()
        return True

    def drawSphere2(self, observe=None, subpoint=None):
        """
        draw sphere and put face color als image overlay:

        https://stackoverflow.com/questions/53074908/
        map-an-image-onto-a-sphere-and-plot-3d-trajectories

        but performance problems

        see also:

        https://space.stackexchange.com/questions/25958/
        how-can-i-plot-a-satellites-orbit-in-3d-from-a-tle-using-python-and-skyfield

        :param observe:
        :param subpoint:
        :return: success
        """

        figure = self.satSphereMat2.figure
        figure.clf()
        figure.subplots_adjust(left=-0.1, right=1.1, bottom=-0.3, top=1.3)
        axe = figure.add_subplot(111, projection='3d')

        # switching all visual grids and planes off
        axe.set_facecolor((0, 0, 0, 0))
        axe.tick_params(colors=self.M_GREY,
                        labelsize=12)
        axe.set_axis_off()
        axe.w_xaxis.set_pane_color((0.0, 0.0, 0.0, 0.0))
        axe.w_yaxis.set_pane_color((0.0, 0.0, 0.0, 0.0))
        axe.w_zaxis.set_pane_color((0.0, 0.0, 0.0, 0.0))

        # calculating sphere
        theta = np.linspace(0, 2 * np.pi, 51)
        cth, sth, zth = [f(theta) for f in [np.cos, np.sin, np.zeros_like]]
        lon0 = self.EARTH_RADIUS * np.vstack((cth, zth, sth))
        longitudes = []
        lonBase = np.arange(-180, 180, 15)
        for phi in np.radians(lonBase):
            cph, sph = [f(phi) for f in [np.cos, np.sin]]
            lon = np.vstack((lon0[0] * cph - lon0[1] * sph,
                             lon0[1] * cph + lon0[0] * sph,
                             lon0[2]))
            longitudes.append(lon)
        lats = []
        latBase = np.arange(-75, 90, 15)
        for phi in np.radians(latBase):
            cph, sph = [f(phi) for f in [np.cos, np.sin]]
            lat = self.EARTH_RADIUS * np.vstack((cth * cph, sth * cph, zth + sph))
            lats.append(lat)

        # plotting sphere and labels
        for i, longitude in enumerate(longitudes):
            x, y, z = longitude
            axe.plot(x, y, z, '-k', lw=1,
                     color=self.M_GREY)
        for i, lat in enumerate(lats):
            x, y, z = lat
            axe.plot(x, y, z, '-k', lw=1,
                     color=self.M_GREY)

        axe.plot([0, 0],
                 [0, 0],
                 [- self.EARTH_RADIUS * 1.1, self.EARTH_RADIUS * 1.1],
                 lw=3,
                 color=self.M_BLUE)
        axe.text(0, 0, self.EARTH_RADIUS * 1.2, 'N',
                 fontsize=14,
                 color=self.M_BLUE)
        axe.text(0, 0, - self.EARTH_RADIUS * 1.2 - 200, 'S',
                 fontsize=14,
                 color=self.M_BLUE)

        # plot world
        for key in self.world.keys():
            shape = self.world[key]
            x, y, z = transform.sphericalToCartesian(azimuth=shape['xRad'],
                                                     altitude=shape['yRad'],
                                                     radius=self.EARTH_RADIUS)
            verts = [list(zip(x, y, z))]
            collect = Poly3DCollection(verts, facecolors=self.M_BLUE, alpha=0.5)
            axe.add_collection3d(collect)

        # empty chart if no satellite is chosen
        if observe is None:
            axe.figure.canvas.draw()
            return False

        # drawing satellite subpoint path
        lat = subpoint.latitude.radians
        lon = subpoint.longitude.radians
        elev = subpoint.elevation.m / 1000 + self.EARTH_RADIUS
        x, y, z = transform.sphericalToCartesian(azimuth=lon,
                                                 altitude=lat,
                                                 radius=elev)
        axe.plot(x, y, z, color=self.M_GREEN)

        # draw satellite position
        self.plotSatPosSphere2, = axe.plot([x[0]], [y[0]], [z[0]],
                                           marker='o',
                                           markersize=10,
                                           color=self.M_PINK)

        # drawing home position location on earth
        lat = self.app.mount.obsSite.location.latitude.radians
        lon = self.app.mount.obsSite.location.longitude.radians
        x, y, z = transform.sphericalToCartesian(altitude=lat,
                                                 azimuth=lon,
                                                 radius=self.EARTH_RADIUS)
        axe.plot([x], [y], [z],
                 marker='.',
                 markersize=10,
                 color=self.M_YELLOW,
                 )

        # finalizing
        self.makeCubeLimits(axe)
        axe.figure.canvas.draw()

        return True

    def drawEarth(self, subpoint=None):
        """
        drawEarth show a full earth view with the path of the subpoint of the satellite
        drawn on it.

        :param subpoint:
        :return: success
        """

        figure = self.satEarthMat.figure
        figure.clf()
        figure.subplots_adjust(left=0.15, right=0.9, bottom=0.15, top=0.95)
        axe = self.satEarthMat.figure.add_subplot(1, 1, 1, facecolor=None)

        axe.set_facecolor((0, 0, 0, 0))
        axe.set_xlim(-180, 180)
        axe.set_ylim(-90, 90)
        axe.spines['bottom'].set_color(self.M_BLUE)
        axe.spines['top'].set_color(self.M_BLUE)
        axe.spines['left'].set_color(self.M_BLUE)
        axe.spines['right'].set_color(self.M_BLUE)
        axe.grid(True, color=self.M_GREY)
        axe.tick_params(axis='x',
                        colors=self.M_BLUE,
                        labelsize=12)
        axe.set_xticks(np.arange(-180, 181, 45))
        axe.tick_params(axis='y',
                        colors=self.M_BLUE,
                        which='both',
                        labelleft=True,
                        labelright=True,
                        labelsize=12)
        axe.set_xlabel('Longitude in degrees',
                       color=self.M_BLUE,
                       fontweight='bold',
                       fontsize=12)
        axe.set_ylabel('Latitude in degrees',
                       color=self.M_BLUE,
                       fontweight='bold',
                       fontsize=12)

        # plot world
        for key in self.world.keys():
            shape = self.world[key]
            axe.plot(shape['xDeg'], shape['yDeg'], color=self.M_GREY)

        # mark the site location in the map
        lat = self.app.mount.obsSite.location.latitude.degrees
        lon = self.app.mount.obsSite.location.longitude.degrees
        axe.plot(lon,
                 lat,
                 marker='.',
                 markersize=10,
                 color=self.M_YELLOW)

        # empty chart if no satellite is chosen
        if subpoint is None:
            axe.figure.canvas.draw()
            return False

        # drawing satellite subpoint path
        lat = subpoint.latitude.degrees
        lon = subpoint.longitude.degrees

        axe.plot(lon,
                 lat,
                 marker='.',
                 markersize=2,
                 linestyle='none',
                 color=self.M_GREEN)

        # show the actual position
        self.plotSatPosEarth, = axe.plot(lon[0],
                                         lat[0],
                                         marker='o',
                                         markersize=10,
                                         linestyle='none',
                                         color=self.M_PINK)
        axe.figure.canvas.draw()
        return True

    def staticHorizon(self, axes=None):
        """

        :param axes: matplotlib axes object
        :return:
        """

        if not self.app.data.horizonP:
            return False

        alt, az = zip(*self.app.data.horizonP)

        axes.fill(az, alt, color=self.M_GREY_LIGHT, zorder=-20)
        axes.plot(az, alt, color=self.M_GREY, zorder=-20, lw=2)

        return True

    def drawHorizonView(self, difference=None):
        """
        drawHorizonView shows the horizon and enable the users to explore a satellite
        passing by

        :param difference:
        :return: success
        """

        figure = self.satHorizonMat.figure
        figure.clf()
        figure.subplots_adjust(left=0.15, right=0.9, bottom=0.15, top=0.95)
        axe = self.satHorizonMat.figure.add_subplot(1, 1, 1, facecolor=None)

        # add horizon limit if selected
        self.staticHorizon(axes=axe)

        axe.set_facecolor((0, 0, 0, 0))
        axe.set_xlim(0, 360)
        axe.set_ylim(0, 90)
        axe.spines['bottom'].set_color(self.M_BLUE)
        axe.spines['top'].set_color(self.M_BLUE)
        axe.spines['left'].set_color(self.M_BLUE)
        axe.spines['right'].set_color(self.M_BLUE)
        axe.grid(True, color=self.M_GREY)
        axe.tick_params(axis='x',
                        colors=self.M_BLUE,
                        labelsize=12)
        axe.set_xticks(np.arange(0, 361, 45))
        axe.tick_params(axis='y',
                        colors=self.M_BLUE,
                        which='both',
                        labelleft=True,
                        labelright=True,
                        labelsize=12)
        axe.set_xlabel('Azimuth in degrees',
                       color=self.M_BLUE,
                       fontweight='bold',
                       fontsize=12)
        axe.set_ylabel('Altitude in degrees',
                       color=self.M_BLUE,
                       fontweight='bold',
                       fontsize=12)

        axe.text(0, 1, 'N',
                 fontsize=14,
                 color=self.M_BLUE)

        axe.text(90, 1, 'E',
                 fontsize=14,
                 color=self.M_BLUE)

        axe.text(180, 1, 'S',
                 fontsize=14,
                 color=self.M_BLUE)

        axe.text(270, 1, 'W',
                 fontsize=14,
                 color=self.M_BLUE)

        axe.text(350, 1, 'N',
                 fontsize=14,
                 color=self.M_BLUE)

        # empty chart if no satellite is chosen
        if difference is None:
            axe.figure.canvas.draw()
            return False

        # orbital calculations
        alt, az, _ = difference.altaz()
        alt = alt.degrees
        az = az.degrees

        # draw path
        axe.plot(az,
                 alt,
                 marker='.',
                 markersize=2,
                 linestyle='none',
                 color=self.M_GREEN)

        # draw actual position
        self.plotSatPosHorizon, = axe.plot(az[0],
                                           alt[0],
                                           marker='X',
                                           markersize=10,
                                           linestyle='none',
                                           color=self.M_PINK)

        axe.figure.canvas.draw()
        return True

    def drawSatellite(self):
        """
        drawSatellite draws 3 different views of the actual satellite situation: a sphere
        a horizon view and an earth view.

        :return: True for test purpose
        """

        timescale = self.app.mount.obsSite.ts
        forecast = np.arange(0, self.FORECAST_TIME, 0.005 * self.FORECAST_TIME / 3) / 24
        now = timescale.now()
        timeVector = timescale.tt_jd(now.tt + forecast)

        if self.satellite is not None:
            observe = self.satellite.at(timeVector)
            subpoint = observe.subpoint()
            difference = (self.satellite - self.app.mount.obsSite.location).at(timeVector)
        else:
            observe = subpoint = difference = None

        self.drawSphere1(observe=observe)
        self.drawSphere2(observe=observe, subpoint=subpoint)
        self.drawEarth(subpoint=subpoint)
        self.drawHorizonView(difference=difference)

        return True
