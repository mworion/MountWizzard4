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


def test_properties_1(app):
    app.framework = 'test'

    app.host = ('localhost', 7624)
    app.apiKey = 'test'
    app.indexPath = 'test'
    app.name = 'test'
    assert app.host == ('localhost', 7624)
    assert app.apiKey == 'test'
    assert app.indexPath == 'test'
    assert app.name == 'test'


def test_properties_2(app):
    app.framework = 'astap'

    app.host = ('localhost', 7624)
    app.apiKey = 'test'
    app.indexPath = 'test'
    app.name = 'test'
    assert app.host == ('localhost', 7624)
    assert app.apiKey == 'test'
    assert app.indexPath == 'test'
    assert app.name == 'test'


def test_init_1(app):
    assert 'astrometry' in app.run
    assert 'astap' in app.run


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


def test_getSolutionFromWCS_5(app):
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    header = hdu[0].header
    header.set('CRVAL1', 180.0)
    header.set('CRVAL2', 60.0)
    header.set('RA', 180.0)
    header.set('DEC', 60.0)
    header.set('A_', 60.0)
    header.set('B_', 60.0)
    header.set('AP_', 60.0)
    header.set('BP_', 60.0)
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


def test_solveClear_1(app):
    app.framework = 'Test'
    suc = app.solveClear()
    assert not suc


def test_solveClear_2(app):
    app.framework = 'astap'
    app.mutexSolve.lock()
    suc = app.solveClear()
    assert suc


def test_solveThreading_1(app):
    app.framework = 'Test'
    suc = app.solveThreading()
    assert not suc


def test_solveThreading_2(app):
    app.framework = 'astap'
    suc = app.solveThreading()
    assert not suc


def test_solveThreading_3(app):
    os.scandir('mw4/test/image')
    app.framework = 'astap'
    file = 'mw4/test/image/m51.fit'
    suc = app.solveThreading(fitsPath=file)
    assert suc


def test_solveThreading_4(app):
    app.framework = 'astap'
    file = 'mw4/test/image/m51.fit'
    suc = app.solveThreading(fitsPath=file)
    assert suc


def test_solveThreading_5(app):
    app.mutexSolve.lock()
    app.framework = 'astap'
    file = 'mw4/test/image/m51.fit'
    suc = app.solveThreading(fitsPath=file)
    assert not suc


def test_abort_1(app):
    app.framework = 'test'
    suc = app.abort()
    assert not suc


def test_abort_2(app):
    app.framework = 'astap'
    with mock.patch.object(app.run['astap'],
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
