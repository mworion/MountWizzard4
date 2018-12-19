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
# local import
from mw4 import mainApp

test = PyQt5.QtWidgets.QApplication([])

mwGlob = {'workDir': '.',
          'configDir': './mw4/test/config/',
          'build': 'test',
          }

'''
@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    global spy
    global app
    app = mainApp.MountWizzard4(mwGlob=mwGlob)
    spy = PyQt5.QtTest.QSignalSpy(app.message)
    yield
    spy = None
    app = None
'''

app = mainApp.MountWizzard4(mwGlob=mwGlob)
spy = PyQt5.QtTest.QSignalSpy(app.message)


#
#
# testing mainW gui booting shutdown
#
#


def test_resizeEvent(qtbot):
    app.hemisphereW.resizeEvent(None)


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


def test_clearHemisphere(qtbot):
    app.data.buildP = [(0, 0), (1, 0)]
    app.hemisphereW.clearHemisphere()
    assert app.data.buildP == []


def test_drawCanvas(qtbot):
    app.hemisphereW.drawHemisphere()
    suc = app.hemisphereW.drawCanvas()
    assert suc


def test_drawCanvasMoving(qtbot):
    app.hemisphereW.drawHemisphere()
    suc = app.hemisphereW.drawCanvasMoving()
    assert suc


def test_drawCanvasStar(qtbot):
    app.hemisphereW.drawHemisphere()
    suc = app.hemisphereW.drawCanvasStar()
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


def test_markerPoint():
    val = app.hemisphereW.markerPoint()
    assert isinstance(val, matplotlib.path.Path)


def test_markerAltAz():
    val = app.hemisphereW.markerAltAz()
    assert isinstance(val, matplotlib.path.Path)
