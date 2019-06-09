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

    def drawSphere(self):

        figure = self.satSphereMat.figure
        figure.clf()
        figure.subplots_adjust(left=0.075, right=0.95, bottom=0.1, top=0.975)

        ax = figure.add_subplot(111, projection='3d')
        ax.set_facecolor((0, 0, 0, 0))
        ax.grid(True, color='#404040')
        ax.tick_params(colors='#2090C0',
                        labelsize=12)

        # Create the mesh in polar coordinates and compute corresponding Z.
        r = np.linspace(0, 1.25, 50)
        p = np.linspace(0, 2 * np.pi, 50)
        R, P = np.meshgrid(r, p)
        Z = ((R ** 2 - 1) ** 2)

        # Express the mesh in the cartesian system.
        X, Y = R * np.cos(P), R * np.sin(P)

        # Plot the surface.
        ax.plot_surface(X, Y, Z, cmap=plt.cm.YlGnBu_r,
                        color='#2090C0')

        # Tweak the limits and add latex math labels.
        ax.set_zlim(0, 1)
        ax.set_xlabel(r'$\phi_\mathrm{real}$',
                      color='#2090C0',
                      fontweight='bold',
                      fontsize=12)
        ax.set_ylabel(r'$\phi_\mathrm{im}$',
                      color='#2090C0',
                      fontweight='bold',
                      fontsize=12)
        ax.set_zlabel(r'$V(\phi)$',
                      color='#2090C0',
                      fontweight='bold',
                      fontsize=12)
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
