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

# external packages

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from logic.modeldata.hipparcos import Hipparcos


@pytest.fixture(autouse=True, scope='function')
def function():
    func = Hipparcos(app=App())
    yield func


def test_data_available(function):
    assert len(function.alignStars) > 0


def test_calculateAlignStarPositionsAltAz_1(function):
    star = dict()
    star['Achernar'] = [0.42636313743386084, -0.9989721040992605, 4.267359632399454e-07,
                        -1.9431237114262957e-07, 0.022680000001570513, 4.512483521476569e-05]
    function.alignStars = star

    function.calculateAlignStarPositionsAltAz()
    assert ['Achernar'] == function.name


def test_calculateAlignStarPositionsAltAz_2(function):
    star = dict()
    star['Achernar'] = [0.42636313743386084, -0.9989721040992605, 4.267359632399454e-07,
                        -1.9431237114262957e-07, 0.022680000001570513, 4.512483521476569e-05]
    star['Acrux'] = [3.257647500944081, -1.1012877251083137, -1.7147915360582993e-07,
                     -7.141291885025191e-08, 0.010169999999992536, 0.00018371089505169385]
    function.alignStars = star

    function.calculateAlignStarPositionsAltAz()
    assert ['Achernar', 'Acrux'] == function.name


def test_calculateAlignStarPositionsAltAz_3(function):
    star = dict()
    star['Achernar'] = [0.42636313743386084, -0.9989721040992605, 4.267359632399454e-07,
                        -1.9431237114262957e-07, 0.022680000001570513, 4.512483521476569e-05]
    star['Acrux'] = [3.257647500944081, -1.1012877251083137, -1.7147915360582993e-07,
                     -7.141291885025191e-08, 0.010169999999992536, 0.00018371089505169385]
    function.alignStars = star
    temp = function.app.mount.obsSite.location
    function.app.mount.obsSite.location = None
    suc = function.calculateAlignStarPositionsAltAz()
    assert not suc
    function.app.mount.obsSite.location = temp


def test_getAlignStarRaDecFromName_1(function):
    star = dict()
    star['Achernar'] = [0.42636313743386084, -0.9989721040992605, 4.267359632399454e-07,
                        -1.9431237114262957e-07, 0.022680000001570513, 4.512483521476569e-05]
    star['Acrux'] = [3.257647500944081, -1.1012877251083137, -1.7147915360582993e-07,
                     -7.141291885025191e-08, 0.010169999999992536, 0.00018371089505169385]
    function.alignStars = star
    ra, dec = function.getAlignStarRaDecFromName('Achernar')
    assert ra is not None
    assert dec is not None


def test_getAlignStarRaDecFromName_2(function):
    star = dict()
    star['Achernar'] = [0.42636313743386084, -0.9989721040992605, 4.267359632399454e-07,
                        -1.9431237114262957e-07, 0.022680000001570513, 4.512483521476569e-05]
    star['Acrux'] = [3.257647500944081, -1.1012877251083137, -1.7147915360582993e-07,
                     -7.141291885025191e-08, 0.010169999999992536, 0.00018371089505169385]
    function.alignStars = star
    ra, dec = function.getAlignStarRaDecFromName('Test')
    assert ra is None
    assert dec is None
