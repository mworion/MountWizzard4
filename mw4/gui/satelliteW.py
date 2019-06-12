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
# Python  v3.6.7
#
# Michael Würtenberger
# (c) 2018
#
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
import time
# external packages
import PyQt5.QtCore
import PyQt5.QtWidgets
import PyQt5.uic
# This import registers the 3D projection, but is otherwise unused.
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np
from skyfield.api import EarthSatellite
# from skyfield.api import Time
# local import
from mw4.gui import widget
from mw4.gui.widgets import satellite_ui
from mw4.base import transform


class SatelliteWindow(widget.MWidget):
    """
    the satellite window class handles

    """

    __all__ = ['SatelliteWindow',
               ]
    version = '0.2'
    logger = logging.getLogger(__name__)

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.ui = satellite_ui.Ui_SatelliteDialog()
        self.ui.setupUi(self)
        self.initUI()

        self.satSphereMat = self.embedMatplot(self.ui.satSphere)
        self.satSphereMat.parentWidget().setStyleSheet(self.BACK_BG)
        self.satHorizonMat = self.embedMatplot(self.ui.satHorizon)
        self.satHorizonMat.parentWidget().setStyleSheet(self.BACK_BG)
        self.satEarthMat = self.embedMatplot(self.ui.satEarth)
        self.satEarthMat.parentWidget().setStyleSheet(self.BACK_BG)

        self.L1 = '1 43205U 18017A   18038.05572532 +.00020608 -51169-6 +11058-3 0  9993'
        self.L2 = '2 43205 029.0165 287.1006 3403068 180.4827 179.1544 08.75117793000017'

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
        self.drawSatellite()
        self.show()

    @staticmethod
    def set_axes_equal(axe):
        """
        Make axes of 3D plot have equal scale so that spheres appear as spheres,
        cubes as cubes, etc..  This is one possible solution to Matplotlib's
        axe.set_aspect('equal') and axe.axis('equal') not working for 3D.

        Input
          axe: a matplotlib axis, e.g., as output from plt.gca().
        """

        x_limits = axe.get_xlim3d()
        y_limits = axe.get_ylim3d()
        z_limits = axe.get_zlim3d()

        x_range = abs(x_limits[1] - x_limits[0])
        x_middle = np.mean(x_limits)
        y_range = abs(y_limits[1] - y_limits[0])
        y_middle = np.mean(y_limits)
        z_range = abs(z_limits[1] - z_limits[0])
        z_middle = np.mean(z_limits)

        # The plot bounding box is a sphere in the sense of the infinity
        # norm, hence I call half the max range the plot radius.
        plot_radius = 0.5 * max([x_range, y_range, z_range])

        axe.set_xlim3d([x_middle - plot_radius, x_middle + plot_radius])
        axe.set_ylim3d([y_middle - plot_radius, y_middle + plot_radius])
        axe.set_zlim3d([z_middle - plot_radius, z_middle + plot_radius])

    def drawSphere(self):

        # draw sphere and put face color als image overlay
        # https://stackoverflow.com/questions/53074908/map-an-image-onto-a-sphere-and-plot-3d-trajectories
        # but performance problems

        # see:
        # https://space.stackexchange.com/questions/25958/how-can-i-plot-a-satellites-orbit-in-3d-from-a-tle-using-python-and-skyfield

        figure = self.satSphereMat.figure
        figure.clf()
        figure.subplots_adjust(left=0, right=1, bottom=0, top=1)

        axe = figure.add_subplot(111, projection='3d')
        axe.set_facecolor((0, 0, 0, 0))
        axe.tick_params(colors=self.M_GREY,
                        labelsize=12)
        axe.set_axis_off()
        axe.w_xaxis.set_pane_color((0.0, 0.0, 0.0, 0.0))
        axe.w_yaxis.set_pane_color((0.0, 0.0, 0.0, 0.0))
        axe.w_zaxis.set_pane_color((0.0, 0.0, 0.0, 0.0))

        axe.xaxis._axinfo["grid"]['color'] = self.M_GREY
        axe.yaxis._axinfo["grid"]['color'] = self.M_GREY
        axe.zaxis._axinfo["grid"]['color'] = self.M_GREY
        # axe.set_aspect('equal')

        re = 6378.

        # drawing sphere
        theta = np.linspace(0, 2 * np.pi, 201)
        cth, sth, zth = [f(theta) for f in [np.cos, np.sin, np.zeros_like]]
        lon0 = re * np.vstack((cth, zth, sth))
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
            lat = re * np.vstack((cth * cph, sth * cph, zth + sph))
            lats.append(lat)

        for i, longitude in enumerate(longitudes):
            x, y, z = longitude
            axe.plot(x, y, z, '-k', lw=1,
                     color='#104860')
            axe.text(x[0], y[0], z[0], f'{lonBase[i]:3d}',
                     color=self.M_WHITE,
                     fontsize=8)
        for i, lat in enumerate(lats):
            x, y, z = lat
            axe.plot(x, y, z, '-k', lw=1,
                     color='#104860')
            axe.text(x[0], y[0], z[0], f'{latBase[i]:3d}',
                     color=self.M_WHITE,
                     fontsize=8)

        # drawing location on earth
        lat = self.app.mount.obsSite.location.latitude.degrees
        lon = self.app.mount.obsSite.location.longitude.degrees
        x, y, z = transform.sphericalToCartesian(np.radians(lat),
                                                 np.radians(lon)
                                                 , re)
        axe.plot([x],
                 [y],
                 [z],
                 marker='o',
                 color=self.M_RED,
                 )

        axe.plot([0, 0],
                 [0, 0],
                 [- re * 1.1, re* 1.1],
                 lw=3,
                 color='#104860')

        axe.text(0, 0, re * 1.2, 'N', color=self.M_BLUE)
        axe.text(0, 0, - re * 1.2 - 200, 'S', color=self.M_BLUE)


        """
        # draw plane
        radius = re - 300
        N = 50
        stride = 1
        u = np.linspace(0, 2 * np.pi, N)
        v = np.linspace(0, np.pi, N)
        x = radius * np.outer(np.cos(u), np.sin(v))
        y = radius * np.outer(np.sin(u), np.sin(v))
        z = radius * np.outer(np.ones(np.size(u)), np.cos(v))
        axe.plot_surface(x, y, z, linewidth=0.2, cstride=stride, rstride=stride,
                         color='red')
        """
        # drawing satellite orbit
        satellite = EarthSatellite(self.L1, self.L2)
        hours = np.arange(0, 10, 0.01)
        timescale = self.app.mount.obsSite.ts
        timeNow = timescale.now().tt_calendar()[0:3]
        time = timescale.utc(*timeNow, hours)
        x, y, z = satellite.at(time).position.km
        axe.plot(x,
                 y,
                 z,
                 color=self.M_GREEN)

        self.set_axes_equal(axe)
        axe.figure.canvas.draw()

    def drawEarth(self):

        figure = self.satEarthMat.figure
        figure.clf()
        figure.subplots_adjust(left=0.15, right=0.9, bottom=0.15, top=0.95)
        axe = self.satEarthMat.figure.add_subplot(1, 1, 1, facecolor=None)

        axe.set_facecolor((0, 0, 0, 0))
        axe.set_xlim(-180, 180)
        axe.set_ylim(-90, 90)
        axe.spines['bottom'].set_color('#2090C0')
        axe.spines['top'].set_color('#2090C0')
        axe.spines['left'].set_color('#2090C0')
        axe.spines['right'].set_color('#2090C0')
        axe.grid(True, color='#404040')
        axe.tick_params(axis='x',
                        colors='#2090C0',
                        labelsize=12)
        axe.set_xticks(np.arange(-180, 181, 45))
        axe.tick_params(axis='y',
                        colors='#2090C0',
                        which='both',
                        labelleft=True,
                        labelright=True,
                        labelsize=12)
        axe.set_xlabel('Longitude in degrees',
                       color='#2090C0',
                       fontweight='bold',
                       fontsize=12)
        axe.set_ylabel('Latitude in degrees',
                       color='#2090C0',
                       fontweight='bold',
                       fontsize=12)

        lat = self.app.mount.obsSite.location.latitude.degrees
        lon = self.app.mount.obsSite.location.longitude.degrees
        axe.plot(lon, lat, marker='o', color=self.M_RED)

        # loading the world image from nasa as PNG as matplotlib only loads png.
        world = plt.imread('world.png')
        # we have to extend this, to get it full in the frame !
        axe.imshow(world, extent=[-180, 180, -90, 90], alpha=0.3)

        # drawing satellite orbit
        satellite = EarthSatellite(self.L1, self.L2)
        hours = np.arange(0, 10, 0.01)
        timescale = self.app.mount.obsSite.ts
        timeNow = timescale.now().tt_calendar()[0:3]
        time = timescale.utc(*timeNow, hours)
        subpoint = satellite.at(time).subpoint()
        lat = subpoint.latitude.degrees
        lon = subpoint.longitude.degrees

        axe.plot(lon,
                 lat,
                 marker='.',
                 linestyle='none',
                 color=self.M_GREEN)

        axe.figure.canvas.draw()

    def drawHorizon(self):

        figure = self.satHorizonMat.figure
        figure.clf()
        figure.subplots_adjust(left=0.15, right=0.9, bottom=0.15, top=0.95)
        axe = self.satHorizonMat.figure.add_subplot(1, 1, 1, facecolor=None)

        axe.set_facecolor((0, 0, 0, 0))
        axe.set_xlim(0, 360)
        axe.set_ylim(0, 90)
        axe.spines['bottom'].set_color('#2090C0')
        axe.spines['top'].set_color('#2090C0')
        axe.spines['left'].set_color('#2090C0')
        axe.spines['right'].set_color('#2090C0')
        axe.grid(True, color='#404040')
        axe.tick_params(axis='x',
                        colors='#2090C0',
                        labelsize=12)
        axe.set_xticks(np.arange(0, 361, 45))
        axe.tick_params(axis='y',
                        colors='#2090C0',
                        which='both',
                        labelleft=True,
                        labelright=True,
                        labelsize=12)
        axe.set_xlabel('Azimuth in degrees',
                       color='#2090C0',
                       fontweight='bold',
                       fontsize=12)
        axe.set_ylabel('Altitude in degrees',
                       color='#2090C0',
                       fontweight='bold',
                       fontsize=12)

        satellite = EarthSatellite(self.L1, self.L2)
        hours = np.arange(0, 10, 0.01)
        timescale = self.app.mount.obsSite.ts
        timeNow = timescale.now().tt_calendar()[0:3]
        time = timescale.utc(*timeNow, hours)

        difference = satellite - self.app.mount.obsSite.location
        alt, az, _ = difference.at(time).altaz()
        alt = alt.degrees
        az = az.degrees

        axe.plot(az,
                 alt,
                 marker='.',
                 linestyle='none',
                 color=self.M_GREEN)

        axe.figure.canvas.draw()

    def drawSatellite(self):
        self.drawSphere()
        self.drawEarth()
        self.drawHorizon()
