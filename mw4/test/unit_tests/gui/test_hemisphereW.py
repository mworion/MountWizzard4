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
# Python  v3.7.5
#
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock
import pytest

# external packages
from skyfield.toposlib import Topos
from skyfield.api import Angle
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QThreadPool
from PyQt5.QtWidgets import QDoubleSpinBox
from PyQt5.QtWidgets import QCheckBox
from mountcontrol.qtmount import Mount
import matplotlib
import PyQt5
import mountcontrol

# local import
from mw4.gui.hemisphereW import HemisphereWindow
from mw4.imaging.camera import Camera
from mw4.dome.dome import Dome
from mw4.modeldata.buildpoints import DataPoint
from mw4.modeldata.hipparcos import Hipparcos
from mw4.astrometry.astrometry import Astrometry


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown(qtbot):
    global app

    class Test2(QObject):
        threadPool = QThreadPool()
        update1s = pyqtSignal()

        mount = Mount(expire=False, verbose=False, pathToData='mw4/test/data')
        mount.obsSite.location = Topos(latitude_degrees=20,
                                       longitude_degrees=10,
                                       elevation_m=500)

    class Test1a:
        checkDomeGeometry = QCheckBox()

    class Test1:
        deviceStat = {'dome': True}
        ui = Test1a()

    class Test(QObject):
        config = {'mainW': {},
                  'showHemisphereW': True}
        uiWindows = {'showImageW': {}}
        mwGlob = {'imageDir': 'mw4/test/image'}

        update1s = pyqtSignal()
        update10s = pyqtSignal()
        update0_1s = pyqtSignal()
        redrawHemisphere = pyqtSignal()
        message = pyqtSignal(str, int)

        mount = Mount(expire=False, verbose=False, pathToData='mw4/test/data')
        mount.obsSite.Alt = Angle(degrees=45)
        mount.obsSite.Az = Angle(degrees=45)

        camera = Camera(app=Test2())
        dome = Dome(app=Test2())
        astrometry = Astrometry(app=Test2())
        data = DataPoint(app=Test2(), configDir='mw4/test/config')
        hipparcos = Hipparcos(app=Test2())
        mainW = Test1()

    with mock.patch.object(HemisphereWindow,
                           'show'):
        app = HemisphereWindow(app=Test())

    qtbot.addWidget(app)

    yield

    del app


def test_initConfig_1():
    suc = app.initConfig()
    assert suc


def test_initConfig_3():
    app.app.config['hemisphereW']['winPosX'] = 10000
    app.app.config['hemisphereW']['winPosY'] = 10000
    suc = app.initConfig()
    assert suc


def test_storeConfig_1():
    app.storeConfig()


def test_resizeEvent_1():
    pass


def test_resizeTimer_1():
    pass


def test_setupAxes1(qtbot):
    app.drawHemisphere()
    val = app.setupAxes()
    assert val is None


def test_setupAxes2(qtbot):
    app.drawHemisphere()
    val = app.setupAxes(app.hemisphereMat)
    assert val


def test_drawBlit_1():
    pass


def test_drawBlitStars_1():
    pass


def test_updateCelestialPath_1(qtbot):
    app.drawHemisphere()
    suc = app.updateCelestialPath()
    assert not suc


def test_updateCelestialPath_3(qtbot):
    app.drawHemisphere()
    app.celestialPath = None
    suc = app.updateCelestialPath()
    assert not suc


def test_updateMeridian_1(qtbot):
    app.drawHemisphere()
    app.app.mount.setting.meridianLimitSlew = 3
    app.app.mount.setting.meridianLimitTrack = 3
    suc = app.updateMeridian(app.app.mount.setting)
    assert suc


def test_updateMeridian_3(qtbot):
    app.drawHemisphere()
    app.app.mount.setting.meridianLimitSlew = None
    app.app.mount.setting.meridianLimitTrack = 3
    suc = app.updateMeridian(app.app.mount.setting)
    assert not suc


def test_updateMeridian_4(qtbot):
    app.drawHemisphere()
    app.app.mount.setting.meridianLimitSlew = 3
    app.app.mount.setting.meridianLimitTrack = None
    suc = app.updateMeridian(app.app.mount.setting)
    assert not suc


def test_updateMeridian_5(qtbot):
    app.drawHemisphere()
    app.app.mount.setting.meridianLimitSlew = 3
    app.app.mount.setting.meridianLimitTrack = 3
    app.meridianTrack = None
    suc = app.updateMeridian(app.app.mount.setting)
    assert not suc


def test_updateMeridian_6(qtbot):
    app.drawHemisphere()
    app.app.mount.setting.meridianLimitSlew = 3
    app.app.mount.setting.meridianLimitTrack = 3
    app.meridianSlew = None
    suc = app.updateMeridian(app.app.mount.setting)
    assert not suc


def test_updateHorizonLimits_1(qtbot):
    app.drawHemisphere()
    app.app.mount.setting.horizonLimitHigh = 80
    app.app.mount.setting.horizonLimitLow = 10
    suc = app.updateHorizonLimits(app.app.mount.setting)
    assert suc


def test_updateHorizonLimits_3(qtbot):
    app.drawHemisphere()
    app.app.mount.setting.horizonLimitHigh = None
    app.app.mount.setting.horizonLimitLow = 10
    suc = app.updateHorizonLimits(app.app.mount.setting)
    assert not suc


def test_updateHorizonLimits_4(qtbot):
    app.drawHemisphere()
    app.app.mount.setting.horizonLimitHigh = 80
    app.app.mount.setting.horizonLimitLow = None
    suc = app.updateHorizonLimits(app.app.mount.setting)
    assert not suc


def test_updateHorizonLimits_5(qtbot):
    app.drawHemisphere()
    app.app.mount.setting.horizonLimitHigh = 80
    app.app.mount.setting.horizonLimitLow = 10
    app.horizonLimitLow = None
    suc = app.updateHorizonLimits(app.app.mount.setting)
    assert not suc


def test_updateHorizonLimits_6(qtbot):
    app.drawHemisphere()
    app.app.mount.setting.horizonLimitHigh = 80
    app.app.mount.setting.horizonLimitLow = 10
    app.horizonLimitHigh = None
    suc = app.updateHorizonLimits(app.app.mount.setting)
    assert not suc


def test_updateSettings_1():
    pass


def test_updatePointerAltAz_1(qtbot):
    app.drawHemisphere()
    app.app.mount.obsSite.Alt = Angle(degrees=5)
    app.app.mount.obsSite.Az = Angle(degrees=5)
    suc = app.updatePointerAltAz()
    assert suc


def test_updatePointerAltAz_3(qtbot):
    app.drawHemisphere()
    app.app.mount.obsSite.Az = None
    suc = app.updatePointerAltAz()
    assert not suc


def test_updatePointerAltAz_4(qtbot):
    app.drawHemisphere()
    app.app.mount.obsSite.Alt = None
    suc = app.updatePointerAltAz()
    assert not suc


def test_updatePointerAltAz_5(qtbot):
    app.drawHemisphere()
    app.app.mount.obsSite.Alt = Angle(degrees=5)
    app.app.mount.obsSite.Az = Angle(degrees=5)
    app.pointerAltAz = None
    suc = app.updatePointerAltAz()
    assert not suc


def test_updateDome_1(qtbot):
    app.drawHemisphere()
    app.app.dome.data = {}
    suc = app.updateDome(45)
    assert suc


def test_updateDome_2(qtbot):
    app.drawHemisphere()
    app.app.dome.data = {}
    suc = app.updateDome(None)
    assert not suc


def test_updateDome_3(qtbot):
    app.drawHemisphere()
    app.app.dome.data = {}
    suc = app.updateDome(45)
    assert suc


def test_updateDome_4(qtbot):
    app.drawHemisphere()
    app.app.dome.data['DOME_ABSOLUTE_POSITION'] = 90
    app.pointerDome = None
    suc = app.updateDome(45)
    assert not suc


def test_updateAlignStar_1(qtbot):
    app.drawHemisphere()
    app.ui.checkShowAlignStar.setChecked(True)
    suc = app.updateAlignStar()
    assert suc


def test_updateAlignStar_3(qtbot):
    app.drawHemisphere()
    app.ui.checkShowAlignStar.setChecked(True)
    app.starsAlign = None
    suc = app.updateAlignStar()
    assert not suc


def test_updateAlignStar_4(qtbot):
    app.drawHemisphere()
    app.ui.checkShowAlignStar.setChecked(True)
    app.starsAlignAnnotate = None
    suc = app.updateAlignStar()
    assert not suc


def test_updateAlignStar_5(qtbot):
    app.drawHemisphere()
    app.ui.checkShowAlignStar.setChecked(False)
    suc = app.updateAlignStar()
    assert not suc


def test_clearHemisphere(qtbot):
    app.app.data.buildP = [(0, 0), (1, 0)]
    app.clearHemisphere()
    assert app.app.data.buildP == []


def test_staticHorizon_1():
    pass


def test_staticModelData_1():
    pass


def staticCelestialEquator_1():
    pass


def test_staticMeridianLimits_1():
    pass


def test_staticHorizonLimits_1():
    pass


def test_drawHemisphereStatic_1():
    pass


def test_drawHemisphereMoving_1():
    pass


def test_drawAlignmentStars_1():
    pass


def test_drawHemisphere_1():
    class Test:
        def set_marker(self, test):
            pass

        def set_color(self, test):
            pass

    app.horizonMarker = Test()
    app.drawHemisphere()
