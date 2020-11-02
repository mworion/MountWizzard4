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
    app.framework = 'indi'

    app.host = ('localhost', 7624)
    assert app.host == ('localhost', 7624)

    app.deviceName = 'test'
    assert app.deviceName == 'test'


def test_properties_2():
    app.framework = 'test'

    app.host = ('localhost', 7624)
    assert app.host == ('localhost', 7624)

    app.deviceName = 'test'
    assert app.deviceName == 'test'


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
    app.isGeometry = True

    with mock.patch.object(app.app.mount,
                           'calcTransformationMatrices',
                           return_value=(Angle(degrees=10), Angle(degrees=10), 0, 0, 0)):
        val = app.slewDome(altitude=0, azimuth=0)
        assert val == -10


def test_slewDome_4():
    app.data = {'AZ': 1}
    app.framework = 'indi'
    app.isGeometry = True

    with mock.patch.object(app.app.mount,
                           'calcTransformationMatrices',
                           return_value=(None, Angle(degrees=10), 0, 0, 0)):
        val = app.slewDome(altitude=0, azimuth=0)
        assert val == 0


def test_slewDome_5():
    app.data = {'AZ': 1}
    app.framework = 'indi'
    app.isGeometry = True

    with mock.patch.object(app.app.mount,
                           'calcTransformationMatrices',
                           return_value=(Angle(degrees=10), None, 0, 0, 0)):
        val = app.slewDome(altitude=0, azimuth=0)
        assert val == 0
