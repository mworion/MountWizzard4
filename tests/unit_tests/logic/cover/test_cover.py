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

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from logic.cover.cover import Cover


@pytest.fixture(autouse=True, scope='function')
def function():
    func = Cover(app=App())
    yield func


def test_properties(function):
    function.framework = 'indi'
    function.host = ('localhost', 7624)
    assert function.host == ('localhost', 7624)

    function.deviceName = 'test'
    assert function.deviceName == 'test'


def test_properties_2(function):
    function.updateRate = 1000
    function.loadConfig = True
    function.framework = 'indi'
    assert function.updateRate == 1000
    assert function.loadConfig


def test_startCommunication_1(function):
    function.framework = ''
    suc = function.startCommunication()
    assert not suc


def test_startCommunication_2(function):
    function.framework = 'indi'
    with mock.patch.object(function.run['indi'],
                           'startCommunication',
                           return_value=True):
        suc = function.startCommunication()
        assert suc


def test_stopCommunication_1(function):
    function.framework = ''
    suc = function.stopCommunication()
    assert not suc


def test_stopCommunication_2(function):
    function.framework = 'indi'
    with mock.patch.object(function.run['indi'],
                           'stopCommunication',
                           return_value=True):
        suc = function.stopCommunication()
        assert suc


def test_closeCover_1(function):
    function.framework = ''
    suc = function.closeCover()
    assert not suc


def test_closeCover_2(function):
    function.framework = 'indi'
    with mock.patch.object(function.run['indi'],
                           'closeCover',
                           return_value=False):
        suc = function.closeCover()
        assert not suc


def test_closeCover_3(function):
    function.framework = 'indi'
    with mock.patch.object(function.run['indi'],
                           'closeCover',
                           return_value=True):
        suc = function.closeCover()
        assert suc


def test_openCover_1(function):
    function.framework = ''
    suc = function.openCover()
    assert not suc


def test_openCover_2(function):
    function.framework = 'indi'
    with mock.patch.object(function.run['indi'],
                           'openCover',
                           return_value=False):
        suc = function.openCover()
        assert not suc


def test_openCover_3(function):
    function.framework = 'indi'
    with mock.patch.object(function.run['indi'],
                           'openCover',
                           return_value=True):
        suc = function.openCover()
        assert suc


def test_haltCover_1(function):
    function.framework = ''
    suc = function.haltCover()
    assert not suc


def test_haltCover_2(function):
    function.framework = 'indi'
    with mock.patch.object(function.run['indi'],
                           'haltCover',
                           return_value=False):
        suc = function.haltCover()
        assert not suc


def test_haltCover_3(function):
    function.framework = 'indi'
    with mock.patch.object(function.run['indi'],
                           'haltCover',
                           return_value=True):
        suc = function.haltCover()
        assert suc


def test_lightOn_1(function):
    function.framework = ''
    suc = function.lightOn()
    assert not suc


def test_lightOn_2(function):
    function.framework = 'indi'
    with mock.patch.object(function.run['indi'],
                           'lightOn',
                           return_value=False):
        suc = function.lightOn()
        assert not suc


def test_lightOn_3(function):
    function.framework = 'indi'
    with mock.patch.object(function.run['indi'],
                           'lightOn',
                           return_value=True):
        suc = function.lightOn()
        assert suc


def test_lightOff_1(function):
    function.framework = ''
    suc = function.lightOff()
    assert not suc


def test_lightOff_2(function):
    function.framework = 'indi'
    with mock.patch.object(function.run['indi'],
                           'lightOff',
                           return_value=False):
        suc = function.lightOff()
        assert not suc


def test_lightOff_3(function):
    function.framework = 'indi'
    with mock.patch.object(function.run['indi'],
                           'lightOff',
                           return_value=True):
        suc = function.lightOff()
        assert suc


def test_lightIntensity_1(function):
    function.framework = ''
    suc = function.lightIntensity(0)
    assert not suc


def test_lightIntensity_2(function):
    function.framework = 'indi'
    with mock.patch.object(function.run['indi'],
                           'lightIntensity',
                           return_value=False):
        suc = function.lightIntensity(0)
        assert not suc


def test_lightIntensity_3(function):
    function.framework = 'indi'
    with mock.patch.object(function.run['indi'],
                           'lightIntensity',
                           return_value=True):
        suc = function.lightIntensity(0)
        assert suc
