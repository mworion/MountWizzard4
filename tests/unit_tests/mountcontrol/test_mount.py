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
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
import os

# external packages
from skyfield.api import Topos

# local imports
from mountcontrol.mount import Mount


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    global m
    m = Mount(host='127.0.0.1',
              pathToData=os.getcwd() + '/data',
              verbose=True)
    yield


def test_properties():
    m.host = 'localhost'
    assert m.host == ('localhost', 3492)

    m.MAC = '00:00:00:00:00:00'
    assert m.MAC == '00:00:00:00:00:00'


def test_checkFormatHost_1():
    val = m.checkFormatHost(None)
    assert val is None


def test_checkFormatHost_2():
    val = m.checkFormatHost(123)
    assert val is None


def test_checkFormatHost_3():
    val = m.checkFormatHost('localhost')
    assert val == ('localhost', 3492)


def test_checkFormatHost_4():
    val = m.checkFormatHost(('localhost', 3492))
    assert val == ('localhost', 3492)


def test_checkFormatMAC_1():
    val = m.checkFormatMAC('')
    assert val is None


def test_checkFormatMAC_2():
    val = m.checkFormatMAC(1234)
    assert val is None


def test_checkFormatMAC_3():
    val = m.checkFormatMAC('00:00:00')
    assert val is None


def test_checkFormatMAC_4():
    val = m.checkFormatMAC('00:00:00:123:00:00')
    assert val is None


def test_checkFormatMAC_5():
    val = m.checkFormatMAC('00:00:00:12K:00:00')
    assert val is None


def test_checkFormatMAC_6():
    val = m.checkFormatMAC('00:00:00:12:00:00')
    assert val == '00:00:00:12:00:00'


def test_checkFormatMAC_7():
    val = m.checkFormatMAC('00:L0:00:12:00:00')
    assert val is None


def test_resetData():
    m.resetData()


def test_calcTransformationMatrices():
    m.obsSite.raJNowTarget = 12
    m.obsSite.timeSidereal = 12
    m.obsSite.decJNowTarget = 10
    m.obsSite.location = Topos(latitude_degrees=49,
                               longitude_degrees=11,
                               elevation_m=500)
    m.obsSite.piersideTarget = 'E'
    val = m.calcTransformationMatrices()
    assert val[0] is None
    assert val[1] is None
    assert val[2] is None
    assert val[3] is None
    assert val[4] is None
