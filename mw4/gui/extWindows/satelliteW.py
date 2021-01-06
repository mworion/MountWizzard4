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
# written in python3, (c) 2019-2021 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import pickle
from io import BytesIO

# external packages
from PyQt5.QtCore import QObject, pyqtSignal, QFile
import numpy as np
import matplotlib.path as mpath
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from skyfield import functions

# local import
from gui.utilities import toolsQtWidget
from gui.widgets import satellite_ui


class SatelliteWindowSignals(QObject):
    """
    The SatelliteWindowSignals class offers a list of signals to be used and instantiated by
    the SatelliteWindow class to get signals for triggers for finished tasks to
    enable a gui to update their values transferred to the caller back.

    This has to be done in a separate class as the signals have to be subclassed from
    QObject and the Mount class itself is subclassed from object
    """

    __all__ = ['SatelliteWindowSignals']

    show = pyqtSignal(object, object)
    update = pyqtSignal(object, object, object)


class SatelliteWindow(toolsQtWidget.MWidget):
    """
    the satellite window class handles

    """

    __all__ = ['SatelliteWindow']

    # length of forecast time in hours
    FORECAST_TIME = 3
    # earth radius
    EARTH_RADIUS = 6378.0

    def __init__(self, app):
        super().__init__()

        self.app = app
        self.threadPool = app.threadPool

        self.ui = satellite_ui.Ui_SatelliteDialog()
        self.ui.setupUi(self)
        self.initUI()
        self.signals = SatelliteWindowSignals()
        self.satellite = None
        self.plotSatPosSphere1 = None
        self.plotSatPosSphere2 = None
        self.plotSatPosHorizon = None
        self.plotSatPosEarth = None

        self.satSphereMat1 = self.embedMatplot(self.ui.satSphere1, constrainedLayout=False)
        self.satSphereMat1.parentWidget().setStyleSheet(self.BACK_BG)
        self.satSphereMat2 = self.embedMatplot(self.ui.satSphere2, constrainedLayout=False)
        self.satSphereMat2.parentWidget().setStyleSheet(self.BACK_BG)
        self.satHorizonMat = self.embedMatplot(self.ui.satHorizon, constrainedLayout=True)
        self.satHorizonMat.parentWidget().setStyleSheet(self.BACK_BG)
        self.satEarthMat = self.embedMatplot(self.ui.satEarth, constrainedLayout=True)
        self.satEarthMat.parentWidget().setStyleSheet(self.BACK_BG)

        self.signals.show.connect(self.drawSatellite)
        self.signals.update.connect(self.updatePositions)

        stream = QFile(':/data/worldmap.dat')
        stream.open(QFile.ReadOnly)
        pickleData = stream.readAll()
        stream.close()
        self.world = pickle.load(BytesIO(pickleData))

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
        x = config.get('winPosX', 160)
        y = config.get('winPosY', 160)

        if x > self.screenSizeX:
            x = 0

        if y > self.screenSizeY:
            y = 0

        self.move(x, y)
        height = config.get('height', 600)
        width = config.get('width', 800)
        self.resize(width, height)

        return True

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

        return True

    def closeEvent(self, closeEvent):
        """
        closeEvent is overloaded to be able to store the data before the windows is close
        and all it's data is garbage collected

        :param closeEvent:
        :return:
        """
        self.storeConfig()
        super().closeEvent(closeEvent)

    def showWindow(self):
        """
        showWindow starts constructing the main window for satellite view and shows the
        window content

        :return: True for test purpose
        """

        self.app.sendSatelliteData.emit()
        self.show()

        return True

    @staticmethod
    def markerSatellite():
        """
        markerSatellite constructs a custom marker for presentation of satellite view

        :return: marker
        """

        circle = mpath.Path.unit_circle()

        rect1p = [[0, 0], [1, 2], [0, 3], [4, 7], [7, 4], [3, 0], [2, 1], [6, 5], [5, 6],
                  [1, 2], [2, 1], [0, 0]]
        rect1p = np.array(rect1p)
        rect1c = [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 79]
        rect1c = np.array(rect1c)
        # concatenate the circle with an internal cutout of the star
        verts = np.concatenate([rect1p,
                                rect1p * -1,
                                circle.vertices])
        codes = np.concatenate([rect1c,
                                rect1c,
                                circle.codes])
        marker = mpath.Path(verts, codes)
        return marker

    def updatePositions(self, observe=None, subpoint=None, altaz=None):
        """
        updatePositions is triggered once a second and update the satellite position in each
        view.

        :return: success
        """
        if observe is None:
            return False
        if subpoint is None:
            return False
        if altaz is None:
            return False

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

        xyz = functions.from_spherical(elev, lat, lon)
        self.plotSatPosSphere2.set_data_3d(xyz)

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
        figure.subplots_adjust(left=-0.1, right=1.1, bottom=-0.3, top=1.2)
        axe = figure.add_subplot(111, projection='3d')

        # switching all visual grids and planes off
        axe.set_facecolor((0, 0, 0, 0))
        axe.tick_params(colors=self.M_GREY,
                        labelsize=12)
        axe.set_axis_off()
        axe.xaxis.set_pane_color((0.0, 0.0, 0.0, 0.0))
        axe.yaxis.set_pane_color((0.0, 0.0, 0.0, 0.0))
        axe.zaxis.set_pane_color((0.0, 0.0, 0.0, 0.0))

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
        axe.plot(x, y, z, color=self.M_WHITE)

        self.plotSatPosSphere1, = axe.plot([x[0]], [y[0]], [z[0]],
                                           marker=self.markerSatellite(),
                                           markersize=16,
                                           linewidth=2,
                                           fillstyle='none',
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
        figure.subplots_adjust(left=-0.1, right=1.1, bottom=-0.3, top=1.2)
        axe = figure.add_subplot(111, projection='3d')

        # switching all visual grids and planes off
        axe.set_facecolor((0, 0, 0, 0))
        axe.tick_params(colors=self.M_GREY,
                        labelsize=12)
        axe.set_axis_off()
        axe.xaxis.set_pane_color((0.0, 0.0, 0.0, 0.0))
        axe.yaxis.set_pane_color((0.0, 0.0, 0.0, 0.0))
        axe.zaxis.set_pane_color((0.0, 0.0, 0.0, 0.0))

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
            x, y, z = functions.from_spherical(self.EARTH_RADIUS, shape['yRad'], shape['xRad'])
            verts = [list(zip(x, y, z))]
            collect = Poly3DCollection(verts, facecolors=self.M_BLUE, alpha=0.5)
            axe.add_collection3d(collect)

        # drawing home position location on earth
        lat = self.app.mount.obsSite.location.latitude.radians
        lon = self.app.mount.obsSite.location.longitude.radians

        x, y, z = functions.from_spherical(self.EARTH_RADIUS, lat, lon)

        axe.plot(x, y, z,
                 marker='.',
                 markersize=12,
                 color=self.M_RED,
                 )

        # empty chart if no satellite is chosen
        if observe is None:
            axe.figure.canvas.draw()
            return False

        # drawing satellite subpoint path
        lat = subpoint.latitude.radians
        lon = subpoint.longitude.radians
        elev = subpoint.elevation.m / 1000 + self.EARTH_RADIUS

        x, y, z = functions.from_spherical(elev, lat, lon)

        axe.plot(x, y, z, color=self.M_WHITE)

        # draw satellite position
        self.plotSatPosSphere2, = axe.plot([x[0]], [y[0]], [z[0]],
                                           marker=self.markerSatellite(),
                                           markersize=16,
                                           linewidth=2,
                                           fillstyle='none',
                                           color=self.M_PINK)

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

        axe, fig = self.generateFlat(widget=self.satEarthMat)

        axe.set_xticks(np.arange(-180, 181, 45))
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
            axe.fill(shape['xDeg'], shape['yDeg'], color=self.M_BLUE, alpha=0.2)
            axe.plot(shape['xDeg'], shape['yDeg'], color=self.M_BLUE, lw=1, alpha=0.4)

        # mark the site location in the map
        lat = self.app.mount.obsSite.location.latitude.degrees
        lon = self.app.mount.obsSite.location.longitude.degrees
        axe.plot(lon,
                 lat,
                 marker='.',
                 markersize=10,
                 color=self.M_RED)

        # empty chart if no satellite is chosen
        if subpoint is None:
            axe.figure.canvas.draw()
            return False

        # drawing satellite subpoint path
        lat = subpoint.latitude.degrees
        lon = subpoint.longitude.degrees

        axe.plot(lon,
                 lat,
                 marker='o',
                 markersize=1,
                 linestyle='none',
                 color=self.M_WHITE)

        # show the actual position
        self.plotSatPosEarth, = axe.plot(lon[0],
                                         lat[0],
                                         marker=self.markerSatellite(),
                                         markersize=16,
                                         linewidth=2,
                                         fillstyle='none',
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
        alt = np.array(alt)
        az = np.array(az)
        altF = np.concatenate([[0], [alt[0]], alt, [alt[-1]], [0]])
        azF = np.concatenate([[0], [0], az, [360], [360]])

        axes.fill(azF,
                  altF,
                  color=self.M_GREEN_LL,
                  alpha=0.7,
                  zorder=-20)

        axes.plot(az,
                  alt,
                  color=self.M_GREEN,
                  marker='',
                  alpha=0.5,
                  zorder=0,
                  lw=3)

        return True

    def drawHorizonView(self, difference=None):
        """
        drawHorizonView shows the horizon and enable the users to explore a satellite
        passing by

        :param difference:
        :return: success
        """

        axe, fig = self.generateFlat(widget=self.satHorizonMat, horizon=True)

        # add horizon limit if selected
        self.staticHorizon(axes=axe)

        # empty chart if no satellite is chosen
        if difference is None:
            axe.figure.canvas.draw()
            return False

        colors = [self.M_RED, self.M_YELLOW, self.M_GREEN]

        # orbital calculations
        for diff in difference:
            alt, az, _ = difference[diff].altaz()
            alt = alt.degrees
            az = az.degrees

            # draw path
            axe.plot(az,
                     alt,
                     marker='.',
                     markersize=3,
                     linestyle='none',
                     color=colors[diff])

        # draw actual position
        self.plotSatPosHorizon, = axe.plot(180,
                                           -10,
                                           marker=self.markerSatellite(),
                                           markersize=16,
                                           linewidth=2,
                                           fillstyle=None,
                                           linestyle='none',
                                           color=self.M_PINK)

        axe.figure.canvas.draw()

        return True

    def drawSatellite(self, satellite=None, satOrbits=None):
        """
        drawSatellite draws 4 different views of the actual satellite situation: two sphere
        views, a horizon view and an earth view.

        :param satellite:
        :param satOrbits:
        :return: True for test purpose
        """

        if satellite is None or satOrbits is None:
            print('none received')
            self.drawSphere1()
            self.drawSphere2()
            self.drawEarth()
            self.drawHorizonView()
            return False

        self.satellite = satellite
        location = self.app.mount.obsSite.location
        timescale = self.app.mount.obsSite.ts

        dayAngle = satellite.model.no_kozai * 24 * 60 / np.pi * 180

        if dayAngle < 400:
            # this means less than one orbit per day (geostationary)
            forecastTime = 24
        else:
            forecastTime = 3

        forecast = np.arange(0, forecastTime, 0.005 * forecastTime / 3) / 24
        now = timescale.now()
        timeVector = timescale.tt_jd(now.tt + forecast)

        timeVectorsHorizon = dict()

        for satOrbit in satOrbits:
            if satOrbit > 2:
                break
            timeRise = satOrbits[satOrbit]['rise']
            timeSettle = satOrbits[satOrbit]['settle']
            showTime = timeSettle.tt - timeRise.tt
            forecast = np.arange(0, showTime, 0.002 * showTime)
            timeVectorsHorizon[satOrbit] = timescale.tt_jd(timeRise.tt + forecast)

        observe = self.satellite.at(timeVector)
        subpoint = observe.subpoint()

        difference = dict()
        for timeVectorHorizon in timeVectorsHorizon:
            diff = (self.satellite - location).at(timeVectorsHorizon[timeVectorHorizon])
            difference[timeVectorHorizon] = diff

        self.drawSphere1(observe=observe)
        self.drawSphere2(observe=observe, subpoint=subpoint)
        self.drawEarth(subpoint=subpoint)
        self.drawHorizonView(difference=difference)

        return True
