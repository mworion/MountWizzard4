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
import numpy as np
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
    app.mainW.ui.checkMeasurement.setChecked(True)
    app.environment.wDevice['local']['data'] = {}
    app.environment.wDevice['sqm']['data'] = {}
    app.measure._measureTask()
    assert app.measure.data['temp'].shape[0]
    assert app.measure.data['humidity'].shape[0]
    assert app.measure.data['press'].shape[0]
    assert app.measure.data['dewTemp'].shape[0]
    assert app.measure.data['sqr'].shape[0]


def test_measureTask_2():
    app.mainW.ui.checkMeasurement.setChecked(True)
    app.environment.wDevice['local']['data']['WEATHER_TEMPERATURE'] = 10
    app.environment.wDevice['local']['data']['WEATHER_BAROMETER'] = 1000
    app.environment.wDevice['local']['data']['WEATHER_DEWPOINT'] = 10
    app.environment.wDevice['local']['data']['WEATHER_HUMIDITY'] = 10
    app.environment.wDevice['sqm']['data']['SKY_BRIGHTNESS'] = 19
    app.measure._measureTask()
    assert app.measure.data['temp'][0] == 10
    assert app.measure.data['humidity'][0] == 10
    assert app.measure.data['press'][0] == 1000
    assert app.measure.data['dewTemp'][0] == 10
    assert app.measure.data['sqr'][0] == 19


def test_measureTask_3():
    app.mainW.ui.checkMeasurement.setChecked(False)
    app.environment.wDevice['local']['data'] = {}
    app.environment.wDevice['sqm']['data'] = {}
    app.measure._measureTask()
    assert app.measure.data['temp'].shape[0] == 0
    assert app.measure.data['humidity'].shape[0] == 0
    assert app.measure.data['press'].shape[0] == 0
    assert app.measure.data['dewTemp'].shape[0] == 0
    assert app.measure.data['sqr'].shape[0] == 0


def test_calculateReference_1():
    app.measure.raRef = 0
    app.measure.decRef = 0
    app.mount.obsSite.raJNow = 1
    app.mount.obsSite.decJNow = 1
    app.measure.data['status'] = np.array([])
    ra, dec = app.measure._calculateReference()
    assert ra == 0
    assert dec == 0


def test_calculateReference_2():
    app.measure.raRef = 0
    app.measure.decRef = 0
    app.mount.obsSite.raJNow = 1
    app.mount.obsSite.decJNow = 1
    app.measure.data['status'] = np.array([0, 0, 0, 0, 0])
    ra, dec = app.measure._calculateReference()
    assert ra == 3600
    assert dec == 3600


def test_calculateReference_3():
    app.measure.raRef = 1800
    app.measure.decRef = 1800
    app.mount.obsSite.raJNow = 1
    app.mount.obsSite.decJNow = 1
    app.measure.data['status'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    ra, dec = app.measure._calculateReference()
    assert ra == 1800
    assert dec == 1800


def test_calculateReference_4():
    app.measure.raRef = 1800
    app.measure.decRef = 1800
    app.mount.obsSite.raJNow = 1
    app.mount.obsSite.decJNow = 1
    app.measure.data['status'] = np.array([0, 0, 0, 0, 1, 0, 0, 0])
    ra, dec = app.measure._calculateReference()
    assert ra == 0
    assert dec == 0
    assert app.measure.raRef is None
    assert app.measure.decRef is None


def test_calculateReference_5():
    app.measure.raRef = None
    app.measure.decRef = None
    app.mount.obsSite.raJNow = 1
    app.mount.obsSite.decJNow = 1
    app.measure.data['status'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    ra, dec = app.measure._calculateReference()
    assert ra == 0
    assert dec == 0
    assert app.measure.raRef is not None
    assert app.measure.decRef is not None

