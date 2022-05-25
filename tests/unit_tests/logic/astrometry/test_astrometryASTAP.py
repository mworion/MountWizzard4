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
#
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
from logic.astrometry.astrometry import Astrometry
from logic.astrometry.astrometryASTAP import AstrometryASTAP


@pytest.fixture(autouse=True, scope='module')
def module_setup_teardown():

    yield

    files = glob.glob('tests/workDir/image/*.fit*')
    for f in files:
        os.remove(f)


@pytest.fixture(autouse=True, scope='function')
def app():
    parent = Astrometry(app=App())
    app = AstrometryASTAP(parent=parent)

    for file in os.listdir('tests/workDir/temp'):
        fileP = os.path.join('tests/workDir/temp', file)
        if 'temp' not in file:
            continue
        os.remove(fileP)
    shutil.copy('tests/testData/m51.fit', 'tests/workDir/image/m51.fit')

    yield app


def test_setDefaultPath_1(app):
    with mock.patch.object(platform,
                           'system',
                           return_value='Darwin'):
        suc = app.setDefaultPath()
        assert suc
        assert app.appPath == '/Applications/ASTAP.app/Contents/MacOS'


def test_setDefaultPath_2(app):
    with mock.patch.object(platform,
                           'system',
                           return_value='Linux'):
        suc = app.setDefaultPath()
        assert suc
        assert app.appPath == '/opt/astap'


def test_setDefaultPath_3(app):
    with mock.patch.object(platform,
                           'system',
                           return_value='Windows'):
        suc = app.setDefaultPath()
        assert suc
        assert app.appPath == 'C:\\Program Files\\astap'


def test_runASTAP_1(app):
    suc, ret = app.runASTAP()
    assert not suc


def test_runASTAP_2(app):
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
        suc, ret = app.runASTAP()
        assert ret == 1
        assert suc


def test_runASTAP_3(app):
    with mock.patch.object(subprocess,
                           'Popen',
                           return_value=None):
        with mock.patch.object(subprocess.Popen,
                               'communicate',
                               return_value=('', ''),
                               side_effect=Exception()):
            suc, ret = app.runASTAP()
            assert not suc


def test_runASTAP_4(app):
    with mock.patch.object(subprocess.Popen,
                           'communicate',
                           return_value=('', ''),
                           side_effect=subprocess.TimeoutExpired('run', 1)):
        suc, ret = app.runASTAP(binPath='clear')
        assert not suc


def test_getWCSHeader_1(app):
    val = app.getWCSHeader()
    assert val is None


def test_getWCSHeader_2(app):
    shutil.copy('tests/testData/tempASTAP.wcs', 'tests/workDir/temp/temp.wcs')
    with open('tests/workDir/temp/temp.wcs') as wcsTextFile:
        val = app.getWCSHeader(wcsTextFile=wcsTextFile)
    assert val


def test_solve_1(app):
    suc = app.solve()
    assert not suc


def test_solve_2(app):
    suc = app.solve()
    assert not suc


def test_solve_3(app):
    with mock.patch.object(app,
                           'runASTAP',
                           return_value=(False, 1)):
        suc = app.solve(fitsPath='tests/workDir/image/m51.fit')
        assert not suc


def test_solve_4(app):
    with mock.patch.object(app,
                           'runASTAP',
                           return_value=(True, 0)):
        suc = app.solve(fitsPath='tests/workDir/image/m51.fit')
        assert not suc


def test_solve_5(app):
    with mock.patch.object(app,
                           'runASTAP',
                           return_value=(True, 0)):
        with mock.patch.object(os,
                               'remove',
                               return_value=True):
            shutil.copy('tests/testData/tempASTAP.wcs', 'tests/workDir/temp/temp.wcs')
            suc = app.solve(fitsPath='tests/workDir/image/m51.fit')
            assert suc


def test_solve_6(app):
    raHint = Angle(hours=10)
    decHint = Angle(degrees=10)
    app.searchRadius = 180
    with mock.patch.object(app,
                           'runASTAP',
                           return_value=(True, 0)):
        with mock.patch.object(os,
                               'remove',
                               return_value=True):
            shutil.copy('tests/testData/tempASTAP.wcs', 'tests/workDir/temp/temp.wcs')
            suc = app.solve(fitsPath='tests/workDir/image/m51.fit',
                            raHint=raHint, decHint=decHint)
            assert suc


def test_abort_1(app):
    app.process = None
    suc = app.abort()
    assert not suc


def test_abort_2(app):
    class Test:
        @staticmethod
        def kill():
            return True
    app.framework = 'ASTAP'
    app.process = Test()
    suc = app.abort()
    assert suc


def test_checkAvailability_1(app):
    with mock.patch.object(os.path,
                           'isfile',
                           return_value=True):
        with mock.patch.object(glob,
                               'glob',
                               return_value='.290'):
            with mock.patch.object(builtins,
                                   'any',
                                   return_value=True):
                with mock.patch.object(platform,
                                       'system',
                                       return_value='Darwin'):
                    suc = app.checkAvailability()
                    assert suc == (True, True)


def test_checkAvailability_2(app):
    with mock.patch.object(os.path,
                           'isfile',
                           return_value=True):
        with mock.patch.object(glob,
                               'glob',
                               return_value='.290'):
            with mock.patch.object(builtins,
                                   'any',
                                   return_value=True):
                with mock.patch.object(platform,
                                       'system',
                                       return_value='Linux'):
                    suc = app.checkAvailability()
                    assert suc == (True, True)


def test_checkAvailability_3(app):
    with mock.patch.object(os.path,
                           'isfile',
                           return_value=True):
        with mock.patch.object(glob,
                               'glob',
                               return_value='.290'):
            with mock.patch.object(builtins,
                                   'any',
                                   return_value=True):
                with mock.patch.object(platform,
                                       'system',
                                       return_value='Windows'):
                    suc = app.checkAvailability()
                    assert suc == (True, True)


def test_checkAvailability_4(app):
    with mock.patch.object(os.path,
                           'isfile',
                           return_value=False):
        with mock.patch.object(glob,
                               'glob',
                               return_value='.290'):
            with mock.patch.object(builtins,
                                   'any',
                                   return_value=False):
                with mock.patch.object(platform,
                                       'system',
                                       return_value='Linux'):
                    suc = app.checkAvailability()
                    assert suc == (False, False)
