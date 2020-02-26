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
from unittest import mock
import pytest
import datetime
# external packages
import indibase
# local import
from mw4.test.test_old.setupQt import setupQt

host_ip = 'astro-mount.fritz.box'


@pytest.fixture(autouse=True, scope='module')
def module_setup_teardown():
    global app, spy, mwGlob, test
    app, spy, mwGlob, test = setupQt()


def test_name():
    app.sensorWeather.framework = 'indi'
    name = 'MBox'
    app.sensorWeather.name = name
    assert name == app.sensorWeather.name
    assert app.sensorWeather.run['indi'].name == name


def test_host():
    app.sensorWeather.framework = 'indi'
    host = ('localhost', 7624)
    app.sensorWeather.host = host
    assert app.sensorWeather.host == host
    assert app.sensorWeather.run['indi'].host == host
    assert app.sensorWeather.run['indi'].client.host == host


def test_startCommunication_1():
    app.sensorWeather.framework = 'indi'
    app.sensorWeather.name = ''
    with mock.patch.object(app.sensorWeather.run['indi'].client,
                           'connectServer',
                           return_value=False):
        suc = app.sensorWeather.run['indi'].startCommunication()
        assert not suc


def test_startCommunication_2():
    app.sensorWeather.framework = ''
    app.sensorWeather.name = ''
    with mock.patch.object(app.sensorWeather.run['indi'].client,
                           'connectServer',
                           return_value=False):
        suc = app.sensorWeather.run['indi'].startCommunication()
        assert not suc


def test_startCommunication_3():
    app.sensorWeather.framework = 'indi'
    app.sensorWeather.name = 'MBox'
    with mock.patch.object(app.sensorWeather.run['indi'].client,
                           'connectServer',
                           return_value=False):
        suc = app.sensorWeather.run['indi'].startCommunication()
        assert not suc


def test_stopCommunication_1():
    app.sensorWeather.framework = 'indi'
    app.sensorWeather.name = ''
    with mock.patch.object(app.sensorWeather.run['indi'].client,
                           'disconnectServer',
                           return_value=False):
        suc = app.sensorWeather.run['indi'].stopCommunication()
        assert not suc


def test_stopCommunication_2():
    app.sensorWeather.framework = ''
    app.sensorWeather.name = ''
    with mock.patch.object(app.sensorWeather.run['indi'].client,
                           'disconnectServer',
                           return_value=False):
        suc = app.sensorWeather.run['indi'].stopCommunication()
        assert not suc


def test_stopCommunication_3():
    app.sensorWeather.framework = 'indi'
    app.sensorWeather.name = 'MBox'
    with mock.patch.object(app.sensorWeather.run['indi'].client,
                           'disconnectServer',
                           return_value=False):
        suc = app.sensorWeather.run['indi'].stopCommunication()
        assert not suc
