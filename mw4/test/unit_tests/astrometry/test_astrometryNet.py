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
import glob
import platform
import subprocess
import shutil
import faulthandler
faulthandler.enable()

# external packages
from PyQt5.QtCore import QThreadPool
from astropy.io import fits

# local import
from mw4.astrometry.astrometry import AstrometryNET, Astrometry


@pytest.fixture(autouse=True, scope='function')
def app():
    class Test:
        threadPool = QThreadPool()

    parent = Astrometry(app=Test(), tempDir='mw4/test/temp')
    app = AstrometryNET(parent=parent)

    for file in os.listdir('mw4/test/temp'):
        fileP = os.path.join('mw4/test/temp', file)
        if 'temp' not in file:
            continue
        os.remove(fileP)
    shutil.copy('mw4/test/testData/m51.fit', 'mw4/test/image/m51.fit')

    yield app


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


def test_getWCSHeader_1(app):
    val = app.getWCSHeader()
    assert val is None


def test_getWCSHeader_2(app):
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    val = app.getWCSHeader(wcsHDU=hdu)
    assert val


def test_solveNet_1(app):
    suc = app.solve()
    assert not suc


def test_solveNet_2(app):
    app.name = 'KStars'
    app.environment = {
        'KStars': {
            'programPath': '',
            'indexPath': '',
        }
    }
    app.indexPath = 'mw4/test/temp'
    with mock.patch.object(app,
                           'runImage2xy',
                           return_value=False):
        suc = app.solve(fitsPath='mw4/test/image/m51.fit')
        assert not suc


def test_solveNet_3(app):
    app.name = 'KStars'
    app.environment = {
        'KStars': {
            'programPath': '',
            'indexPath': '',
        }
    }
    app.indexPath = 'mw4/test/temp'
    with mock.patch.object(app,
                           'runImage2xy',
                           return_value=True):
        with mock.patch.object(app,
                               'runSolveField',
                               return_value=False):
            suc = app.solve(fitsPath='mw4/test/image/m51.fit')
            assert not suc


def test_solveNet_4(app):
    app.name = 'KStars'
    app.environment = {
        'KStars': {
            'programPath': '',
            'indexPath': '',
        }
    }
    app.indexPath = 'mw4/test/temp'
    with mock.patch.object(app,
                           'runImage2xy',
                           return_value=True):
        with mock.patch.object(app,
                               'runSolveField',
                               return_value=True):
            suc = app.solve(fitsPath='mw4/test/image/m51.fit')
            assert not suc


def test_solveNet_5(app):
    app.name = 'CloudMakers'
    app.environment = {
        'CloudMakers': {
            'programPath': '',
            'indexPath': '',
        }
    }
    app.indexPath = 'mw4/test/temp'
    with mock.patch.object(app,
                           'runImage2xy',
                           return_value=True):
        with mock.patch.object(app,
                               'runSolveField',
                               return_value=True):
            with mock.patch.object(os,
                                   'remove',
                                   return_value=True):
                shutil.copy('mw4/test/testData/tempNET.wcs', 'mw4/test/temp/temp.wcs')
                suc = app.solve(fitsPath='mw4/test/image/m51.fit')
                assert not suc


def test_solveNet_6(app):
    app.name = 'KStars'
    app.environment = {
        'KStars': {
            'programPath': '',
            'indexPath': '',
        }
    }
    app.indexPath = 'mw4/test/temp'
    with mock.patch.object(app,
                           'runImage2xy',
                           return_value=True):
        with mock.patch.object(app,
                               'runSolveField',
                               return_value=True):
            with mock.patch.object(os,
                                   'remove',
                                   return_value=True):
                shutil.copy('mw4/test/testData/tempNET.solved', 'mw4/test/temp/temp.solved')
                suc = app.solve(fitsPath='mw4/test/image/m51.fit')
                assert not suc


def test_solveNet_7(app):
    app.name = 'KStars'
    app.environment = {
        'KStars': {
            'programPath': '',
            'indexPath': '',
        }
    }
    app.indexPath = 'mw4/test/temp'
    with mock.patch.object(app,
                           'runImage2xy',
                           return_value=True):
        with mock.patch.object(app,
                               'runSolveField',
                               return_value=True):
            with mock.patch.object(os,
                                   'remove',
                                   return_value=True):
                shutil.copy('mw4/test/testData/tempNET.wcs', 'mw4/test/temp/temp.wcs')
                shutil.copy('mw4/test/testData/tempNET.solved', 'mw4/test/temp/temp.solved')
                suc = app.solve(fitsPath='mw4/test/image/m51.fit')
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
                app.setEnvironment()
                val = app.checkAvailability()
                assert val == ['CloudMakers', 'KStars']


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
                app.setEnvironment()
                val = app.checkAvailability()
                assert val == ['local-all', 'local-user']


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
                app.setEnvironment()
                val = app.checkAvailability()
                assert val == []
