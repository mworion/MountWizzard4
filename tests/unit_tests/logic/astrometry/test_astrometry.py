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
# written in python3, (c) 2019-2021 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
from unittest import mock
import pytest
import os
import numpy as np
import shutil
import glob

# external packages
from astropy.io import fits
from PyQt5.QtCore import QThreadPool, QObject, pyqtSignal

# local import
from logic.astrometry.astrometry import Astrometry


@pytest.fixture(autouse=True, scope='module')
def module_setup_teardown():

    yield

    files = glob.glob('tests/image/*.fit*')
    for f in files:
        os.remove(f)


@pytest.fixture(autouse=True, scope='function')
def app():
    class Test(QObject):
        threadPool = QThreadPool()
        message = pyqtSignal(object, object)
        mwGlob = {'tempDir': 'tests/temp'}

    shutil.copy('tests/testData/m51.fit', 'tests/image/m51.fit')
    shutil.copy('tests/testData/astrometry.cfg', 'tests/temp/astrometry.cfg')
    app = Astrometry(app=Test())

    yield app
    app.threadPool.waitForDone(3000)


def test_properties_1(app):
    app.framework = 'test'

    app.host = ('localhost', 7624)
    app.apiKey = 'test'
    app.indexPath = 'test'
    app.deviceName = 'test'
    app.timeout = 30
    app.searchRadius = 20
    assert app.host == ('localhost', 7624)
    assert app.apiKey == 'test'
    assert app.indexPath == 'test'
    assert app.deviceName == 'test'
    assert app.timeout == 30
    assert app.searchRadius == 20


def test_properties_2(app):
    app.framework = 'astap'

    app.host = ('localhost', 7624)
    app.apiKey = 'test'
    app.indexPath = 'test'
    app.deviceName = 'test'
    app.timeout = 30
    app.searchRadius = 20
    assert app.host == ('localhost', 7624)
    assert app.apiKey == 'test'
    assert app.indexPath == 'test'
    assert app.deviceName == 'test'
    assert app.timeout == 30
    assert app.searchRadius == 20


def test_init_1(app):
    assert 'astrometry' in app.run
    assert 'astap' in app.run


def test_readFitsData_1(app):
    file = 'tests/image/test1.fit'
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    header = hdu[0].header
    header['RA'] = 8.0
    header['DEC'] = 45.0
    hdu.writeto(file)
    ra, dec, sc, ra1, dec1 = app.readFitsData(file)
    assert ra
    assert dec
    assert sc
    assert ra1
    assert dec1


def test_readFitsData_2(app):
    file = 'tests/image/test2.fit'
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    header = hdu[0].header
    header['OBJCTRA'] = '+8 00 00'
    header['OBJCTDEC'] = '45 00 00'
    hdu.writeto(file)
    ra, dec, sc, ra1, dec1 = app.readFitsData(file)
    assert ra
    assert dec
    assert sc
    assert ra1
    assert dec1


def test_readFitsData_3(app):
    file = 'tests/image/test3.fit'
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    hdu.writeto(file)
    ra, dec, sc, ra1, dec1 = app.readFitsData(file)
    assert ra.hours == 0
    assert dec.degrees == 0
    assert sc == 1
    assert ra1 == 0
    assert dec1 == 0


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
    assert not solve['mirroredS']

    assert header['RA'] == header['CRVAL1']
    assert header['DEC'] == header['CRVAL2']


def test_getSolutionFromWCS_1b(app):
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    header = hdu[0].header
    header.set('CRVAL1', 180.0)
    header.set('CRVAL2', 60.0)
    header.set('OBJCTRA', '12 00 00')
    header.set('OBJCTDEC', '60 00 00')
    solve, header = app.getSolutionFromWCS(fitsHeader=header,
                                           wcsHeader=header)
    assert solve['raJ2000S'].hours == 12
    assert solve['decJ2000S'].degrees == 60
    assert solve['angleS'] == 0
    assert solve['scaleS'] == 0
    assert not solve['mirroredS']


def test_getSolutionFromWCS_1c(app):
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    header = hdu[0].header
    header.set('CRVAL1', 180.0)
    header.set('CRVAL2', 60.0)
    solve, header = app.getSolutionFromWCS(fitsHeader=header,
                                           wcsHeader=header)
    assert solve['raJ2000S'].hours == 12
    assert solve['decJ2000S'].degrees == 60
    assert solve['angleS'] == 0
    assert solve['scaleS'] == 0
    assert not solve['mirroredS']


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
    assert not solve['mirroredS']

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
    assert not solve['mirroredS']

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
    assert not solve['mirroredS']

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
    assert not solve['mirroredS']

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
    app.framework = 'astap'
    file = 'tests/image/m51.fit'
    app.mutexSolve.lock()
    suc = app.solveThreading(fitsPath=file)
    assert not suc
    app.mutexSolve.unlock()


def test_solveThreading_4(app):
    app.framework = 'astap'
    file = 'tests/image/m51.fit'
    with mock.patch.object(app.threadPool,
                           'start'):
        suc = app.solveThreading(fitsPath=file)
        app.mutexSolve.unlock()
        assert suc


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


def test_checkAvailability_1(app):
    app.framework = 'test'
    val = app.checkAvailability()
    assert val == (False, False)


def test_checkAvailability_2(app):
    app.framework = 'astap'
    with mock.patch.object(app.run['astap'],
                           'checkAvailability',
                           return_value=(True, True)):
        val = app.checkAvailability()
        assert val == (True, True)


def test_startCommunication(app):
    app.framework = 'astap'
    with mock.patch.object(app,
                           'checkAvailability',
                           return_value=(True, True)):
        suc = app.startCommunication()
        assert suc


def test_stopCommunication(app):
    app.framework = 'astrometry'
    suc = app.stopCommunication()
    assert suc
