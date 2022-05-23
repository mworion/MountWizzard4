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
# written in python3, (c) 2019-2022 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
import unittest.mock as mock

# external packages
from PyQt5.QtCore import QThreadPool, QObject, pyqtSignal

# local import
from logic.cover.cover import Cover


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    class Test(QObject):
        threadPool = QThreadPool()
        message = pyqtSignal(str, int)
        messageN = pyqtSignal(object, object, object, object)

    global app
    app = Cover(app=Test())

    yield

    app.threadPool.waitForDone(1000)


def test_properties():
    app.framework = 'indi'
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
    with mock.patch.object(app.run['indi'],
                           'startCommunication',
                           return_value=True):
        suc = app.startCommunication()
        assert suc


def test_stopCommunication_1():
    app.framework = ''
    suc = app.stopCommunication()
    assert not suc


def test_stopCommunication_2():
    app.framework = 'indi'
    with mock.patch.object(app.run['indi'],
                           'stopCommunication',
                           return_value=True):
        suc = app.stopCommunication()
        assert suc


def test_closeCover_1():
    app.framework = ''
    suc = app.closeCover()
    assert not suc


def test_closeCover_2():
    app.framework = 'indi'
    with mock.patch.object(app.run['indi'],
                           'closeCover',
                           return_value=False):
        suc = app.closeCover()
        assert not suc


def test_closeCover_3():
    app.framework = 'indi'
    with mock.patch.object(app.run['indi'],
                           'closeCover',
                           return_value=True):
        suc = app.closeCover()
        assert suc


def test_openCover_1():
    app.framework = ''
    suc = app.openCover()
    assert not suc


def test_openCover_2():
    app.framework = 'indi'
    with mock.patch.object(app.run['indi'],
                           'openCover',
                           return_value=False):
        suc = app.openCover()
        assert not suc


def test_openCover_3():
    app.framework = 'indi'
    with mock.patch.object(app.run['indi'],
                           'openCover',
                           return_value=True):
        suc = app.openCover()
        assert suc


def test_haltCover_1():
    app.framework = ''
    suc = app.haltCover()
    assert not suc


def test_haltCover_2():
    app.framework = 'indi'
    with mock.patch.object(app.run['indi'],
                           'haltCover',
                           return_value=False):
        suc = app.haltCover()
        assert not suc


def test_haltCover_3():
    app.framework = 'indi'
    with mock.patch.object(app.run['indi'],
                           'haltCover',
                           return_value=True):
        suc = app.haltCover()
        assert suc


def test_lightOn_1():
    app.framework = ''
    suc = app.lightOn()
    assert not suc


def test_lightOn_2():
    app.framework = 'indi'
    with mock.patch.object(app.run['indi'],
                           'lightOn',
                           return_value=False):
        suc = app.lightOn()
        assert not suc


def test_lightOn_3():
    app.framework = 'indi'
    with mock.patch.object(app.run['indi'],
                           'lightOn',
                           return_value=True):
        suc = app.lightOn()
        assert suc


def test_lightOff_1():
    app.framework = ''
    suc = app.lightOff()
    assert not suc


def test_lightOff_2():
    app.framework = 'indi'
    with mock.patch.object(app.run['indi'],
                           'lightOff',
                           return_value=False):
        suc = app.lightOff()
        assert not suc


def test_lightOff_3():
    app.framework = 'indi'
    with mock.patch.object(app.run['indi'],
                           'lightOff',
                           return_value=True):
        suc = app.lightOff()
        assert suc


def test_lightIntensity_1():
    app.framework = ''
    suc = app.lightIntensity(0)
    assert not suc


def test_lightIntensity_2():
    app.framework = 'indi'
    with mock.patch.object(app.run['indi'],
                           'lightIntensity',
                           return_value=False):
        suc = app.lightIntensity(0)
        assert not suc


def test_lightIntensity_3():
    app.framework = 'indi'
    with mock.patch.object(app.run['indi'],
                           'lightIntensity',
                           return_value=True):
        suc = app.lightIntensity(0)
        assert suc
