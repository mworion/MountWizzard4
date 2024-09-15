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
# GUI with PySide for python
#
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
from unittest import mock
import pytest
import astropy
import os
import numpy as np
import shutil
import glob

# external packages
from astropy.io import fits

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from logic.plateSolve.plateSolve import PlateSolve
from base.loggerMW import setupLogging
setupLogging()


@pytest.fixture(autouse=True, scope='function')
def function():
    files = glob.glob('tests/workDir/image/*.fit*')
    for f in files:
        os.remove(f)
    shutil.copy('tests/testData/m51.fit', 'tests/workDir/image/m51.fit')
    shutil.copy('tests/testData/astrometry.cfg', 'tests/workDir/temp/astrometry.cfg')
    func = PlateSolve(app=App())
    yield func


@pytest.fixture
def mocked_sleepAndEvents(monkeypatch, function):
    def test(a):
        function.solveLoopRunning = False

    monkeypatch.setattr('logic.plateSolve.plateSolve.sleepAndEvents', test)


def test_properties_1(function):
    function.framework = 'test'

    function.host = ('localhost', 7624)
    function.apiKey = 'test'
    function.indexPath = 'test'
    function.deviceName = 'test'
    function.timeout = 30
    function.searchRadius = 20
    assert function.host == ('localhost', 7624)
    assert function.apiKey == 'test'
    assert function.indexPath == 'test'
    assert function.deviceName == 'test'
    assert function.timeout == 30
    assert function.searchRadius == 20


def test_properties_2(function):
    function.framework = 'astap'

    function.host = ('localhost', 7624)
    function.apiKey = 'test'
    function.indexPath = 'test'
    function.deviceName = 'test'
    function.timeout = 30
    function.searchRadius = 20
    assert function.host == ('localhost', 7624)
    assert function.apiKey == 'test'
    assert function.indexPath == 'test'
    assert function.deviceName == 'test'
    assert function.timeout == 30
    assert function.searchRadius == 20


def test_init_1(function):
    assert 'watney' in function.run
    assert 'astrometry' in function.run
    assert 'astap' in function.run


def test_solve_1(function):
    function.framework = 'astap'
    file = 'tests/workDir/image/m51.fit'
    function.solve(imagePath=file)


def test_abort_2(function):
    function.framework = 'astap'
    with mock.patch.object(function.run['astap'],
                           'abort',
                           return_value=True):
        function.abort()


def test_startCommunication_1(function, mocked_sleepAndEvents):
    function.framework = 'astap'
    with mock.patch.object(function,
                           'checkAvailabilityProgram',
                           return_value=True):
        with mock.patch.object(function,
                               'checkAvailabilityIndex',
                               return_value=True):
            function.startCommunication()


def test_startCommunication_2(function, mocked_sleepAndEvents):
    function.framework = 'astap'
    with mock.patch.object(function,
                           'checkAvailabilityProgram',
                           return_value=False):
        with mock.patch.object(function,
                               'checkAvailabilityIndex',
                               return_value=True):
            function.startCommunication()


def test_stopCommunication(function):
    function.framework = 'astrometry'
    function.stopCommunication()
