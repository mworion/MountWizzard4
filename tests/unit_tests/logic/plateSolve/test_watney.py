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
import shutil
import subprocess
import os
import glob
import platform
import builtins

# external packages
from skyfield.api import Angle

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from logic.plateSolve.plateSolve import PlateSolve
from logic.plateSolve.watney import Watney
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
    shutil.copy('tests/testData/m51.fit', 'tests/workDir/image/m51.fit')
    
    parent = PlateSolve(app=App())
    func = Watney(parent=parent)
    yield func


def test_setDefaultPath_1(function):
    with mock.patch.object(platform,
                           'system',
                           return_value='Darwin'):
        suc = function.setDefaultPath()
        assert suc
        assert function.appPath == function.parent.app.mwGlob['workDir'] + \
               '/watney-cli'


def test_saveConfigFile(function):
    suc = function.saveConfigFile()
    assert suc


def test_runWatney_1(function):
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
        suc, ret = function.runWatney(['test'])
        assert ret == 1
        assert suc


def test_runWatney_2(function):
    with mock.patch.object(subprocess,
                           'Popen',
                           return_value=None):
        with mock.patch.object(subprocess.Popen,
                               'communicate',
                               return_value=('', ''),
                               side_effect=Exception()):
            suc, ret = function.runWatney(['test'])
            assert not suc


def test_runWatney_3(function):
    with mock.patch.object(subprocess.Popen,
                           'communicate',
                           return_value=('', ''),
                           side_effect=subprocess.TimeoutExpired('run', 1)):
        suc, ret = function.runWatney(['test'])
        assert not suc


def test_solve_1(function):
    suc = function.solve()
    assert not suc


def test_solve_2(function):
    with mock.patch.object(function,
                           'runWatney',
                           return_value=(False, 1)):
        suc = function.solve(fitsPath='tests/workDir/image/m51.fit')
        assert not suc


def test_solve_3(function):
    with mock.patch.object(function,
                           'runWatney',
                           return_value=(True, 0)):
        suc = function.solve(fitsPath='tests/workDir/image/m51.fit')
        assert not suc


def test_solve_4(function):
    function.searchRadius = 180
    with mock.patch.object(function,
                           'runWatney',
                           return_value=(True, 0)):
        with mock.patch.object(os,
                               'remove',
                               return_value=True):
            shutil.copy('tests/testData/temp.wcs', 'tests/workDir/temp/temp.wcs')
            suc = function.solve(fitsPath='tests/workDir/image/m51.fit')
            assert suc


def test_solve_5(function):
    raHint = Angle(hours=10)
    decHint = Angle(degrees=10)
    fovHint = 5
    function.searchRadius = 18
    with mock.patch.object(function,
                           'runWatney',
                           return_value=(True, 0)):
        with mock.patch.object(os,
                               'remove',
                               return_value=True):
            shutil.copy('tests/testData/temp.wcs', 'tests/workDir/temp/temp.wcs')
            suc = function.solve(fitsPath='tests/workDir/image/m51.fit',
                                 raHint=raHint, decHint=decHint, fovHint=fovHint)
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
    function.framework = 'ASTAP'
    function.process = Test()
    suc = function.abort()
    assert suc


def test_checkAvailability_1(function):
    with mock.patch.object(os.path,
                           'isfile',
                           return_value=True):
        with mock.patch.object(glob,
                               'glob',
                               return_value='.qdb'):
            suc = function.checkAvailability(appPath='test', indexPath='test')
            assert suc == (True, False)


def test_checkAvailability_2(function):
    with mock.patch.object(os.path,
                           'isfile',
                           return_value=False):
        with mock.patch.object(glob,
                               'glob',
                               return_value='.290'):
            with mock.patch.object(builtins,
                                   'sum',
                                   return_value=407):
                with mock.patch.object(platform,
                                       'system',
                                       return_value='Darwin'):
                    suc = function.checkAvailability(appPath='test', indexPath='test')
                    assert suc == (False, True)


def test_checkAvailability_3(function):
    with mock.patch.object(os.path,
                           'isfile',
                           return_value=False):
        with mock.patch.object(glob,
                               'glob',
                               return_value='.290'):
            with mock.patch.object(builtins,
                                   'sum',
                                   return_value=407):
                with mock.patch.object(platform,
                                       'system',
                                       return_value='Windows'):
                    suc = function.checkAvailability(appPath='test', indexPath='test')
                    assert suc == (False, True)


def test_checkAvailability_4(function):
    with mock.patch.object(os.path,
                           'isfile',
                           return_value=True):
        with mock.patch.object(glob,
                               'glob',
                               return_value='.290'):
            with mock.patch.object(builtins,
                                   'sum',
                                   return_value=407):
                with mock.patch.object(platform,
                                       'system',
                                       return_value='Linux'):
                    suc = function.checkAvailability(appPath='test', indexPath='test')
                    assert suc == (True, True)


def test_checkAvailability_5(function):
    with mock.patch.object(os.path,
                           'isfile',
                           return_value=True):
        with mock.patch.object(glob,
                               'glob',
                               return_value='.290'):
            with mock.patch.object(builtins,
                                   'sum',
                                   return_value=814):
                with mock.patch.object(platform,
                                       'system',
                                       return_value='Linux'):
                    suc = function.checkAvailability(appPath='test', indexPath='test')
                    assert suc == (True, True)


def test_checkAvailability_6(function):
    with mock.patch.object(os.path,
                           'isfile',
                           return_value=True):
        with mock.patch.object(glob,
                               'glob',
                               return_value='.290'):
            with mock.patch.object(builtins,
                                   'sum',
                                   return_value=0):
                with mock.patch.object(platform,
                                       'system',
                                       return_value='Linux'):
                    suc = function.checkAvailability(appPath='test', indexPath='test')
                    assert suc == (True, False)
