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
    function.framework = 'Test'
    suc = function.solve()
    assert not suc


def test_solve_2(function):
    function.framework = 'astap'
    suc = function.solve()
    assert not suc


def test_solve_3(function):
    function.framework = 'astap'
    file = 'tests/workDir/image/m51.fit'
    suc = function.solve(imagePath=file)
    assert not suc
    function.mutexSolve.unlock()


def test_solve_4(function):
    function.framework = 'astap'
    file = 'tests/workDir/image/m51.fit'
    with mock.patch.object(function.threadPool,
                           'start'):
        suc = function.solve(imagePath=file)
        assert suc


def test_abort_1(function):
    function.framework = 'test'
    suc = function.abort()
    assert not suc


def test_abort_2(function):
    function.framework = 'astap'
    with mock.patch.object(function.run['astap'],
                           'abort',
                           return_value=True):
        suc = function.abort()
        assert suc


def test_checkAvailabilityProgram_1(function):
    function.framework = 'astap'
    with mock.patch.object(function.run['astap'],
                           'checkAvailabilityProgram',
                           return_value=True):
        val = function.checkAvailabilityProgram()
        assert val


def test_checkAvailabilityIndex_1(function):
    function.framework = 'astap'
    with mock.patch.object(function.run['astap'],
                           'checkAvailabilityIndex',
                           return_value=True):
        val = function.checkAvailabilityIndex()
        assert val


def test_startCommunication(function):
    function.framework = 'astap'
    with mock.patch.object(function,
                           'checkAvailabilityProgram',
                           return_value=True):
        with mock.patch.object(function,
                               'checkAvailabilityIndex',
                               return_value=True):
            suc = function.startCommunication()
            assert suc


def test_stopCommunication(function):
    function.framework = 'astrometry'
    suc = function.stopCommunication()
    assert suc
