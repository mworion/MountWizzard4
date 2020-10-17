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
# written in python3 , (c) 2019, 2020 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
from unittest import mock
import pytest
import os
import json
import platform

# external packages
from PyQt5.QtCore import QThreadPool, QObject

# local import
if not platform.system() == 'Windows':
    pytest.skip("skipping windows-only tests", allow_module_level=True)

from logic.automation.automateWindows import AutomateWindows

# todo: https://github.com/pywinauto/pywinauto/issues/858


@pytest.fixture(autouse=True, scope='module')
def module(qapp):
    yield


@pytest.fixture(autouse=True, scope='function')
def function(module):
    class Test(QObject):
        threadPool = QThreadPool()
        mwGlob = {'tempDir': 'tests/temp',
                  'dataDir': 'tests/data',
                  }

    window = AutomateWindows(app=Test())

    yield window

    window.deleteLater()


def test_writeCometMPC_1(function):
    function.installPath = 'tests/temp'

    suc = function.writeCometMPC()
    assert not suc


def test_writeCometMPC_2(function):
    function.installPath = 'tests/temp'

    data = {'test': 'test'}

    suc = function.writeCometMPC(datas=data)
    assert not suc


def test_writeCometMPC_3(function):
    function.installPath = 'tests/temp'

    data = [{'test': 'test'}]

    suc = function.writeCometMPC(datas=data)
    assert suc
    assert os.path.isfile('tests/temp/minorPlanets.mpc')


def test_writeCometMPC_4(function):
    function.installPath = 'tests/temp'

    with open('tests/testData/mpc_comet_test.json') as f:
        data = json.load(f)

    testData = [data[0]]

    suc = function.writeCometMPC(datas=testData)
    assert suc


def test_writeCometMPC_5(function):
    function.installPath = 'tests/temp'

    with open('tests/testData/mpc_comet_test.json') as f:
        data = json.load(f)

    testData = [data[0]]

    suc = function.writeCometMPC(datas=testData)
    assert suc

    with open('tests/temp/minorPlanets.mpc', 'r') as f:
        testLine = f.readline()

    with open('tests/testData/mpc_comet_test.txt', 'r') as f:
        refLine = f.readline()

    assert testLine == refLine

"""
def test_writeCometMPC_6(function):
    function.installPath = 'tests/temp'

    with open('tests/testData/mpc_comet_test.json') as f:
        data = json.load(f)

    suc = function.writeCometMPC(datas=data)
    assert suc

    with open('tests/temp/minorPlanets.mpc', 'r') as f:
        testLines = f.readlines()

    with open('tests/testData/mpc_comet_test.txt', 'r') as f:
        refLines = f.readlines()

    for test, ref in zip(testLines, refLines):
        assert test == ref
"""


def test_writeAsteroidMPC_1(function):
    function.installPath = 'tests/temp'

    suc = function.writeAsteroidMPC()
    assert not suc


def test_writeAsteroidMPC_2(function):
    function.installPath = 'tests/temp'

    data = {'test': 'test'}

    suc = function.writeAsteroidMPC(datas=data)
    assert not suc


def test_writeAsteroidMPC_3(function):
    function.installPath = 'tests/temp'

    data = [{'test': 'test'}]

    suc = function.writeAsteroidMPC(datas=data)
    assert suc
    assert os.path.isfile('tests/temp/minorPlanets.mpc')


def test_writeAsteroidMPC_4(function):
    function.installPath = 'tests/temp'

    with open('tests/testData/mpc_asteroid_test.json') as f:
        data = json.load(f)

    testData = [data[0]]

    suc = function.writeAsteroidMPC(datas=testData)
    assert suc

"""
def test_writeAsteroidMPC_5(function):
    function.installPath = 'tests/temp'

    with open('tests/testData/mpc_Asteroid_test.json') as f:
        data = json.load(f)

    testData = [data[0]]

    suc = function.writeAsteroidMPC(datas=testData)
    assert suc

    with open('tests/temp/minorPlanets.mpc', 'r') as f:
        testLine = f.readline()

    with open('tests/testData/mpc_asteroid_test.txt', 'r') as f:
        refLine = f.readline()

    assert testLine == refLine


def test_writeAsteroidMPC_6(function):
    function.installPath = 'tests/temp'

    with open('tests/testData/mpc_asteroid_test.json') as f:
        data = json.load(f)

    suc = function.writeAsteroidMPC(datas=data)
    assert suc

    with open('tests/temp/minorPlanets.mpc', 'r') as f:
        testLines = f.readlines()

    with open('tests/testData/mpc_asteroid_test.txt', 'r') as f:
        refLines = f.readlines()

    for test, ref in zip(testLines, refLines):
        assert test == ref
"""
