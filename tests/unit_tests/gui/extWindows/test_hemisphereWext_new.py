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
from PyQt5.QtWidgets import QMessageBox
from skyfield.api import Angle

# local import
from tests.baseTestSetup import App
from gui.extWindows.hemisphereW import HemisphereWindow


@pytest.fixture(autouse=True, scope='module')
def module(qapp):
    yield


@pytest.fixture(autouse=True, scope='function')
def function(module):

    window = HemisphereWindow(app=App())
    yield window


def test_markerPoint(function):
    function.markerPoint()


def test_markerAltAz(function):
    function.markerAltAz()


def test_markerStar(function):
    function.markerStar()


def test_configOperationMode_1(function):
    function.ui.checkShowAlignStar.setChecked(True)
    suc = function.configOperationMode()
    assert suc
    assert function.ui.checkPolarAlignment.isEnabled()


def test_configOperationMode_2(function):
    function.ui.checkShowAlignStar.setChecked(False)
    function.ui.checkPolarAlignment.setChecked(True)
    suc = function.configOperationMode()
    assert suc
    assert not function.ui.checkPolarAlignment.isEnabled()
    assert function.ui.checkEditNone.isChecked()


def test_setOperationMode_1(function):
    function.ui.checkEditNone.setChecked(True)
    with mock.patch.object(function,
                           'drawHemisphere'):
        suc = function.setOperationMode()
        assert suc
        assert function.operationMode == 'normal'


def test_setOperationMode_2(function):
    function.ui.checkEditBuildPoints.setChecked(True)
    with mock.patch.object(function,
                           'drawHemisphere'):
        suc = function.setOperationMode()
        assert suc
        assert function.operationMode == 'build'


def test_setOperationMode_3(function):
    function.ui.checkEditHorizonMask.setChecked(True)
    with mock.patch.object(function,
                           'drawHemisphere'):
        suc = function.setOperationMode()
        assert suc
        assert function.operationMode == 'horizon'


def test_setOperationMode_4(function):
    function.ui.checkPolarAlignment.setChecked(True)
    with mock.patch.object(function,
                           'drawHemisphere'):
        suc = function.setOperationMode()
        assert suc
        assert function.operationMode == 'star'


def test_showMouseCoordinates_1(function):
    class Event:
        xdata = 1
        ydata = None

    suc = function.showMouseCoordinates(Event())
    assert not suc


def test_showMouseCoordinates_2(function):
    class Event:
        xdata = None
        ydata = 1

    suc = function.showMouseCoordinates(Event())
    assert not suc


def test_showMouseCoordinates_3(function):
    class Event:
        xdata = 10
        ydata = 10

    suc = function.showMouseCoordinates(Event())
    assert suc
    assert function.ui.azimuth.text() == '10.0'
    assert function.ui.altitude.text() == '10.0'


def test_slewDialog_1(function):
    with mock.patch.object(QMessageBox,
                           'question',
                           return_value=QMessageBox.No):
        suc = function.slewDialog(10, 10)
        assert not suc


def test_slewDialog_2(function):
    with mock.patch.object(QMessageBox,
                           'question',
                           return_value=QMessageBox.Yes):
        suc = function.slewDialog(10, 10)
        assert suc


def test_slewSelectedTarget_1(function):
    with mock.patch.object(function.app.mount.obsSite,
                           'setTargetAltAz',
                           return_value=False):
        suc = function.slewSelectedTarget(10, 10)
        assert not suc


def test_slewSelectedTarget_2(function):
    function.app.mount.obsSite.haJNowTarget = 0
    function.app.mount.obsSite.decJNowTarget = 0
    function.app.mount.obsSite.piersideTarget = 'E'
    function.app.mount.obsSite.location.latitude = Angle(degrees=0)
    with mock.patch.object(function.app.mount.obsSite,
                           'setTargetAltAz',
                           return_value=True):
        with mock.patch.object(function.app.dome,
                               'slewDome',
                               return_value=5):
            suc = function.slewSelectedTarget(10, 10)
            assert not suc


def test_slewSelectedTarget_3(function):
    function.app.mount.obsSite.haJNowTarget = 0
    function.app.mount.obsSite.decJNowTarget = 0
    function.app.mount.obsSite.piersideTarget = 'E'
    function.app.mount.obsSite.location.latitude = Angle(degrees=0)
    with mock.patch.object(function.app.mount.obsSite,
                           'setTargetAltAz',
                           return_value=True):
        with mock.patch.object(function.app.dome,
                               'slewDome',
                               return_value=5):
            with mock.patch.object(function.app.mount.obsSite,
                                   'startSlewing',
                                   return_value=True):
                suc = function.slewSelectedTarget(10, 10)
                assert suc


def test_onMouseNormal_1(function):
    class Event:
        xdata = 10
        ydata = 10
        inaxes = False
        dblclick = False
        button = 0

    suc = function.onMouseNormal(Event())
    assert not suc


def test_onMouseNormal_2(function):
    class Event:
        xdata = 10
        ydata = 10
        inaxes = True
        dblclick = True
        button = 0

    suc = function.onMouseNormal(Event())
    assert not suc


def test_onMouseNormal_3(function):
    class Event:
        xdata = 10
        ydata = 10
        inaxes = True
        dblclick = False
        button = 1

    suc = function.onMouseNormal(Event())
    assert not suc


def test_onMouseNormal_4(function):
    class Event:
        xdata = 10
        ydata = 10
        inaxes = True
        dblclick = True
        button = 1

    with mock.patch.object(function,
                           'slewDialog',
                           return_value=False):
        suc = function.onMouseNormal(Event())
        assert not suc


def test_onMouseNormal_5(function):
    class Event:
        xdata = 10
        ydata = 10
        inaxes = True
        dblclick = True
        button = 1

    with mock.patch.object(function,
                           'slewDialog',
                           return_value=True):
        with mock.patch.object(function,
                               'slewSelectedTarget',
                               return_value=False):
            suc = function.onMouseNormal(Event())
            assert not suc


def test_onMouseNormal_6(function):
    class Event:
        xdata = 10
        ydata = 10
        inaxes = True
        dblclick = True
        button = 1

    with mock.patch.object(function,
                           'slewDialog',
                           return_value=True):
        with mock.patch.object(function,
                               'slewSelectedTarget',
                               return_value=True):
            suc = function.onMouseNormal(Event())
            assert suc
