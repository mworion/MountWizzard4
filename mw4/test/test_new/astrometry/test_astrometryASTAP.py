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

# local import
from mw4.astrometry.astrometry import Astrometry


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    class Test:
        threadPool = QThreadPool()

    global app
    app = Astrometry(app=Test(), tempDir='mw4/test/temp')
    yield
    del app


def test_solve_1():
    suc = app.solverASTAP.solve()
    assert not suc


def test_solve_2():
    a = {
         'programPath': '/Applications/ASTAP.app/Contents/MacOS',
         'indexPath': '/Applications/ASTAP.app/Contents/MacOS',
         'solver': app.solverASTAP,
        }
    app.solverSelected = 'ASTAP'
    with mock.patch.object(app.solverASTAP,
                           'runASTAP',
                           return_value=False):
        suc = app.solverASTAP.solve(solver=a,
                                    fitsPath='mw4/test/image/nonsolve.fits',
                                    timeout=5,
                                    )
    assert not suc


def test_solve_3():
    a = {
         'programPath': '/Applications/ASTAP.app/Contents/MacOS',
         'indexPath': '/Applications/ASTAP.app/Contents/MacOS',
         'solver': app.solverASTAP,
        }
    with mock.patch.object(app.solverASTAP,
                           'runASTAP',
                           return_value=True):
        suc = app.solverASTAP.solve(solver=a,
                                    fitsPath='mw4/test/image/nonsolve.fits',
                                    timeout=5,
                                    )
    assert not suc


def test_solve_4():
    a = {
         'programPath': '/Applications/ASTAP.app/Contents/MacOS',
         'indexPath': '/Applications/ASTAP.app/Contents/MacOS',
         'solver': app.solverASTAP,
        }
    with mock.patch.object(app.solverASTAP,
                           'runASTAP',
                           return_value=True):
        suc = app.solverASTAP.solve(solver=a,
                                    fitsPath='mw4/test/image/m51.fits',
                                    timeout=5,
                                    )
    assert not suc


def test_solve_5():
    src = 'mw4/test/temp/temp_astap.wcs'
    dest = 'mw4/test/temp//temp.wcs'
    shutil.copy(src, dest)
    a = {
         'programPath': '/Applications/ASTAP.app/Contents/MacOS',
         'indexPath': '/Applications/ASTAP.app/Contents/MacOS',
         'solver': app.solverASTAP,
        }
    app.solverSelected = 'ASTAP'
    with mock.patch.object(app.solverASTAP,
                           'runASTAP',
                           return_value=True):
        with mock.patch.object(os,
                               'remove'):
            suc = app.solverASTAP.solve(solver=a,
                                        fitsPath='mw4/test/image/m51.fits',
                                        timeout=5,
                                        )
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
    app.solverEnviron['ASTAP']['solver'].process = Test()
    suc = app.abort()
    assert suc
