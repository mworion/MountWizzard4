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
# local import
from mw4.astrometry import astrometry
from mw4.test.test_old.setupQt import setupQt


@pytest.fixture(autouse=True, scope='module')
def module_setup_teardown():
    global app, spy, mwGlob, test
    app, spy, mwGlob, test = setupQt()


def test_solve_1():
    suc = app.astrometry.solverASTAP.solve()
    assert not suc


def test_solve_2():
    a = {
         'programPath': '/Applications/ASTAP.app/Contents/MacOS',
         'indexPath': '/Applications/ASTAP.app/Contents/MacOS',
         'solver': app.astrometry.solverASTAP,
        }
    app.astrometry.solverSelected = 'ASTAP'
    with mock.patch.object(app.astrometry.solverASTAP,
                           'runASTAP',
                           return_value=False):
        suc = app.astrometry.solverASTAP.solve(solver=a,
                                               fitsPath=mwGlob['imageDir'] + '/nonsolve.fits',
                                               timeout=5,
                                               )
    assert not suc


def test_solve_3():
    a = {
         'programPath': '/Applications/ASTAP.app/Contents/MacOS',
         'indexPath': '/Applications/ASTAP.app/Contents/MacOS',
         'solver': app.astrometry.solverASTAP,
        }
    with mock.patch.object(app.astrometry.solverASTAP,
                           'runASTAP',
                           return_value=True):
        suc = app.astrometry.solverASTAP.solve(solver=a,
                                               fitsPath=mwGlob['imageDir'] + '/nonsolve.fits',
                                               timeout=5,
                                               )
    assert not suc


def test_solve_4():
    a = {
         'programPath': '/Applications/ASTAP.app/Contents/MacOS',
         'indexPath': '/Applications/ASTAP.app/Contents/MacOS',
         'solver': app.astrometry.solverASTAP,
        }
    with mock.patch.object(app.astrometry.solverASTAP,
                           'runASTAP',
                           return_value=True):
        suc = app.astrometry.solverASTAP.solve(solver=a,
                                               fitsPath=mwGlob['imageDir'] + '/m51.fits',
                                               timeout=5,
                                               )
    assert not suc


def test_solve_5():
    src = mwGlob['tempDir'] + '/temp_astap.wcs'
    dest = mwGlob['tempDir'] + '/temp.wcs'
    shutil.copy(src, dest)
    a = {
         'programPath': '/Applications/ASTAP.app/Contents/MacOS',
         'indexPath': '/Applications/ASTAP.app/Contents/MacOS',
         'solver': app.astrometry.solverASTAP,
        }
    app.astrometry.solverSelected = 'ASTAP'
    with mock.patch.object(app.astrometry.solverASTAP,
                           'runASTAP',
                           return_value=True):
        with mock.patch.object(os,
                               'remove'):
            suc = app.astrometry.solverASTAP.solve(solver=a,
                                                   fitsPath=mwGlob['imageDir'] + '/m51.fits',
                                                   timeout=5,
                                                   )
            assert suc


def test_abort_1():
    app.astrometry.process = None
    suc = app.astrometry.abort()
    assert not suc


def test_abort_2():
    class Test:
        @staticmethod
        def kill():
            return True
    app.astrometry.framework = 'ASTAP'
    app.astrometry.solverEnviron['ASTAP']['solver'].process = Test()
    suc = app.astrometry.abort()
    assert suc
