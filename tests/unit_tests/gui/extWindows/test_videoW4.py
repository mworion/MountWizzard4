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
#
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest

# external packages

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.extWindows.videoW1 import VideoWindow1


@pytest.fixture(autouse=True, scope='function')
def function(qapp):
    func = VideoWindow1(app=App())
    yield func


def test_initConfig_1(function):
    suc = function.initConfig()
    assert suc


def test_initConfig_2(function):
    suc = function.initConfig()
    assert suc

    function.app.config['videoW4'] = {'winPosX': 10000}
    suc = function.initConfig()
    assert suc


def test_initConfig_3(function):
    suc = function.initConfig()
    assert suc

    function.app.config['videoW4'] = {'winPosY': 10000}
    suc = function.initConfig()
    assert suc


def test_initConfig_4(function):
    function.app.config['videoW4'] = {}
    function.app.config['videoW4']['winPosX'] = 100
    function.app.config['videoW4']['winPosY'] = 100
    suc = function.initConfig()
    assert suc


def test_storeConfig_1(function):
    if 'videoW4' in function.app.config:
        del function.app.config['videoW4']

    suc = function.storeConfig()
    assert suc


def test_storeConfig_2(function):
    function.app.config['videoW4'] = {}

    suc = function.storeConfig()
    assert suc

