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
from mw4.gui.hemisphereWext import HemisphereWindowExt
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


def test_setupAxes1(qtbot):
    app.drawHemisphere()
    suc = app.setupAxes(app.hemisphereMat)
    assert suc


def test_setupAxes2(qtbot):
    app.drawHemisphere()
    app.setupAxes(app.hemisphereMat)


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


def test_markerPoint():
    val = app.markerPoint()
    assert isinstance(val, matplotlib.path.Path)


def test_markerAltAz():
    val = app.markerAltAz()
    assert isinstance(val, matplotlib.path.Path)


def test_markerStar():
    val = app.markerStar()
    assert isinstance(val, matplotlib.path.Path)


def test_clearHemisphere(qtbot):
    app.app.data.buildP = [(0, 0), (1, 0)]
    app.clearHemisphere()
    assert app.app.data.buildP == []


def test_setOperationMode_1():
    assert app.MODE is not None
    assert 'normal' in app.MODE
    assert 'build' in app.MODE
    assert 'horizon' in app.MODE
    assert 'star' in app.MODE


def test_setOperationMode_2():
    class Test:
        def set_marker(self, test):
            pass

        def set_color(self, test):
            pass

    app.ui.checkEditNone.setChecked(True)
    app.horizonMarker = Test()
    app.pointsBuild = Test()
    suc = app.setOperationMode()
    assert suc


def test_setOperationMode_3():
    class Test:
        def set_marker(self, test):
            pass

        def set_color(self, test):
            pass

    app.ui.checkPolarAlignment.setChecked(True)
    app.horizonMarker = Test()
    app.pointsBuild = Test()
    suc = app.setOperationMode()
    assert suc


def test_setOperationMode_4():
    class Test:
        def set_marker(self, test):
            pass

        def set_color(self, test):
            pass

    app.ui.checkEditBuildPoints.setChecked(True)
    app.horizonMarker = Test()
    app.pointsBuild = Test()
    suc = app.setOperationMode()
    assert suc


def test_setOperationMode_5():
    class Test:
        def set_marker(self, test):
            pass

        def set_color(self, test):
            pass

    app.ui.checkEditHorizonMask.setChecked(True)
    app.horizonMarker = Test()
    app.pointsBuild = Test()
    suc = app.setOperationMode()
    app.ui.checkEditNone.setChecked(True)
    assert suc


def test_getIndexPoint_0():
    class Test:
        pass
    event = Test()
    event.xdata = 180
    event.ydata = 45
    plane = []
    epsilon = 0
    index = app.getIndexPoint(event=event,
                                          plane=plane,
                                          epsilon=epsilon,
                                          )
    assert not index


def test_getIndexPoint_1():
    event = None
    plane = None
    epsilon = 0
    index = app.getIndexPoint(event=event,
                                          plane=plane,
                                          epsilon=epsilon,
                                          )
    assert not index


def test_getIndexPoint_2():
    class Test:
        pass
    event = Test()
    event.xdata = 180
    event.ydata = 45
    plane = None
    epsilon = 0
    index = app.getIndexPoint(event=event,
                                          plane=plane,
                                          epsilon=epsilon,
                                          )
    assert not index


def test_getIndexPoint_3():
    class Test:
        pass
    event = Test()
    event.xdata = 180
    event.ydata = 45
    plane = [(45, 0), (45, 360)]
    epsilon = 0
    index = app.getIndexPoint(event=event,
                                          plane=plane,
                                          epsilon=epsilon,
                                          )
    assert not index


def test_getIndexPoint_4():
    class Test:
        pass
    event = Test()
    event.xdata = 180
    event.ydata = 45
    plane = [(45, 0), (45, 360)]
    epsilon = 200
    index = app.getIndexPoint(event=event,
                                          plane=plane,
                                          epsilon=epsilon,
                                          )
    assert index == 0


def test_getIndexPoint_5():
    class Test:
        pass
    event = Test()
    event.xdata = 182
    event.ydata = 45
    plane = [(45, 0), (45, 360)]
    epsilon = 200
    index = app.getIndexPoint(event=event,
                                          plane=plane,
                                          epsilon=epsilon,
                                          )
    assert index == 1


def test_getIndexPointX_1():
    event = None
    plane = None
    index = app.getIndexPointX(event=event,
                                           plane=plane,
                                           )
    assert not index


def test_getIndexPointX_2():
    class Test:
        pass
    event = Test()
    event.xdata = 182
    event.ydata = 45
    plane = None
    index = app.getIndexPointX(event=event,
                                           plane=plane,
                                           )
    assert not index


def test_getIndexPointX_3():
    class Test:
        pass
    event = Test()
    event.xdata = 180
    event.ydata = 45
    plane = [(45, 0), (45, 360)]
    index = app.getIndexPointX(event=event,
                                           plane=plane,
                                           )
    assert index == 0


def test_getIndexPointX_4():
    class Test:
        pass
    event = Test()
    event.xdata = 182
    event.ydata = 45
    plane = [(45, 0), (45, 360)]
    index = app.getIndexPointX(event=event,
                                           plane=plane,
                                           )
    assert index == 0


def test_getIndexPointX_5():
    class Test:
        pass
    event = Test()
    event.xdata = 182
    event.ydata = 45
    plane = [(45, 0), (45, 180), (45, 360)]
    index = app.getIndexPointX(event=event,
                                           plane=plane,
                                           )
    assert index == 1


def test_getIndexPointX_6():
    class Test:
        pass
    event = Test()
    event.xdata = 182
    event.ydata = 45
    plane = [(45, 0)]
    index = app.getIndexPointX(event=event,
                                           plane=plane,
                                           )
    assert not index


def test_onMouseNormal_1():
    class Test:
        pass
    event = Test()
    event.inaxes = False
    suc = app.onMouseNormal(event=event)
    assert not suc


def test_onMouseNormal_2():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.button = 0
    event.dblclick = False
    suc = app.onMouseNormal(event=event)
    assert not suc


def test_onMouseNormal_3():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.button = 1
    event.dblclick = False
    suc = app.onMouseNormal(event=event)
    assert not suc


def test_onMouseNormal_4():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.button = 0
    event.dblclick = True
    suc = app.onMouseNormal(event=event)
    assert not suc


def test_onMouseNormal_5():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.button = 1
    event.dblclick = True
    event.xdata = 180
    event.ydata = 45
    app.app.dome.framework = 'indi'
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'question',
                           return_value=PyQt5.QtWidgets.QMessageBox.No):
        suc = app.onMouseNormal(event=event)
        assert not suc


def test_onMouseNormal_6():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.button = 1
    event.dblclick = True
    event.xdata = 180
    event.ydata = 45
    app.app.dome.framework = 'indi'
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'question',
                           return_value=PyQt5.QtWidgets.QMessageBox.Yes):
        with mock.patch.object(mountcontrol.obsSite.Connection,
                               'communicate',
                               return_value=(True, '1', 1)):
            with mock.patch.object(app.app.mount.obsSite,
                                   'setTargetAltAz',
                                   return_value=True):
                suc = app.onMouseNormal(event=event)
                assert not suc


def test_addHorizonPoint_1():
    class Test:
        pass
    event = Test()
    event.xdata = 180
    event.ydata = 45
    app.app.data.horizonP = [(0, 0), (10, 10), (0, 360)]
    suc = app.addHorizonPoint(data=app.app.data, event=event)
    assert suc


def test_addHorizonPoint_2():
    class Test:
        pass
    event = Test()
    event.xdata = 180
    event.ydata = 45
    app.app.data.horizonP = [(0, 0)]
    suc = app.addHorizonPoint(data=app.app.data, event=event)
    assert suc


def test_addHorizonPoint_3():
    class Test:
        pass
    event = Test()
    event.xdata = 180
    event.ydata = 45
    suc = app.addHorizonPoint(data=app.app.data, event=event)
    assert suc


def test_deleteHorizonPoint_1():
    class Test:
        pass
    event = Test()
    event.xdata = 10
    event.ydata = 10
    app.app.data.horizonP = [(0, 0), (10, 10), (0, 360)]
    suc = app.deleteHorizonPoint(data=app.app.data, event=event)
    assert suc


def test_deleteHorizonPoint_2():
    class Test:
        pass
    event = Test()
    event.xdata = 180
    event.ydata = 45
    app.app.data.horizonP = [(0, 0), (10, 10), (0, 360)]
    suc = app.deleteHorizonPoint(data=app.app.data, event=event)
    assert not suc


def test_deleteHorizonPoint_3():
    class Test:
        pass
    event = Test()
    event.xdata = 180
    event.ydata = 45
    app.app.data.horizonP = [(0, 0)]
    suc = app.deleteHorizonPoint(data=app.app.data, event=event)
    assert not suc


def test_editHorizonMask_1():
    class Test:
        def set_data(self, test, test1):
            pass

        def set_xy(self, test):
            pass

    event = Test()
    event.xdata = 180
    event.ydata = 45
    event.button = 1
    app.horizonMarker = Test()
    app.horizonFill = Test()
    suc = app.editHorizonMask(data=app.app.data, event=event)
    assert suc


def test_editHorizonMask_2():
    class Test:
        def set_data(self, test, test1):
            pass

        def set_xy(self, test):
            pass

    event = Test()
    event.xdata = 180
    event.ydata = 45
    event.button = 3
    app.horizonMarker = Test()
    app.horizonFill = Test()
    app.app.data.horizonP = [(0, 0), (45, 180), (0, 360)]

    suc = app.editHorizonMask(data=app.app.data, event=event)
    assert suc


def test_editHorizonMask_3():
    class Test:
        def set_data(self, test, test1):
            pass

        def set_xy(self, test):
            pass

    event = Test()
    event.xdata = 180
    event.ydata = 45
    event.button = 2
    app.horizonMarker = Test()
    app.horizonFill = Test()
    suc = app.editHorizonMask(data=app.app.data, event=event)
    assert not suc


def test_deleteBuildPointPoint_1():
    axes = app.hemisphereMat.figure.axes[0]
    app.pointsBuildAnnotate.append(axes.annotate('', xy=(0, 0)))
    app.pointsBuildAnnotate.append(axes.annotate('', xy=(0, 0)))
    app.pointsBuildAnnotate.append(axes.annotate('', xy=(0, 0)))

    class Test:
        pass
    event = Test()
    event.xdata = 10
    event.ydata = 10
    app.app.data.buildP = [(0, 0), (10, 10), (0, 360)]
    suc = app.deleteBuildPoint(data=app.app.data, event=event)
    assert suc


def test_deleteBuildPointPoint_2():
    class Test:
        pass
    event = Test()
    event.xdata = 180
    event.ydata = 45
    app.app.data.buildP = [(0, 0), (10, 10), (0, 360)]
    suc = app.deleteBuildPoint(data=app.app.data, event=event)
    assert not suc


def test_editBuildPoints_1():
    app.app.data.buildP = [(0, 0), (10, 10), (0, 360)]
    axes = app.hemisphereMat.figure.axes[0]
    app.pointsBuildAnnotate.append(axes.annotate('', xy=(0, 0)))
    app.pointsBuildAnnotate.append(axes.annotate('', xy=(0, 0)))
    app.pointsBuildAnnotate.append(axes.annotate('', xy=(0, 0)))

    class Test:
        def set_data(self, test, test1):
            pass

        def set_xy(self, test):
            pass

    event = Test()
    event.xdata = 180
    event.ydata = 45
    event.button = 1
    app.pointsBuild = Test()
    suc = app.editBuildPoints(data=app.app.data, event=event, axes=axes)
    assert suc

"""
def test_editBuildPoints_2():
    app.app.data.buildP = [(0, 0), (10, 10), (45, 180)]
    axes = app.hemisphereMat.figure.axes[0]
    app.pointsBuildAnnotate.append(axes.annotate('', xy=(180, 45)))
    app.pointsBuildAnnotate.append(axes.annotate('', xy=(45, 180)))
    app.pointsBuildAnnotate.append(axes.annotate('', xy=(0, 0)))

    class Test:
        def set_data(self, test, test1):
            pass

        def set_xy(self, test):
            pass

    event = Test()
    event.xdata = 180
    event.ydata = 45
    event.button = 3
    app.pointsBuild = Test()
    suc = app.editBuildPoints(data=app.app.data, event=event, axes=axes)
    assert suc
"""


def test_editBuildPoints_3():
    app.app.data.buildP = [(0, 0), (10, 10), (0, 360)]
    axes = app.hemisphereMat.figure.axes[0]
    app.pointsBuildAnnotate.append(axes.annotate('', xy=(0, 0)))
    app.pointsBuildAnnotate.append(axes.annotate('', xy=(0, 0)))
    app.pointsBuildAnnotate.append(axes.annotate('', xy=(0, 0)))

    class Test:
        def set_data(self, test, test1):
            pass

        def set_xy(self, test):
            pass

    event = Test()
    event.xdata = 180
    event.ydata = 45
    event.button = 2
    app.pointsBuild = Test()
    suc = app.editBuildPoints(data=app.app.data, event=event, axes=axes)
    assert not suc


def test_onMouseEdit_1():
    class Test:
        pass
    event = Test()
    event.inaxes = False
    suc = app.onMouseEdit(event=event)
    assert not suc


def test_onMouseEdit_2():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.dblclick = False
    suc = app.onMouseEdit(event=event)
    assert not suc


def test_onMouseEdit_2b():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.dblclick = True
    suc = app.onMouseEdit(event=event)
    assert not suc


def test_onMouseEdit_3():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.dblclick = False
    app.ui.checkEditHorizonMask.setChecked(False)
    app.ui.checkEditBuildPoints.setChecked(False)
    with mock.patch.object(app,
                           'editHorizonMask',
                           return_value=True):
        with mock.patch.object(app,
                               'editBuildPoints',
                               return_value=True):
            suc = app.onMouseEdit(event=event)
            assert not suc


def test_onMouseEdit_4():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.dblclick = False
    app.ui.checkEditHorizonMask.setChecked(True)
    app.ui.checkEditBuildPoints.setChecked(False)
    with mock.patch.object(app,
                           'editHorizonMask',
                           return_value=True):
        with mock.patch.object(app,
                               'editBuildPoints',
                               return_value=True):
            suc = app.onMouseEdit(event=event)
            assert suc


def test_onMouseEdit_5():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.dblclick = False
    app.ui.checkEditHorizonMask.setChecked(False)
    app.ui.checkEditBuildPoints.setChecked(True)
    with mock.patch.object(app,
                           'editHorizonMask',
                           return_value=True):
        with mock.patch.object(app,
                               'editBuildPoints',
                               return_value=True):
            suc = app.onMouseEdit(event=event)
            assert suc


def test_onMouseEdit_6():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.dblclick = False
    app.ui.checkEditHorizonMask.setChecked(True)
    app.ui.checkEditBuildPoints.setChecked(False)
    with mock.patch.object(app,
                           'editHorizonMask',
                           return_value=False):
        with mock.patch.object(app,
                               'editBuildPoints',
                               return_value=True):
            suc = app.onMouseEdit(event=event)
            assert not suc


def test_onMouseEdit_7():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.dblclick = False
    app.ui.checkEditHorizonMask.setChecked(False)
    app.ui.checkEditBuildPoints.setChecked(True)
    with mock.patch.object(app,
                           'editHorizonMask',
                           return_value=True):
        with mock.patch.object(app,
                               'editBuildPoints',
                               return_value=False):
            suc = app.onMouseEdit(event=event)
            assert not suc


def test_onMouseStar_1():
    class Test:
        pass
    event = Test()
    event.inaxes = False
    event.dblclick = False
    suc = app.onMouseStar(event=event)
    assert not suc


def test_onMouseStar_2():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.button = 2
    event.dblclick = False
    suc = app.onMouseStar(event=event)
    assert not suc


def test_onMouseStar_3():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.button = 1
    event.dblclick = True
    suc = app.onMouseStar(event=event)
    assert not suc


def test_onMouseStar_4():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.button = 1
    event.dblclick = False
    event.xdata = 180
    event.ydata = 45
    app.app.hipparcos.az = [180]
    app.app.hipparcos.alt = [45]
    app.app.hipparcos.name = ['test']
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'question',
                           return_value=PyQt5.QtWidgets.QMessageBox.No):
        suc = app.onMouseStar(event=event)
        assert not suc


def test_onMouseStar_5():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.button = 1
    event.dblclick = False
    event.xdata = 180
    event.ydata = 45
    app.app.hipparcos.az = [180]
    app.app.hipparcos.alt = [45]
    app.app.hipparcos.name = ['test']
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'question',
                           return_value=PyQt5.QtWidgets.QMessageBox.Yes):
        with mock.patch.object(mountcontrol.obsSite.Connection,
                               'communicate',
                               return_value=(True, '1', 1)):
            suc = app.onMouseStar(event=event)
            assert not suc


def test_onMouseStar_6():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.button = 1
    event.dblclick = False
    event.xdata = 180
    event.ydata = 45
    app.app.hipparcos.az = [180]
    app.app.hipparcos.alt = [45]
    app.app.hipparcos.name = ['test']
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'question',
                           return_value=PyQt5.QtWidgets.QMessageBox.Yes):
        with mock.patch.object(mountcontrol.obsSite.Connection,
                               'communicate',
                               return_value=(True, '1', 1)):
            with mock.patch.object(app.app.mount.obsSite,
                                   'setTargetRaDec',
                                   return_value=True):
                suc = app.onMouseStar(event=event)
                assert not suc


def test_onMouseStar_7():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.button = 1
    event.dblclick = False
    event.xdata = 180
    event.ydata = 45
    app.app.hipparcos.az = []
    app.app.hipparcos.alt = []
    app.app.hipparcos.name = []
    suc = app.onMouseStar(event=event)
    assert not suc


def test_onMouseStar_8():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.button = 1
    event.dblclick = False
    event.xdata = 180
    event.ydata = 45
    app.app.hipparcos.az = [180]
    app.app.hipparcos.alt = [45]
    app.app.hipparcos.name = ['test']
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'question',
                           return_value=PyQt5.QtWidgets.QMessageBox.Yes):
        with mock.patch.object(mountcontrol.obsSite.Connection,
                               'communicate',
                               return_value=(True, '1', 1)):
            with mock.patch.object(app.app.mount.obsSite,
                                   'setTargetRaDec',
                                   return_value=False):
                suc = app.onMouseStar(event=event)
                assert not suc


def test_onMouseStar_9():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.button = 3
    event.dblclick = False
    event.xdata = 180
    event.ydata = 45
    app.app.dome.framework = 'indi'
    app.app.hipparcos.az = [180]
    app.app.hipparcos.alt = [45]
    app.app.hipparcos.name = ['test']
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'question',
                           return_value=PyQt5.QtWidgets.QMessageBox.Yes):
        with mock.patch.object(mountcontrol.obsSite.Connection,
                               'communicate',
                               return_value=(True, '1', 1)):
            with mock.patch.object(app.app.mount.obsSite,
                                   'setTargetRaDec',
                                   return_value=True):
                suc = app.onMouseStar(event=event)
                assert not suc


def test_drawHemisphere_1():
    class Test:
        def set_marker(self, test):
            pass

        def set_color(self, test):
            pass

    app.horizonMarker = Test()
    app.drawHemisphere()

