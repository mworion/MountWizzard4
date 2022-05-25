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
from PyQt5.QtCore import QThreadPool
from astropy.io import fits

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from logic.astrometry.astrometry import Astrometry
from logic.astrometry.astrometryNET import AstrometryNET


@pytest.fixture(autouse=True, scope='module')
def module_setup_teardown():

    yield

    files = glob.glob('tests/workDir/image/*.fit*')
    for f in files:
        os.remove(f)


@pytest.fixture(autouse=True, scope='function')
def app():
    parent = Astrometry(app=App())
    app = AstrometryNET(parent=parent)

    for file in os.listdir('tests/workDir/temp'):
        fileP = os.path.join('tests/workDir/temp', file)
        if 'temp' not in file:
            continue
        os.remove(fileP)

    yield app


def test_setDefaultPath_1(app):
    with mock.patch.object(platform,
                           'system',
                           return_value='Darwin'):
        suc = app.setDefaultPath()
        assert suc
        assert app.appPath == '/Applications/KStars.app/Contents/MacOS/astrometry/bin'


def test_setDefaultPath_2(app):
    with mock.patch.object(platform,
                           'system',
                           return_value='Linux'):
        suc = app.setDefaultPath()
        assert suc
        assert app.appPath == '/usr/bin'


def test_setDefaultPath_3(app):
    with mock.patch.object(platform,
                           'system',
                           return_value='Windows'):
        suc = app.setDefaultPath()
        assert suc
        assert app.appPath == ''


def test_runImage2xy_1(app):
    suc = app.runImage2xy()
    assert not suc


def test_runImage2xy_2(app):
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
        suc = app.runImage2xy()
    assert not suc


def test_runImage2xy_3(app):
    with mock.patch.object(subprocess,
                           'Popen',
                           return_value=None):
        with mock.patch.object(subprocess.Popen,
                               'communicate',
                               return_value=('', ''),
                               side_effect=Exception()):
            suc = app.runImage2xy()
            assert not suc


def test_runImage2xy_4(app):
    with mock.patch.object(subprocess.Popen,
                           'communicate',
                           return_value=('', ''),
                           side_effect=subprocess.TimeoutExpired('run', 1)):
        suc = app.runImage2xy(binPath='clear')
        assert not suc


def test_runSolveField_1(app):
    suc = app.runSolveField()
    assert not suc


def test_runSolveField_2(app):
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
        suc = app.runSolveField()
    assert not suc


def test_runSolveField_3(app):
    with mock.patch.object(subprocess,
                           'Popen',
                           return_value=None):
        with mock.patch.object(subprocess.Popen,
                               'communicate',
                               return_value=('', ''),
                               side_effect=Exception()):
            suc = app.runSolveField()
            assert not suc


def test_runSolveField_4(app):
    with mock.patch.object(subprocess.Popen,
                           'communicate',
                           return_value=('', ''),
                           side_effect=subprocess.TimeoutExpired('run', 1)):
        suc = app.runSolveField(binPath='clear')
        assert not suc


def test_getWCSHeader_1(app):
    val = app.getWCSHeader()
    assert val is None


def test_getWCSHeader_2(app):
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    val = app.getWCSHeader(wcsHDU=hdu)
    assert val


def test_solve_1(app):
    suc = app.solve()
    assert not suc


def test_solve_2(app):
    app.indexPath = 'tests/workDir/temp'
    with mock.patch.object(app,
                           'runImage2xy',
                           return_value=False):
        shutil.copy('tests/testData/m51.fit', 'tests/workDir/image/m51.fit')
        suc = app.solve(fitsPath='tests/workDir/image/m51.fit')
        assert not suc


def test_solve_3(app):
    app.indexPath = 'tests/workDir/temp'
    with mock.patch.object(app,
                           'runImage2xy',
                           return_value=True):
        with mock.patch.object(app,
                               'runSolveField',
                               return_value=False):
            shutil.copy('tests/testData/m51.fit', 'tests/workDir/image/m51.fit')
            suc = app.solve(fitsPath='tests/workDir/image/m51.fit')
            assert not suc


def test_solve_4(app):
    app.indexPath = 'tests/workDir/temp'
    with mock.patch.object(app,
                           'runImage2xy',
                           return_value=True):
        with mock.patch.object(app,
                               'runSolveField',
                               return_value=True):
            shutil.copy('tests/testData/m51.fit', 'tests/workDir/image/m51.fit')
            suc = app.solve(fitsPath='tests/workDir/image/m51.fit')
            assert not suc


def test_solve_5(app):
    app.indexPath = 'tests/workDir/temp'
    with mock.patch.object(app,
                           'runImage2xy',
                           return_value=True):
        with mock.patch.object(app,
                               'runSolveField',
                               return_value=True):
            with mock.patch.object(os,
                                   'remove',
                                   return_value=True):
                shutil.copy('tests/testData/tempNET.wcs', 'tests/workDir/temp/temp.wcs')
                shutil.copy('tests/testData/m51.fit', 'tests/workDir/image/m51.fit')
                suc = app.solve(fitsPath='tests/workDir/image/m51.fit')
                assert not suc


def test_solve_6(app):
    app.indexPath = 'tests/workDir/temp'
    with mock.patch.object(app,
                           'runImage2xy',
                           return_value=True):
        with mock.patch.object(app,
                               'runSolveField',
                               return_value=True):
            with mock.patch.object(os,
                                   'remove',
                                   return_value=True):
                shutil.copy('tests/testData/tempNET.solved', 'tests/workDir/temp/temp.solved')
                shutil.copy('tests/testData/m51.fit', 'tests/workDir/image/m51.fit')
                suc = app.solve(fitsPath='tests/workDir/image/m51.fit')
                assert not suc


def test_solve_7(app):
    app.indexPath = 'tests/workDir/temp'
    app.appPath = 'Astrometry.app'
    with mock.patch.object(app,
                           'runImage2xy',
                           return_value=True):
        with mock.patch.object(app,
                               'runSolveField',
                               return_value=True):
            with mock.patch.object(os,
                                   'remove',
                                   return_value=True):
                shutil.copy('tests/testData/tempNET.wcs', 'tests/workDir/temp/temp.wcs')
                shutil.copy('tests/testData/tempNET.solved', 'tests/workDir/temp/temp.solved')
                shutil.copy('tests/testData/m51.fit', 'tests/workDir/image/m51.fit')
                suc = app.solve(fitsPath='tests/workDir/image/m51.fit')
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
    app.framework = 'KStars'
    app.process = Test()
    suc = app.abort()
    assert suc


def test_checkAvailability_1(app):
    with mock.patch.object(os.path,
                           'isfile',
                           return_value=True):
        with mock.patch.object(glob,
                               'glob',
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
                               return_value=False):
            with mock.patch.object(platform,
                                   'system',
                                   return_value='Linux'):
                suc = app.checkAvailability()
                assert suc == (False, False)
