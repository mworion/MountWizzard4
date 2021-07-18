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
# written in python3, (c) 2019-2021 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
import unittest.mock as mock

# external packages
from PyQt5.QtCore import QThreadPool, QObject, pyqtSignal
from mountcontrol.mount import Mount
from skyfield.api import Angle
import numpy as np

# local import
from logic.dome.dome import Dome


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    class Test(QObject):
        threadPool = QThreadPool()
        message = pyqtSignal(str, int)
        update1s = pyqtSignal()
        mount = Mount(host='localhost', MAC='00:00:00:00:00:00', verbose=False,
                      pathToData='tests/data')
    global app
    app = Dome(app=Test())

    yield

    app.threadPool.waitForDone(1000)


def test_properties_1():
    app.settlingTime = 1
    assert app.settlingTime == 1


def test_startCommunication_1():
    app.framework = ''
    suc = app.startCommunication()
    assert not suc


def test_startCommunication_2():
    app.framework = 'indi'
    suc = app.startCommunication()
    assert not suc


def test_stopCommunication_1():
    app.framework = ''
    suc = app.stopCommunication()
    assert not suc


def test_stopCommunication_2():
    app.framework = 'indi'
    app.app.update1s.connect(app.checkSlewingDome)
    suc = app.stopCommunication()
    assert suc


def test_waitSettlingAndEmit():
    suc = app.waitSettlingAndEmit()
    assert suc


def test_checkSlewingDome_1():
    app.data['Slewing'] = False
    with mock.patch.object(app.settlingWait,
                           'start'):
        suc = app.checkSlewingDome()
        assert suc


def test_checkSlewingDome_2():
    app.isSlewing = True
    app.data['Slewing'] = False
    with mock.patch.object(app.settlingWait,
                           'start'):
        suc = app.checkSlewingDome()
        assert suc


def test_checkSlewingDome_3():
    app.data['Slewing'] = True
    with mock.patch.object(app.settlingWait,
                           'start'):
        suc = app.checkSlewingDome()
        assert suc


def test_checkSlewingDome_4():
    app.counterStartSlewing = 0
    app.isSlewing = False
    app.data['Slewing'] = False
    with mock.patch.object(app.settlingWait,
                           'start'):
        suc = app.checkSlewingDome()
        assert suc


def test_checkTargetConditions_1():
    app.overshoot = None
    app.targetShutterDist = None
    app.shutterZenithDist = None
    app.radius = None
    app.shutterWidth = None
    suc = app.checkTargetConditions()
    assert not suc


def test_checkTargetConditions_2():
    app.overshoot = None
    app.targetShutterDist = 0.1
    app.shutterZenithDist = None
    app.radius = None
    app.shutterWidth = None
    suc = app.checkTargetConditions()
    assert not suc


def test_checkTargetConditions_3():
    app.overshoot = None
    app.targetShutterDist = 0.1
    app.shutterZenithDist = 0.2
    app.radius = None
    app.shutterWidth = None
    suc = app.checkTargetConditions()
    assert not suc


def test_checkTargetConditions_4():
    app.overshoot = 0
    app.targetShutterDist = 0.1
    app.shutterZenithDist = 0.2
    app.radius = None
    app.shutterWidth = None
    suc = app.checkTargetConditions()
    assert not suc


def test_checkTargetConditions_5():
    app.overshoot = 0
    app.targetShutterDist = 0.1
    app.shutterZenithDist = 0.2
    app.radius = 1.5
    app.shutterWidth = None
    suc = app.checkTargetConditions()
    assert not suc


def test_checkTargetConditions_6():
    app.overshoot = 0
    app.targetShutterDist = 0.5
    app.shutterZenithDist = 0.2
    app.radius = 1.5
    app.shutterWidth = 0.8
    suc = app.checkTargetConditions()
    assert not suc


def test_checkTargetConditions_7():
    app.overshoot = 0
    app.targetShutterDist = 0.1
    app.shutterZenithDist = 0.2
    app.radius = 1.5
    app.shutterWidth = 0.8
    suc = app.checkTargetConditions()
    assert suc


def test_calcTargetRectanglePoints_1():
    app.targetShutterDist = 0.1
    app.shutterZenithDist = 0.2
    app.radius = 10
    app.shutterWidth = 1.2
    a, b, c = app.calcTargetRectanglePoints(0)
    assert a[0] == -0.1
    assert a[1] == 0.5
    assert b[0] == 10
    assert b[1] == 0.5
    assert c[0] == 10
    assert c[1] == -0.5


def test_calcTargetRectanglePoints_2():
    app.targetShutterDist = 0.1
    app.shutterZenithDist = 0.2
    app.radius = 10
    app.shutterWidth = 1.2
    a, b, c = app.calcTargetRectanglePoints(90)
    assert round(a[0], 5) == 0.5
    assert round(a[1], 5) == 0.1
    assert round(b[0], 5) == 0.5
    assert round(b[1], 5) == -10
    assert round(c[0], 5) == -0.5
    assert round(c[1], 5) == -10


def test_targetInDomeShutter_1():
    A = np.array([0, 0])
    B = np.array([0, 3])
    C = np.array([4, 3])
    M = np.array([2, 1])
    suc = app.targetInDomeShutter(A, B, C, M)
    assert suc


def test_targetInDomeShutter_2():
    A = np.array([0, 0])
    B = np.array([0, 3])
    C = np.array([4, 3])
    M = np.array([5, 4])
    suc = app.targetInDomeShutter(A, B, C, M)
    assert not suc


def test_targetInDomeShutter_3():
    A = np.array([0, 0])
    B = np.array([0, 3])
    C = np.array([4, 3])
    M = np.array([2, 3])
    suc = app.targetInDomeShutter(A, B, C, M)
    assert suc


def test_targetInDomeShutter_4():
    A = np.array([2, 0])
    B = np.array([0, 2])
    C = np.array([3, 5])
    M = np.array([0, 0])
    suc = app.targetInDomeShutter(A, B, C, M)
    assert not suc


def test_targetInDomeShutter_5():
    A = np.array([2, 0])
    B = np.array([0, 2])
    C = np.array([3, 5])
    M = np.array([2, 2])
    suc = app.targetInDomeShutter(A, B, C, M)
    assert suc


def test_checkSlewNeeded_1():
    with mock.patch.object(app,
                           'checkTargetConditions',
                           return_value=False):
        suc = app.checkSlewNeeded(0, 0)
        assert not suc


def test_checkSlewNeeded_2():
    with mock.patch.object(app,
                           'checkTargetConditions',
                           return_value=True):
        with mock.patch.object(app,
                               'calcTargetRectanglePoints',
                               return_value=(0, 1, 2)):
            with mock.patch.object(app,
                                   'targetInDomeShutter',
                                   return_value=False):
                suc = app.checkSlewNeeded(0, 0)
                assert not suc


def test_checkSlewNeeded_3():
    with mock.patch.object(app,
                           'checkTargetConditions',
                           return_value=True):
        with mock.patch.object(app,
                               'calcTargetRectanglePoints',
                               return_value=(0, 1, 2)):
            with mock.patch.object(app,
                                   'targetInDomeShutter',
                                   return_value=True):
                suc = app.checkSlewNeeded(0, 0)
                assert suc


def test_slewDome_0():
    app.data = {}
    suc = app.slewDome()
    assert not suc


def test_slewDome_1():
    app.data = {}
    suc = app.slewDome()
    assert not suc


def test_slewDome_2():
    app.data = {'AZ': 1}
    app.framework = 'indi'
    suc = app.slewDome()
    assert not suc


def test_slewDome_3():
    app.data = {'AZ': 1}
    app.framework = 'indi'
    app.useGeometry = True

    with mock.patch.object(app.app.mount,
                           'calcTransformationMatricesTarget',
                           return_value=(Angle(degrees=10), Angle(degrees=10),
                                         [0, 0, 0], None, None)):
        val = app.slewDome(altitude=0, azimuth=0)
        assert val == -10


def test_slewDome_4():
    app.data = {'AZ': 1}
    app.framework = 'indi'
    app.useGeometry = True

    with mock.patch.object(app.app.mount,
                           'calcTransformationMatricesTarget',
                           return_value=(None, Angle(degrees=10),
                                         [0, 0, 0], None, None)):
        val = app.slewDome(altitude=0, azimuth=0)
        assert val == 0


def test_slewDome_5():
    app.data = {'AZ': 1}
    app.framework = 'indi'
    app.useGeometry = True

    with mock.patch.object(app.app.mount,
                           'calcTransformationMatricesTarget',
                           return_value=(Angle(degrees=10), None,
                                         [0, 0, 0], None, None)):
        val = app.slewDome(altitude=0, azimuth=0)
        assert val == 0


def test_followDome_0():
    app.data = {}
    suc = app.followDome()
    assert not suc


def test_followDome_1():
    app.data = {}
    suc = app.followDome()
    assert not suc


def test_followDome_2():
    app.data = {'AZ': 1}
    app.framework = 'indi'
    suc = app.followDome()
    assert not suc


def test_followDome_3():
    app.data = {'AZ': 1}
    app.framework = 'indi'
    app.useGeometry = True

    with mock.patch.object(app.app.mount,
                           'calcTransformationMatricesActual',
                           return_value=(Angle(degrees=10), Angle(degrees=10),
                                         [0, 0, 0], None, None)):
        val = app.followDome(altitude=0, azimuth=0)
        assert val == -10


def test_followDome_4():
    app.data = {'AZ': 1}
    app.framework = 'indi'
    app.useGeometry = True

    with mock.patch.object(app.app.mount,
                           'calcTransformationMatricesActual',
                           return_value=(None, Angle(degrees=10),
                                         [0, 0, 0], None, None)):
        val = app.followDome(altitude=0, azimuth=0)
        assert val == 0


def test_followDome_5():
    app.data = {'AZ': 1}
    app.framework = 'indi'
    app.useGeometry = True

    with mock.patch.object(app.app.mount,
                           'calcTransformationMatricesActual',
                           return_value=(Angle(degrees=10), None,
                                         [0, 0, 0], None, None)):
        val = app.followDome(altitude=0, azimuth=0)
        assert val == 0


def test_openShutter_1():
    app.data = {}
    suc = app.openShutter()
    assert not suc


def test_openShutter_2():
    app.data = {'AZ': 1}
    app.framework = 'indi'
    with mock.patch.object(app.run['indi'],
                           'openShutter',
                           return_value=False):
        suc = app.openShutter()
        assert not suc


def test_openShutter_3():
    app.data = {'AZ': 1}
    app.framework = 'indi'
    with mock.patch.object(app.run['indi'],
                           'openShutter',
                           return_value=True):
        suc = app.openShutter()
        assert suc


def test_closeShutter_1():
    app.data = {}
    suc = app.closeShutter()
    assert not suc


def test_closeShutter_2():
    app.data = {'AZ': 1}
    app.framework = 'indi'
    with mock.patch.object(app.run['indi'],
                           'closeShutter',
                           return_value=False):
        suc = app.closeShutter()
        assert not suc


def test_closeShutter_3():
    app.data = {'AZ': 1}
    app.framework = 'indi'
    with mock.patch.object(app.run['indi'],
                           'closeShutter',
                           return_value=True):
        suc = app.closeShutter()
        assert suc


def test_abortSlew_1():
    app.data = {}
    suc = app.abortSlew()
    assert not suc


def test_abortSlew_2():
    app.data = {'AZ': 1}
    app.framework = 'indi'
    with mock.patch.object(app.run['indi'],
                           'abortSlew',
                           return_value=False):
        suc = app.abortSlew()
        assert not suc


def test_abortSlew_3():
    app.data = {'AZ': 1}
    app.framework = 'indi'
    with mock.patch.object(app.run['indi'],
                           'abortSlew',
                           return_value=True):
        suc = app.abortSlew()
        assert suc
