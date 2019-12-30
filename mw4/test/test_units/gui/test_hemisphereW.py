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
import PyQt5.QtWidgets
import PyQt5.QtTest
import PyQt5.QtCore
import skyfield.api as api
import matplotlib.path
import mountcontrol
# local import
from mw4.test.test_units.setupQt import setupQt


@pytest.fixture(autouse=True, scope='module')
def module_setup_teardown():
    global app, spy, mwGlob, test
    app, spy, mwGlob, test = setupQt()
    app.config['showHemisphereW'] = True
    app.toggleWindow(windowTag='showHemisphereW')


def test_storeConfig_1():
    app.uiWindows['showHemisphereW']['classObj'].storeConfig()


def test_initConfig_1():
    suc = app.uiWindows['showHemisphereW']['classObj'].initConfig()
    assert suc


def test_initConfig_3():
    app.config['hemisphereW']['winPosX'] = 10000
    app.config['hemisphereW']['winPosY'] = 10000
    suc = app.uiWindows['showHemisphereW']['classObj'].initConfig()
    assert suc


def test_setupAxes1(qtbot):
    app.uiWindows['showHemisphereW']['classObj'].drawHemisphere()
    suc = app.uiWindows['showHemisphereW']['classObj'].setupAxes(app.uiWindows['showHemisphereW']['classObj'].hemisphereMat)
    assert suc


def test_setupAxes2(qtbot):
    app.uiWindows['showHemisphereW']['classObj'].drawHemisphere()
    app.uiWindows['showHemisphereW']['classObj'].setupAxes(app.uiWindows['showHemisphereW']['classObj'].hemisphereMat)


def test_drawCanvas(qtbot):
    app.uiWindows['showHemisphereW']['classObj'].drawHemisphere()
    suc = app.uiWindows['showHemisphereW']['classObj'].drawCanvas()
    assert suc


def test_updateCelestialPath_1(qtbot):
    app.uiWindows['showHemisphereW']['classObj'].drawHemisphere()
    suc = app.uiWindows['showHemisphereW']['classObj'].updateCelestialPath()
    assert suc


def test_updateCelestialPath_3(qtbot):
    app.uiWindows['showHemisphereW']['classObj'].drawHemisphere()
    app.uiWindows['showHemisphereW']['classObj'].celestialPath = None
    suc = app.uiWindows['showHemisphereW']['classObj'].updateCelestialPath()
    assert not suc


def test_updateMeridian_1(qtbot):
    app.uiWindows['showHemisphereW']['classObj'].drawHemisphere()
    app.mount.setting.meridianLimitSlew = 3
    app.mount.setting.meridianLimitTrack = 3
    suc = app.uiWindows['showHemisphereW']['classObj'].updateMeridian()
    assert suc


def test_updateMeridian_3(qtbot):
    app.uiWindows['showHemisphereW']['classObj'].drawHemisphere()
    app.mount.setting.meridianLimitSlew = None
    app.mount.setting.meridianLimitTrack = 3
    suc = app.uiWindows['showHemisphereW']['classObj'].updateMeridian()
    assert not suc


def test_updateMeridian_4(qtbot):
    app.uiWindows['showHemisphereW']['classObj'].drawHemisphere()
    app.mount.setting.meridianLimitSlew = 3
    app.mount.setting.meridianLimitTrack = None
    suc = app.uiWindows['showHemisphereW']['classObj'].updateMeridian()
    assert not suc


def test_updateMeridian_5(qtbot):
    app.uiWindows['showHemisphereW']['classObj'].drawHemisphere()
    app.mount.setting.meridianLimitSlew = 3
    app.mount.setting.meridianLimitTrack = 3
    app.uiWindows['showHemisphereW']['classObj'].meridianTrack = None
    suc = app.uiWindows['showHemisphereW']['classObj'].updateMeridian()
    assert not suc


def test_updateMeridian_6(qtbot):
    app.uiWindows['showHemisphereW']['classObj'].drawHemisphere()
    app.mount.setting.meridianLimitSlew = 3
    app.mount.setting.meridianLimitTrack = 3
    app.uiWindows['showHemisphereW']['classObj'].meridianSlew = None
    suc = app.uiWindows['showHemisphereW']['classObj'].updateMeridian()
    assert not suc


def test_updateHorizonLimits_1(qtbot):
    app.uiWindows['showHemisphereW']['classObj'].drawHemisphere()
    app.mount.setting.horizonLimitHigh = 80
    app.mount.setting.horizonLimitLow = 10
    suc = app.uiWindows['showHemisphereW']['classObj'].updateHorizonLimits()
    assert suc


def test_updateHorizonLimits_3(qtbot):
    app.uiWindows['showHemisphereW']['classObj'].drawHemisphere()
    app.mount.setting.horizonLimitHigh = None
    app.mount.setting.horizonLimitLow = 10
    suc = app.uiWindows['showHemisphereW']['classObj'].updateHorizonLimits()
    assert not suc


def test_updateHorizonLimits_4(qtbot):
    app.uiWindows['showHemisphereW']['classObj'].drawHemisphere()
    app.mount.setting.horizonLimitHigh = 80
    app.mount.setting.horizonLimitLow = None
    suc = app.uiWindows['showHemisphereW']['classObj'].updateHorizonLimits()
    assert not suc


def test_updateHorizonLimits_5(qtbot):
    app.uiWindows['showHemisphereW']['classObj'].drawHemisphere()
    app.mount.setting.horizonLimitHigh = 80
    app.mount.setting.horizonLimitLow = 10
    app.uiWindows['showHemisphereW']['classObj'].horizonLimitLow = None
    suc = app.uiWindows['showHemisphereW']['classObj'].updateHorizonLimits()
    assert not suc


def test_updateHorizonLimits_6(qtbot):
    app.uiWindows['showHemisphereW']['classObj'].drawHemisphere()
    app.mount.setting.horizonLimitHigh = 80
    app.mount.setting.horizonLimitLow = 10
    app.uiWindows['showHemisphereW']['classObj'].horizonLimitHigh = None
    suc = app.uiWindows['showHemisphereW']['classObj'].updateHorizonLimits()
    assert not suc


def test_updatePointerAltAz_1(qtbot):
    app.uiWindows['showHemisphereW']['classObj'].drawHemisphere()
    app.mount.obsSite.Alt = api.Angle(degrees=5)
    app.mount.obsSite.Az = api.Angle(degrees=5)
    suc = app.uiWindows['showHemisphereW']['classObj'].updatePointerAltAz()
    assert suc


def test_updatePointerAltAz_3(qtbot):
    app.uiWindows['showHemisphereW']['classObj'].drawHemisphere()
    app.mount.obsSite.Az = None
    suc = app.uiWindows['showHemisphereW']['classObj'].updatePointerAltAz()
    assert not suc


def test_updatePointerAltAz_4(qtbot):
    app.uiWindows['showHemisphereW']['classObj'].drawHemisphere()
    app.mount.obsSite.Alt = None
    suc = app.uiWindows['showHemisphereW']['classObj'].updatePointerAltAz()
    assert not suc


def test_updatePointerAltAz_5(qtbot):
    app.uiWindows['showHemisphereW']['classObj'].drawHemisphere()
    app.mount.obsSite.Alt = api.Angle(degrees=5)
    app.mount.obsSite.Az = api.Angle(degrees=5)
    app.uiWindows['showHemisphereW']['classObj'].pointerAltAz = None
    suc = app.uiWindows['showHemisphereW']['classObj'].updatePointerAltAz()
    assert not suc


def test_updateDome_1(qtbot):
    app.uiWindows['showHemisphereW']['classObj'].drawHemisphere()
    app.dome.data = {}
    suc = app.uiWindows['showHemisphereW']['classObj'].updateDome(45)
    assert suc


def test_updateDome_3(qtbot):
    app.uiWindows['showHemisphereW']['classObj'].drawHemisphere()
    app.dome.data = {}
    suc = app.uiWindows['showHemisphereW']['classObj'].updateDome(45)
    assert suc


def test_updateDome_4(qtbot):
    app.uiWindows['showHemisphereW']['classObj'].drawHemisphere()
    app.dome.data['DOME_ABSOLUTE_POSITION'] = 90
    app.uiWindows['showHemisphereW']['classObj'].pointerDome = None
    suc = app.uiWindows['showHemisphereW']['classObj'].updateDome(45)
    assert not suc


def test_updateAlignStar_1(qtbot):
    app.uiWindows['showHemisphereW']['classObj'].drawHemisphere()
    app.uiWindows['showHemisphereW']['classObj'].ui.checkShowAlignStar.setChecked(True)
    suc = app.uiWindows['showHemisphereW']['classObj'].updateAlignStar()
    assert suc


def test_updateAlignStar_3(qtbot):
    app.uiWindows['showHemisphereW']['classObj'].drawHemisphere()
    app.uiWindows['showHemisphereW']['classObj'].ui.checkShowAlignStar.setChecked(True)
    app.uiWindows['showHemisphereW']['classObj'].starsAlign = None
    suc = app.uiWindows['showHemisphereW']['classObj'].updateAlignStar()
    assert not suc


def test_updateAlignStar_4(qtbot):
    app.uiWindows['showHemisphereW']['classObj'].drawHemisphere()
    app.uiWindows['showHemisphereW']['classObj'].ui.checkShowAlignStar.setChecked(True)
    app.uiWindows['showHemisphereW']['classObj'].starsAlignAnnotate = None
    suc = app.uiWindows['showHemisphereW']['classObj'].updateAlignStar()
    assert not suc


def test_updateAlignStar_5(qtbot):
    app.uiWindows['showHemisphereW']['classObj'].drawHemisphere()
    app.uiWindows['showHemisphereW']['classObj'].ui.checkShowAlignStar.setChecked(False)
    suc = app.uiWindows['showHemisphereW']['classObj'].updateAlignStar()
    assert not suc


def test_markerPoint():
    val = app.uiWindows['showHemisphereW']['classObj'].markerPoint()
    assert isinstance(val, matplotlib.path.Path)


def test_markerAltAz():
    val = app.uiWindows['showHemisphereW']['classObj'].markerAltAz()
    assert isinstance(val, matplotlib.path.Path)


def test_markerStar():
    val = app.uiWindows['showHemisphereW']['classObj'].markerStar()
    assert isinstance(val, matplotlib.path.Path)


def test_clearHemisphere(qtbot):
    app.data.buildP = [(0, 0), (1, 0)]
    app.uiWindows['showHemisphereW']['classObj'].clearHemisphere()
    assert app.data.buildP == []


def test_setOperationMode_1():
    assert app.uiWindows['showHemisphereW']['classObj'].MODE is not None
    assert 'normal' in app.uiWindows['showHemisphereW']['classObj'].MODE
    assert 'build' in app.uiWindows['showHemisphereW']['classObj'].MODE
    assert 'horizon' in app.uiWindows['showHemisphereW']['classObj'].MODE
    assert 'star' in app.uiWindows['showHemisphereW']['classObj'].MODE


def test_setOperationMode_2():
    class Test:
        def set_marker(self, test):
            pass

        def set_color(self, test):
            pass

    app.uiWindows['showHemisphereW']['classObj'].ui.checkEditNone.setChecked(True)
    app.uiWindows['showHemisphereW']['classObj'].horizonMarker = Test()
    app.uiWindows['showHemisphereW']['classObj'].pointsBuild = Test()
    suc = app.uiWindows['showHemisphereW']['classObj'].setOperationMode()
    assert suc


def test_setOperationMode_3():
    class Test:
        def set_marker(self, test):
            pass

        def set_color(self, test):
            pass

    app.uiWindows['showHemisphereW']['classObj'].ui.checkPolarAlignment.setChecked(True)
    app.uiWindows['showHemisphereW']['classObj'].horizonMarker = Test()
    app.uiWindows['showHemisphereW']['classObj'].pointsBuild = Test()
    suc = app.uiWindows['showHemisphereW']['classObj'].setOperationMode()
    assert suc


def test_setOperationMode_4():
    class Test:
        def set_marker(self, test):
            pass

        def set_color(self, test):
            pass

    app.uiWindows['showHemisphereW']['classObj'].ui.checkEditBuildPoints.setChecked(True)
    app.uiWindows['showHemisphereW']['classObj'].horizonMarker = Test()
    app.uiWindows['showHemisphereW']['classObj'].pointsBuild = Test()
    suc = app.uiWindows['showHemisphereW']['classObj'].setOperationMode()
    assert suc


def test_setOperationMode_5():
    class Test:
        def set_marker(self, test):
            pass

        def set_color(self, test):
            pass

    app.uiWindows['showHemisphereW']['classObj'].ui.checkEditHorizonMask.setChecked(True)
    app.uiWindows['showHemisphereW']['classObj'].horizonMarker = Test()
    app.uiWindows['showHemisphereW']['classObj'].pointsBuild = Test()
    suc = app.uiWindows['showHemisphereW']['classObj'].setOperationMode()
    app.uiWindows['showHemisphereW']['classObj'].ui.checkEditNone.setChecked(True)
    assert suc


def test_getIndexPoint_0():
    class Test:
        pass
    event = Test()
    event.xdata = 180
    event.ydata = 45
    plane = []
    epsilon = 0
    index = app.uiWindows['showHemisphereW']['classObj'].getIndexPoint(event=event,
                                          plane=plane,
                                          epsilon=epsilon,
                                          )
    assert not index


def test_getIndexPoint_1():
    event = None
    plane = None
    epsilon = 0
    index = app.uiWindows['showHemisphereW']['classObj'].getIndexPoint(event=event,
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
    index = app.uiWindows['showHemisphereW']['classObj'].getIndexPoint(event=event,
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
    index = app.uiWindows['showHemisphereW']['classObj'].getIndexPoint(event=event,
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
    index = app.uiWindows['showHemisphereW']['classObj'].getIndexPoint(event=event,
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
    index = app.uiWindows['showHemisphereW']['classObj'].getIndexPoint(event=event,
                                          plane=plane,
                                          epsilon=epsilon,
                                          )
    assert index == 1


def test_getIndexPointX_1():
    event = None
    plane = None
    index = app.uiWindows['showHemisphereW']['classObj'].getIndexPointX(event=event,
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
    index = app.uiWindows['showHemisphereW']['classObj'].getIndexPointX(event=event,
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
    index = app.uiWindows['showHemisphereW']['classObj'].getIndexPointX(event=event,
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
    index = app.uiWindows['showHemisphereW']['classObj'].getIndexPointX(event=event,
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
    index = app.uiWindows['showHemisphereW']['classObj'].getIndexPointX(event=event,
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
    index = app.uiWindows['showHemisphereW']['classObj'].getIndexPointX(event=event,
                                           plane=plane,
                                           )
    assert not index


def test_onMouseNormal_1():
    class Test:
        pass
    event = Test()
    event.inaxes = False
    suc = app.uiWindows['showHemisphereW']['classObj'].onMouseNormal(event=event)
    assert not suc


def test_onMouseNormal_2():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.button = 0
    event.dblclick = False
    suc = app.uiWindows['showHemisphereW']['classObj'].onMouseNormal(event=event)
    assert not suc


def test_onMouseNormal_3():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.button = 1
    event.dblclick = False
    suc = app.uiWindows['showHemisphereW']['classObj'].onMouseNormal(event=event)
    assert not suc


def test_onMouseNormal_4():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.button = 0
    event.dblclick = True
    suc = app.uiWindows['showHemisphereW']['classObj'].onMouseNormal(event=event)
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
    app.dome.framework = 'indi'
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'question',
                           return_value=PyQt5.QtWidgets.QMessageBox.No):
        suc = app.uiWindows['showHemisphereW']['classObj'].onMouseNormal(event=event)
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
    app.dome.framework = 'indi'
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'question',
                           return_value=PyQt5.QtWidgets.QMessageBox.Yes):
        with mock.patch.object(mountcontrol.obsSite.Connection,
                               'communicate',
                               return_value=(True, '1', 1)):
            with mock.patch.object(app.mount.obsSite,
                                   'setTargetAltAz',
                                   return_value=True):
                suc = app.uiWindows['showHemisphereW']['classObj'].onMouseNormal(event=event)
                assert suc


def test_addHorizonPoint_1():
    class Test:
        pass
    event = Test()
    event.xdata = 180
    event.ydata = 45
    app.data.horizonP = [(0, 0), (10, 10), (0, 360)]
    suc = app.uiWindows['showHemisphereW']['classObj'].addHorizonPoint(data=app.data, event=event)
    assert suc


def test_addHorizonPoint_2():
    class Test:
        pass
    event = Test()
    event.xdata = 180
    event.ydata = 45
    app.data.horizonP = [(0, 0)]
    suc = app.uiWindows['showHemisphereW']['classObj'].addHorizonPoint(data=app.data, event=event)
    assert suc


def test_addHorizonPoint_3():
    class Test:
        pass
    event = Test()
    event.xdata = 180
    event.ydata = 45
    suc = app.uiWindows['showHemisphereW']['classObj'].addHorizonPoint(data=app.data, event=event)
    assert suc


def test_deleteHorizonPoint_1():
    class Test:
        pass
    event = Test()
    event.xdata = 10
    event.ydata = 10
    app.data.horizonP = [(0, 0), (10, 10), (0, 360)]
    suc = app.uiWindows['showHemisphereW']['classObj'].deleteHorizonPoint(data=app.data, event=event)
    assert suc


def test_deleteHorizonPoint_2():
    class Test:
        pass
    event = Test()
    event.xdata = 180
    event.ydata = 45
    app.data.horizonP = [(0, 0), (10, 10), (0, 360)]
    suc = app.uiWindows['showHemisphereW']['classObj'].deleteHorizonPoint(data=app.data, event=event)
    assert not suc


def test_deleteHorizonPoint_3():
    class Test:
        pass
    event = Test()
    event.xdata = 180
    event.ydata = 45
    app.data.horizonP = [(0, 0)]
    suc = app.uiWindows['showHemisphereW']['classObj'].deleteHorizonPoint(data=app.data, event=event)
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
    app.uiWindows['showHemisphereW']['classObj'].horizonMarker = Test()
    app.uiWindows['showHemisphereW']['classObj'].horizonFill = Test()
    suc = app.uiWindows['showHemisphereW']['classObj'].editHorizonMask(data=app.data, event=event)
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
    app.uiWindows['showHemisphereW']['classObj'].horizonMarker = Test()
    app.uiWindows['showHemisphereW']['classObj'].horizonFill = Test()
    suc = app.uiWindows['showHemisphereW']['classObj'].editHorizonMask(data=app.data, event=event)
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
    app.uiWindows['showHemisphereW']['classObj'].horizonMarker = Test()
    app.uiWindows['showHemisphereW']['classObj'].horizonFill = Test()
    suc = app.uiWindows['showHemisphereW']['classObj'].editHorizonMask(data=app.data, event=event)
    assert not suc


def test_deleteBuildPointPoint_1():
    axes = app.uiWindows['showHemisphereW']['classObj'].hemisphereMat.figure.axes[0]
    app.uiWindows['showHemisphereW']['classObj'].pointsBuildAnnotate.append(axes.annotate('', xy=(0, 0)))
    app.uiWindows['showHemisphereW']['classObj'].pointsBuildAnnotate.append(axes.annotate('', xy=(0, 0)))
    app.uiWindows['showHemisphereW']['classObj'].pointsBuildAnnotate.append(axes.annotate('', xy=(0, 0)))

    class Test:
        pass
    event = Test()
    event.xdata = 10
    event.ydata = 10
    app.data.buildP = [(0, 0), (10, 10), (0, 360)]
    suc = app.uiWindows['showHemisphereW']['classObj'].deleteBuildPoint(data=app.data, event=event)
    assert suc


def test_deleteBuildPointPoint_2():
    class Test:
        pass
    event = Test()
    event.xdata = 180
    event.ydata = 45
    app.data.buildP = [(0, 0), (10, 10), (0, 360)]
    suc = app.uiWindows['showHemisphereW']['classObj'].deleteBuildPoint(data=app.data, event=event)
    assert not suc


def test_editBuildPoints_1():
    app.data.buildP = [(0, 0), (10, 10), (0, 360)]
    axes = app.uiWindows['showHemisphereW']['classObj'].hemisphereMat.figure.axes[0]
    app.uiWindows['showHemisphereW']['classObj'].pointsBuildAnnotate.append(axes.annotate('', xy=(0, 0)))
    app.uiWindows['showHemisphereW']['classObj'].pointsBuildAnnotate.append(axes.annotate('', xy=(0, 0)))
    app.uiWindows['showHemisphereW']['classObj'].pointsBuildAnnotate.append(axes.annotate('', xy=(0, 0)))

    class Test:
        def set_data(self, test, test1):
            pass

        def set_xy(self, test):
            pass

    event = Test()
    event.xdata = 180
    event.ydata = 45
    event.button = 1
    app.uiWindows['showHemisphereW']['classObj'].pointsBuild = Test()
    suc = app.uiWindows['showHemisphereW']['classObj'].editBuildPoints(data=app.data, event=event, axes=axes)
    assert suc

"""
def test_editBuildPoints_2():
    app.data.buildP = [(0, 0), (10, 10), (45, 180)]
    axes = app.uiWindows['showHemisphereW']['classObj'].hemisphereMat.figure.axes[0]
    app.uiWindows['showHemisphereW']['classObj'].pointsBuildAnnotate.append(axes.annotate('', xy=(180, 45)))
    app.uiWindows['showHemisphereW']['classObj'].pointsBuildAnnotate.append(axes.annotate('', xy=(45, 180)))
    app.uiWindows['showHemisphereW']['classObj'].pointsBuildAnnotate.append(axes.annotate('', xy=(0, 0)))

    class Test:
        def set_data(self, test, test1):
            pass

        def set_xy(self, test):
            pass

    event = Test()
    event.xdata = 180
    event.ydata = 45
    event.button = 3
    app.uiWindows['showHemisphereW']['classObj'].pointsBuild = Test()
    suc = app.uiWindows['showHemisphereW']['classObj'].editBuildPoints(data=app.data, event=event, axes=axes)
    assert suc
"""


def test_editBuildPoints_3():
    app.data.buildP = [(0, 0), (10, 10), (0, 360)]
    axes = app.uiWindows['showHemisphereW']['classObj'].hemisphereMat.figure.axes[0]
    app.uiWindows['showHemisphereW']['classObj'].pointsBuildAnnotate.append(axes.annotate('', xy=(0, 0)))
    app.uiWindows['showHemisphereW']['classObj'].pointsBuildAnnotate.append(axes.annotate('', xy=(0, 0)))
    app.uiWindows['showHemisphereW']['classObj'].pointsBuildAnnotate.append(axes.annotate('', xy=(0, 0)))

    class Test:
        def set_data(self, test, test1):
            pass

        def set_xy(self, test):
            pass

    event = Test()
    event.xdata = 180
    event.ydata = 45
    event.button = 2
    app.uiWindows['showHemisphereW']['classObj'].pointsBuild = Test()
    suc = app.uiWindows['showHemisphereW']['classObj'].editBuildPoints(data=app.data, event=event, axes=axes)
    assert not suc


def test_onMouseEdit_1():
    class Test:
        pass
    event = Test()
    event.inaxes = False
    suc = app.uiWindows['showHemisphereW']['classObj'].onMouseEdit(event=event)
    assert not suc


def test_onMouseEdit_2():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.dblclick = False
    suc = app.uiWindows['showHemisphereW']['classObj'].onMouseEdit(event=event)
    assert not suc


def test_onMouseEdit_2b():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.dblclick = True
    suc = app.uiWindows['showHemisphereW']['classObj'].onMouseEdit(event=event)
    assert not suc


def test_onMouseEdit_3():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.dblclick = False
    app.uiWindows['showHemisphereW']['classObj'].ui.checkEditHorizonMask.setChecked(False)
    app.uiWindows['showHemisphereW']['classObj'].ui.checkEditBuildPoints.setChecked(False)
    with mock.patch.object(app.uiWindows['showHemisphereW']['classObj'],
                           'editHorizonMask',
                           return_value=True):
        with mock.patch.object(app.uiWindows['showHemisphereW']['classObj'],
                               'editBuildPoints',
                               return_value=True):
            suc = app.uiWindows['showHemisphereW']['classObj'].onMouseEdit(event=event)
            assert not suc


def test_onMouseEdit_4():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.dblclick = False
    app.uiWindows['showHemisphereW']['classObj'].ui.checkEditHorizonMask.setChecked(True)
    app.uiWindows['showHemisphereW']['classObj'].ui.checkEditBuildPoints.setChecked(False)
    with mock.patch.object(app.uiWindows['showHemisphereW']['classObj'],
                           'editHorizonMask',
                           return_value=True):
        with mock.patch.object(app.uiWindows['showHemisphereW']['classObj'],
                               'editBuildPoints',
                               return_value=True):
            suc = app.uiWindows['showHemisphereW']['classObj'].onMouseEdit(event=event)
            assert suc


def test_onMouseEdit_5():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.dblclick = False
    app.uiWindows['showHemisphereW']['classObj'].ui.checkEditHorizonMask.setChecked(False)
    app.uiWindows['showHemisphereW']['classObj'].ui.checkEditBuildPoints.setChecked(True)
    with mock.patch.object(app.uiWindows['showHemisphereW']['classObj'],
                           'editHorizonMask',
                           return_value=True):
        with mock.patch.object(app.uiWindows['showHemisphereW']['classObj'],
                               'editBuildPoints',
                               return_value=True):
            suc = app.uiWindows['showHemisphereW']['classObj'].onMouseEdit(event=event)
            assert suc


def test_onMouseEdit_6():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.dblclick = False
    app.uiWindows['showHemisphereW']['classObj'].ui.checkEditHorizonMask.setChecked(True)
    app.uiWindows['showHemisphereW']['classObj'].ui.checkEditBuildPoints.setChecked(False)
    with mock.patch.object(app.uiWindows['showHemisphereW']['classObj'],
                           'editHorizonMask',
                           return_value=False):
        with mock.patch.object(app.uiWindows['showHemisphereW']['classObj'],
                               'editBuildPoints',
                               return_value=True):
            suc = app.uiWindows['showHemisphereW']['classObj'].onMouseEdit(event=event)
            assert not suc


def test_onMouseEdit_7():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.dblclick = False
    app.uiWindows['showHemisphereW']['classObj'].ui.checkEditHorizonMask.setChecked(False)
    app.uiWindows['showHemisphereW']['classObj'].ui.checkEditBuildPoints.setChecked(True)
    with mock.patch.object(app.uiWindows['showHemisphereW']['classObj'],
                           'editHorizonMask',
                           return_value=True):
        with mock.patch.object(app.uiWindows['showHemisphereW']['classObj'],
                               'editBuildPoints',
                               return_value=False):
            suc = app.uiWindows['showHemisphereW']['classObj'].onMouseEdit(event=event)
            assert not suc


def test_onMouseStar_1():
    class Test:
        pass
    event = Test()
    event.inaxes = False
    event.dblclick = False
    suc = app.uiWindows['showHemisphereW']['classObj'].onMouseStar(event=event)
    assert not suc


def test_onMouseStar_2():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.button = 2
    event.dblclick = False
    suc = app.uiWindows['showHemisphereW']['classObj'].onMouseStar(event=event)
    assert not suc


def test_onMouseStar_3():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.button = 1
    event.dblclick = True
    suc = app.uiWindows['showHemisphereW']['classObj'].onMouseStar(event=event)
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
    app.hipparcos.az = [180]
    app.hipparcos.alt = [45]
    app.hipparcos.name = ['test']
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'question',
                           return_value=PyQt5.QtWidgets.QMessageBox.No):
        suc = app.uiWindows['showHemisphereW']['classObj'].onMouseStar(event=event)
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
    app.hipparcos.az = [180]
    app.hipparcos.alt = [45]
    app.hipparcos.name = ['test']
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'question',
                           return_value=PyQt5.QtWidgets.QMessageBox.Yes):
        with mock.patch.object(mountcontrol.obsSite.Connection,
                               'communicate',
                               return_value=(True, '1', 1)):
            suc = app.uiWindows['showHemisphereW']['classObj'].onMouseStar(event=event)
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
    app.hipparcos.az = [180]
    app.hipparcos.alt = [45]
    app.hipparcos.name = ['test']
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'question',
                           return_value=PyQt5.QtWidgets.QMessageBox.Yes):
        with mock.patch.object(mountcontrol.obsSite.Connection,
                               'communicate',
                               return_value=(True, '1', 1)):
            with mock.patch.object(app.mount.obsSite,
                                   'setTargetRaDec',
                                   return_value=True):
                suc = app.uiWindows['showHemisphereW']['classObj'].onMouseStar(event=event)
                assert suc


def test_onMouseStar_7():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.button = 1
    event.dblclick = False
    event.xdata = 180
    event.ydata = 45
    app.hipparcos.az = []
    app.hipparcos.alt = []
    app.hipparcos.name = []
    suc = app.uiWindows['showHemisphereW']['classObj'].onMouseStar(event=event)
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
    app.hipparcos.az = [180]
    app.hipparcos.alt = [45]
    app.hipparcos.name = ['test']
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'question',
                           return_value=PyQt5.QtWidgets.QMessageBox.Yes):
        with mock.patch.object(mountcontrol.obsSite.Connection,
                               'communicate',
                               return_value=(True, '1', 1)):
            with mock.patch.object(app.mount.obsSite,
                                   'setTargetRaDec',
                                   return_value=False):
                suc = app.uiWindows['showHemisphereW']['classObj'].onMouseStar(event=event)
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
    app.dome.framework = 'indi'
    app.hipparcos.az = [180]
    app.hipparcos.alt = [45]
    app.hipparcos.name = ['test']
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'question',
                           return_value=PyQt5.QtWidgets.QMessageBox.Yes):
        with mock.patch.object(mountcontrol.obsSite.Connection,
                               'communicate',
                               return_value=(True, '1', 1)):
            with mock.patch.object(app.mount.obsSite,
                                   'setTargetRaDec',
                                   return_value=True):
                suc = app.uiWindows['showHemisphereW']['classObj'].onMouseStar(event=event)
                assert suc


def test_drawHemisphere_1():
    class Test:
        def set_marker(self, test):
            pass

        def set_color(self, test):
            pass
    app.uiWindows['showHemisphereW']['classObj'].horizonMarker = Test()
    app.mainW.genBuildMin()
    app.uiWindows['showHemisphereW']['classObj'].drawHemisphere()
