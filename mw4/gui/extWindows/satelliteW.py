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
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection
from skyfield import functions
from skyfield.api import wgs84
import matplotlib.pyplot as plt

# local import
from gui.utilities import toolsQtWidget
from gui.widgets import satellite_ui


class SatelliteWindowSignals(QObject):
    """
    """
    __all__ = ['SatelliteWindowSignals']
    show = pyqtSignal(object, object, object, object)
    update = pyqtSignal(object, object)


class SatelliteWindow(toolsQtWidget.MWidget):
    """
    """
    __all__ = ['SatelliteWindow']
    FORECAST_TIME = 3
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
        self.satSphereMat1 = self.embedMatplot(self.ui.satSphere1,
                                               constrainedLayout=False)
        self.satSphereMat2 = self.embedMatplot(self.ui.satSphere2,
                                               constrainedLayout=False)
        self.satHorizonMat = self.embedMatplot(self.ui.satHorizon)
        self.satEarthMat = self.embedMatplot(self.ui.satEarth)

        self.colors = [self.M_RED_L, self.M_YELLOW_L, self.M_GREEN_L]

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
        self.ui.tabWidget.setCurrentIndex(config.get('tabWidget', 0))

        return True

    def storeConfig(self):
        """
        :return: True for test purpose
        """
        if 'satelliteW' not in self.app.config:
            self.app.config['satelliteW'] = {}

        config = self.app.config['satelliteW']
        config['winPosX'] = self.pos().x()
        config['winPosY'] = self.pos().y()
        config['height'] = self.height()
        config['width'] = self.width()
        config['tabWidget'] = self.ui.tabWidget.currentIndex()
        return True

    def closeEvent(self, closeEvent):
        """
        :param closeEvent:
        :return:
        """
        self.storeConfig()
        plt.close(self.satSphereMat1.figure)
        plt.close(self.satSphereMat2.figure)
        plt.close(self.satHorizonMat.figure)
        plt.close(self.satEarthMat.figure)
        super().closeEvent(closeEvent)

    def showWindow(self):
        """
        :return: True for test purpose
        """
        self.app.sendSatelliteData.emit()
        self.show()
        return True

    @staticmethod
    def markerSatellite():
        """
        markerSatellite constructs a custom marker for presentation of
        satellite view

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

    def updatePositions(self, now=None, location=None):
        """
        updatePositions is triggered once a second and update the satellite
        position in each view.

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
        if self.plotSatPosSphere1 is None:
            return False
        if self.plotSatPosSphere2 is None:
            return False

        observe = self.satellite.at(now)
        subpoint = wgs84.subpoint(observe)

        difference = self.satellite - location
        ra, dec, _ = difference.at(now).radec()
        altaz = difference.at(now).altaz()
        alt, az, _ = altaz

        alt, az, _ = altaz
        self.ui.satRa.setText(f'{ra.hours:3.2f}')
        self.ui.satDec.setText(f'{dec.degrees:3.2f}')
        self.ui.satLatitude.setText(f'{subpoint.latitude.degrees:3.2f}')
        self.ui.satLongitude.setText(f'{subpoint.longitude.degrees:3.2f}')
        self.ui.satAltitude.setText(f'{alt.degrees:3.2f}')
        self.ui.satAzimuth.setText(f'{az.degrees:3.2f}')

        x, y, z = observe.position.km
        self.plotSatPosSphere1.set_data_3d((x, y, z))

        lat = subpoint.latitude.radians
        lon = subpoint.longitude.radians
        elev = subpoint.elevation.m / 1000 + self.EARTH_RADIUS * 1.1

        xyz = functions.from_spherical(elev, lat, lon)
        self.plotSatPosSphere2.set_data_3d(xyz)

        lat = subpoint.latitude.degrees
        lon = subpoint.longitude.degrees
        self.plotSatPosEarth.set_data((lon, lat))

        alt, az, _ = altaz
        alt = alt.degrees
        az = az.degrees
        self.plotSatPosHorizon.set_data((az, alt))

        self.satSphereMat1.figure.canvas.draw()
        self.satSphereMat2.figure.canvas.draw()
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

        axe.set_facecolor((0, 0, 0, 0))
        axe.tick_params(colors=self.M_GREY, labelsize=12)
        axe.set_axis_off()
        axe.xaxis.set_pane_color((0.0, 0.0, 0.0, 0.0))
        axe.yaxis.set_pane_color((0.0, 0.0, 0.0, 0.0))
        axe.zaxis.set_pane_color((0.0, 0.0, 0.0, 0.0))

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

        for i, longitude in enumerate(longitudes):
            x, y, z = longitude
            axe.plot(x, y, z, lw=1, color=self.M_GREY)
        for i, lat in enumerate(lats):
            x, y, z = lat
            axe.plot(x, y, z, lw=1, color=self.M_GREY)

        axe.plot([0, 0], [0, 0],
                 [- self.EARTH_RADIUS * 1.1, self.EARTH_RADIUS * 1.1],
                 lw=3, color=self.M_BLUE)
        axe.text(0, 0, self.EARTH_RADIUS * 1.2, 'N', fontsize=14,
                 color=self.M_BLUE)
        axe.text(0, 0, - self.EARTH_RADIUS * 1.2 - 200, 'S', fontsize=14,
                 color=self.M_BLUE)

        if observe is None:
            axe.figure.canvas.draw()
            return False

        x, y, z = observe.position.km
        axe.plot(x, y, z, color=self.M_WHITE)
        self.plotSatPosSphere1, = axe.plot([x[0]], [y[0]], [z[0]],
                                           marker=self.markerSatellite(),
                                           markersize=25,
                                           linewidth=2,
                                           fillstyle='none',
                                           color=self.M_PINK_H)
        self.makeCubeLimits(axe)
        axe.figure.canvas.draw()
        return True

    def drawSphere2(self, observe=None):
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
        figure = self.satSphereMat2.figure
        figure.clf()
        figure.subplots_adjust(left=-0.1, right=1.1, bottom=-0.3, top=1.2)
        axe = figure.add_subplot(111, projection='3d')

        axe.set_facecolor((0, 0, 0, 0))
        axe.tick_params(colors=self.M_GREY, labelsize=12)
        axe.set_axis_off()
        axe.xaxis.set_pane_color((0.0, 0.0, 0.0, 0.0))
        axe.yaxis.set_pane_color((0.0, 0.0, 0.0, 0.0))
        axe.zaxis.set_pane_color((0.0, 0.0, 0.0, 0.0))

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
        for i, longitude in enumerate(longitudes):
            x, y, z = longitude
            axe.plot(x, y, z, lw=1, color=self.M_GREY)
        for i, lat in enumerate(lats):
            x, y, z = lat
            axe.plot(x, y, z, lw=1, color=self.M_GREY)

        axe.plot([0, 0], [0, 0],
                 [- self.EARTH_RADIUS * 1.1, self.EARTH_RADIUS * 1.1],
                 lw=3, color=self.M_BLUE)
        axe.text(0, 0, self.EARTH_RADIUS * 1.2, 'N', fontsize=14,
                 color=self.M_BLUE)
        axe.text(0, 0, - self.EARTH_RADIUS * 1.2 - 200, 'S', fontsize=14,
                 color=self.M_BLUE)

        for key in self.world.keys():
            shape = self.world[key]
            x, y, z = functions.from_spherical(self.EARTH_RADIUS,
                                               shape['yRad'],
                                               shape['xRad'])
            verts = [list(zip(x, y, z))]
            collect = Line3DCollection(verts,
                                       colors=self.M_BLUE1,
                                       lw=1,
                                       alpha=1)
            axe.add_collection3d(collect)
            collect = Poly3DCollection(verts,
                                       edgecolors=self.M_BLUE,
                                       alpha=0.3)
            axe.add_collection3d(collect)

        lat = self.app.mount.obsSite.location.latitude.radians
        lon = self.app.mount.obsSite.location.longitude.radians
        x, y, z = functions.from_spherical(self.EARTH_RADIUS, lat, lon)
        axe.plot(x, y, z, marker='.', markersize=12, color=self.M_YELLOW_H)

        if observe is None:
            axe.figure.canvas.draw()
            return False

        subpoints = wgs84.subpoint(observe)
        lat = subpoints.latitude.radians
        lon = subpoints.longitude.radians
        elev = subpoints.elevation.m / 1000 + self.EARTH_RADIUS * 1.1
        x, y, z = functions.from_spherical(elev, lat, lon)
        axe.plot(x, y, z, color=self.M_WHITE)
        self.plotSatPosSphere2, = axe.plot([x[0]], [y[0]], [z[0]],
                                           marker=self.markerSatellite(),
                                           markersize=25,
                                           linewidth=2,
                                           fillstyle='none',
                                           color=self.M_PINK_H)
        self.makeCubeLimits(axe)
        axe.figure.canvas.draw()
        return True

    @staticmethod
    def unlinkWrap(dat, limits=[-180, 180], thresh=0.95):
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

    def drawEarth(self, obsSite=None, satOrbits=None, altitude=[], azimuth=[]):
        """
        drawEarth show a full earth view with the path of the subpoint of the
        satellite drawn on it.

        :param obsSite:
        :param satOrbits:
        :param altitude:
        :param azimuth:
        :return: success
        """
        axe, fig = self.generateFlat(widget=self.satEarthMat)
        axe.set_xticks(np.arange(-180, 181, 45))
        axe.set_xlabel('Longitude in degrees')
        axe.set_ylabel('Latitude in degrees')
        axe.set_ylim([-90, 90])
        axe.set_xlim([-180, 180])

        for key in self.world.keys():
            shape = self.world[key]
            axe.fill(shape['xDeg'], shape['yDeg'], color=self.M_BLUE, alpha=0.2)
            axe.plot(shape['xDeg'], shape['yDeg'], color=self.M_BLUE, lw=1, alpha=0.4)

        if not satOrbits or obsSite is None:
            axe.figure.canvas.draw()
            return False

        lat = obsSite.location.latitude.degrees
        lon = obsSite.location.longitude.degrees
        axe.plot(lon, lat, marker='.', markersize=5, color=self.M_YELLOW_H)

        ts = obsSite.ts
        subpoint = wgs84.subpoint(self.satellite.at(ts.now()))
        lat = subpoint.latitude.degrees
        lon = subpoint.longitude.degrees
        self.plotSatPosEarth, = axe.plot(lon, lat,
                                         marker=self.markerSatellite(),
                                         markersize=25, lw=2, fillstyle='none',
                                         ls='none', color=self.M_PINK_H,
                                         zorder=10)

        for i, satOrbit in enumerate(satOrbits):
            rise = satOrbit['rise'].tt
            settle = satOrbit['settle'].tt
            step = 0.005 * (settle - rise)

            if satOrbit['flip'] is None:
                satOrbit['flip'] = satOrbit['settle']

            flip = satOrbit['flip'].tt

            vector = np.arange(rise, flip, step)
            vecT = ts.tt_jd(vector)
            subpoints = wgs84.subpoint(self.satellite.at(vecT))
            lat = subpoints.latitude.degrees
            lon = subpoints.longitude.degrees
            for slc in self.unlinkWrap(lon):
                axe.plot(lon[slc], lat[slc], lw=4, color=self.colors[i])

            vector = np.arange(flip, settle, step)
            vecT = ts.tt_jd(vector)
            subpoints = wgs84.subpoint(self.satellite.at(vecT))
            lat = subpoints.latitude.degrees
            lon = subpoints.longitude.degrees
            for slc in self.unlinkWrap(lon):
                axe.plot(lon[slc], lat[slc], color=self.colors[i],
                         lw=4, linestyle=(0, (0.5, 0.5)))

        rise = satOrbits[0]['rise'].tt
        settle = satOrbits[-1]['settle'].tt
        step = 0.001 * (settle - rise)
        vector = np.arange(rise - 0.15, settle, step)
        vecT = ts.tt_jd(vector)
        subpoints = wgs84.subpoint(self.satellite.at(vecT))
        lat = subpoints.latitude.degrees
        lon = subpoints.longitude.degrees
        for slc in self.unlinkWrap(lon):
            axe.plot(lon[slc], lat[slc], lw=1, color=self.M_WHITE_L, zorder=-10)
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

        axes.fill(azF, altF, color=self.M_GREEN_LL, alpha=0.7, zorder=-10)
        axes.plot(az, alt, color=self.M_GREEN, marker='', alpha=0.5, lw=3)
        return True

    def drawHorizonView(self, obsSite=None, satOrbits=None, altitude=[], azimuth=[]):
        """
        drawHorizonView shows the horizon and enable the users to explore a
        satellite passing by

        :param obsSite:
        :param satOrbits:
        :param altitude:
        :param azimuth:
        :return: success
        """
        axe, fig = self.generateFlat(widget=self.satHorizonMat, horizon=True)
        self.staticHorizon(axes=axe)

        if not satOrbits or obsSite is None:
            axe.figure.canvas.draw()
            return False

        ts = obsSite.ts
        for i, satOrbit in enumerate(satOrbits):
            rise = satOrbit['rise'].tt
            settle = satOrbit['settle'].tt
            step = 0.005 * (settle - rise)

            if satOrbit['flip'] is None:
                satOrbit['flip'] = satOrbit['settle']

            flip = satOrbit['flip'].tt
            vector = np.arange(rise, flip, step)
            vecT = ts.tt_jd(vector)
            alt, az, _ = (self.satellite - obsSite.location).at(vecT).altaz()
            for slc in self.unlinkWrap(az.degrees):
                axe.plot(az.degrees[slc], alt.degrees[slc], lw=4,
                         color=self.colors[i])

            vector = np.arange(flip, settle, step)
            vecT = ts.tt_jd(vector)
            alt, az, _ = (self.satellite - obsSite.location).at(vecT).altaz()
            for slc in self.unlinkWrap(az.degrees):
                axe.plot(az.degrees[slc], alt.degrees[slc], color=self.colors[i],
                         lw=4, linestyle=(0, (0.5, 0.5)))

        for slc in self.unlinkWrap(azimuth):
            axe.plot(azimuth[slc], altitude[slc],
                     color=self.M_WHITE, lw=4, linestyle=(0, (0.5, 0.5)))

        ts = obsSite.ts
        alt, az, _ = (self.satellite - obsSite.location).at(ts.now()).altaz()
        self.plotSatPosHorizon, = axe.plot(az.degrees, alt.degrees,
                                           marker=self.markerSatellite(),
                                           markersize=25, lw=2, fillstyle='none',
                                           ls='none', color=self.M_PINK_H,
                                           zorder=10)
        axe.figure.canvas.draw()
        return True

    def drawSatellite(self, satellite=None, satOrbits=None, altitude=[], azimuth=[]):
        """
        drawSatellite draws 4 different views of the actual satellite
        situation: two sphere views, a horizon view and an earth view.
        satellites with an day angle < 400 means less than one orbit per day and
        might be stationary visible (geostationary)

        :param satellite:
        :param satOrbits:
        :param altitude:
        :param azimuth:
        :return: True for test purpose
        """
        if satellite is None or satOrbits is None:
            self.drawSphere1()
            self.drawSphere2()
            self.drawEarth()
            self.drawHorizonView()
            return False

        self.satellite = satellite
        timescale = self.app.mount.obsSite.ts
        dayAngle = satellite.model.no_kozai * 24 * 60 / np.pi * 180
        if dayAngle < 400:
            forecastTime = 24
        else:
            forecastTime = 3

        forecast = np.arange(0, forecastTime, 0.005 * forecastTime / 3) / 24
        now = timescale.now()
        timeVector = timescale.tt_jd(now.tt + forecast)
        observe = self.satellite.at(timeVector)

        self.drawSphere1(observe=observe)
        self.drawSphere2(observe=observe)
        self.drawEarth(self.app.mount.obsSite,
                       satOrbits=satOrbits, altitude=altitude, azimuth=azimuth)
        self.drawHorizonView(self.app.mount.obsSite,
                             satOrbits=satOrbits, altitude=altitude, azimuth=azimuth)
        return True
