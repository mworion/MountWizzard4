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
import os
import platform
import numpy as np
import subprocess
from astropy.io import fits

# external packages
# local import
from mw4.astrometry import astrometry
from mw4.test.test_units.setupQt import setupQt


@pytest.fixture(autouse=True, scope='module')
def module_setup_teardown():
    global app, spy, mwGlob, test
    app, spy, mwGlob, test = setupQt()
    yield


def test_init_1():
    home = os.environ.get('HOME')
    app.astrometry.solveApp = {
        'KStars': {
            'programPath': '/Applications/Astrometry.app/Contents/MacOS',
            'indexPath': home + '/Library/Application Support/Astrometry',
            'solve': app.astrometry.solveNET,
            'abort': app.astrometry.abortNET,
        }
    }
    assert os.path.isfile(app.mwGlob['tempDir'] + '/astrometry.cfg')


def test_checkAvailability_1():
    app.astrometry.solveApp = {
        'CloudMakers': {
            'programPath': '',
            'indexPath': '',
            'solve': app.astrometry.solveNET,
            'abort': app.astrometry.abortNET,
        }
    }
    suc = app.astrometry.checkAvailability()
    assert suc
    assert app.astrometry.available == {}


def test_checkAvailability_3():
    app.astrometry.solveApp = {
        'KStars': {
            'programPath': '/Applications/KStars.app/Contents/MacOS/astrometry/bin',
            'indexPath': '/usr/share/astrometry',
            'solve': app.astrometry.solveNET,
            'abort': app.astrometry.abortNET,
        }
    }
    suc = app.astrometry.checkAvailability()
    assert suc
    assert app.astrometry.available == {}


def test_checkAvailability_4():
    app.astrometry.solveApp = {
        'KStars': {
            'programPath': '/Applications/Astrometry.app/Contents/MacOS',
            'indexPath': '/Users/mw/Library/Application Support/Astrometry',
            'solve': app.astrometry.solveNET,
            'abort': app.astrometry.abortNET,
        }
    }
    suc = app.astrometry.checkAvailability()
    assert suc
    assert 'KStars' in app.astrometry.available


def test_readFitsData_1():
    file = mwGlob['imageDir'] + '/m51.fits'
    ra, dec, sc, ra1, dec1 = app.astrometry.readFitsData(file)
    assert ra
    assert dec
    assert sc
    assert ra1
    assert dec1


def test_abort_1():
    suc = app.astrometry.abort()
    assert not suc


def test_solveClear():
    app.astrometry.mutexSolve.lock()
    app.astrometry.solveClear()


def test_solveThreading_1():
    suc = app.astrometry.solveThreading()
    assert not suc


def test_solveThreading_2():
    home = os.environ.get('HOME')
    app.astrometry.solveApp = {
        'KStars': {
            'programPath': '/Applications/Astrometry.app/Contents/MacOS',
            'indexPath': home + '/Library/Application Support/Astrometry',
            'solve': app.astrometry.solveNET,
            'abort': app.astrometry.abortNET,
        }
    }
    suc = app.astrometry.solveThreading(app='KStars')
    assert not suc


def test_solveThreading_3():
    home = os.environ.get('HOME')
    app.astrometry.solveApp = {
        'KStars': {
            'programPath': '/Applications/Astrometry.app/Contents/MacOS',
            'indexPath': home + '/Library/Application Support/Astrometry',
            'solve': app.astrometry.solveNET,
            'abort': app.astrometry.abortNET,
        }
    }
    file = mwGlob['imageDir'] + '/m51.fits'
    suc = app.astrometry.solveThreading(app='KStars',
                                        fitsPath=file,
                                        )
    assert suc


def test_solveThreading_4():
    home = os.environ.get('HOME')
    app.astrometry.solveApp = {
        'KStars': {
            'programPath': '/Applications/Astrometry.app/Contents/MacOS',
            'indexPath': home + '/Library/Application Support/Astrometry',
            'solve': app.astrometry.solveNET,
            'abort': app.astrometry.abortNET,
        }
    }
    file = mwGlob['imageDir'] + '/m51.fits'
    suc = app.astrometry.solveThreading(app='KStars',
                                        fitsPath=file,
                                        )
    assert not suc


def test_solveThreading_5():
    app.astrometry.solveApp = {
        'CloudMakers': {
            'programPath': '',
            'indexPath': '',
            'solve': app.astrometry.solveNET,
            'abort': app.astrometry.abortNET,
        }
    }
    file = mwGlob['imageDir'] + '/m51.fits'
    suc = app.astrometry.solveThreading(app='KStars',
                                        fitsPath=file,
                                        )
    assert not suc


def test_abort_1():
    suc = app.astrometry.abort()
    assert not suc


def test_abort_2():
    home = os.environ.get('HOME')
    app.astrometry.solveApp = {
        'KStars': {
            'programPath': '/Applications/Astrometry.app/Contents/MacOS',
            'indexPath': home + '/Library/Application Support/Astrometry',
            'solve': app.astrometry.solveNET,
            'abort': app.astrometry.abortNET,
        }
    }
    suc = app.astrometry.abort(app='KStars')
    assert suc
