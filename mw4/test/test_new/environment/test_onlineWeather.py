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
# Python  v3.7.5
#
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
import unittest.mock as mock
import json

# external packages
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal
import requests
from skyfield.toposlib import Topos

# local import
from mw4.environment.onlineWeather import OnlineWeather


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    class Test2:
        location = Topos(latitude_degrees=20,
                         longitude_degrees=10,
                         elevation_m=500)
    class Test1:
        obsSite = Test2()
    class Test(QObject):
        threadPool = QThreadPool()
        message = pyqtSignal(str, int)
        update10s = pyqtSignal()
        mount = Test1()
    global app
    app = OnlineWeather(app=Test())
    yield
    del app


def test_properties():
    app.keyAPI = 'test'
    assert app.keyAPI == 'test'
    app.online = True
    assert app.online


def test_startCommunication_1():
    app.running = False
    suc = app.startCommunication()
    assert suc
    assert app.running


def test_stopCommunication_1():
    app.running = True
    suc = app.stopCommunication()
    assert suc
    assert not app.running


def test_getDewPoint_1():
    val = app.getDewPoint(-100, 10)
    assert not val


def test_getDewPoint_2():
    val = app.getDewPoint(100, 10)
    assert not val


def test_getDewPoint_3():
    val = app.getDewPoint(10, -10)
    assert not val


def test_getDewPoint_4():
    val = app.getDewPoint(10, 110)
    assert not val


def test_getDewPoint_5():
    val = app.getDewPoint(10, 10)
    assert val == -20.216642415771897


def test_updateOpenWeatherMapDataWorker_1():
    suc = app.updateOpenWeatherMapDataWorker()
    assert not suc


def test_updateOpenWeatherMapDataWorker_2():
    data = {'test': {}}
    suc = app.updateOpenWeatherMapDataWorker(data=data)
    assert not suc


def test_updateOpenWeatherMapDataWorker_3():
    entry = {'main': {'temp': 290,
                      'grnd_level': 1000,
                      'humidity': 50},
             'clouds': {'all': 100},
             'wind': {'speed': 10,
                      'deg': 260},
             'rain': {'3h': 10}
             }
    data = {'list': [entry]}
    suc = app.updateOpenWeatherMapDataWorker(data=data)
    assert suc


def test_getOpenWeatherMapDataWorker_1():
    val = app.getOpenWeatherMapDataWorker()
    assert val is None


def test_getOpenWeatherMapDataWorker_2():
    val = app.getOpenWeatherMapDataWorker('http://localhost')
    assert val is None


def test_getOpenWeatherMapDataWorker_3():
    class Test:
        status_code = 300
    with mock.patch.object(requests,
                           'get',
                           return_value=Test()):
        val = app.getOpenWeatherMapDataWorker('http://localhost')
        assert val is None


def test_getOpenWeatherMapDataWorker_4():
    class Test:
        status_code = 300
    with mock.patch.object(requests,
                           'get',
                           side_effect=Exception(),
                           return_value=Test()):
        val = app.getOpenWeatherMapDataWorker('http://localhost')
        assert val is None


def test_getOpenWeatherMapDataWorker_5():
    class Test:
        status_code = 200

        @staticmethod
        def json():
            return 'test'

    with mock.patch.object(requests,
                           'get',
                           return_value=Test()):
        val = app.getOpenWeatherMapDataWorker('http://localhost')
        assert val == 'test'


def test_updateOpenWeatherMapData_1():
    suc = app.updateOpenWeatherMapData()
    assert not suc


def test_updateOpenWeatherMapData_2():
    app.keyAPI = 'test'
    suc = app.updateOpenWeatherMapData()
    assert not suc


def test_updateOpenWeatherMapData_3():
    app.keyAPI = 'test'
    app.online = True
    suc = app.updateOpenWeatherMapData()
    assert not suc


def test_updateOpenWeatherMapData_4():
    app.keyAPI = 'test'
    app.online = True
    app.running = True
    suc = app.updateOpenWeatherMapData()
    assert suc

