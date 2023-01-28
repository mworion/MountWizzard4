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
# written in python3, (c) 2019-2023 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages

# local import
from base.driverDataClass import DriverData, Signals
from base.loggerMW import setupLogging

setupLogging()

app = DriverData()
Sig = Signals()


def test_storeAscomProperty_1():
    app.data = {'YES': 0}

    res = app.storePropertyToData(None, 'YES')
    assert not res
    assert 'YES' not in app.data


def test_storeAscomProperty_2():
    app.data = {'YES': 0,
                'NO': 0}

    res = app.storePropertyToData(None, 'YES', 'NO')
    assert not res
    assert 'YES' not in app.data
    assert 'NO' not in app.data


def test_storeAscomProperty_3():
    app.data = {'YES': 0,
                'NO': 0}

    res = app.storePropertyToData(10, 'YES', 'NO')
    assert res
    assert 'YES' in app.data
    assert 'NO' in app.data


def test_storeAscomProperty_4():
    app.data = {}

    res = app.storePropertyToData(10, 'YES', 'NO')
    assert res
    assert 'YES' in app.data
    assert 'NO' in app.data


def test_storeAscomProperty_5():
    app.data = {'NO': 0}

    res = app.storePropertyToData(None, 'YES', 'NO')
    assert not res
    assert 'YES' not in app.data
    assert 'NO' not in app.data