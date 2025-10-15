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
from PyQt5.QtCore import QThreadPool, QObject, pyqtSignal

# local import
from mw4.indibase.indiBase import Device


@pytest.fixture(autouse=True, scope='function')
def function():
    function = Device()
    yield function


def test_getNumber_0(function):
    function.testNumberVec = {'propertyType': 'defNumberVector',
                              'elementList':
                                  {
                                    'test1': {'value': 10, },
                                  },
                              }
    val = function.getNumber('testNumberVec')
    assert val == {'test1': 10}


def test_getNumber_1(function):
    function.testNumberVec = {'propertyType': 'setNumberVector',
                              'elementList':
                                  {
                                    'test1': {'value': 10, },
                                  },
                              }
    val = function.getNumber('testNumberVec')
    assert val == {'test1': 10}


def test_getNumber_2(function):
    function.testNumberVec = {'propertyType': 'setNumberVector',
                              'elementList':
                                  {
                                    'test1': {'value': 10, },
                                  },
                              }
    val = function.getNumber('test')
    assert val == {}


def test_getNumber_3(function):
    function.testNumberVec = {'propertyType': 'test',
                              'elementList':
                                  {
                                    'test1': {'value': 10, },
                                  },
                              }
    val = function.getNumber('testNumberVec')
    assert val == {}


def test_getNumber_4(function):
    function.testNumberVec = {'propertyType': 'setNumberVector',
                              'elementList': {},
                              }
    val = function.getNumber('testNumberVec')
    assert val == {}


def test_getText_0(function):
    function.testTextVec = {'propertyType': 'defTextVector',
                            'elementList':
                                {
                                  'test1': {'value': 'test', },
                                },
                            }
    val = function.getText('testTextVec')
    assert val == {'test1': 'test'}


def test_getText_1(function):
    function.testTextVec = {'propertyType': 'setTextVector',
                            'elementList':
                                {
                                  'test1': {'value': 'test', },
                                },
                            }
    val = function.getText('testTextVec')
    assert val == {'test1': 'test'}


def test_getText_2(function):
    function.testTextVec = {'propertyType': 'setTextVector',
                            'elementList':
                                {
                                  'test1': {'value': 'test', },
                                },
                            }
    val = function.getText('test')
    assert val == {}


def test_getText_3(function):
    function.testTextVec = {'propertyType': 'test',
                            'elementList':
                                {
                                  'test1': {'value': 'test', },
                                },
                            }
    val = function.getText('testTextVec')
    assert val == {}


def test_getText_4(function):
    function.testTextVec = {'propertyType': 'setTextVector',
                            'elementList': {},
                            }
    val = function.getText('testTextVec')
    assert val == {}


def test_getSwitch_0(function):
    function.testSwitchVec = {'propertyType': 'defSwitchVector',
                              'elementList':
                                  {
                                    'test1': {'value': 'On', },
                                  },
                              }
    val = function.getSwitch('testSwitchVec')
    assert val == {'test1': 'On'}


def test_getSwitch_1(function):
    function.testSwitchVec = {'propertyType': 'setSwitchVector',
                              'elementList':
                                  {
                                    'test1': {'value': 'On', },
                                  },
                              }
    val = function.getSwitch('testSwitchVec')
    assert val == {'test1': 'On'}


def test_getSwitch_2(function):
    function.testSwitchVec = {'propertyType': 'setSwitchVector',
                              'elementList':
                                  {
                                    'test1': {'value': 'On', },
                                  },
                              }
    val = function.getSwitch('test')
    assert val == {}


def test_getSwitch_3(function):
    function.testSwitchVec = {'propertyType': 'test',
                              'elementList':
                                  {
                                    'test1': {'value': 'On', },
                                  },
                              }
    val = function.getSwitch('testSwitchVec')
    assert val == {}


def test_getSwitch_4(function):
    function.testSwitchVec = {'propertyType': 'setSwitchVector',
                              'elementList': {},
                              }
    val = function.getSwitch('testSwitchVec')
    assert val == {}


def test_getLight_0(function):
    function.testLightVec = {'propertyType': 'defLightVector',
                             'elementList':
                                 {
                                   'test1': {'value': 'On', },
                                 },
                             }
    val = function.getLight('testLightVec')
    assert val == {'test1': 'On'}


def test_getLight_1(function):
    function.testLightVec = {'propertyType': 'setLightVector',
                             'elementList':
                                 {
                                   'test1': {'value': 'On', },
                                 },
                             }
    val = function.getLight('testLightVec')
    assert val == {'test1': 'On'}


def test_getLight_2(function):
    function.testLightVec = {'propertyType': 'setLightVector',
                             'elementList':
                                 {
                                   'test1': {'value': 'On', },
                                 },
                             }
    val = function.getLight('test')
    assert val == {}


def test_getLight_3(function):
    function.testLightVec = {'propertyType': 'test',
                             'elementList':
                                 {
                                   'test1': {'value': 'On', },
                                 },
                             }
    val = function.getLight('testLightVec')
    assert val == {}


def test_getLight_4(function):
    function.testLightVec = {'propertyType': 'setLightVector',
                             'elementList': {},
                             }
    val = function.getLight('testLightVec')
    assert val == {}


def test_getBlob_0(function):
    function.testBLOBVec = {'propertyType': 'defBLOBVector',
                            'elementList':
                                {
                                  'testBLOBVec': {'value': 'test', },
                                },
                            }
    val = function.getBlob('testBLOBVec')
    assert val == {'value': 'test'}


def test_getBlob_1(function):
    function.testBLOBVec = {'propertyType': 'setBLOBVector',
                            'elementList':
                                {
                                  'testBLOBVec': {'value': 'test', },
                                },
                            }
    val = function.getBlob('testBLOBVec')
    assert val == {'value': 'test'}


def test_getBlob_2(function):
    function.testBLOBVec = {'propertyType': 'setBLOBVector',
                            'elementList':
                                {
                                  'testBLOBVec': {'value': 'test', },
                                },
                            }
    val = function.getBlob('test')
    assert val == {}


def test_getBlob_3(function):
    function.testBLOBVec = {'propertyType': 'test',
                            'elementList':
                                {
                                  'testBLOBVec': {'value': 'test', },
                                },
                            }
    val = function.getBlob('testBLOBVec')
    assert val == {}
