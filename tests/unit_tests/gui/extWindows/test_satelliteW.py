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
#
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
import unittest.mock as mock

# external packages
import matplotlib
matplotlib.use('Qt5Agg')
from PyQt5.QtGui import QCloseEvent
import matplotlib.pyplot as plt
from skyfield.api import EarthSatellite
from skyfield.api import Angle
from skyfield.api import load

# local import
from tests.baseTestSetupExtWindows import App
from gui.utilities.toolsQtWidget import MWidget
from gui.extWindows.satelliteW import SatelliteWindow
from resource import resources


@pytest.fixture(autouse=True, scope='module')
def module(qapp):
    ts = load.timescale(builtin=True)
    yield ts


@pytest.fixture(autouse=True, scope='function')
def function(module):

    window = SatelliteWindow(app=App())
    window.app.mount.obsSite.ts = module
    yield window


def test_initConfig_1(function):
    suc = function.initConfig()
    assert suc


def test_initConfig_2(function):
    suc = function.initConfig()
    assert suc

    function.app.config['satelliteW'] = {'winPosX': 10000}
    suc = function.initConfig()
    assert suc


def test_initConfig_3(function):
    suc = function.initConfig()
    assert suc

    function.app.config['satelliteW'] = {'winPosY': 10000}
    suc = function.initConfig()
    assert suc


def test_storeConfig_1(function):
    if 'satelliteW' in function.app.config:
        del function.app.config['satelliteW']

    suc = function.storeConfig()
    assert suc


def test_storeConfig_2(function):
    function.app.config['satelliteW'] = {}

    suc = function.storeConfig()
    assert suc


def test_closeEvent_1(function):
    with mock.patch.object(function,
                           'show'):
        with mock.patch.object(MWidget,
                               'closeEvent'):
            function.closeEvent(QCloseEvent)


def test_showWindow(function):
    with mock.patch.object(MWidget,
                           'show'):
        suc = function.showWindow()
        assert suc


def test_markerSatellite(function):
    val = function.markerSatellite()
    assert val is not None


def test_updatePositions_1(function):
    suc = function.updatePositions()
    assert not suc


def test_updatePositions_2(function):
    suc = function.updatePositions(observe='t')
    assert not suc


def test_updatePositions_3(function):
    suc = function.updatePositions(observe='t', subpoint='t')
    assert not suc


def test_updatePositions_4(function):
    suc = function.updatePositions(observe='t', subpoint='t', altaz='t')
    assert not suc


def test_updatePositions_5(function):
    function.satellite = 1
    suc = function.updatePositions(observe='t', subpoint='t', altaz='t')
    assert not suc


def test_updatePositions_6(function):
    function.satellite = 1
    function.plotSatPosEarth = 1

    suc = function.updatePositions(observe='t', subpoint='t', altaz='t')
    assert not suc


def test_updatePositions_7(function):
    function.satellite = 1
    function.plotSatPosEarth = 1
    function.plotSatPosHorizon = 1

    suc = function.updatePositions(observe='t', subpoint='t', altaz='t')
    assert not suc


def test_updatePositions_8(function):
    function.satellite = 1
    function.plotSatPosEarth = 1
    function.plotSatPosHorizon = 1
    function.plotSatPosSphere1 = 1

    suc = function.updatePositions(observe='t', subpoint='t', altaz='t')
    assert not suc


def test_updatePositions_9(function):
    tle = ["TIANGONG 1",
           "1 37820U 11053A   14314.79851609  .00064249  00000-0  44961-3 0  5637",
           "2 37820  42.7687 147.7173 0010686 283.6368 148.1694 15.73279710179072"]
    function.satellite = EarthSatellite(*tle[1:3], name=tle[0])

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    function.plotSatPosEarth, = plt.plot([1, 0], [1, 0])
    function.plotSatPosHorizon, = plt.plot([1, 0], [1, 0])
    function.plotSatPosSphere1, = ax.plot([1], [1], [1])
    function.plotSatPosSphere2, = ax.plot([1], [1], [1])

    now = function.app.mount.obsSite.ts.now()
    observe = function.satellite.at(now)
    subpoint = observe.subpoint()
    difference = function.satellite - function.app.mount.obsSite.location
    altaz = difference.at(now).altaz()

    with mock.patch.object(function.plotSatPosSphere1,
                           'set_data_3d'):
        with mock.patch.object(function.plotSatPosSphere2,
                               'set_data_3d'):
            with mock.patch.object(function.plotSatPosEarth,
                                   'set_data'):
                with mock.patch.object(function.plotSatPosHorizon,
                                       'set_data'):
                    suc = function.updatePositions(observe=observe,
                                                   subpoint=subpoint,
                                                   altaz=altaz)
                    assert suc


def test_makeCubeLimits_1(function):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    function.makeCubeLimits(ax)


def test_makeCubeLimits_2(function):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    function.makeCubeLimits(ax, hw=(1, 2, 3))


def test_makeCubeLimits_3(function):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    function.makeCubeLimits(ax, hw=3)


def test_drawSphere1_1(function):
    function.drawSphere1()


def test_drawSphere2_1(function):
    function.app.mount.obsSite.location.latitude = Angle(degrees=45)
    function.app.mount.obsSite.location.longitude = Angle(degrees=45)
    function.drawSphere2()


def test_drawEarth_1(function):
    function.drawEarth(function.app.mount.obsSite)


def test_staticHorizon_1(function):
    function.app.data.horizonP = []
    axe, _ = function.generateFlat(widget=function.satHorizonMat, horizon=False)
    suc = function.staticHorizon(axe)
    assert not suc


def test_staticHorizon_2(function):
    axe, _ = function.generateFlat(widget=function.satHorizonMat, horizon=False)
    function.app.data.horizonP = [(0, 0), (0, 360)]
    suc = function.staticHorizon(axe)
    assert suc


def test_drawHorizonView_1(function):
    function.drawHorizonView()


def test_drawSatellite_1(function):
    with mock.patch.object(function,
                           'drawSphere1'):
        with mock.patch.object(function,
                               'drawSphere2'):
            with mock.patch.object(function,
                                   'drawEarth'):
                with mock.patch.object(function,
                                       'drawHorizonView'):
                    suc = function.drawSatellite()
                    assert not suc


def test_drawSatellite_2(function, module):
    tle = ["TIANGONG 1",
           "1 37820U 11053A   14314.79851609  .00064249  00000-0  44961-3 0  5637",
           "2 37820  42.7687 147.7173 0010686 283.6368 148.1694 15.73279710179072"]
    satellite = EarthSatellite(*tle[1:3], name=tle[0])

    tt = module.now().tt

    t0 = module.tt_jd(tt + 0)
    t1 = module.tt_jd(tt + 0.1)
    t2 = module.tt_jd(tt + 0.2)
    t3 = module.tt_jd(tt + 0.3)

    satOrbits = [{'rise': t0,
                  'settle': t1},
                 {'rise': t2,
                  'settle': t3}
                 ]

    with mock.patch.object(function,
                           'drawSphere1'):
        with mock.patch.object(function,
                               'drawSphere2'):
            with mock.patch.object(function,
                                   'drawEarth'):
                with mock.patch.object(function,
                                       'drawHorizonView'):
                    suc = function.drawSatellite(satellite=satellite, satOrbits=satOrbits)
                    assert suc


def test_drawSatellite_3(function, module):
    tle = ["TIANGONG 1",
           "1 37820U 11053A   14314.79851609  .00064249  00000-0  44961-3 0  5637",
           "2 37820  42.7687 147.7173 0010686 283.6368 148.1694 00.03279710179072"]
    satellite = EarthSatellite(*tle[1:3], name=tle[0])

    tt = module.now().tt

    t0 = module.tt_jd(tt + 0)
    t1 = module.tt_jd(tt + 0.1)
    t2 = module.tt_jd(tt + 0.2)
    t3 = module.tt_jd(tt + 0.3)
    t4 = module.tt_jd(tt + 0.4)

    satOrbits = [{'rise': t0,
                  'flip': t0,
                  'settle': t1},
                 {'rise': t2,
                  'flip': t2,
                  'settle': t3},
                 {'rise': t3,
                  'flip': t3,
                  'settle': t4},
                 ]

    suc = function.drawSatellite(satellite=satellite, satOrbits=satOrbits)
    assert suc


def test_drawSatellite_4(function, module):
    tle = ["TIANGONG 1",
           "1 37820U 11053A   14314.79851609  .00064249  00000-0  44961-3 0  5637",
           "2 37820  42.7687 147.7173 0010686 283.6368 148.1694 00.03279710179072"]
    satellite = EarthSatellite(*tle[1:3], name=tle[0])

    tt = module.now().tt

    t1 = module.tt_jd(tt + 0.1)
    t2 = module.tt_jd(tt + 0.2)
    t3 = module.tt_jd(tt + 0.3)
    t4 = module.tt_jd(tt + 0.4)

    satOrbits = [{
                  'flip': t1,
                  'settle': t1},
                 {'rise': t2,
                  'flip': t2,
                  'settle': t3},
                 {'rise': t3,
                  'flip': t3,
                  'settle': t4},
                 ]

    suc = function.drawSatellite(satellite=satellite, satOrbits=satOrbits)
    assert suc


def test_drawSatellite_5(function, module):
    tle = ["TIANGONG 1",
           "1 37820U 11053A   14314.79851609  .00064249  00000-0  44961-3 0  5637",
           "2 37820  42.7687 147.7173 0010686 283.6368 148.1694 00.03279710179072"]
    satellite = EarthSatellite(*tle[1:3], name=tle[0])

    tt = module.now().tt

    t0 = module.tt_jd(tt + 0)
    t1 = module.tt_jd(tt + 0.1)
    t2 = module.tt_jd(tt + 0.2)
    t3 = module.tt_jd(tt + 0.3)
    t4 = module.tt_jd(tt + 0.4)

    satOrbits = [{'rise': t0,
                  'flip': t1,
                  },
                 {'rise': t2,
                  'flip': t2,
                  'settle': t3},
                 {'rise': t3,
                  'flip': t3,
                  'settle': t4},
                 ]

    suc = function.drawSatellite(satellite=satellite, satOrbits=satOrbits)
    assert suc
