############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import pickle
import unittest.mock as mock

import pyqtgraph as pg
import pytest
from gui.extWindows.satelliteW import SatelliteWindow
from gui.utilities.toolsQtWidget import MWidget

# external packages
from PySide6.QtGui import QCloseEvent
from skyfield.api import Angle, EarthSatellite

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(scope="module")
def function(qapp):
    with mock.patch.object(pickle, "load"):
        func = SatelliteWindow(app=App())
        yield func
        func.app.threadPool.waitForDone(10000)


def test_initConfig_1(function):
    function.initConfig()


def test_storeConfig_1(function):
    if "satelliteW" in function.app.config:
        del function.app.config["satelliteW"]

    function.storeConfig()


def test_storeConfig_2(function):
    function.app.config["satelliteW"] = {}

    function.storeConfig()


def test_closeEvent_1(function):
    function.app.mount.signals.pointDone.connect(function.updatePointerAltAz)
    function.app.colorChange.connect(function.colorChange)
    with mock.patch.object(function, "show"):
        with mock.patch.object(MWidget, "closeEvent"):
            function.closeEvent(QCloseEvent)


def test_showWindow(function):
    with mock.patch.object(MWidget, "show"):
        function.showWindow()


def test_colorChange(function):
    with mock.patch.object(function, "drawSatellite"):
        function.colorChange()


def test_updatePointerAltAz_1(function):
    function.pointerAltAz = None
    function.updatePointerAltAz()


def test_updatePointerAltAz_2(function):
    function.pointerAltAz = pg.PlotDataItem()
    function.app.mount.obsSite.Alt = Angle(degrees=80)
    function.app.mount.obsSite.Az = None
    function.updatePointerAltAz()


def test_updatePointerAltAz_3(function):
    function.pointerAltAz = pg.PlotDataItem()
    function.app.mount.obsSite.Alt = None
    function.app.mount.obsSite.Az = Angle(degrees=80)
    function.updatePointerAltAz()


def test_updatePointerAltAz_4(function):
    function.pointerAltAz = pg.PlotDataItem()
    function.app.mount.obsSite.Alt = Angle(degrees=80)
    function.app.mount.obsSite.Az = Angle(degrees=80)
    function.updatePointerAltAz()


def test_updatePositions_3(function):
    function.updatePositions("t", "loc")


def test_updatePositions_4(function):
    function.satellite = 1
    function.updatePositions("t", "loc")


def test_updatePositions_5(function):
    function.satellite = 1
    function.plotSatPosEarth = 1

    function.updatePositions("t", "loc")


def test_updatePositions_6(function):
    tle = [
        "CALSPHERE 1",
        "1 00900U 64063C   21307.74429300  .00000461  00000-0  48370-3 0  9996",
        "2 00900  90.1716  36.8626 0025754 343.8320 164.5583 13.73613883839670",
    ]
    ts = function.app.mount.obsSite.ts
    now = ts.tt_jd(2459523.2430)
    function.satellite = EarthSatellite(*tle[1:3], name=tle[0])

    function.plotSatPosEarth = pg.PlotDataItem(x=[1, 0], y=[1, 0])
    function.plotSatPosHorizon = pg.PlotDataItem(x=[1, 0], y=[1, 0])
    location = function.app.mount.obsSite.location
    with mock.patch.object(function.plotSatPosEarth, "setData"):
        with mock.patch.object(function.plotSatPosHorizon, "setData"):
            function.updatePositions(now, location)


def test_updatePositions_7(function):
    tle = [
        "CALSPHERE 1",
        "1 00900U 64063C   21307.74429300  .00000461  00000-0  48370-3 0  9996",
        "2 00900  90.1716  36.8626 0025754 343.8320 164.5583 13.73613883839670",
    ]
    ts = function.app.mount.obsSite.ts
    now = ts.tt_jd(2459523.2430)

    function.satellite = EarthSatellite(*tle[1:3], name=tle[0])

    function.plotSatPosEarth = pg.PlotDataItem(x=[1, 0], y=[1, 0])
    function.plotSatPosHorizon = pg.PlotDataItem(x=[1, 0], y=[1, 0])
    location = function.app.mount.obsSite.location
    with mock.patch.object(function.plotSatPosEarth, "setData"):
        with mock.patch.object(function.plotSatPosHorizon, "setData"):
            function.updatePositions(now, location)


def test_unlinkWrap(function):
    data = [1, 2, 3, 170, 180, -180, -100, 3, 4]
    for slc in function.unlinkWrap(data):
        a = slc


def test_prepareEarth(function):
    function.prepareEarth(pg.PlotItem())


def test_drawShoreLine(function):
    function.world = {"1": {"xDeg": [0], "yDeg": [0]}}
    function.drawShoreLine(pg.PlotItem())


def test_drawPosition(function):
    function.drawPosition(pg.PlotItem())


def test_prepareSatellite(function):
    function.prepareSatellite([], [])


def test_prepareEarthSatellite(function):
    function.prepareEarthSatellite(pg.PlotItem())


def test_drawEarthTrajectory_1(function):
    tle = [
        "CALSPHERE 1",
        "1 00900U 64063C   22026.93541167  .00000330  00000+0  34283-3 0  9994",
        "2 00900  90.1667  38.3458 0029262  87.9699 341.0031 13.73667773851231",
    ]
    function.satellite = EarthSatellite(*tle[1:3], name=tle[0])
    ts = function.app.mount.obsSite.ts
    tt = 2459610
    t0 = ts.tt_jd(tt + 0)
    t1 = ts.tt_jd(tt + 0.1)
    t2 = ts.tt_jd(tt + 0.2)
    t3 = ts.tt_jd(tt + 0.3)
    t4 = ts.tt_jd(tt + 0.4)

    satOrbits = [
        {"rise": t0, "flip": t0, "culminate": t0, "settle": t1},
        {"rise": t2, "culminate": t2, "settle": t3},
        {"rise": t3, "culminate": t3, "flip": t3, "settle": t4},
    ]
    function.satOrbits = satOrbits
    function.drawEarthTrajectory(pg.PlotItem())


def test_drawEarth_1(function):
    with mock.patch.object(function, "prepareEarthSatellite"):
        with mock.patch.object(function, "drawEarthTrajectory"):
            function.drawEarth()


def test_prepareHorizon(function):
    function.prepareHorizon(pg.PlotItem())


def test_prepareHorizonSatellite(function):
    function.prepareHorizonSatellite(pg.PlotItem())


def test_preparePointer(function):
    function.preparePointer(pg.PlotItem())


def test_drawHorizonTrajectory_1(function):
    tle = [
        "CALSPHERE 1",
        "1 00900U 64063C   22026.93541167  .00000330  00000+0  34283-3 0  9994",
        "2 00900  90.1667  38.3458 0029262  87.9699 341.0031 13.73667773851231",
    ]
    function.satellite = EarthSatellite(*tle[1:3], name=tle[0])
    tt = 2459610
    ts = function.app.mount.obsSite.ts
    t0 = ts.tt_jd(tt + 0)
    t1 = ts.tt_jd(tt + 0.1)
    t2 = ts.tt_jd(tt + 0.2)
    t3 = ts.tt_jd(tt + 0.3)
    t4 = ts.tt_jd(tt + 0.4)

    satOrbits = [
        {"rise": t0, "flip": t0, "culminate": t0, "settle": t1},
        {"rise": t2, "culminate": t2, "settle": t3},
        {"rise": t3, "culminate": t3, "flip": t3, "settle": t4},
    ]
    function.satOrbits = satOrbits
    function.drawHorizonTrajectory(pg.PlotItem(), [], [])


def test_drawHorizon(function):
    function.drawHorizon()


def test_drawHorizonView_1(function):
    with mock.patch.object(function, "prepareHorizon"):
        with mock.patch.object(function, "drawHorizonTrajectory"):
            with mock.patch.object(function, "prepareHorizonSatellite"):
                with mock.patch.object(function, "preparePointer"):
                    with mock.patch.object(function, "drawHorizon"):
                        function.drawHorizonView(1, 1)


def test_drawSatellite_1(function):
    with mock.patch.object(function, "drawEarth"):
        with mock.patch.object(function, "drawHorizonView"):
            function.drawSatellite(1, None, 1, 1, "")


def test_drawSatellite_2(function):
    with mock.patch.object(function, "drawEarth"):
        with mock.patch.object(function, "drawHorizonView"):
            function.drawSatellite(1, [1], 1, 1, "")
