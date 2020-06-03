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
# written in python3 , (c) 2019, 2020 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
import unittest.mock as mock
from queue import Queue
import faulthandler
faulthandler.enable()

# external packages
from PyQt5.QtCore import QThreadPool
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal
import matplotlib.pyplot as plt
from mountcontrol.mount import Mount
from skyfield.toposlib import Topos
from skyfield.api import EarthSatellite

# local import
from mw4.gui.satelliteW import SatelliteWindow

from mw4.resource import resources


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    global Test

    class Test1:
        horizonP = {(10, 0), (15, 360)}

    class Test(QObject):
        config = {'mainW': {}}
        update1s = pyqtSignal()
        messageQueue = Queue()
        threadPool = QThreadPool()
        mount = Mount(host='localhost', MAC='00:00:00:00:00:00', expire=False, verbose=False,
                      pathToData='mw4/test/data')
        data = Test1()
        mount.obsSite.location = Topos(latitude_degrees=20,
                                       longitude_degrees=10,
                                       elevation_m=500)

    yield


def test_initConfig_1(qtbot):
    app = SatelliteWindow(app=Test())
    qtbot.addWidget(app)

    app.app.config['satelliteW'] = {}
    suc = app.initConfig()
    assert suc


def test_initConfig_2(qtbot):
    app = SatelliteWindow(app=Test())
    qtbot.addWidget(app)

    del app.app.config['satelliteW']
    suc = app.initConfig()
    assert suc


def test_initConfig_3(qtbot):
    app = SatelliteWindow(app=Test())
    qtbot.addWidget(app)

    app.app.config['satelliteW'] = {}
    app.app.config['satelliteW']['winPosX'] = 10000
    app.app.config['satelliteW']['winPosY'] = 10000
    suc = app.initConfig()
    assert suc


def test_storeConfig_1(qtbot):
    app = SatelliteWindow(app=Test())
    qtbot.addWidget(app)

    if 'satelliteW' in app.app.config:
        del app.app.config['satelliteW']
    suc = app.storeConfig()
    assert suc


def test_storeConfig_2(qtbot):
    app = SatelliteWindow(app=Test())
    qtbot.addWidget(app)

    app.app.config['satelliteW'] = {}
    suc = app.storeConfig()
    assert suc


def test_closeEvent_1(qtbot):
    app = SatelliteWindow(app=Test())
    qtbot.addWidget(app)

    app.closeEvent(QCloseEvent())


def test_resizeEvent(qtbot):
    app = SatelliteWindow(app=Test())
    qtbot.addWidget(app)

    app.resizeEvent(None)


def test_updatePositions_1(qtbot):
    app = SatelliteWindow(app=Test())
    qtbot.addWidget(app)

    suc = app.updatePositions()
    assert not suc


def test_updatePositions_2(qtbot):
    app = SatelliteWindow(app=Test())
    qtbot.addWidget(app)

    suc = app.updatePositions(observe='t')
    assert not suc


def test_updatePositions_3(qtbot):
    app = SatelliteWindow(app=Test())
    qtbot.addWidget(app)

    suc = app.updatePositions(observe='t', subpoint='t')
    assert not suc


def test_updatePositions_4(qtbot):
    app = SatelliteWindow(app=Test())
    qtbot.addWidget(app)

    suc = app.updatePositions(observe='t', subpoint='t', altaz='t')
    assert not suc


def test_updatePositions_5(qtbot):
    app = SatelliteWindow(app=Test())
    qtbot.addWidget(app)
    app.satellite = 1

    suc = app.updatePositions(observe='t', subpoint='t', altaz='t')
    assert not suc


def test_updatePositions_6(qtbot):
    app = SatelliteWindow(app=Test())
    qtbot.addWidget(app)
    app.satellite = 1
    app.plotSatPosEarth = 1

    suc = app.updatePositions(observe='t', subpoint='t', altaz='t')
    assert not suc


def test_updatePositions_7(qtbot):
    app = SatelliteWindow(app=Test())
    qtbot.addWidget(app)
    app.satellite = 1
    app.plotSatPosEarth = 1
    app.plotSatPosHorizon = 1

    suc = app.updatePositions(observe='t', subpoint='t', altaz='t')
    assert not suc


def test_updatePositions_8(qtbot):
    app = SatelliteWindow(app=Test())
    qtbot.addWidget(app)
    app.satellite = 1
    app.plotSatPosEarth = 1
    app.plotSatPosHorizon = 1
    app.plotSatPosSphere1 = 1

    suc = app.updatePositions(observe='t', subpoint='t', altaz='t')
    assert not suc


def test_updatePositions_9(qtbot):
    app = SatelliteWindow(app=Test())
    qtbot.addWidget(app)
    tle = ["TIANGONG 1",
           "1 37820U 11053A   14314.79851609  .00064249  00000-0  44961-3 0  5637",
           "2 37820  42.7687 147.7173 0010686 283.6368 148.1694 15.73279710179072"]
    app.satellite = EarthSatellite(*tle[1:3], name=tle[0])

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    app.plotSatPosEarth, = plt.plot([1, 0], [1, 0])
    app.plotSatPosHorizon, = plt.plot([1, 0], [1, 0])
    app.plotSatPosSphere1, = ax.plot([1], [1], [1])
    app.plotSatPosSphere2, = ax.plot([1], [1], [1])

    now = app.app.mount.obsSite.ts.now()
    observe = app.satellite.at(now)
    subpoint = observe.subpoint()
    difference = app.satellite - app.app.mount.obsSite.location
    altaz = difference.at(now).altaz()

    with mock.patch.object(app.plotSatPosSphere1,
                           'set_data_3d'):
        with mock.patch.object(app.plotSatPosSphere2,
                               'set_data_3d'):
            with mock.patch.object(app.plotSatPosEarth,
                                   'set_data'):
                with mock.patch.object(app.plotSatPosHorizon,
                                       'set_data'):
                    suc = app.updatePositions(observe=observe,
                                              subpoint=subpoint,
                                              altaz=altaz)
                    assert suc


def test_makeCubeLimits_1(qtbot):
    app = SatelliteWindow(app=Test())
    qtbot.addWidget(app)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    app.makeCubeLimits(ax)


def test_makeCubeLimits_2(qtbot):
    app = SatelliteWindow(app=Test())
    qtbot.addWidget(app)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    app.makeCubeLimits(ax, hw=(1, 2, 3))


def test_makeCubeLimits_3(qtbot):
    app = SatelliteWindow(app=Test())
    qtbot.addWidget(app)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    app.makeCubeLimits(ax, hw=3)


def test_drawSphere1_1(qtbot):
    app = SatelliteWindow(app=Test())
    qtbot.addWidget(app)

    app.drawSphere1()


def test_drawSphere2_1(qtbot):
    app = SatelliteWindow(app=Test())
    qtbot.addWidget(app)

    app.drawSphere2()


def test_drawEarth_1(qtbot):
    app = SatelliteWindow(app=Test())
    qtbot.addWidget(app)

    app.drawEarth()


def test_drawHorizonView_1(qtbot):
    app = SatelliteWindow(app=Test())
    qtbot.addWidget(app)

    app.drawHorizonView()


def test_drawSatellite_1(qtbot):
    app = SatelliteWindow(app=Test())
    qtbot.addWidget(app)

    suc = app.drawSatellite()
    assert not suc


def test_drawSatellite_2(qtbot):
    app = SatelliteWindow(app=Test())
    qtbot.addWidget(app)

    tle = ["TIANGONG 1",
           "1 37820U 11053A   14314.79851609  .00064249  00000-0  44961-3 0  5637",
           "2 37820  42.7687 147.7173 0010686 283.6368 148.1694 15.73279710179072"]
    satellite = EarthSatellite(*tle[1:3], name=tle[0])

    satOrbits = {}

    suc = app.drawSatellite(satellite=satellite, satOrbits=satOrbits)
    assert suc
