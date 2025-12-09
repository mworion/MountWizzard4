############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10_micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################

import json
import os
import shutil
import unittest.mock as mock

import pytest


import requests

from mw4.base.loggerMW import setupLogging
from mw4.logic.environment.boltwoodWeather import BoltwoodWeather


from tests.unit_tests.unitTestAddOns.baseTestApp import App

setupLogging()


@pytest.fixture(autouse=True, scope="function")
def function():
    func = BoltwoodWeather(app=App())
    yield func


def test_startCommunication_(function):
    function.enabled = False
    with mock.patch.object(function, "pollBoltwoodData"):
        function.startCommunication()
        assert function.enabled


def test_stopCommunication_1(function):
    function.running = True
    function.enabled = True
    function.stopCommunication()
    assert not function.running
    assert not function.enabled

