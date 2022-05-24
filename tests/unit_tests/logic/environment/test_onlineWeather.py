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
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
import unittest.mock as mock

# external packages
from PyQt5.QtCore import QThreadPool, QObject, pyqtSignal
import requests
from skyfield.api import wgs84
from mountcontrol.mount import Mount

# local import
from logic.environment.onlineWeather import OnlineWeather
from base.loggerMW import setupLogging
setupLogging()


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    class Test(QObject):
        threadPool = QThreadPool()
        mes = pyqtSignal(object, object, object, object)
        update10s = pyqtSignal()
        mount = Mount(host='localhost', MAC='00:00:00:00:00:00', verbose=False,
                      pathToData='tests/workDir/data')
        mount.obsSite.location = wgs84.latlon(latitude_degrees=20,
                                       longitude_degrees=10,
                                       elevation_m=500)

    global app

    class Test1:
        status_code = 200

        @staticmethod
        def json():
            return 'test'

    with mock.patch.object(requests,
                           'get',
                           return_value=Test1()):
        app = OnlineWeather(app=Test())

    yield

    app.threadPool.waitForDone(1000)


def test_properties():
    with mock.patch.object(app,
                           'updateOpenWeatherMapData'):
        app.keyAPI = 'test'
        assert app.keyAPI == 'test'
        app.online = True
        assert app.online


def test_startCommunication_1():
    app.running = False
    with mock.patch.object(app,
                           'updateOpenWeatherMapData'):
        suc = app.startCommunication()
        assert not suc
        assert not app.running


def test_startCommunication_2():
    app.running = False
    app.apiKey = 'test'
    with mock.patch.object(app,
                           'updateOpenWeatherMapData'):
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


def test_updateOpenWeatherMapDataWorker_4():
    data = {'list': []}
    suc = app.updateOpenWeatherMapDataWorker(data=data)
    assert not suc


def test_getOpenWeatherMapDataWorker_1():
    val = app.getOpenWeatherMapDataWorker()
    assert val is None


def test_getOpenWeatherMapDataWorker_2():
    class Test:
        status_code = 300
    with mock.patch.object(requests,
                           'get',
                           return_value=Test()):
        val = app.getOpenWeatherMapDataWorker('http://localhost')
        assert val is None


def test_getOpenWeatherMapDataWorker_3():
    class Test:
        status_code = 300
    with mock.patch.object(requests,
                           'get',
                           side_effect=Exception(),
                           return_value=Test()):
        val = app.getOpenWeatherMapDataWorker('http://localhost')
        assert val is None


def test_getOpenWeatherMapDataWorker_4():
    class Test:
        status_code = 300
    with mock.patch.object(requests,
                           'get',
                           side_effect=TimeoutError(),
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
    app.online = True
    suc = app.updateOpenWeatherMapData()
    assert not suc


def test_updateOpenWeatherMapData_3():
    app.online = True
    app.running = True
    suc = app.updateOpenWeatherMapData()
    assert suc


def test_updateOpenWeatherMapData_4():
    app.online = False
    app.running = True
    with mock.patch.object(app,
                           'stopCommunication'):
        suc = app.updateOpenWeatherMapData()
        assert not suc

