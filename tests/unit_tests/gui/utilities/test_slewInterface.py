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
import unittest.mock as mock
import pytest

# external packages
from skyfield.api import Angle

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.utilities.slewInterface import SlewInterface


@pytest.fixture(autouse=True, scope='function')
def function(qapp):

    func = SlewInterface()
    func.app = App()
    func.msg = func.app.msg
    yield func


def test_slewSelectedTargetWithDome_0(function):
    function.app.mount.obsSite.AltTarget = None
    function.app.deviceStat['dome'] = None
    suc = function.slewSelectedTargetWithDome()
    assert not suc


def test_slewSelectedTargetWithDome_2(function):
    function.app.mount.obsSite.AltTarget = Angle(degrees=10)
    function.app.mount.obsSite.AzTarget = Angle(degrees=10)
    function.app.deviceStat['dome'] = False
    with mock.patch.object(function.app.mount.obsSite,
                           'startSlewing',
                           return_value=True):
        suc = function.slewSelectedTargetWithDome()
        assert suc


def test_slewSelectedTargetWithDome_3(function):
    function.app.mount.obsSite.AltTarget = Angle(degrees=10)
    function.app.mount.obsSite.AzTarget = Angle(degrees=10)
    function.app.deviceStat['dome'] = False
    with mock.patch.object(function.app.mount.obsSite,
                           'startSlewing',
                           return_value=False):
        suc = function.slewSelectedTargetWithDome()
        assert not suc


def test_slewSelectedTargetWithDome_4(function):
    function.app.mount.obsSite.AltTarget = Angle(degrees=10)
    function.app.mount.obsSite.AzTarget = Angle(degrees=10)
    function.app.deviceStat['dome'] = True
    with mock.patch.object(function.app.mount.obsSite,
                           'startSlewing',
                           return_value=False):
        with mock.patch.object(function.app.dome,
                               'slewDome',
                               return_value=10):
            suc = function.slewSelectedTargetWithDome()
            assert not suc


def test_slewTargetAltAz_1(function):
    with mock.patch.object(function.app.mount.obsSite,
                           'setTargetAltAz',
                           return_value=False):
        with mock.patch.object(function,
                               'slewSelectedTargetWithDome',
                               return_value=False):
            suc = function.slewTargetAltAz(100, 10)
            assert not suc


def test_slewTargetAltAz_2(function):
    with mock.patch.object(function.app.mount.obsSite,
                           'setTargetAltAz',
                           return_value=False):
        with mock.patch.object(function,
                               'slewSelectedTargetWithDome',
                               return_value=True):
            suc = function.slewTargetAltAz(-10, 10)
            assert not suc


def test_slewTargetAltAz_3(function):
    with mock.patch.object(function.app.mount.obsSite,
                           'setTargetAltAz',
                           return_value=True):
        with mock.patch.object(function,
                               'slewSelectedTargetWithDome',
                               return_value=True):
            suc = function.slewTargetAltAz(100, 10)
            assert suc


def test_slewTargetRaDec_0(function):
    temp = function.app.mount.obsSite.timeJD
    function.app.mount.obsSite.timeJD = None

    suc = function.slewTargetRaDec(Angle(hours=10), Angle(degrees=10))
    assert not suc
    function.app.mount.obsSite.timeJD = temp


def test_slewTargetRaDec_1(function):
    with mock.patch.object(function.app.mount.obsSite,
                           'setTargetRaDec',
                           return_value=False):
        with mock.patch.object(function,
                               'slewSelectedTargetWithDome',
                               return_value=False):
            suc = function.slewTargetRaDec(Angle(hours=10), Angle(degrees=10))
            assert not suc


def test_slewTargetRaDec_2(function):
    with mock.patch.object(function.app.mount.obsSite,
                           'setTargetRaDec',
                           return_value=False):
        with mock.patch.object(function,
                               'slewSelectedTargetWithDome',
                               return_value=True):
            suc = function.slewTargetRaDec(Angle(hours=-10), Angle(degrees=10))
            assert not suc


def test_slewTargetRaDec_3(function):
    with mock.patch.object(function.app.mount.obsSite,
                           'setTargetRaDec',
                           return_value=True):
        with mock.patch.object(function,
                               'slewSelectedTargetWithDome',
                               return_value=True):
            suc = function.slewTargetRaDec(Angle(hours=10), Angle(degrees=10))
            assert suc


def test_slewTargetRaDec_4(function):
    with mock.patch.object(function.app.mount.obsSite,
                           'setTargetRaDec',
                           return_value=True):
        with mock.patch.object(function,
                               'slewSelectedTargetWithDome',
                               return_value=True):
            suc = function.slewTargetRaDec(Angle(hours=10), Angle(degrees=10),
                                           epoch='JNow')
            assert suc


def test_slewTargetRaDec_5(function):
    with mock.patch.object(function.app.mount.obsSite,
                           'setTargetRaDec',
                           return_value=True):
        with mock.patch.object(function,
                               'slewSelectedTargetWithDome',
                               return_value=True):
            suc = function.slewTargetRaDec(10, 10,
                                           epoch='JNow')
            assert suc
