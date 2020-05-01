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
# written in python 3, (c) 2019, 2020 by mworion
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
import faulthandler
faulthandler.enable()

# external packages
from PyQt5.QtCore import QThreadPool

# local import
from mw4.astrometry.astrometry import AstrometryASTAP, Astrometry


@pytest.fixture(autouse=True, scope='function')
def app():
    class Test:
        threadPool = QThreadPool()

    parent = Astrometry(app=Test(), tempDir='mw4/test/temp')
    app = AstrometryASTAP(parent=parent)

    for file in os.listdir('mw4/test/temp'):
        fileP = os.path.join('mw4/test/temp', file)
        if 'temp' not in file:
            continue
        os.remove(fileP)
    shutil.copy('mw4/test/testData/m51.fit', 'mw4/test/image/m51.fit')

    yield app


def test_setSolverEnviron_1(app):
    with mock.patch.object(platform,
                           'system',
                           return_value='Windows'):
        app.setEnvironment()
        assert 'ASTAP-Win' in list(app.environment.keys())


def test_setSolverEnviron_2(app):
    with mock.patch.object(platform,
                           'system',
                           return_value='Linux'):
        app.setEnvironment()
        assert 'ASTAP-Linux' in list(app.environment.keys())


def test_setSolverEnviron_3(app):
    with mock.patch.object(platform,
                           'system',
                           return_value='Darwin'):
        app.setEnvironment()
        assert 'ASTAP-Mac' in list(app.environment.keys())


def test_runASTAP_1(app):
    suc = app.runASTAP()
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
        suc = app.runASTAP()
        assert not suc


def test_runASTAP_3(app):
    with mock.patch.object(subprocess,
                           'Popen',
                           side_effect=Exception()):
        suc = app.runASTAP()
        assert not suc


def test_runASTAP_4(app):
    with mock.patch.object(subprocess,
                           'Popen',
                           side_effect=subprocess.TimeoutExpired):
        suc = app.runASTAP(binPath='clear', timeout=1)
        assert not suc


def test_getWCSHeader_1(app):
    val = app.getWCSHeader()
    assert val is None


def test_getWCSHeader_2(app):
    shutil.copy('mw4/test/testData/tempASTAP.wcs', 'mw4/test/temp/temp.wcs')
    val = app.getWCSHeader(wcsTextFile='mw4/test/temp/temp.wcs')
    assert val


def test_solveASTAP_1(app):
    suc = app.solve()
    assert not suc


def test_solveASTAP_2(app):
    suc = app.solve()
    assert not suc


def test_solveASTAP_3(app):
    app.name = 'ASTAP-Mac'
    with mock.patch.object(app,
                           'runASTAP',
                           return_value=False):
        suc = app.solve(fitsPath='mw4/test/image/m51.fit')
        assert not suc


def test_solveASTAP_4(app):
    app.name = 'ASTAP-Mac'
    with mock.patch.object(app,
                           'runASTAP',
                           return_value=True):
        suc = app.solve(fitsPath='mw4/test/image/m51.fit')
        assert not suc


def test_solveASTAP_5(app):
    app.name = 'ASTAP-Mac'
    with mock.patch.object(app,
                           'runASTAP',
                           return_value=True):
        with mock.patch.object(os,
                               'remove',
                               return_value=True):
            shutil.copy('mw4/test/testData/tempASTAP.wcs', 'mw4/test/temp/temp.wcs')
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
    app.framework = 'ASTAP'
    app.process = Test()
    suc = app.abort()
    assert suc


def test_checkAvailability_1(app):
    with mock.patch.object(platform,
                           'system',
                           return_value='Darwin'):
        app.setEnvironment()
        val = app.checkAvailability()
        assert not val


def test_checkAvailability_2(app):
    with mock.patch.object(platform,
                           'system',
                           return_value='Linux'):
        app.setEnvironment()
        val = app.checkAvailability()
        assert not val


def test_checkAvailability_3(app):
    with mock.patch.object(platform,
                           'system',
                           return_value='Windows'):
        app.setEnvironment()
        val = app.checkAvailability()
        assert not val


def test_checkAvailability_4(app):
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
                assert val
