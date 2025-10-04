############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest

# external packages
from skyfield.api import Angle, Star

# local import
from mw4.logic.modelBuild.modelHandling import writeRetrofitData
from mw4.mountcontrol.model import Model
from mw4.mountcontrol.modelStar import ModelStar
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="function")
def function():
    yield


def test_writeRetrofitData_1(function):
    val = writeRetrofitData({}, {})
    assert val == {}


def test_writeRetrofitData_2(function):
    class Parent:
        obsSite = App().mount.obsSite

    model = Model(parent=Parent())
    a = ModelStar(
        coord=Star(ra_hours=0, dec_degrees=0),
        errorAngle=Angle(degrees=0),
        errorRMS=1,
        number=1,
        obsSite=App().mount.obsSite,
    )
    model.addStar(a)
    model.terms = 22
    model.errorRMS = 10
    model.orthoError = 10
    model.polarError = 10

    val = writeRetrofitData(model, [{}])
    assert val
