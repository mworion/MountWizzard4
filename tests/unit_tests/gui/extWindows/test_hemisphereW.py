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
import unittest.mock as mock
import pytest

# external packages
from skyfield.toposlib import Topos
from skyfield.api import Angle
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import QEvent
from PyQt5.QtWidgets import QCheckBox
from PyQt5.QtWidgets import QLineEdit
from mountcontrol.qtmount import Mount
import matplotlib.pyplot as plt

# local import
from gui.utilities.widget import MWidget
from gui.extWindows.hemisphereW import HemisphereWindow
from logic.imaging.camera import Camera
from logic.dome.dome import Dome
from logic.modeldata.buildpoints import DataPoint
from logic.modeldata.hipparcos import Hipparcos
from logic.astrometry.astrometry import Astrometry


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown(qtbot):
    global app

    class Test2(QObject):
        threadPool = QThreadPool()
        update1s = pyqtSignal()
        mwGlob = {'configDir': 'tests/config',
                  'tempDir': 'tests/temp'}

        mount = Mount(host='localhost', MAC='00:00:00:00:00:00', verbose=False,
                      pathToData='tests/data')
        mount.obsSite.location = Topos(latitude_degrees=20,
                                       longitude_degrees=10,
                                       elevation_m=500)

    class Test1a:
        checkDomeGeometry = QCheckBox()
        statusDualAxisTracking = QLineEdit()

    class Test1:
        ui = Test1a()

    class Test(QObject):
        config = {'mainW': {},
                  'showHemisphereW': True}
        uiWindows = {'showImageW': {}}
        mwGlob = {'imageDir': 'tests/image'}

        update1s = pyqtSignal()
        update10s = pyqtSignal()
        update0_1s = pyqtSignal()
        redrawHemisphere = pyqtSignal()
        message = pyqtSignal(str, int)

        mount = Mount(host='localhost', MAC='00:00:00:00:00:00', verbose=False,
                      pathToData='tests/data')
        mount.obsSite.Alt = Angle(degrees=45)
        mount.obsSite.Az = Angle(degrees=45)

        camera = Camera(app=Test2())
        dome = Dome(app=Test2())
        astrometry = Astrometry(app=Test2())
        data = DataPoint(app=Test2())
        hipparcos = Hipparcos(app=Test2())
        deviceStat = {'dome': True}
        mainW = Test1()

    with mock.patch.object(HemisphereWindow,
                           'show'):
        app = HemisphereWindow(app=Test())
        qtbot.addWidget(app)

    yield


def test_drawBlit_1():
    suc = app.drawBlit()
    assert suc


def test_drawBlit_2():
    app.mutexDraw.lock()
    suc = app.drawBlit()
    assert not suc


def test_drawBlit_3():
    app.hemisphereBack = None
    suc = app.drawBlit()
    assert suc


def test_drawBlitStars_1():
    suc = app.drawBlitStars()
    assert suc


def test_drawBlitStars_2():
    app.mutexDraw.lock()
    suc = app.drawBlitStars()
    assert not suc


def test_drawBlitStars_3():
    app.hemisphereBackStars = None
    suc = app.drawBlitStars()
    assert suc


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
    with mock.patch.object(app,
                           'updateCelestialPath',
                           return_value=False):
        with mock.patch.object(app,
                               'updateHorizonLimits',
                               return_value=False):
            with mock.patch.object(app,
                                   'updateMeridian',
                                   return_value=False):
                with mock.patch.object(app,
                                       'drawHemisphere'):
                    suc = app.updateSettings()
                    assert not suc


def test_updateSettings_2():
    with mock.patch.object(app,
                           'updateCelestialPath',
                           return_value=True):
        with mock.patch.object(app,
                               'updateHorizonLimits',
                               return_value=False):
            with mock.patch.object(app,
                                   'updateMeridian',
                                   return_value=False):
                with mock.patch.object(app,
                                       'drawHemisphere'):
                    suc = app.updateSettings()
                    assert suc


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
    suc = app.clearHemisphere()
    assert suc
    assert app.app.data.buildP == []


def test_staticHorizon_1():
    app.ui.checkUseHorizon.setChecked(False)
    app.app.data.horizonP = [(0, 0), (40, 100), (0, 360)]
    suc = app.staticHorizon()
    assert not suc


def test_staticHorizon_2():
    app.ui.checkUseHorizon.setChecked(True)
    app.app.data.horizonP = [(0, 0), (40, 100), (0, 360)]
    axes = plt.axes(label=1)
    suc = app.staticHorizon(axes=axes)
    assert suc


def test_staticModelData_1():
    app.app.data.buildP = []
    suc = app.staticModelData()
    assert not suc


def test_staticModelData_2():
    app.ui.checkShowSlewPath.setChecked(False)
    app.app.data.buildP = [(0, 0), (40, 100), (0, 360)]
    axes = plt.axes(label=2)
    suc = app.staticModelData(axes=axes)
    assert suc


def test_staticModelData_3():
    app.ui.checkShowSlewPath.setChecked(True)
    app.app.data.buildP = [(0, 0), (40, 100), (0, 360)]
    axes = plt.axes(label=3)
    suc = app.staticModelData(axes=axes)
    assert suc


def staticCelestialEquator_1():
    app.ui.checkShowCelestial.setChecked(False)
    axes = plt.axes(label=4)
    suc = app.staticCelestialEquator(axes=axes)
    assert suc


def test_staticMeridianLimits_1():
    app.app.mount.setting.meridianLimitSlew = None
    app.app.mount.setting.meridianLimitTrack = None
    app.ui.checkShowMeridian.setChecked(False)
    axes = plt.axes(label=5)
    suc = app.staticMeridianLimits(axes=axes)
    assert suc


def test_staticMeridianLimits_2():
    app.app.mount.setting.meridianLimitSlew = 3
    app.app.mount.setting.meridianLimitTrack = 5
    app.ui.checkShowMeridian.setChecked(True)
    axes = plt.axes(label=6)
    suc = app.staticMeridianLimits(axes=axes)
    assert suc


def test_staticHorizonLimits_1():
    app.app.mount.setting.horizonLimitHigh = None
    app.app.mount.setting.horizonLimitLow = None
    axes = plt.axes(label=7)
    suc = app.staticHorizonLimits(axes=axes)
    assert suc


def test_staticHorizonLimits_2():
    app.app.mount.setting.horizonLimitHigh = 90
    app.app.mount.setting.horizonLimitLow = 10
    axes = plt.axes(label=8)
    suc = app.staticHorizonLimits(axes=axes)
    assert suc


def test_drawHemisphereStatic_1():
    app.mutexDraw.lock()
    axes = plt.axes(label=9)
    suc = app.drawHemisphereStatic(axes=axes)
    assert not suc


def test_drawHemisphereStatic_2():
    axes = plt.axes(label=10)
    suc = app.drawHemisphereStatic(axes=axes)
    assert suc


def test_drawHemisphereMoving_1():
    axes = plt.axes(label=11)
    suc = app.drawHemisphereMoving(axes=axes)
    assert suc


def test_drawAlignmentStars_1():
    axes = plt.axes(label=12)
    suc = app.drawAlignmentStars(axes=axes)
    assert suc


def test_drawHemisphere_1():
    class Test:
        def set_marker(self, test):
            pass

        def set_color(self, test):
            pass

    app.horizonMarker = Test()
    app.drawHemisphere()
