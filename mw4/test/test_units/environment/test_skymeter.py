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
from mw4.test.test_units.setupQt import setupQt

host_ip = 'astro-mount.fritz.box'


@pytest.fixture(autouse=True, scope='module')
def module_setup_teardown():
    global app, spy, mwGlob, test
    app, spy, mwGlob, test = setupQt()


def test_name():
    app.skymeter.framework = 'indi'
    name = 'MBox'
    app.skymeter.name = name
    assert name == app.skymeter.name
    assert app.skymeter.run['indi'].name == name


def test_host():
    app.skymeter.framework = 'indi'
    host = ('localhost', 7624)
    app.skymeter.host = host
    assert app.skymeter.host == host
    assert app.skymeter.run['indi'].host == host
    assert app.skymeter.run['indi'].client.host == host


def test_startCommunication_1():
    app.skymeter.framework = 'indi'
    app.skymeter.name = ''
    with mock.patch.object(app.skymeter.run['indi'].client,
                           'connectServer',
                           return_value=False):
        suc = app.skymeter.run['indi'].startCommunication()
        assert not suc


def test_startCommunication_2():
    app.skymeter.framework = ''
    app.skymeter.name = ''
    with mock.patch.object(app.skymeter.run['indi'].client,
                           'connectServer',
                           return_value=False):
        suc = app.skymeter.run['indi'].startCommunication()
        assert not suc


def test_startCommunication_3():
    app.skymeter.framework = 'indi'
    app.skymeter.name = 'MBox'
    with mock.patch.object(app.skymeter.run['indi'].client,
                           'connectServer',
                           return_value=False):
        suc = app.skymeter.run['indi'].startCommunication()
        assert not suc


def test_stopCommunication_1():
    app.skymeter.framework = 'indi'
    app.skymeter.name = ''
    with mock.patch.object(app.skymeter.run['indi'].client,
                           'disconnectServer',
                           return_value=False):
        suc = app.skymeter.run['indi'].stopCommunication()
        assert not suc


def test_stopCommunication_2():
    app.skymeter.framework = ''
    app.skymeter.name = ''
    with mock.patch.object(app.skymeter.run['indi'].client,
                           'disconnectServer',
                           return_value=False):
        suc = app.skymeter.run['indi'].stopCommunication()
        assert not suc


def test_stopCommunication_3():
    app.skymeter.framework = 'indi'
    app.skymeter.name = 'MBox'
    with mock.patch.object(app.skymeter.run['indi'].client,
                           'disconnectServer',
                           return_value=False):
        suc = app.skymeter.run['indi'].stopCommunication()
        assert not suc

