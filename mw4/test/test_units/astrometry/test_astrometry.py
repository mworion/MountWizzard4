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
# external packages
from astropy.io import fits
# local import
from mw4.astrometry import astrometry
from mw4.test.test_units.setupQt import setupQt


@pytest.fixture(autouse=True, scope='module')
def module_setup_teardown():
    global app, spy, mwGlob, test
    app, spy, mwGlob, test = setupQt()


def test_init_1():
    home = os.environ.get('HOME')
    app.astrometry.solverEnviron = {
        'KStars': {
            'programPath': '/Applications/Astrometry.app/Contents/MacOS',
            'indexPath': home + '/Library/Application Support/Astrometry',
            'solver': app.astrometry.solverNET,
        }
    }
    assert os.path.isfile(app.mwGlob['tempDir'] + '/astrometry.cfg')


def test_checkAvailability_1():
    app.astrometry.solverEnviron = {
        'CloudMakers': {
            'programPath': '',
            'indexPath': '',
            'solver': app.astrometry.solverNET,
        }
    }
    val = app.astrometry.checkAvailability()
    assert val == {}


def test_checkAvailability_3():
    app.astrometry.solverEnviron = {
        'KStars': {
            'programPath': '/Applications/KStars.app/Contents/MacOS/astrometry/bin',
            'indexPath': '/usr/share/astrometry',
            'solver': app.astrometry.solverNET,
        }
    }
    val = app.astrometry.checkAvailability()
    assert val == {}


def test_checkAvailability_4():
    app.astrometry.solverEnviron = {
        'KStars': {
            'programPath': '/Applications/Astrometry.app/Contents/MacOS',
            'indexPath': '/Users/mw/Library/Application Support/Astrometry',
            'solver': app.astrometry.solverNET,
        }
    }
    val = app.astrometry.checkAvailability()
    assert 'KStars' in val


def test_readFitsData_1():
    file = mwGlob['imageDir'] + '/m51.fits'
    ra, dec, sc, ra1, dec1 = app.astrometry.readFitsData(file)
    assert ra
    assert dec
    assert sc
    assert ra1
    assert dec1


def test_calcAngleScaleFromWCS_1():
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    header = hdu[0].header
    scaleX = 2
    for angleX in range(-180, 180, 1):
        phi = np.radians(angleX)
        CD11 = scaleX * np.cos(phi)
        CD12 = scaleX * np.sin(phi)
        header.set('CD1_1', CD11)
        header.set('CD1_2', CD12)
        angle, scale, flip = app.astrometry.calcAngleScaleFromWCS(wcsHeader=header)
        assert np.round(scale, 0) == scaleX * 3600
        assert np.round(angle, 3) == np.round(angleX, 3)


def test_calcAngleScaleFromWCS_2():
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    header = hdu[0].header
    angle, scale, flip = app.astrometry.calcAngleScaleFromWCS(wcsHeader=header)
    assert angle == 0
    assert scale == 0


def test_getSolutionFromWCS_1():
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    header = hdu[0].header
    header.set('CRVAL1', 180.0)
    header.set('CRVAL2', 60.0)
    header.set('RA', 180.0)
    header.set('DEC', 60.0)
    solve, header = app.astrometry.getSolutionFromWCS(fitsHeader=header,
                                                      wcsHeader=header)
    assert solve['raJ2000S'].hours == 12
    assert solve['decJ2000S'].degrees == 60
    assert solve['angleS'] == 0
    assert solve['scaleS'] == 0
    assert not solve['flippedS']

    assert header['RA'] == header['CRVAL1']
    assert header['DEC'] == header['CRVAL2']


def test_getSolutionFromWCS_2():
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    header = hdu[0].header
    header.set('CRVAL1', 180.0)
    header.set('CRVAL2', 60.0)
    header.set('RA', 180.0)
    header.set('DEC', 60.0)
    solve, header = app.astrometry.getSolutionFromWCS(fitsHeader=header,
                                                      wcsHeader=header,
                                                      updateFits=True)
    assert solve['raJ2000S'].hours == 12
    assert solve['decJ2000S'].degrees == 60
    assert solve['angleS'] == 0
    assert solve['scaleS'] == 0
    assert not solve['flippedS']

    assert header['RA'] == header['CRVAL1']
    assert header['DEC'] == header['CRVAL2']


def test_abort_1():
    suc = app.astrometry.abort()
    assert not suc


def test_solveClear():
    app.astrometry.mutexSolve.lock()
    app.astrometry.solveClear()


def test_solveThreading_1():
    suc = app.astrometry.solveThreading()
    app.astrometry.mutexSolve.unlock()
    assert not suc


def test_solveThreading_2():
    home = os.environ.get('HOME')
    app.astrometry.solverEnviron = {
        'KStars': {
            'programPath': '/Applications/Astrometry.app/Contents/MacOS',
            'indexPath': home + '/Library/Application Support/Astrometry',
            'solver': app.astrometry.solverNET,
        }
    }
    app.astrometry.solverSelected = 'KStars'
    suc = app.astrometry.solveThreading()
    assert not suc


def test_solveThreading_3():
    home = os.environ.get('HOME')
    app.astrometry.solverEnviron = {
        'KStars': {
            'programPath': '/Applications/Astrometry.app/Contents/MacOS',
            'indexPath': home + '/Library/Application Support/Astrometry',
            'solver': app.astrometry.solverNET,
        }
    }
    app.astrometry.solverSelected = 'KStars'
    file = mwGlob['imageDir'] + '/m51.fits'
    suc = app.astrometry.solveThreading(fitsPath=file)
    assert suc


def test_solveThreading_5():
    app.astrometry.solverEnviron = {
        'CloudMakers': {
            'programPath': '',
            'indexPath': '',
            'solver': app.astrometry.solverNET,
        }
    }
    app.astrometry.solverSelected = 'KStars'
    file = mwGlob['imageDir'] + '/m51.fits'
    suc = app.astrometry.solveThreading(fitsPath=file)
    assert not suc


def test_abort_1():
    home = os.environ.get('HOME')
    app.astrometry.solverEnviron = {
        'KStars': {
            'programPath': '/Applications/Astrometry.app/Contents/MacOS',
            'indexPath': home + '/Library/Application Support/Astrometry',
            'solver': app.astrometry.solverNET,
        }
    }
    app.astrometry.solverSelected = 'KStars'
    with mock.patch.object(app.astrometry.solverNET,
                           'abort',
                           return_value=True):
        suc = app.astrometry.abort()
        assert suc
