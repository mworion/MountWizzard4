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

# local import
from mw4.gui import widget
from mw4.gui.widgets import satellite_ui


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
        self.resize(800, height)

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

    def closeEvent(self, closeEvent):
        self.storeConfig()

        # gui signals

        super().closeEvent(closeEvent)

    def showWindow(self):
        self.drawSatellite()
        self.show()

    @staticmethod
    def makeCubeLimits(axis, centers=None, hw=None):
        """

        :param axis:
        :param centers:
        :param hw:
        :return:
        """

        limits = axis.get_xlim(), axis.get_ylim(), axis.get_zlim()
        if centers is None:
            centers = [0.5 * sum(pair) for pair in limits]

        if hw is None:
            widths = [pair[1] - pair[0] for pair in limits]
            hw = 0.5 * max(widths)
            axis.set_xlim(centers[0] - hw, centers[0] + hw)
            axis.set_ylim(centers[1] - hw, centers[1] + hw)
            axis.set_zlim(centers[2] - hw, centers[2] + hw)

        else:
            try:
                hwx, hwy, hwz = hw
                axis.set_xlim(centers[0] - hwx, centers[0] + hwx)
                axis.set_ylim(centers[1] - hwy, centers[1] + hwy)
                axis.set_zlim(centers[2] - hwz, centers[2] + hwz)

            except Exception as e:
                ax.set_xlim(centers[0] - hw, centers[0] + hw)
                ax.set_ylim(centers[1] - hw, centers[1] + hw)
                ax.set_zlim(centers[2] - hw, centers[2] + hw)

        return centers, hw

    def drawSphere(self):

        # see:
        # https://space.stackexchange.com/questions/25958/how-can-i-plot-a-satellites-orbit-in-3d-from-a-tle-using-python-and-skyfield

        figure = self.satSphereMat.figure
        figure.clf()
        figure.subplots_adjust(left=0.075, right=0.95, bottom=0.1, top=0.975)

        ax = figure.add_subplot(111, projection='3d')
        ax.set_facecolor((0, 0, 0, 0))
        ax.tick_params(colors='#2090C0',
                        labelsize=12)
        ax.w_xaxis.set_pane_color((0.0, 0.0, 0.0, 0.0))
        ax.w_yaxis.set_pane_color((0.0, 0.0, 0.0, 0.0))
        ax.w_zaxis.set_pane_color((0.0, 0.0, 0.0, 0.0))
        ax.xaxis._axinfo["grid"]['color'] = self.M_GREY
        ax.yaxis._axinfo["grid"]['color'] = self.M_GREY
        ax.zaxis._axinfo["grid"]['color'] = self.M_GREY
        # ax.set_aspect('equal')

        halfpi, pi, twopi = [f * np.pi for f in (0.5, 1, 2)]
        degs, rads = 180 / pi, pi / 180
        re = 6378.

        theta = np.linspace(0, twopi, 201)
        cth, sth, zth = [f(theta) for f in [np.cos, np.sin, np.zeros_like]]
        lon0 = re * np.vstack((cth, zth, sth))
        lons = []
        for phi in rads * np.arange(0, 180, 15):
            cph, sph = [f(phi) for f in [np.cos, np.sin]]
            lon = np.vstack((lon0[0] * cph - lon0[1] * sph,
                             lon0[1] * cph + lon0[0] * sph,
                             lon0[2]))
            lons.append(lon)

        lat0 = re * np.vstack((cth, sth, zth))
        lats = []
        for phi in rads * np.arange(-75, 90, 15):
            cph, sph = [f(phi) for f in [np.cos, np.sin]]
            lat = re * np.vstack((cth * cph, sth * cph, zth + sph))
            lats.append(lat)

        for x, y, z in lons:
            ax.plot(x, y, z, '-k', color=self.M_BLUE)
        for x, y, z in lats:
            ax.plot(x, y, z, '-k', color=self.M_BLUE)

        centers, hw = self.makeCubeLimits(ax)

        ax.figure.canvas.draw()

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
        axe.figure.canvas.draw()

    def drawSatellite(self):
        self.drawSphere()
        self.drawEarth()
        self.drawHorizon()
