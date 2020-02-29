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
import shutil
import subprocess
import os

# external packages
from PyQt5.QtCore import QThreadPool
from astropy.io import fits
import numpy as np

# local import
from mw4.astrometry.astrometry import AstrometryASTAP, Astrometry


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    class Test:
        threadPool = QThreadPool()

    global app, parent
    parent = Astrometry(app=Test(), tempDir='mw4/test/temp')
    app = AstrometryASTAP(parent=parent)
    for file in os.listdir('mw4/test/temp'):
        fileP = os.path.join('mw4/test/temp', file)
        if 'temp' not in file:
            continue
        os.remove(fileP)
    yield
    del app, parent


def test_runASTAP_1():
    suc = app.runASTAP()
    assert not suc


def test_runASTAP_2():
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


def test_getWCSHeader_1():
    val = app.getWCSHeader()
    assert val is None


def test_getWCSHeader_2():
    shutil.copy('mw4/test/testData/tempASTAP.wcs', 'mw4/test/temp/temp.wcs')
    val = app.getWCSHeader(wcsTextFile='mw4/test/temp/temp.wcs')
    assert val


def test_solveASTAP_1():
    suc = app.solve()
    assert not suc


def test_solveASTAP_2():
    parent.solverEnviron = {
        'ASTAP': {
            'programPath': '/Applications',
            'indexPath': '/Library/Application Support/Astrometry',
            'solver': app,
        }
    }
    suc = app.solve(solver=parent.solverEnviron['ASTAP'])
    assert not suc


def test_solveASTAP_4():
    parent.solverEnviron = {
        'ASTAP': {
            'programPath': '/Applications',
            'indexPath': '/Library/Application Support/Astrometry',
            'solver': app,
        }
    }
    with mock.patch.object(app,
                           'runASTAP',
                           return_value=False):
        suc = app.solve(solver=parent.solverEnviron['ASTAP'],
                        fitsPath='mw4/test/image/m51.fit')
        assert not suc


def test_solveASTAP_5():
    parent.solverEnviron = {
        'ASTAP': {
            'programPath': '/Applications',
            'indexPath': '/Library/Application Support/Astrometry',
            'solver': app,
        }
    }
    with mock.patch.object(app,
                           'runASTAP',
                           return_value=True):
        suc = app.solve(solver=parent.solverEnviron['ASTAP'],
                        fitsPath='mw4/test/image/m51.fit')
        assert not suc


def test_solveASTAP_6():
    parent.solverEnviron = {
        'ASTAP': {
            'programPath': '/Applications',
            'indexPath': '/Library/Application Support/Astrometry',
            'solver': app,
        }
    }
    with mock.patch.object(app,
                           'runASTAP',
                           return_value=True):
        with mock.patch.object(os,
                               'remove',
                               return_value=True):
            shutil.copy('mw4/test/testData/tempASTAP.wcs', 'mw4/test/temp/temp.wcs')
            suc = app.solve(solver=parent.solverEnviron['ASTAP'],
                            fitsPath='mw4/test/image/m51.fit')
            assert suc


def test_abort_1():
    app.process = None
    suc = app.abort()
    assert not suc


def test_abort_2():
    class Test:
        @staticmethod
        def kill():
            return True
    app.framework = 'ASTAP'
    app.process = Test()
    suc = app.abort()
    assert suc
