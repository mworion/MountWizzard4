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


def test_setUpdateConfig_1():
    app.skymeter.name = 'test'
    suc = app.skymeter.run['indi'].setUpdateConfig('false')
    assert not suc


def test_setUpdateConfig_2():
    app.skymeter.name = 'test'
    app.skymeter.run['indi'].device = None
    suc = app.skymeter.run['indi'].setUpdateConfig('test')
    assert not suc


def test_setUpdateConfig_3():
    class Test:
        @staticmethod
        def getNumber(test):
            return {}
    app.skymeter.name = 'test'
    app.skymeter.run['indi'].device = Test()
    suc = app.skymeter.run['indi'].setUpdateConfig('test')
    assert not suc


def test_setUpdateConfig_4():
    class Test:
        @staticmethod
        def getNumber(test):
            return {'PERIOD': 1}
    app.skymeter.run['indi'].name = 'test'
    app.skymeter.run['indi'].device = Test()
    suc = app.skymeter.run['indi'].setUpdateConfig('test')
    assert not suc


def test_setUpdateConfig_5():
    class Test:
        @staticmethod
        def getNumber(test):
            return {'PERIOD': 10}
    app.skymeter.run['indi'].name = 'test'
    app.skymeter.run['indi'].device = Test()
    with mock.patch.object(app.skymeter.run['indi'].client,
                           'sendNewNumber',
                           return_value=False):
        suc = app.skymeter.run['indi'].setUpdateConfig('test')
        assert not suc


def test_setUpdateConfig_6():
    class Test:
        @staticmethod
        def getNumber(test):
            return {'PERIOD': 10}
    app.skymeter.run['indi'].name = 'test'
    app.skymeter.run['indi'].device = Test()
    with mock.patch.object(app.skymeter.run['indi'].client,
                           'sendNewNumber',
                           return_value=True):
        suc = app.skymeter.run['indi'].setUpdateConfig('test')
        assert suc