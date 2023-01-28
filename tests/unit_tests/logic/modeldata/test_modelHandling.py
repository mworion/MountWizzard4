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
from skyfield.api import Star, Angle
from mountcontrol.modelStar import ModelStar
from mountcontrol.model import Model

# local import
from logic.modeldata.modelHandling import writeRetrofitData
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope='function')
def function():
    yield


def test_writeRetrofitData_1(function):
    val = writeRetrofitData({}, {})
    assert val == {}


def test_writeRetrofitData_2(function):
    model = Model()
    stars = list()
    a = ModelStar()
    a.obsSite = App().mount.obsSite
    a.coord = Star(ra_hours=0, dec_degrees=0)
    a.errorAngle = Angle(degrees=0)
    a.errorRMS = 1
    a.number = 1
    stars.append(a)
    model._starList = stars
    model.terms = 22
    model.errorRMS = 10
    model.orthoError = 10
    model.polarError = 10

    val = writeRetrofitData(model, [{}])
    assert val

