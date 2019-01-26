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
# Python  v3.6.7
#
# Michael Würtenberger
# (c) 2018
#
# Licence APL2.0
#
###########################################################
# standard libraries
from unittest import mock
import pytest
# external packages
import PyQt5.QtWidgets
# local import
from mw4 import mainApp

test = PyQt5.QtWidgets.QApplication([])

mwGlob = {'workDir': '.',
          'configDir': './mw4/test/config',
          'dataDir': './mw4/test/config',
          'modeldata': 'test',
          }


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    global app
    app = mainApp.MountWizzard4(mwGlob=mwGlob)
    yield


def test_measureTask_1():
    app.environment.wDevice['local']['data'] = {}
    app.environment.wDevice['sqm']['data'] = {}
    app.measure._measureTask()
    assert 0 == app.measure.data['temp']
    assert 0 == app.measure.data['humidity']
    assert 0 == app.measure.data['press']
    assert 0 == app.measure.data['dewTemp']
    assert 0 == app.measure.data['sqr']


def test_measureTask_2():
    app.environment.wDevice['local']['data']['WEATHER_TEMPERATURE'] = 10
    app.environment.wDevice['local']['data']['WEATHER_BAROMETER'] = 1000
    app.environment.wDevice['local']['data']['WEATHER_DEWPOINT'] = 10
    app.environment.wDevice['local']['data']['WEATHER_HUMIDITY'] = 10
    app.environment.wDevice['sqm']['data']['SKY_BRIGHTNESS'] = 19
    app.measure._measureTask()
    assert 10 == app.measure.data['temp'][0]
    assert 10 == app.measure.data['humidity'][0]
    assert 1000 == app.measure.data['press'][0]
    assert 10 == app.measure.data['dewTemp'][0]
    assert 19 == app.measure.data['sqr'][0]


def test_measureTask_3():
    app.measure.raRef = 0
    app.measure.decRef = 0
    app.mount.obsSite.raJNow = 1
    app.mount.obsSite.decJNow = 1
    app.mount.obsSite.status = 1
    app.measure._measureTask()
    assert 0 == app.measure.data['raJNow']
    assert 0 == app.measure.data['decJNow']


def test_measureTask_4():
    app.measure.raRef = 0
    app.measure.decRef = 0
    app.mount.obsSite.raJNow = 1
    app.mount.obsSite.decJNow = 1
    app.mount.obsSite.status = 0
    app.measure._measureTask()
    assert 3600 == app.measure.data['raJNow'][0]
    assert 3600 == app.measure.data['decJNow'][0]


def test_measureTask_5():
    app.measure.raRef = 1800
    app.measure.decRef = 1800
    app.mount.obsSite.raJNow = 1
    app.mount.obsSite.decJNow = 1
    app.mount.obsSite.status = 0
    app.measure._measureTask()
    assert 1800 == app.measure.data['raJNow'][0]
    assert 1800 == app.measure.data['decJNow'][0]
