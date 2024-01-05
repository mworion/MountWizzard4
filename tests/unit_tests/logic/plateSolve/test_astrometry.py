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
from unittest import mock
import pytest
import os
import glob
import platform
import shutil
import subprocess

# external packages

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from logic.plateSolve.astrometry import Astrometry
from logic.plateSolve.plateSolve import PlateSolve
from base.loggerMW import setupLogging
setupLogging()

@pytest.fixture(autouse=True, scope='function')
def function():
    files = glob.glob('tests/workDir/image/*.fit*')
    for f in files:
        os.remove(f)
    for file in os.listdir('tests/workDir/temp'):
        fileP = os.path.join('tests/workDir/temp', file)
        if 'temp' not in file:
            continue
        os.remove(fileP)

    parent = PlateSolve(app=App())
    func = Astrometry(parent=parent)
    yield func


def test_setDefaultPath_1(function):
    with mock.patch.object(platform,
                           'system',
                           return_value='Darwin'):
        suc = function.setDefaultPath()
        assert suc
        assert function.appPath == '/Applications/KStars.app/Contents/MacOS/astrometry/bin'


def test_setDefaultPath_2(function):
    with mock.patch.object(platform,
                           'system',
                           return_value='Linux'):
        suc = function.setDefaultPath()
        assert suc
        assert function.appPath == '/usr/bin'


def test_setDefaultPath_3(function):
    with mock.patch.object(platform,
                           'system',
                           return_value='Windows'):
        suc = function.setDefaultPath()
        assert suc
        assert function.appPath == ''


def test_saveConfigFile(function):
    suc = function.saveConfigFile()
    assert suc


def test_runImage2xy_1(function):
    suc = function.runImage2xy()
    assert not suc


def test_runImage2xy_2(function):
    class Test1:
        @staticmethod
        def decode():
            return 'decode'

    class Test:
        returncode = '1'
        stderr = Test1()
        stdout = Test1()

        @staticmethod
        def communicate(timeout=0):
            return Test1(), Test1()

    with mock.patch.object(subprocess,
                           'Popen',
                           return_value=Test()):
        suc = function.runImage2xy()
    assert not suc


def test_runImage2xy_3(function):
    with mock.patch.object(subprocess,
                           'Popen',
                           return_value=None):
        with mock.patch.object(subprocess.Popen,
                               'communicate',
                               return_value=('', ''),
                               side_effect=Exception()):
            suc = function.runImage2xy()
            assert not suc


def test_runImage2xy_4(function):
    with mock.patch.object(subprocess.Popen,
                           'communicate',
                           return_value=('', ''),
                           side_effect=subprocess.TimeoutExpired('run', 1)):
        suc = function.runImage2xy(binPath='clear')
        assert not suc


def test_runSolveField_1(function):
    suc = function.runSolveField()
    assert not suc


def test_runSolveField_2(function):
    class Test1:
        @staticmethod
        def decode():
            return 'decode'

    class Test:
        returncode = '1'
        stderr = Test1()
        stdout = Test1()

        @staticmethod
        def communicate(timeout=0):
            return Test1(), Test1()

    with mock.patch.object(subprocess,
                           'Popen',
                           return_value=Test()):
        suc = function.runSolveField()
    assert not suc


def test_runSolveField_3(function):
    with mock.patch.object(subprocess,
                           'Popen',
                           return_value=None):
        with mock.patch.object(subprocess.Popen,
                               'communicate',
                               return_value=('', ''),
                               side_effect=Exception()):
            suc = function.runSolveField()
            assert not suc


def test_runSolveField_4(function):
    with mock.patch.object(subprocess.Popen,
                           'communicate',
                           return_value=('', ''),
                           side_effect=subprocess.TimeoutExpired('run', 1)):
        suc = function.runSolveField(binPath='clear')
        assert not suc


def test_solve_1(function):
    suc = function.solve()
    assert not suc


def test_solve_2(function):
    function.indexPath = 'tests/workDir/temp'
    with mock.patch.object(function,
                           'runImage2xy',
                           return_value=False):
        shutil.copy('tests/testData/m51.fit', 'tests/workDir/image/m51.fit')
        suc = function.solve(fitsPath='tests/workDir/image/m51.fit')
        assert not suc


def test_solve_3(function):
    function.indexPath = 'tests/workDir/temp'
    with mock.patch.object(function,
                           'runImage2xy',
                           return_value=True):
        with mock.patch.object(function,
                               'runSolveField',
                               return_value=False):
            shutil.copy('tests/testData/m51.fit', 'tests/workDir/image/m51.fit')
            suc = function.solve(fitsPath='tests/workDir/image/m51.fit')
            assert not suc


def test_solve_4(function):
    function.indexPath = 'tests/workDir/temp'
    with mock.patch.object(function,
                           'runImage2xy',
                           return_value=True):
        with mock.patch.object(function,
                               'runSolveField',
                               return_value=True):
            shutil.copy('tests/testData/m51.fit', 'tests/workDir/image/m51.fit')
            suc = function.solve(fitsPath='tests/workDir/image/m51.fit')
            assert not suc


def test_solve_5(function):
    function.indexPath = 'tests/workDir/temp'
    function.appPath = 'Astrometry.app'
    with mock.patch.object(function,
                           'runImage2xy',
                           return_value=True):
        with mock.patch.object(function,
                               'runSolveField',
                               return_value=True):
            with mock.patch.object(os,
                                   'remove',
                                   return_value=True):
                shutil.copy('tests/testData/temp.wcs', 'tests/workDir/temp/temp.wcs')
                shutil.copy('tests/testData/tempNET.solved', 'tests/workDir/temp/temp.solved')
                shutil.copy('tests/testData/m51.fit', 'tests/workDir/image/m51.fit')
                suc = function.solve(fitsPath='tests/workDir/image/m51.fit')
                assert suc


def test_abort_1(function):
    function.process = None
    suc = function.abort()
    assert not suc


def test_abort_2(function):
    class Test:
        @staticmethod
        def kill():
            return True
    function.framework = 'KStars'
    function.process = Test()
    suc = function.abort()
    assert suc


def test_checkAvailability_0(function):
    with mock.patch.object(os.path,
                           'isfile',
                           return_value=True):
        with mock.patch.object(glob,
                               'glob',
                               return_value=True):
            with mock.patch.object(platform,
                                   'system',
                                   return_value='Darwin'):
                suc = function.checkAvailability('test', 'test')
                assert suc == (True, True)


def test_checkAvailability_1(function):
    with mock.patch.object(os.path,
                           'isfile',
                           return_value=True):
        with mock.patch.object(glob,
                               'glob',
                               return_value=True):
            with mock.patch.object(platform,
                                   'system',
                                   return_value='Darwin'):
                suc = function.checkAvailability()
                assert suc == (True, True)


def test_checkAvailability_2(function):
    with mock.patch.object(os.path,
                           'isfile',
                           return_value=True):
        with mock.patch.object(glob,
                               'glob',
                               return_value=True):
            with mock.patch.object(platform,
                                   'system',
                                   return_value='Linux'):
                suc = function.checkAvailability()
                assert suc == (True, True)


def test_checkAvailability_3(function):
    with mock.patch.object(os.path,
                           'isfile',
                           return_value=True):
        with mock.patch.object(glob,
                               'glob',
                               return_value=True):
            with mock.patch.object(platform,
                                   'system',
                                   return_value='Windows'):
                suc = function.checkAvailability()
                assert suc == (True, True)


def test_checkAvailability_4(function):
    with mock.patch.object(os.path,
                           'isfile',
                           return_value=False):
        with mock.patch.object(glob,
                               'glob',
                               return_value=False):
            with mock.patch.object(platform,
                                   'system',
                                   return_value='Linux'):
                suc = function.checkAvailability()
                assert suc == (False, False)
