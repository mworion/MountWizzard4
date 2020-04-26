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
# Python  v3.7.5
#
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
# standard libraries
from unittest import mock
import pytest
import os
import subprocess
import shutil

# external packages
from PyQt5.QtCore import QThreadPool
from astropy.io import fits
import numpy as np

# local import
from mw4.astrometry.astrometry import AstrometryNET, Astrometry


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    class Test:
        threadPool = QThreadPool()

    global app, parent
    parent = Astrometry(app=Test(), tempDir='mw4/test/temp')
    app = AstrometryNET(parent=parent)
    for file in os.listdir('mw4/test/temp'):
        fileP = os.path.join('mw4/test/temp', file)
        if 'temp' not in file:
            continue
        os.remove(fileP)
    shutil.copy('mw4/test/testData/m51.fit', 'mw4/test/image/m51.fit')

    yield


def test_runImage2xy_1():
    suc = app.runImage2xy()
    assert not suc


def test_runImage2xy_2():
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


def test_runSolveField_1():
    suc = app.runSolveField()
    assert not suc


def test_runSolveField_2():
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


def test_getWCSHeader_1():
    val = app.getWCSHeader()
    assert val is None


def test_getWCSHeader_2():
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    val = app.getWCSHeader(wcsHDU=hdu)
    assert val


def test_solveNet_1():
    suc = app.solve()
    assert not suc


def test_solveNet_2():
    parent.solverEnviron = {
        'KStars': {
            'programPath': '/Applications',
            'indexPath': '/Library/Application Support/Astrometry',
            'solver': app,
        }
    }
    suc = app.solve(solver=parent.solverEnviron['KStars'])
    assert not suc


def test_solveNet_3():
    parent.solverEnviron = {
        'KStars': {
            'programPath': '/Applications',
            'indexPath': '/Library/Application Support/Astrometry',
            'solver': app,
        }
    }
    with mock.patch.object(app,
                           'runImage2xy',
                           return_value=False):
        suc = app.solve(solver=parent.solverEnviron['KStars'],
                        fitsPath='mw4/test/image/m51.fit')
        assert not suc


def test_solveNet_4():
    parent.solverEnviron = {
        'KStars': {
            'programPath': '/Applications',
            'indexPath': '/Library/Application Support/Astrometry',
            'solver': app,
        }
    }
    with mock.patch.object(app,
                           'runImage2xy',
                           return_value=True):
        with mock.patch.object(app,
                               'runSolveField',
                               return_value=False):
            suc = app.solve(solver=parent.solverEnviron['KStars'],
                            fitsPath='mw4/test/image/m51.fit')
            assert not suc


def test_solveNet_5():
    parent.solverEnviron = {
        'KStars': {
            'programPath': '/Applications',
            'indexPath': '/Library/Application Support/Astrometry',
            'solver': app,
        }
    }
    with mock.patch.object(app,
                           'runImage2xy',
                           return_value=True):
        with mock.patch.object(app,
                               'runSolveField',
                               return_value=True):
            suc = app.solve(solver=parent.solverEnviron['KStars'],
                            fitsPath='mw4/test/image/m51.fit')
            assert not suc


def test_solveNet_6():
    parent.solverEnviron = {
        'KStars': {
            'programPath': '/Applications',
            'indexPath': '/Library/Application Support/Astrometry',
            'solver': app,
        }
    }
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
                suc = app.solve(solver=parent.solverEnviron['KStars'],
                                fitsPath='mw4/test/image/m51.fit')
                assert not suc


def test_solveNet_7():
    parent.solverEnviron = {
        'KStars': {
            'programPath': '/Applications/KStars.app/Contents/MacOS/astrometry/bin',
            'indexPath': '/Library/Application Support/Astrometry',
            'solver': app,
        }
    }
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
                suc = app.solve(solver=parent.solverEnviron['KStars'],
                                fitsPath='mw4/test/image/m51.fit')
                assert suc


def test_abortNet_1():
    app.process = None
    suc = app.abort()
    assert not suc


def test_abortNet_2():
    class Test:
        @staticmethod
        def kill():
            return True
    app.process = Test()
    suc = app.abort()
    assert suc
