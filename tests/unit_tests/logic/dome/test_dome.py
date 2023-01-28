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

# external packages
from skyfield.api import Angle
import numpy as np

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from logic.dome.dome import Dome


@pytest.fixture(autouse=True, scope='function')
def function():
    func = Dome(app=App())
    yield func


def test_properties_1(function):
    function.settlingTime = 1
    assert function.settlingTime == 1


def test_properties_2(function):
    function.updateRate = 1000
    function.loadConfig = True
    function.framework = 'indi'
    assert function.updateRate == 1000
    assert function.loadConfig


def test_startCommunication_1(function):
    function.domeStarted = False
    function.framework = ''
    suc = function.startCommunication()
    assert not suc
    assert not function.domeStarted


def test_startCommunication_2(function):
    function.framework = 'indi'
    function.domeStarted = False
    with mock.patch.object(function.run['indi'],
                           'startCommunication',
                           return_value=False):
        suc = function.startCommunication()
        assert not suc
        assert function.domeStarted


def test_startCommunication_3(function):
    function.framework = 'indi'
    function.domeStarted = False
    with mock.patch.object(function.run['indi'],
                           'startCommunication',
                           return_value=True):
        suc = function.startCommunication()
        assert suc
        assert function.domeStarted


def test_stopCommunication_1(function):
    function.framework = ''
    suc = function.stopCommunication()
    assert not suc


def test_stopCommunication_2(function):
    function.framework = 'indi'
    function.domeStarted = True
    function.app.update1s.connect(function.checkSlewingDome)
    with mock.patch.object(function.run['indi'],
                           'startCommunication',
                           return_value=True):
        suc = function.stopCommunication()
        assert suc
        assert not function.domeStarted


def test_stopCommunication_3(function):
    function.framework = 'indi'
    function.domeStarted = True
    function.app.update1s.connect(function.checkSlewingDome)
    with mock.patch.object(function.run['indi'],
                           'startCommunication',
                           return_value=False):
        suc = function.stopCommunication()
        assert suc
        assert not function.domeStarted


def test_waitSettlingAndEmit(function):
    suc = function.waitSettlingAndEmit()
    assert suc


def test_checkSlewingDome_1(function):
    function.data['Slewing'] = False
    with mock.patch.object(function.settlingWait,
                           'start'):
        suc = function.checkSlewingDome()
        assert suc


def test_checkSlewingDome_2(function):
    function.isSlewing = True
    function.data['Slewing'] = False
    with mock.patch.object(function.settlingWait,
                           'start'):
        suc = function.checkSlewingDome()
        assert suc


def test_checkSlewingDome_3(function):
    function.data['Slewing'] = True
    with mock.patch.object(function.settlingWait,
                           'start'):
        suc = function.checkSlewingDome()
        assert suc


def test_checkSlewingDome_4(function):
    function.counterStartSlewing = 0
    function.isSlewing = False
    function.data['Slewing'] = False
    with mock.patch.object(function.settlingWait,
                           'start'):
        suc = function.checkSlewingDome()
        assert suc


def test_checkTargetConditions_1(function):
    function.overshoot = None
    function.openingHysteresis = None
    function.clearanceZenith = None
    function.radius = None
    function.clearOpening = None
    suc = function.checkTargetConditions()
    assert not suc


def test_checkTargetConditions_2(function):
    function.overshoot = None
    function.openingHysteresis = 0.1
    function.clearanceZenith = None
    function.radius = None
    function.clearOpening = None
    suc = function.checkTargetConditions()
    assert not suc


def test_checkTargetConditions_3(function):
    function.overshoot = None
    function.openingHysteresis = 0.1
    function.clearanceZenith = 0.2
    function.radius = None
    function.clearOpening = None
    suc = function.checkTargetConditions()
    assert not suc


def test_checkTargetConditions_4(function):
    function.overshoot = 0
    function.openingHysteresis = 0.1
    function.clearanceZenith = 0.2
    function.radius = None
    function.clearOpening = None
    suc = function.checkTargetConditions()
    assert not suc


def test_checkTargetConditions_5(function):
    function.overshoot = 0
    function.openingHysteresis = 0.1
    function.clearanceZenith = 0.2
    function.radius = 1.5
    function.clearOpening = None
    suc = function.checkTargetConditions()
    assert not suc


def test_checkTargetConditions_6(function):
    function.overshoot = 0
    function.openingHysteresis = 0.5
    function.clearanceZenith = 0.2
    function.radius = 1.5
    function.clearOpening = 0.8
    suc = function.checkTargetConditions()
    assert not suc


def test_checkTargetConditions_7(function):
    function.overshoot = 0
    function.openingHysteresis = 0.1
    function.clearanceZenith = 0.2
    function.radius = 1.5
    function.clearOpening = 0.8
    suc = function.checkTargetConditions()
    assert suc


def test_calcTargetRectanglePoints_1(function):
    function.openingHysteresis = 0.1
    function.clearanceZenith = 0.2
    function.radius = 10
    function.clearOpening = 1.2
    a, b, c = function.calcTargetRectanglePoints(0)
    assert a[0] == -0.1
    assert a[1] == 0.5
    assert b[0] == 10
    assert b[1] == 0.5
    assert c[0] == 10
    assert c[1] == -0.5


def test_calcTargetRectanglePoints_2(function):
    function.openingHysteresis = 0.1
    function.clearanceZenith = 0.2
    function.radius = 10
    function.clearOpening = 1.2
    a, b, c = function.calcTargetRectanglePoints(90)
    assert round(a[0], 5) == 0.5
    assert round(a[1], 5) == 0.1
    assert round(b[0], 5) == 0.5
    assert round(b[1], 5) == -10
    assert round(c[0], 5) == -0.5
    assert round(c[1], 5) == -10


def test_targetInDomeShutter_1(function):
    A = np.array([0, 0])
    B = np.array([0, 3])
    C = np.array([4, 3])
    M = np.array([2, 1])
    suc = function.targetInDomeShutter(A, B, C, M)
    assert suc


def test_targetInDomeShutter_2(function):
    A = np.array([0, 0])
    B = np.array([0, 3])
    C = np.array([4, 3])
    M = np.array([5, 4])
    suc = function.targetInDomeShutter(A, B, C, M)
    assert not suc


def test_targetInDomeShutter_3(function):
    A = np.array([0, 0])
    B = np.array([0, 3])
    C = np.array([4, 3])
    M = np.array([2, 3])
    suc = function.targetInDomeShutter(A, B, C, M)
    assert suc


def test_targetInDomeShutter_4(function):
    A = np.array([2, 0])
    B = np.array([0, 2])
    C = np.array([3, 5])
    M = np.array([0, 0])
    suc = function.targetInDomeShutter(A, B, C, M)
    assert not suc


def test_targetInDomeShutter_5(function):
    A = np.array([2, 0])
    B = np.array([0, 2])
    C = np.array([3, 5])
    M = np.array([2, 2])
    suc = function.targetInDomeShutter(A, B, C, M)
    assert suc


def test_checkSlewNeeded_1(function):
    with mock.patch.object(function,
                           'checkTargetConditions',
                           return_value=False):
        suc = function.checkSlewNeeded(0, 0)
        assert suc


def test_checkSlewNeeded_2(function):
    with mock.patch.object(function,
                           'checkTargetConditions',
                           return_value=True):
        with mock.patch.object(function,
                               'calcTargetRectanglePoints',
                               return_value=(0, 1, 2)):
            with mock.patch.object(function,
                                   'targetInDomeShutter',
                                   return_value=False):
                suc = function.checkSlewNeeded(0, 0)
                assert suc


def test_checkSlewNeeded_3(function):
    with mock.patch.object(function,
                           'checkTargetConditions',
                           return_value=True):
        with mock.patch.object(function,
                               'calcTargetRectanglePoints',
                               return_value=(0, 1, 2)):
            with mock.patch.object(function,
                                   'targetInDomeShutter',
                                   return_value=True):
                suc = function.checkSlewNeeded(0, 0)
                assert not suc


def test_checkSlewNeeded_4(function):
    function.data['ABS_DOME_POSITION.DOME_ABSOLUTE_POSITION'] = 0
    function.openingHysteresis = 0.0
    function.clearanceZenith = 0.3
    function.radius = 1.5
    function.clearOpening = 0.8
    with mock.patch.object(function,
                           'checkTargetConditions',
                           return_value=True):
        suc = function.checkSlewNeeded(0, 0)
        assert not suc


def test_calcSlewTarget_1(function):
    def func():
        return None, Angle(degrees=10), [5, 10, 0], None, None

    azimuth = 20
    altitude = 20
    function.useGeometry = False
    alt, az, x, y = function.calcSlewTarget(azimuth, altitude, func)
    assert alt == 20
    assert az == 20
    assert x is None
    assert y is None


def test_calcSlewTarget_2(function):
    def func():
        return None, Angle(degrees=10), [5, 10, 0], None, None

    azimuth = 20
    altitude = 20
    function.useGeometry = True

    alt, az, x, y = function.calcSlewTarget(azimuth, altitude, func)
    assert alt == 20
    assert az == 20
    assert x == 5
    assert y == 10


def test_calcSlewTarget_3(function):
    def func():
        return Angle(degrees=10), Angle(degrees=10), [5, 10, 0], None, None

    azimuth = 20
    altitude = 20
    function.useGeometry = True

    alt, az, x, y = function.calcSlewTarget(azimuth, altitude, func)
    assert alt == 10
    assert az == 10
    assert x == 5
    assert y == 10


def test_calcOvershoot_1(function):
    function.overshoot = False
    val = function.calcOvershoot(100)
    assert val == 100
    assert function.lastFinalAz is None


def test_calcOvershoot_2(function):
    function.overshoot = True
    function.avoidFirstSlewOvershoot = True
    val = function.calcOvershoot(100)
    assert val == 100
    assert not function.avoidFirstSlewOvershoot
    assert function.lastFinalAz is None


def test_calcOvershoot_3(function):
    function.clearOpening = 0.8
    function.openingHysteresis = 0.2
    function.radius = 1.5
    function.avoidFirstSlewOvershoot = False
    function.overshoot = True
    function.app.mount.obsSite.AzDirection = None
    val = function.calcOvershoot(100)
    assert val == 100


def test_calcOvershoot_4(function):
    function.clearOpening = 0.8
    function.openingHysteresis = 0.2
    function.radius = 1.5
    function.avoidFirstSlewOvershoot = False
    function.overshoot = True
    function.lastFinalAz = None
    function.app.mount.obsSite.AzDirection = 1
    val = function.calcOvershoot(100)
    assert round(val, 3) == 107.595


def test_calcOvershoot_5(function):
    function.clearOpening = 0.8
    function.openingHysteresis = 0.2
    function.radius = 1.5
    function.avoidFirstSlewOvershoot = False
    function.overshoot = True
    function.lastFinalAz = 10
    function.app.mount.obsSite.AzDirection = 1
    val = function.calcOvershoot(100)
    assert round(val, 3) == 107.595


def test_calcOvershoot_6(function):
    function.clearOpening = 0.8
    function.openingHysteresis = 0.2
    function.radius = 1.5
    function.avoidFirstSlewOvershoot = False
    function.app.mount.obsSite.AzDirection = 1
    function.overshoot = True
    function.lastFinalAz = 10
    val = function.calcOvershoot(30)
    assert round(val, 3) == 37.595


def test_calcOvershoot_7(function):
    function.clearOpening = 0.8
    function.openingHysteresis = 0.2
    function.radius = 1.5
    function.avoidFirstSlewOvershoot = False
    function.app.mount.obsSite.AzDirection = -1
    function.overshoot = True
    function.lastFinalAz = 10
    val = function.calcOvershoot(30)
    assert round(val, 3) == 22.405


def test_calcOvershoot_8(function):
    function.clearOpening = 0.8
    function.openingHysteresis = 0.2
    function.radius = 1.5
    function.avoidFirstSlewOvershoot = False
    function.app.mount.obsSite.AzDirection = -1
    function.overshoot = True
    function.lastFinalAz = 10
    val = function.calcOvershoot(15)
    assert round(val, 3) == 10


def test_slewDome_1(function):
    function.data = {}
    suc = function.slewDome()
    assert not suc


def test_slewDome_2(function):
    function.data = {'AZ': 1}
    function.framework = 'indi'
    val = (10, 10, None, None)
    with mock.patch.object(function,
                           'calcSlewTarget',
                           return_value=val):
        with mock.patch.object(function.run['indi'],
                               'slewToAltAz',
                               return_value=val):
            delta = function.slewDome(0, 0, False)
            assert delta == -10


def test_slewDome_3(function):
    function.data = {'AZ': 1}
    function.framework = 'indi'
    function.useDynamicFollowing = True
    val = (10, 10, 0, 0)
    with mock.patch.object(function,
                           'calcSlewTarget',
                           return_value=val):
        with mock.patch.object(function.run['indi'],
                               'slewToAltAz',
                               return_value=val):
            with mock.patch.object(function,
                                   'checkSlewNeeded',
                                   return_value=False):
                delta = function.slewDome(0, 0, False)
                assert delta == -10


def test_slewDome_4(function):
    function.data = {'AZ': 1}
    function.framework = 'indi'
    function.useDynamicFollowing = True
    val = (10, 10, 0, 0)
    with mock.patch.object(function,
                           'calcSlewTarget',
                           return_value=val):
        with mock.patch.object(function.run['indi'],
                               'slewToAltAz',
                               return_value=val):
            with mock.patch.object(function,
                                   'checkSlewNeeded',
                                   return_value=False):
                delta = function.slewDome(0, 0, True)
                assert delta == -10


def test_avoidFirstOvershoot(function):
    function.avoidFirstSlewOvershoot = False
    suc = function.avoidFirstOvershoot()
    assert suc
    assert function.avoidFirstSlewOvershoot


def test_openShutter_1(function):
    function.data = {}
    suc = function.openShutter()
    assert not suc


def test_openShutter_2(function):
    function.data = {'AZ': 1}
    function.framework = 'indi'
    with mock.patch.object(function.run['indi'],
                           'openShutter',
                           return_value=False):
        suc = function.openShutter()
        assert not suc


def test_openShutter_3(function):
    function.data = {'AZ': 1}
    function.framework = 'indi'
    with mock.patch.object(function.run['indi'],
                           'openShutter',
                           return_value=True):
        suc = function.openShutter()
        assert suc


def test_closeShutter_1(function):
    function.data = {}
    suc = function.closeShutter()
    assert not suc


def test_closeShutter_2(function):
    function.data = {'AZ': 1}
    function.framework = 'indi'
    with mock.patch.object(function.run['indi'],
                           'closeShutter',
                           return_value=False):
        suc = function.closeShutter()
        assert not suc


def test_closeShutter_3(function):
    function.data = {'AZ': 1}
    function.framework = 'indi'
    with mock.patch.object(function.run['indi'],
                           'closeShutter',
                           return_value=True):
        suc = function.closeShutter()
        assert suc


def test_slewCW_1(function):
    function.data = {}
    suc = function.slewCW()
    assert not suc


def test_slewCW_2(function):
    function.data = {'AZ': 1}
    function.framework = 'indi'
    with mock.patch.object(function.run['indi'],
                           'slewCW',
                           return_value=False):
        suc = function.slewCW()
        assert not suc


def test_slewCW_3(function):
    function.data = {'AZ': 1}
    function.framework = 'indi'
    with mock.patch.object(function.run['indi'],
                           'slewCW',
                           return_value=True):
        suc = function.slewCW()
        assert suc


def test_slewCCW_1(function):
    function.data = {}
    suc = function.slewCCW()
    assert not suc


def test_slewCCW_2(function):
    function.data = {'AZ': 1}
    function.framework = 'indi'
    with mock.patch.object(function.run['indi'],
                           'slewCCW',
                           return_value=False):
        suc = function.slewCCW()
        assert not suc


def test_slewCCW_3(function):
    function.data = {'AZ': 1}
    function.framework = 'indi'
    with mock.patch.object(function.run['indi'],
                           'slewCCW',
                           return_value=True):
        suc = function.slewCCW()
        assert suc


def test_abortSlew_1(function):
    function.data = {}
    suc = function.abortSlew()
    assert not suc


def test_abortSlew_2(function):
    function.data = {'AZ': 1}
    function.framework = 'indi'
    with mock.patch.object(function.run['indi'],
                           'abortSlew',
                           return_value=False):
        suc = function.abortSlew()
        assert not suc


def test_abortSlew_3(function):
    function.data = {'AZ': 1}
    function.framework = 'indi'
    with mock.patch.object(function.run['indi'],
                           'abortSlew',
                           return_value=True):
        suc = function.abortSlew()
        assert suc
