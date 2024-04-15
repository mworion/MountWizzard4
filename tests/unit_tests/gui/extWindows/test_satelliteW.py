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
# written in python3, (c) 2019-2023 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
import unittest.mock as mock
import pickle

# external packages
from PyQt5.QtGui import QCloseEvent
from skyfield.api import EarthSatellite
from skyfield.api import Angle
import pyqtgraph as pg

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.utilities.toolsQtWidget import MWidget
from gui.extWindows.satelliteW import SatelliteWindow


@pytest.fixture(scope='module')
def function(qapp):
    with mock.patch.object(pickle,
                           'load'):
        func = SatelliteWindow(app=App())
        yield func
        del func


def test_initConfig_1(function):
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
    function.app.mount.signals.pointDone.connect(function.updatePointerAltAz)
    function.app.colorChange.connect(function.colorChange)
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


def test_colorChange(function):
    with mock.patch.object(function,
                           'drawSatellite'):
        suc = function.colorChange()
        assert suc

        
def test_updatePointerAltAz_1(function):
    function.pointerAltAz = None
    suc = function.updatePointerAltAz(function.app.mount.obsSite)
    assert not suc


def test_updatePointerAltAz_2(function):
    function.pointerAltAz = pg.PlotDataItem()
    function.app.mount.obsSite.Alt = Angle(degrees=80)
    function.app.mount.obsSite.Az = None
    suc = function.updatePointerAltAz(function.app.mount.obsSite)
    assert not suc


def test_updatePointerAltAz_3(function):
    function.pointerAltAz = pg.PlotDataItem()
    function.app.mount.obsSite.Alt = None
    function.app.mount.obsSite.Az = Angle(degrees=80)
    suc = function.updatePointerAltAz(function.app.mount.obsSite)
    assert not suc


def test_updatePointerAltAz_4(function):
    function.pointerAltAz = pg.PlotDataItem()
    function.app.mount.obsSite.Alt = Angle(degrees=80)
    function.app.mount.obsSite.Az = Angle(degrees=80)
    suc = function.updatePointerAltAz(function.app.mount.obsSite)
    assert suc


def test_updatePositions_1(function):
    suc = function.updatePositions()
    assert not suc


def test_updatePositions_2(function):
    suc = function.updatePositions(now='t')
    assert not suc


def test_updatePositions_3(function):
    suc = function.updatePositions(now='t', location='loc')
    assert not suc


def test_updatePositions_4(function):
    function.satellite = 1
    suc = function.updatePositions(now='t', location='loc')
    assert not suc


def test_updatePositions_5(function):
    function.satellite = 1
    function.plotSatPosEarth = 1

    suc = function.updatePositions(now='t', location='loc')
    assert not suc


def test_updatePositions_6(function):
    tle = ["CALSPHERE 1",
           "1 00900U 64063C   21307.74429300  .00000461  00000-0  48370-3 0  9996",
           "2 00900  90.1716  36.8626 0025754 343.8320 164.5583 13.73613883839670"]
    ts = function.app.mount.obsSite.ts
    now = ts.tt_jd(2459523.2430)
    function.satellite = EarthSatellite(*tle[1:3], name=tle[0])

    function.plotSatPosEarth = pg.PlotDataItem(x=[1, 0], y=[1, 0])
    function.plotSatPosHorizon = pg.PlotDataItem(x=[1, 0], y=[1, 0])
    location = function.app.mount.obsSite.location
    with mock.patch.object(function.plotSatPosEarth,
                           'setData'):
        with mock.patch.object(function.plotSatPosHorizon,
                               'setData'):
            suc = function.updatePositions(now=now, location=location)
            assert suc


def test_updatePositions_7(function):
    tle = ["CALSPHERE 1",
           "1 00900U 64063C   21307.74429300  .00000461  00000-0  48370-3 0  9996",
           "2 00900  90.1716  36.8626 0025754 343.8320 164.5583 13.73613883839670"]
    ts = function.app.mount.obsSite.ts
    now = ts.tt_jd(2459523.2430)

    function.satellite = EarthSatellite(*tle[1:3], name=tle[0])

    function.plotSatPosEarth = pg.PlotDataItem(x=[1, 0], y=[1, 0])
    function.plotSatPosHorizon = pg.PlotDataItem(x=[1, 0], y=[1, 0])
    location = function.app.mount.obsSite.location
    with mock.patch.object(function.plotSatPosEarth,
                           'setData'):
        with mock.patch.object(function.plotSatPosHorizon,
                               'setData'):
            suc = function.updatePositions(now=now, location=location)
            assert suc


def test_unlinkWrap_1(function):
    data = [1, 2, 3, 170, 180, -180, -100, 3, 4]
    for slc in function.unlinkWrap(data):
        a = slc


def test_unlinkWrap_2(function):
    data = None
    for slc in function.unlinkWrap(data):
        a = slc


def test_unlinkWrap_3(function):
    data = []
    for slc in function.unlinkWrap(data):
        a = slc


def test_prepareEarth(function):
    suc = function.prepareEarth(pg.PlotItem())
    assert suc


def test_drawShoreLine(function):
    function.world = {'1': {'xDeg': [0], 'yDeg': [0]}}
    suc = function.drawShoreLine(pg.PlotItem())
    assert suc


def test_drawEarth_0(function):
    suc = function.drawEarth()
    assert not suc


def test_drawEarth_1(function):
    function.app.mount.obsSite.location.latitude = Angle(degrees=45)
    function.app.mount.obsSite.location.longitude = Angle(degrees=11)
    obsSite = function.app.mount.obsSite
    suc = function.drawEarth(obsSite=obsSite)
    assert not suc


def test_drawEarth_2(function):
    tle = ["CALSPHERE 1",
           "1 00900U 64063C   22026.93541167  .00000330  00000+0  34283-3 0  9994",
           "2 00900  90.1667  38.3458 0029262  87.9699 341.0031 13.73667773851231"]
    function.satellite = EarthSatellite(*tle[1:3], name=tle[0])
    ts = function.app.mount.obsSite.ts
    tt = 2459610
    t0 = ts.tt_jd(tt + 0)
    t1 = ts.tt_jd(tt + 0.1)
    t2 = ts.tt_jd(tt + 0.2)
    t3 = ts.tt_jd(tt + 0.3)
    t4 = ts.tt_jd(tt + 0.4)

    satOrbits = [{'rise': t0,
                  'flip': t0,
                  'culminate': t0,
                  'settle': t1},
                 {'rise': t2,
                  'flip': t2,
                  'culminate': t2,
                  'settle': t3},
                 {'rise': t3,
                  'culminate': t3,
                  'flip': t3,
                  'settle': t4},
                 ]
    function.app.mount.obsSite.location.latitude = Angle(degrees=45)
    function.app.mount.obsSite.location.longitude = Angle(degrees=11)
    obsSite = function.app.mount.obsSite
    suc = function.drawEarth(obsSite=obsSite, satOrbits=satOrbits)
    assert suc


def test_drawEarth_3(function):
    tle = ["CALSPHERE 1",
           "1 00900U 64063C   22026.93541167  .00000330  00000+0  34283-3 0  9994",
           "2 00900  90.1667  38.3458 0029262  87.9699 341.0031 13.73667773851231"]
    function.satellite = EarthSatellite(*tle[1:3], name=tle[0])
    ts = function.app.mount.obsSite.ts
    tt = 2459610
    t0 = ts.tt_jd(tt + 0)
    t1 = ts.tt_jd(tt + 0.1)
    t2 = ts.tt_jd(tt + 0.2)
    t3 = ts.tt_jd(tt + 0.3)
    t4 = ts.tt_jd(tt + 0.4)

    satOrbits = [{'rise': t0,
                  'flip': t0,
                  'culminate': t0,
                  'settle': t1},
                 {'rise': t2,
                  'culminate': t2,
                  'settle': t3},
                 {'rise': t3,
                  'culminate': t3,
                  'flip': t3,
                  'settle': t4},
                 ]
    function.app.mount.obsSite.location.latitude = Angle(degrees=45)
    function.app.mount.obsSite.location.longitude = Angle(degrees=11)
    obsSite = function.app.mount.obsSite
    suc = function.drawEarth(obsSite=obsSite, satOrbits=satOrbits)
    assert suc


def test_drawHorizonView_2(function):
    tle = ["CALSPHERE 1",
           "1 00900U 64063C   22026.93541167  .00000330  00000+0  34283-3 0  9994",
           "2 00900  90.1667  38.3458 0029262  87.9699 341.0031 13.73667773851231"]
    function.satellite = EarthSatellite(*tle[1:3], name=tle[0])
    tt = 2459610
    ts = function.app.mount.obsSite.ts
    t0 = ts.tt_jd(tt + 0)
    t1 = ts.tt_jd(tt + 0.1)
    t2 = ts.tt_jd(tt + 0.2)
    t3 = ts.tt_jd(tt + 0.3)
    t4 = ts.tt_jd(tt + 0.4)

    satOrbits = [{'rise': t0,
                  'flip': t0,
                  'culminate': t0,
                  'settle': t1},
                 {'rise': t2,
                  'flip': t2,
                  'culminate': t2,
                  'settle': t3},
                 {'rise': t3,
                  'culminate': t3,
                  'flip': t3,
                  'settle': t4},
                 ]
    function.app.mount.obsSite.location.latitude = Angle(degrees=45)
    function.app.mount.obsSite.location.longitude = Angle(degrees=11)
    obsSite = function.app.mount.obsSite
    suc = function.drawHorizonView(obsSite=obsSite, satOrbits=satOrbits,
                                   altitude=[], azimuth=[])
    assert suc


def test_drawHorizonView_3(function):
    tle = ["CALSPHERE 1",
           "1 00900U 64063C   22026.93541167  .00000330  00000+0  34283-3 0  9994",
           "2 00900  90.1667  38.3458 0029262  87.9699 341.0031 13.73667773851231"]
    function.satellite = EarthSatellite(*tle[1:3], name=tle[0])
    tt = 2459610
    ts = function.app.mount.obsSite.ts
    t0 = ts.tt_jd(tt + 0)
    t1 = ts.tt_jd(tt + 0.1)
    t2 = ts.tt_jd(tt + 0.2)
    t3 = ts.tt_jd(tt + 0.3)
    t4 = ts.tt_jd(tt + 0.4)

    satOrbits = [{'rise': t0,
                  'flip': t0,
                  'culminate': t0,
                  'settle': t1},
                 {'rise': t2,
                  'culminate': t2,
                  'settle': t3},
                 {'rise': t3,
                  'culminate': t3,
                  'flip': t3,
                  'settle': t4},
                 ]
    function.app.mount.obsSite.location.latitude = Angle(degrees=45)
    function.app.mount.obsSite.location.longitude = Angle(degrees=11)
    obsSite = function.app.mount.obsSite
    suc = function.drawHorizonView(obsSite=obsSite, satOrbits=satOrbits,
                                   altitude=[], azimuth=[])
    assert suc


def test_drawSatellite_1(function):
    with mock.patch.object(function,
                           'drawEarth'):
        suc = function.drawSatellite()
        assert not suc


def test_drawSatellite_2(function):
    tle = ["ISS (ZARYA)",
           "1 25544U 98067A   21103.51063550  .00000247  00000-0  12689-4 0  9995",
           "2 25544  51.6440 302.6231 0002845 223.0251 174.3348 15.48881931278570"]
    satellite = EarthSatellite(*tle[1:3], name=tle[0])
    tt = 2459610
    ts = function.app.mount.obsSite.ts
    t0 = ts.tt_jd(tt + 0)
    t1 = ts.tt_jd(tt + 0.1)
    t2 = ts.tt_jd(tt + 0.2)
    t3 = ts.tt_jd(tt + 0.3)
    t4 = ts.tt_jd(tt + 0.4)

    satOrbits = [{'rise': t0,
                  'flip': t0,
                  'culminate': t0,
                  'settle': t1},
                 {'rise': t2,
                  'flip': t2,
                  'culminate': t2,
                  'settle': t3},
                 {'rise': t3,
                  'culminate': t3,
                  'flip': t3,
                  'settle': t4},
                 ]
    with mock.patch.object(function,
                           'drawEarth'):
        with mock.patch.object(function,
                               'drawHorizonView'):
            suc = function.drawSatellite(satellite=satellite,
                                         satOrbits=satOrbits)
            assert suc


def test_drawSatellite_3(function):
    tle = ["METEOSAT-10 (MSG-3)",
           "1 38552U 12035B   22026.87212005  .00000071  00000+0  00000+0 0  9997",
           "2 38552   1.3428  31.3751 0000057 333.5373  84.7153  1.00279964 34791"]

    satellite = EarthSatellite(*tle[1:3], name=tle[0])
    tt = 2459610
    ts = function.app.mount.obsSite.ts
    t0 = ts.tt_jd(tt + 0)
    t1 = ts.tt_jd(tt + 0.1)
    t2 = ts.tt_jd(tt + 0.2)
    t3 = ts.tt_jd(tt + 0.3)
    t4 = ts.tt_jd(tt + 0.4)

    satOrbits = [{'rise': t0,
                  'flip': t0,
                  'culminate': t0,
                  'settle': t1},
                 {'rise': t2,
                  'flip': t2,
                  'culminate': t2,
                  'settle': t3},
                 {'rise': t3,
                  'culminate': t3,
                  'flip': t3,
                  'settle': t4},
                 ]
    with mock.patch.object(function,
                           'drawEarth'):
        with mock.patch.object(function,
                               'drawHorizonView'):
            suc = function.drawSatellite(satellite=satellite,
                                         satOrbits=satOrbits)
            assert suc
