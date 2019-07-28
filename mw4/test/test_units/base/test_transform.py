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
# Python  v3.7.4
#
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
# standard libraries
from unittest import mock
import time
import pytest
# external packages
# local import
from mw4.test.test_units.setupQt import setupQt
from mw4.base import tpool


@pytest.fixture(autouse=True, scope='module')
def module_setup_teardown():
    global app, spy, mwGlob, test, host
    app, spy, mwGlob, test = setupQt()
    host_ip = '192.168.2.250'
    host = (host_ip, 80)
    yield


def test_JNowToJ2000_1():
    pass


def test_J2000T0JNow():
    pass


def test_J2000T0AltAz():
    pass


def test_checkIsHours():
    pass


def test_stringT0Degree():
    pass


def test_convertToAngle():
    pass


def test_convertToDMS():
    pass


def test_convertToHMS():
    pass


def test_sphericalToCartesian():
    pass


def test_cartesianToSpherical():
    pass


def test_polarToCartesian():
    pass


def test_cartesianToPolar():
    pass
