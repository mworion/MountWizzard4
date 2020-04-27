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
import platform
import numpy as np
import shutil
import glob
import faulthandler
faulthandler.enable()

# external packages
from astropy.io import fits
from PyQt5.QtCore import QThreadPool

# local import
from mw4.astrometry.astrometry import Astrometry


@pytest.fixture(autouse=True, scope='function')
def app():
    class Test:
        threadPool = QThreadPool()

    shutil.copy('mw4/test/testData/astrometry.cfg', 'mw4/test/temp/astrometry.cfg')
    shutil.copy('mw4/test/testData/m51.fit', 'mw4/test/image/m51.fit')
    app = Astrometry(app=Test(), tempDir='mw4/test/temp')

    yield app

    files = glob.glob('mw4/test/image/*.fit*')
    for f in files:
        os.remove(f)


def test_init_1(app):
    home = os.environ.get('HOME')
    app.solverEnviron = {
        'KStars': {
            'programPath': '/Applications/Astrometry.app/Contents/MacOS',
            'indexPath': home + '/Library/Application Support/Astrometry',
            'solver': app.solverNET,
        }
    }
    assert os.path.isfile('mw4/test/temp/astrometry.cfg')


def test_setSolverEnviron_1(app):
    with mock.patch.object(platform,
                           'system',
                           return_value='Windows'):
        app.setSolverEnviron()


def test_setSolverEnviron_2(app):
    with mock.patch.object(platform,
                           'system',
                           return_value='Linux'):
        app.setSolverEnviron()


def test_setSolverEnviron_3(app):
    with mock.patch.object(platform,
                           'system',
                           return_value='Darwin'):
        app.setSolverEnviron()


def test_checkAvailability_1(app):
    app.solverEnviron = {
        'CloudMakers': {
            'programPath': '',
            'indexPath': '',
            'solver': app.solverNET,
        }
    }
    val = app.checkAvailability()
    assert val == {}


def test_checkAvailability_3(app):
    app.solverEnviron = {
        'KStars': {
            'programPath': '/Applications/KStars.app/Contents/MacOS/astrometry/bin',
            'indexPath': '/usr/share/astrometry',
            'solver': app.solverNET,
        }
    }
    val = app.checkAvailability()
    assert val == {}


def test_checkAvailability_4(app):
    app.solverEnviron = {
        'CloudMakers': {
            'programPath': '/Applications/Astrometry.app/Contents/MacOS',
            'indexPath': '/Users/mw/Library/Application Support/Astrometry',
            'solver': app.solverNET,
        }
    }
    app.checkAvailability()


def test_readFitsData_1(app):
    os.scandir('mw4/test/image')
    file = 'mw4/test/image/m51.fit'
    ra, dec, sc, ra1, dec1 = app.readFitsData(file)
    assert ra
    assert dec
    assert sc
    assert ra1
    assert dec1


def test_calcAngleScaleFromWCS_1(app):
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
        angle, scale, flip = app.calcAngleScaleFromWCS(wcsHeader=header)
        assert np.round(scale, 0) == scaleX * 3600
        assert np.round(angle, 3) == np.round(angleX, 3)


def test_calcAngleScaleFromWCS_2(app):
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    header = hdu[0].header
    angle, scale, flip = app.calcAngleScaleFromWCS(wcsHeader=header)
    assert angle == 0
    assert scale == 0


def test_getSolutionFromWCS_1(app):
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    header = hdu[0].header
    header.set('CRVAL1', 180.0)
    header.set('CRVAL2', 60.0)
    header.set('RA', 180.0)
    header.set('DEC', 60.0)
    solve, header = app.getSolutionFromWCS(fitsHeader=header,
                                           wcsHeader=header)
    assert solve['raJ2000S'].hours == 12
    assert solve['decJ2000S'].degrees == 60
    assert solve['angleS'] == 0
    assert solve['scaleS'] == 0
    assert not solve['flippedS']

    assert header['RA'] == header['CRVAL1']
    assert header['DEC'] == header['CRVAL2']


def test_getSolutionFromWCS_2(app):
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    header = hdu[0].header
    header.set('CRVAL1', 180.0)
    header.set('CRVAL2', 60.0)
    header.set('RA', 180.0)
    header.set('DEC', 60.0)
    solve, header = app.getSolutionFromWCS(fitsHeader=header,
                                           wcsHeader=header,
                                           updateFits=True)
    assert solve['raJ2000S'].hours == 12
    assert solve['decJ2000S'].degrees == 60
    assert solve['angleS'] == 0
    assert solve['scaleS'] == 0
    assert not solve['flippedS']

    assert header['RA'] == header['CRVAL1']
    assert header['DEC'] == header['CRVAL2']


def test_getSolutionFromWCS_3(app):
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    header = hdu[0].header
    header.set('CRVAL1', 180.0)
    header.set('CRVAL2', 60.0)
    header.set('RA', 180.0)
    header.set('DEC', 60.0)
    header.set('CTYPE1', 'TAN')
    header.set('CTYPE2', 'TAN')
    solve, header = app.getSolutionFromWCS(fitsHeader=header,
                                           wcsHeader=header,
                                           updateFits=True)
    assert solve['raJ2000S'].hours == 12
    assert solve['decJ2000S'].degrees == 60
    assert solve['angleS'] == 0
    assert solve['scaleS'] == 0
    assert not solve['flippedS']

    assert header['RA'] == header['CRVAL1']
    assert header['DEC'] == header['CRVAL2']


def test_getSolutionFromWCS_4(app):
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    header = hdu[0].header
    header.set('CRVAL1', 180.0)
    header.set('CRVAL2', 60.0)
    header.set('RA', 180.0)
    header.set('DEC', 60.0)
    header.set('CTYPE1', 'TAN-SIP')
    header.set('CTYPE2', 'TAN-SIP')
    solve, header = app.getSolutionFromWCS(fitsHeader=header,
                                           wcsHeader=header,
                                           updateFits=True)
    assert solve['raJ2000S'].hours == 12
    assert solve['decJ2000S'].degrees == 60
    assert solve['angleS'] == 0
    assert solve['scaleS'] == 0
    assert not solve['flippedS']

    assert header['RA'] == header['CRVAL1']
    assert header['DEC'] == header['CRVAL2']


def test_solveClear_1(app):
    app.framework = 'Test'
    suc = app.solveClear()
    assert not suc


def test_solveClear_2(app):
    app.framework = 'CloudMakers'
    app.mutexSolve.lock()
    suc = app.solveClear()
    assert suc


def test_solveThreading_1(app):
    app.framework = 'Test'
    suc = app.solveThreading()
    assert not suc


def test_solveThreading_2(app):
    home = os.environ.get('HOME')
    app.solverEnviron = {
        'KStars': {
            'programPath': '/Applications/Astrometry.app/Contents/MacOS',
            'indexPath': home + '/Library/Application Support/Astrometry',
            'solver': app.solverNET,
        }
    }
    app.framework = 'KStars'
    suc = app.solveThreading()
    assert not suc


def test_solveThreading_3(app):
    os.scandir('mw4/test/image')
    home = os.environ.get('HOME')
    app.solverEnviron = {
        'KStars': {
            'programPath': '/Applications/Astrometry.app/Contents/MacOS',
            'indexPath': home + '/Library/Application Support/Astrometry',
            'solver': app.solverNET,
        }
    }
    app.framework = 'KStars'
    file = 'mw4/test/image/m51.fit'
    suc = app.solveThreading(fitsPath=file)
    assert suc


def test_solveThreading_5(app):
    app.solverEnviron = {
        'CloudMakers': {
            'programPath': '',
            'indexPath': '',
            'solver': app.solverNET,
        }
    }
    app.framework = 'KStars'
    file = 'mw4/test/image/m51.fits'
    suc = app.solveThreading(fitsPath=file)
    assert not suc


def test_abort_1(app):
    app.solverEnviron = {
        'KStars': {
            'programPath': '/Applications/Astrometry.app/Contents/MacOS',
            'indexPath': '/Library/Application Support/Astrometry',
            'solver': app.solverNET,
        }
    }
    app.framework = 'test'
    suc = app.abort()
    assert not suc


def test_abort_2(app):

    app.solverEnviron = {
        'KStars': {
            'programPath': '/Applications/Astrometry.app/Contents/MacOS',
            'indexPath': '/Library/Application Support/Astrometry',
            'solver': app.solverNET,
        }
    }
    app.framework = 'KStars'
    with mock.patch.object(app.solverNET,
                           'abort',
                           return_value=True):
        suc = app.abort()
        assert suc


def test_startCommunication(app):
    suc = app.startCommunication()
    assert suc


def test_stopCommunication(app):
    suc = app.stopCommunication()
    assert suc
