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
# Python  v3.6.7
#
# Michael Würtenberger
# (c) 2018
#
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock
import pytest
import json
# external packages
import PyQt5.QtWidgets
import PyQt5.QtTest
import PyQt5.QtCore
import skyfield.api as api
import matplotlib.path
import mountcontrol
# local import
from mw4 import mainApp
from mw4.test.test_setupQt import setupQt


@pytest.fixture(autouse=True, scope='module')
def module_setup_teardown():
    global app, spy, mwGlob, test
    app, spy, mwGlob, test = setupQt()
    yield


def test_storeConfig_1():
    app.hemisphereW.storeConfig()


def test_initConfig_1():
    app.config['hemisphereW'] = {}
    suc = app.hemisphereW.initConfig()
    assert suc


def test_initConfig_2():
    del app.config['hemisphereW']
    suc = app.hemisphereW.initConfig()
    assert not suc


def test_initConfig_3():
    app.config['hemisphereW'] = {}
    app.config['hemisphereW']['winPosX'] = 10000
    app.config['hemisphereW']['winPosY'] = 10000
    suc = app.hemisphereW.initConfig()
    assert suc


def test_closeEvent(qtbot):
    app.hemisphereW.closeEvent(None)


def test_toggleWindow1(qtbot):
    app.hemisphereW.showStatus = True
    with mock.patch.object(app.hemisphereW,
                           'close',
                           return_value=None):
        app.hemisphereW.toggleWindow()
        assert not app.hemisphereW.showStatus


def test_toggleWindow2(qtbot):
    app.hemisphereW.showStatus = False
    with mock.patch.object(app.hemisphereW,
                           'showWindow',
                           return_value=None):
        app.hemisphereW.toggleWindow()
        assert app.hemisphereW.showStatus


def test_showWindow1(qtbot):
    app.hemisphereW.showStatus = False
    app.hemisphereW.showWindow()
    assert app.hemisphereW.showStatus


def test_clearAxes1(qtbot):
    app.hemisphereW.drawHemisphere()
    axes = app.hemisphereW.hemisphereMat.figure.axes[0]
    suc = app.hemisphereW.clearAxes(axes, True)
    assert suc


def test_clearAxes2(qtbot):
    app.hemisphereW.drawHemisphere()
    axes = app.hemisphereW.hemisphereMat.figure.axes[0]
    suc = app.hemisphereW.clearAxes(axes, False)
    assert not suc


def test_drawCanvas(qtbot):
    app.hemisphereW.drawHemisphere()
    suc = app.hemisphereW.drawCanvas()
    assert suc


def test_updateCelestialPath_1(qtbot):
    app.hemisphereW.drawHemisphere()
    app.hemisphereW.showStatus = True
    suc = app.hemisphereW.updateCelestialPath()
    assert suc


def test_updateCelestialPath_2(qtbot):
    app.hemisphereW.drawHemisphere()
    app.hemisphereW.showStatus = False
    suc = app.hemisphereW.updateCelestialPath()
    assert not suc


def test_updateCelestialPath_3(qtbot):
    app.hemisphereW.drawHemisphere()
    app.hemisphereW.showStatus = True
    app.hemisphereW.celestialPath = None
    suc = app.hemisphereW.updateCelestialPath()
    assert not suc


def test_updateMeridian_1(qtbot):
    app.hemisphereW.drawHemisphere()
    app.hemisphereW.showStatus = True
    app.mount.sett.meridianLimitSlew = 3
    app.mount.sett.meridianLimitTrack = 3
    suc = app.hemisphereW.updateMeridian()
    assert suc


def test_updateMeridian_2(qtbot):
    app.hemisphereW.drawHemisphere()
    app.hemisphereW.showStatus = False
    app.mount.sett.meridianLimitSlew = 3
    app.mount.sett.meridianLimitTrack = 3
    suc = app.hemisphereW.updateMeridian()
    assert not suc


def test_updateMeridian_3(qtbot):
    app.hemisphereW.drawHemisphere()
    app.hemisphereW.showStatus = True
    app.mount.sett.meridianLimitSlew = None
    app.mount.sett.meridianLimitTrack = 3
    suc = app.hemisphereW.updateMeridian()
    assert not suc


def test_updateMeridian_4(qtbot):
    app.hemisphereW.drawHemisphere()
    app.hemisphereW.showStatus = True
    app.mount.sett.meridianLimitSlew = 3
    app.mount.sett.meridianLimitTrack = None
    suc = app.hemisphereW.updateMeridian()
    assert not suc


def test_updateMeridian_5(qtbot):
    app.hemisphereW.drawHemisphere()
    app.hemisphereW.showStatus = True
    app.mount.sett.meridianLimitSlew = 3
    app.mount.sett.meridianLimitTrack = 3
    app.hemisphereW.meridianTrack = None
    suc = app.hemisphereW.updateMeridian()
    assert not suc


def test_updateMeridian_6(qtbot):
    app.hemisphereW.drawHemisphere()
    app.hemisphereW.showStatus = True
    app.mount.sett.meridianLimitSlew = 3
    app.mount.sett.meridianLimitTrack = 3
    app.hemisphereW.meridianSlew = None
    suc = app.hemisphereW.updateMeridian()
    assert not suc


def test_updateHorizonLimits_1(qtbot):
    app.hemisphereW.drawHemisphere()
    app.hemisphereW.showStatus = True
    app.mount.sett.horizonLimitHigh = 80
    app.mount.sett.horizonLimitLow = 10
    suc = app.hemisphereW.updateHorizonLimits()
    assert suc


def test_updateHorizonLimits_2(qtbot):
    app.hemisphereW.drawHemisphere()
    app.hemisphereW.showStatus = False
    app.mount.sett.horizonLimitHigh = 80
    app.mount.sett.horizonLimitLow = 10
    suc = app.hemisphereW.updateHorizonLimits()
    assert not suc


def test_updateHorizonLimits_3(qtbot):
    app.hemisphereW.drawHemisphere()
    app.hemisphereW.showStatus = True
    app.mount.sett.horizonLimitHigh = None
    app.mount.sett.horizonLimitLow = 10
    suc = app.hemisphereW.updateHorizonLimits()
    assert not suc


def test_updateHorizonLimits_4(qtbot):
    app.hemisphereW.drawHemisphere()
    app.hemisphereW.showStatus = True
    app.mount.sett.horizonLimitHigh = 80
    app.mount.sett.horizonLimitLow = None
    suc = app.hemisphereW.updateHorizonLimits()
    assert not suc


def test_updateHorizonLimits_5(qtbot):
    app.hemisphereW.drawHemisphere()
    app.hemisphereW.showStatus = True
    app.mount.sett.horizonLimitHigh = 80
    app.mount.sett.horizonLimitLow = 10
    app.hemisphereW.horizonLimitLow = None
    suc = app.hemisphereW.updateHorizonLimits()
    assert not suc


def test_updateHorizonLimits_6(qtbot):
    app.hemisphereW.drawHemisphere()
    app.hemisphereW.showStatus = True
    app.mount.sett.horizonLimitHigh = 80
    app.mount.sett.horizonLimitLow = 10
    app.hemisphereW.horizonLimitHigh = None
    suc = app.hemisphereW.updateHorizonLimits()
    assert not suc


def test_updatePointerAltAz_1(qtbot):
    app.hemisphereW.drawHemisphere()
    app.hemisphereW.showStatus = True
    app.mount.obsSite.Alt = api.Angle(degrees=5)
    app.mount.obsSite.Az = api.Angle(degrees=5)
    suc = app.hemisphereW.updatePointerAltAz()
    assert suc


def test_updatePointerAltAz_2(qtbot):
    app.hemisphereW.drawHemisphere()
    app.hemisphereW.showStatus = False
    suc = app.hemisphereW.updatePointerAltAz()
    assert not suc


def test_updatePointerAltAz_3(qtbot):
    app.hemisphereW.drawHemisphere()
    app.hemisphereW.showStatus = True
    app.mount.obsSite.Az = None
    suc = app.hemisphereW.updatePointerAltAz()
    assert not suc


def test_updatePointerAltAz_4(qtbot):
    app.hemisphereW.drawHemisphere()
    app.hemisphereW.showStatus = True
    app.mount.obsSite.Alt = None
    suc = app.hemisphereW.updatePointerAltAz()
    assert not suc


def test_updatePointerAltAz_5(qtbot):
    app.hemisphereW.drawHemisphere()
    app.hemisphereW.showStatus = True
    app.mount.obsSite.Alt = api.Angle(degrees=5)
    app.mount.obsSite.Az = api.Angle(degrees=5)
    app.hemisphereW.pointerAltAz = None
    suc = app.hemisphereW.updatePointerAltAz()
    assert not suc


def test_updateDome_1(qtbot):
    app.hemisphereW.drawHemisphere()
    app.hemisphereW.showStatus = True
    app.mount.obsSite.Az = api.Angle(degrees=5)
    suc = app.hemisphereW.updateDome()
    assert suc


def test_updateDome_2(qtbot):
    app.hemisphereW.drawHemisphere()
    app.hemisphereW.showStatus = False
    app.mount.obsSite.Az = api.Angle(degrees=5)
    suc = app.hemisphereW.updateDome()
    assert not suc


def test_updateDome_3(qtbot):
    app.hemisphereW.drawHemisphere()
    app.hemisphereW.showStatus = True
    app.mount.obsSite.Az = None
    suc = app.hemisphereW.updateDome()
    assert not suc


def test_updateDome_4(qtbot):
    app.hemisphereW.drawHemisphere()
    app.hemisphereW.showStatus = True
    app.mount.obsSite.Az = 90
    app.hemisphereW.pointerDome = None
    suc = app.hemisphereW.updateDome()
    assert not suc


def test_updateAlignStar_1(qtbot):
    app.hemisphereW.drawHemisphere()
    app.hemisphereW.showStatus = True
    app.hemisphereW.ui.checkShowAlignStar.setChecked(True)
    suc = app.hemisphereW.updateAlignStar()
    assert suc


def test_updateAlignStar_2(qtbot):
    app.hemisphereW.drawHemisphere()
    app.hemisphereW.showStatus = False
    app.hemisphereW.ui.checkShowAlignStar.setChecked(True)
    suc = app.hemisphereW.updateAlignStar()
    assert not suc


def test_updateAlignStar_3(qtbot):
    app.hemisphereW.drawHemisphere()
    app.hemisphereW.showStatus = True
    app.hemisphereW.ui.checkShowAlignStar.setChecked(True)
    app.hemisphereW.starsAlign = None
    suc = app.hemisphereW.updateAlignStar()
    assert not suc


def test_updateAlignStar_4(qtbot):
    app.hemisphereW.drawHemisphere()
    app.hemisphereW.showStatus = True
    app.hemisphereW.ui.checkShowAlignStar.setChecked(True)
    app.hemisphereW.starsAlignAnnotate = None
    suc = app.hemisphereW.updateAlignStar()
    assert not suc


def test_updateAlignStar_5(qtbot):
    app.hemisphereW.drawHemisphere()
    app.hemisphereW.showStatus = True
    app.hemisphereW.ui.checkShowAlignStar.setChecked(False)
    suc = app.hemisphereW.updateAlignStar()
    assert not suc


def test_markerPoint():
    val = app.hemisphereW.markerPoint()
    assert isinstance(val, matplotlib.path.Path)


def test_markerAltAz():
    val = app.hemisphereW.markerAltAz()
    assert isinstance(val, matplotlib.path.Path)


def test_markerStar():
    val = app.hemisphereW.markerStar()
    assert isinstance(val, matplotlib.path.Path)


def test_clearHemisphere(qtbot):
    app.data.buildP = [(0, 0), (1, 0)]
    app.hemisphereW.clearHemisphere()
    assert app.data.buildP == []


def test_setOperationMode_1():
    assert app.hemisphereW.MODE is not None
    assert 'normal' in app.hemisphereW.MODE
    assert 'build' in app.hemisphereW.MODE
    assert 'horizon' in app.hemisphereW.MODE
    assert 'star' in app.hemisphereW.MODE


def test_setOperationMode_2():
    class Test:
        def set_marker(self, test):
            pass

        def set_color(self, test):
            pass

    app.hemisphereW.ui.checkEditNone.setChecked(True)
    app.hemisphereW.horizonMarker = Test()
    app.hemisphereW.pointsBuild = Test()
    suc = app.hemisphereW.setOperationMode()
    assert suc


def test_setOperationMode_3():
    class Test:
        def set_marker(self, test):
            pass

        def set_color(self, test):
            pass

    app.hemisphereW.ui.checkPolarAlignment.setChecked(True)
    app.hemisphereW.horizonMarker = Test()
    app.hemisphereW.pointsBuild = Test()
    suc = app.hemisphereW.setOperationMode()
    assert suc


def test_setOperationMode_4():
    class Test:
        def set_marker(self, test):
            pass

        def set_color(self, test):
            pass

    app.hemisphereW.ui.checkEditBuildPoints.setChecked(True)
    app.hemisphereW.horizonMarker = Test()
    app.hemisphereW.pointsBuild = Test()
    suc = app.hemisphereW.setOperationMode()
    assert suc


def test_setOperationMode_5():
    class Test:
        def set_marker(self, test):
            pass

        def set_color(self, test):
            pass

    app.hemisphereW.ui.checkEditHorizonMask.setChecked(True)
    app.hemisphereW.horizonMarker = Test()
    app.hemisphereW.pointsBuild = Test()
    suc = app.hemisphereW.setOperationMode()
    app.hemisphereW.ui.checkEditNone.setChecked(True)
    assert suc


def test_getIndexPoint_0():
    class Test:
        pass
    event = Test()
    event.xdata = 180
    event.ydata = 45
    plane = []
    epsilon = 0
    index = app.hemisphereW.getIndexPoint(event=event,
                                          plane=plane,
                                          epsilon=epsilon,
                                          )
    assert not index


def test_getIndexPoint_1():
    event = None
    plane = None
    epsilon = 0
    index = app.hemisphereW.getIndexPoint(event=event,
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
    index = app.hemisphereW.getIndexPoint(event=event,
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
    index = app.hemisphereW.getIndexPoint(event=event,
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
    index = app.hemisphereW.getIndexPoint(event=event,
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
    index = app.hemisphereW.getIndexPoint(event=event,
                                          plane=plane,
                                          epsilon=epsilon,
                                          )
    assert index == 1


def test_getIndexPointX_1():
    event = None
    plane = None
    index = app.hemisphereW.getIndexPointX(event=event,
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
    index = app.hemisphereW.getIndexPointX(event=event,
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
    index = app.hemisphereW.getIndexPointX(event=event,
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
    index = app.hemisphereW.getIndexPointX(event=event,
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
    index = app.hemisphereW.getIndexPointX(event=event,
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
    index = app.hemisphereW.getIndexPointX(event=event,
                                           plane=plane,
                                           )
    assert not index


def test_onMouseNormal_1():
    class Test:
        pass
    event = Test()
    event.inaxes = False
    suc = app.hemisphereW.onMouseNormal(event=event)
    assert not suc


def test_onMouseNormal_2():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.button = 0
    event.dblclick = False
    suc = app.hemisphereW.onMouseNormal(event=event)
    assert not suc


def test_onMouseNormal_3():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.button = 1
    event.dblclick = False
    suc = app.hemisphereW.onMouseNormal(event=event)
    assert not suc


def test_onMouseNormal_4():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.button = 0
    event.dblclick = True
    suc = app.hemisphereW.onMouseNormal(event=event)
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
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'question',
                           return_value=PyQt5.QtWidgets.QMessageBox.No):
        suc = app.hemisphereW.onMouseNormal(event=event)
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
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'question',
                           return_value=PyQt5.QtWidgets.QMessageBox.Yes):
        with mock.patch.object(mountcontrol.obsSite.Connection,
                               'communicate',
                               return_value=(True, '1', 1)):
            suc = app.hemisphereW.onMouseNormal(event=event)
            assert suc


def test_addHorizonPoint_1():
    class Test:
        pass
    event = Test()
    event.xdata = 180
    event.ydata = 45
    app.data.horizonP = [(0, 0), (10, 10), (0, 360)]
    suc = app.hemisphereW.addHorizonPoint(data=app.data, event=event)
    assert suc


def test_addHorizonPoint_2():
    class Test:
        pass
    event = Test()
    event.xdata = 180
    event.ydata = 45
    app.data.horizonP = [(0, 0)]
    suc = app.hemisphereW.addHorizonPoint(data=app.data, event=event)
    assert suc


def test_addHorizonPoint_3():
    class Test:
        pass
    event = Test()
    event.xdata = 180
    event.ydata = 45
    suc = app.hemisphereW.addHorizonPoint(data=app.data, event=event)
    assert suc


def test_deleteHorizonPoint_1():
    class Test:
        pass
    event = Test()
    event.xdata = 10
    event.ydata = 10
    app.data.horizonP = [(0, 0), (10, 10), (0, 360)]
    suc = app.hemisphereW.deleteHorizonPoint(data=app.data, event=event)
    assert suc


def test_deleteHorizonPoint_2():
    class Test:
        pass
    event = Test()
    event.xdata = 180
    event.ydata = 45
    app.data.horizonP = [(0, 0), (10, 10), (0, 360)]
    suc = app.hemisphereW.deleteHorizonPoint(data=app.data, event=event)
    assert not suc


def test_deleteHorizonPoint_3():
    class Test:
        pass
    event = Test()
    event.xdata = 180
    event.ydata = 45
    app.data.horizonP = [(0, 0)]
    suc = app.hemisphereW.deleteHorizonPoint(data=app.data, event=event)
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
    app.hemisphereW.horizonMarker = Test()
    app.hemisphereW.horizonFill = Test()
    suc = app.hemisphereW.editHorizonMask(data=app.data, event=event)
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
    app.hemisphereW.horizonMarker = Test()
    app.hemisphereW.horizonFill = Test()
    suc = app.hemisphereW.editHorizonMask(data=app.data, event=event)
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
    app.hemisphereW.horizonMarker = Test()
    app.hemisphereW.horizonFill = Test()
    suc = app.hemisphereW.editHorizonMask(data=app.data, event=event)
    assert not suc


def test_deleteBuildPointPoint_1():
    axes = app.hemisphereW.hemisphereMat.figure.axes[0]
    app.hemisphereW.pointsBuildAnnotate.append(axes.annotate('', xy=(0, 0)))
    app.hemisphereW.pointsBuildAnnotate.append(axes.annotate('', xy=(0, 0)))
    app.hemisphereW.pointsBuildAnnotate.append(axes.annotate('', xy=(0, 0)))

    class Test:
        pass
    event = Test()
    event.xdata = 10
    event.ydata = 10
    app.data.buildP = [(0, 0), (10, 10), (0, 360)]
    suc = app.hemisphereW.deleteBuildPoint(data=app.data, event=event)
    assert suc


def test_deleteBuildPointPoint_2():
    class Test:
        pass
    event = Test()
    event.xdata = 180
    event.ydata = 45
    app.data.buildP = [(0, 0), (10, 10), (0, 360)]
    suc = app.hemisphereW.deleteBuildPoint(data=app.data, event=event)
    assert not suc


def test_editBuildPoints_1():
    axes = app.hemisphereW.hemisphereMat.figure.axes[0]
    app.hemisphereW.pointsBuildAnnotate.append(axes.annotate('', xy=(0, 0)))
    app.hemisphereW.pointsBuildAnnotate.append(axes.annotate('', xy=(0, 0)))
    app.hemisphereW.pointsBuildAnnotate.append(axes.annotate('', xy=(0, 0)))

    class Test:
        def set_data(self, test, test1):
            pass

        def set_xy(self, test):
            pass

    event = Test()
    event.xdata = 180
    event.ydata = 45
    event.button = 1
    app.hemisphereW.pointsBuild = Test()
    suc = app.hemisphereW.editBuildPoints(data=app.data, event=event, axes=axes)
    assert suc


def test_editBuildPoints_2():
    axes = app.hemisphereW.hemisphereMat.figure.axes[0]
    app.hemisphereW.pointsBuildAnnotate.append(axes.annotate('', xy=(0, 0)))
    app.hemisphereW.pointsBuildAnnotate.append(axes.annotate('', xy=(0, 0)))
    app.hemisphereW.pointsBuildAnnotate.append(axes.annotate('', xy=(0, 0)))

    class Test:
        def set_data(self, test, test1):
            pass

        def set_xy(self, test):
            pass

    event = Test()
    event.xdata = 180
    event.ydata = 45
    event.button = 3
    app.hemisphereW.pointsBuild = Test()
    suc = app.hemisphereW.editBuildPoints(data=app.data, event=event, axes=axes)
    assert suc


def test_editBuildPoints_3():
    axes = app.hemisphereW.hemisphereMat.figure.axes[0]
    app.hemisphereW.pointsBuildAnnotate.append(axes.annotate('', xy=(0, 0)))
    app.hemisphereW.pointsBuildAnnotate.append(axes.annotate('', xy=(0, 0)))
    app.hemisphereW.pointsBuildAnnotate.append(axes.annotate('', xy=(0, 0)))

    class Test:
        def set_data(self, test, test1):
            pass

        def set_xy(self, test):
            pass

    event = Test()
    event.xdata = 180
    event.ydata = 45
    event.button = 2
    app.hemisphereW.pointsBuild = Test()
    suc = app.hemisphereW.editBuildPoints(data=app.data, event=event, axes=axes)
    assert not suc


def test_onMouseEdit_1():
    class Test:
        pass
    event = Test()
    event.inaxes = False
    suc = app.hemisphereW.onMouseEdit(event=event)
    assert not suc


def test_onMouseEdit_2():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.dblclick = False
    suc = app.hemisphereW.onMouseEdit(event=event)
    assert not suc


def test_onMouseEdit_2b():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.dblclick = True
    suc = app.hemisphereW.onMouseEdit(event=event)
    assert not suc


def test_onMouseEdit_3():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.dblclick = False
    app.hemisphereW.ui.checkEditHorizonMask.setChecked(False)
    app.hemisphereW.ui.checkEditBuildPoints.setChecked(False)
    with mock.patch.object(app.hemisphereW,
                           'editHorizonMask',
                           return_value=True):
        with mock.patch.object(app.hemisphereW,
                               'editBuildPoints',
                               return_value=True):
            suc = app.hemisphereW.onMouseEdit(event=event)
            assert not suc


def test_onMouseEdit_4():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.dblclick = False
    app.hemisphereW.ui.checkEditHorizonMask.setChecked(True)
    app.hemisphereW.ui.checkEditBuildPoints.setChecked(False)
    with mock.patch.object(app.hemisphereW,
                           'editHorizonMask',
                           return_value=True):
        with mock.patch.object(app.hemisphereW,
                               'editBuildPoints',
                               return_value=True):
            suc = app.hemisphereW.onMouseEdit(event=event)
            assert suc


def test_onMouseEdit_5():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.dblclick = False
    app.hemisphereW.ui.checkEditHorizonMask.setChecked(False)
    app.hemisphereW.ui.checkEditBuildPoints.setChecked(True)
    with mock.patch.object(app.hemisphereW,
                           'editHorizonMask',
                           return_value=True):
        with mock.patch.object(app.hemisphereW,
                               'editBuildPoints',
                               return_value=True):
            suc = app.hemisphereW.onMouseEdit(event=event)
            assert suc


def test_onMouseEdit_6():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.dblclick = False
    app.hemisphereW.ui.checkEditHorizonMask.setChecked(True)
    app.hemisphereW.ui.checkEditBuildPoints.setChecked(False)
    with mock.patch.object(app.hemisphereW,
                           'editHorizonMask',
                           return_value=False):
        with mock.patch.object(app.hemisphereW,
                               'editBuildPoints',
                               return_value=True):
            suc = app.hemisphereW.onMouseEdit(event=event)
            assert not suc


def test_onMouseEdit_7():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.dblclick = False
    app.hemisphereW.ui.checkEditHorizonMask.setChecked(False)
    app.hemisphereW.ui.checkEditBuildPoints.setChecked(True)
    with mock.patch.object(app.hemisphereW,
                           'editHorizonMask',
                           return_value=True):
        with mock.patch.object(app.hemisphereW,
                               'editBuildPoints',
                               return_value=False):
            suc = app.hemisphereW.onMouseEdit(event=event)
            assert not suc


def test_onMouseStar_1():
    class Test:
        pass
    event = Test()
    event.inaxes = False
    event.dblclick = False
    suc = app.hemisphereW.onMouseStar(event=event)
    assert not suc


def test_onMouseStar_2():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.button = 2
    event.dblclick = False
    suc = app.hemisphereW.onMouseStar(event=event)
    assert not suc


def test_onMouseStar_3():
    class Test:
        pass
    event = Test()
    event.inaxes = True
    event.button = 1
    event.dblclick = True
    suc = app.hemisphereW.onMouseStar(event=event)
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
        suc = app.hemisphereW.onMouseStar(event=event)
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
            suc = app.hemisphereW.onMouseStar(event=event)
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
                                   'slewRaDec',
                                   return_value=True):
                suc = app.hemisphereW.onMouseStar(event=event)
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
    suc = app.hemisphereW.onMouseStar(event=event)
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
                                   'slewRaDec',
                                   return_value=False):
                suc = app.hemisphereW.onMouseStar(event=event)
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
                                   'slewRaDec',
                                   return_value=True):
                suc = app.hemisphereW.onMouseStar(event=event)
                assert suc


def test_drawHemisphere_1():
    class Test:
        def set_marker(self, test):
            pass

        def set_color(self, test):
            pass
    app.hemisphereW.horizonMarker = Test()
    app.mainW.genBuildMin()
    app.hemisphereW.drawHemisphere()
