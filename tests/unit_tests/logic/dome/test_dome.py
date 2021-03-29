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
                           'calcTransformationMatrices',
                           return_value=(Angle(degrees=10), Angle(degrees=10),
                                         [0, 0, 0], None, None)):
        val = app.slewDome(altitude=0, azimuth=0)
        assert val == -10


def test_slewDome_4():
    app.data = {'AZ': 1}
    app.framework = 'indi'
    app.useGeometry = True

    with mock.patch.object(app.app.mount,
                           'calcTransformationMatrices',
                           return_value=(None, Angle(degrees=10),
                                         [0, 0, 0], None, None)):
        val = app.slewDome(altitude=0, azimuth=0)
        assert val == 0


def test_slewDome_5():
    app.data = {'AZ': 1}
    app.framework = 'indi'
    app.useGeometry = True

    with mock.patch.object(app.app.mount,
                           'calcTransformationMatrices',
                           return_value=(Angle(degrees=10), None,
                                         [0, 0, 0], None, None)):
        val = app.slewDome(altitude=0, azimuth=0)
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
