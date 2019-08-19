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
# Python  v3.7.4
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
# external packages
# local import
from mw4.astrometry import astrometry
from mw4.test.test_units.setupQt import setupQt


@pytest.fixture(autouse=True, scope='module')
def module_setup_teardown():
    global app, spy, mwGlob, test
    app, spy, mwGlob, test = setupQt()
    yield


def test_solve_1():
    suc = app.astrometry.solveASTAP()
    assert not suc


def test_solve_2():
    with mock.patch.object(app.astrometry,
                           'runASTAP',
                           return_value=False):
        suc = app.astrometry.solveASTAP(app='ASTAP',
                                        fitsPath=mwGlob['imageDir'] + '/nonsolve.fits',
                                        timeout=5,
                                        )
    assert not suc


def test_solve_3():
    with mock.patch.object(app.astrometry,
                           'runASTAP',
                           return_value=True):
        suc = app.astrometry.solveASTAP(app='ASTAP',
                                        fitsPath=mwGlob['imageDir'] + '/nonsolve.fits',
                                        timeout=5,
                                        )
    assert not suc


def test_solve_4():
    app.astrometry.solveApp = {
        'ASTAP': {
            'programPath': '/Applications/ASTAP.app/Contents/MacOS',
            'indexPath': '/Applications/ASTAP.app/Contents/MacOS',
            'solve': app.astrometry.solveASTAP,
            'abort': app.astrometry.abortASTAP,
        }
    }
    with mock.patch.object(app.astrometry,
                           'runASTAP',
                           return_value=True):
        suc = app.astrometry.solveASTAP(app='ASTAP',
                                        fitsPath=mwGlob['imageDir'] + '/nonsolve.fits',
                                        timeout=5,
                                        )
    assert not suc
