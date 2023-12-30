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
# written in python3, (c) 2019-2023 by mworion
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

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from logic.plateSolve.plateSolve import PlateSolve
from base.loggerMW import setupLogging
setupLogging()


@pytest.fixture(autouse=True, scope='function')
def function():
    files = glob.glob('tests/workDir/image/*.fit*')
    for f in files:
        os.remove(f)
    shutil.copy('tests/testData/m51.fit', 'tests/workDir/image/m51.fit')
    shutil.copy('tests/testData/astrometry.cfg', 'tests/workDir/temp/astrometry.cfg')
    func = PlateSolve(app=App())
    yield func


def test_properties_1(function):
    function.framework = 'test'

    function.host = ('localhost', 7624)
    function.apiKey = 'test'
    function.indexPath = 'test'
    function.deviceName = 'test'
    function.timeout = 30
    function.searchRadius = 20
    assert function.host == ('localhost', 7624)
    assert function.apiKey == 'test'
    assert function.indexPath == 'test'
    assert function.deviceName == 'test'
    assert function.timeout == 30
    assert function.searchRadius == 20


def test_properties_2(function):
    function.framework = 'astap'

    function.host = ('localhost', 7624)
    function.apiKey = 'test'
    function.indexPath = 'test'
    function.deviceName = 'test'
    function.timeout = 30
    function.searchRadius = 20
    assert function.host == ('localhost', 7624)
    assert function.apiKey == 'test'
    assert function.indexPath == 'test'
    assert function.deviceName == 'test'
    assert function.timeout == 30
    assert function.searchRadius == 20


def test_init_1(function):
    assert 'astrometry' in function.run
    assert 'astap' in function.run


def test_readFitsData_1(function):
    file = 'tests/workDir/image/test1.fit'
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    header = hdu[0].header
    header['RA'] = 8.0
    header['DEC'] = 45.0
    hdu.writeto(file)
    ra, dec, sc = function.readFitsData(file)
    assert ra
    assert dec
    assert sc is None


def test_calcAngleScaleFromWCS_1(function):
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
        angle, scale, flip = function.calcAngleScaleFromWCS(wcsHeader=header)
        assert np.round(scale, 0) == scaleX * 3600
        assert np.round(angle, 3) == np.round(angleX, 3)


def test_calcAngleScaleFromWCS_2(function):
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    header = hdu[0].header
    angle, scale, flip = function.calcAngleScaleFromWCS(wcsHeader=header)
    assert angle == 0
    assert scale == 0


def test_getSolutionFromWCS_1(function):
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    header = hdu[0].header
    header.set('CRVAL1', 180.0)
    header.set('CRVAL2', 60.0)
    solve, header = function.getSolutionFromWCS(fitsHeader=header,
                                                wcsHeader=header)
    assert solve['raJ2000S'].hours == 12
    assert solve['decJ2000S'].degrees == 60
    assert solve['angleS'] == 0
    assert solve['scaleS'] == 0
    assert not solve['mirroredS']


def test_getSolutionFromWCS_2(function):
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    header = hdu[0].header
    header.set('CRVAL1', 180.0)
    header.set('CRVAL2', 60.0)
    solve, header = function.getSolutionFromWCS(fitsHeader=header,
                                                wcsHeader=header,
                                                updateFits=True)
    assert solve['raJ2000S'].hours == 12
    assert solve['decJ2000S'].degrees == 60
    assert solve['angleS'] == 0
    assert solve['scaleS'] == 0
    assert not solve['mirroredS']

    assert header['RA'] == header['CRVAL1']
    assert header['DEC'] == header['CRVAL2']


def test_getSolutionFromWCS_3(function):
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    header = hdu[0].header
    header.set('CRVAL1', 180.0)
    header.set('CRVAL2', 60.0)
    header.set('RA', 180.0)
    header.set('DEC', 60.0)
    header.set('CTYPE1', 'TAN')
    header.set('CTYPE2', 'TAN')
    solve, header = function.getSolutionFromWCS(fitsHeader=header,
                                                wcsHeader=header,
                                                updateFits=True)
    assert solve['raJ2000S'].hours == 12
    assert solve['decJ2000S'].degrees == 60
    assert solve['angleS'] == 0
    assert solve['scaleS'] == 0
    assert not solve['mirroredS']

    assert header['RA'] == header['CRVAL1']
    assert header['DEC'] == header['CRVAL2']


def test_getSolutionFromWCS_4(function):
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    header = hdu[0].header
    header.set('CRVAL1', 180.0)
    header.set('CRVAL2', 60.0)
    header.set('RA', 180.0)
    header.set('DEC', 60.0)
    header.set('CTYPE1', 'TAN-SIP')
    header.set('CTYPE2', 'TAN-SIP')
    solve, header = function.getSolutionFromWCS(fitsHeader=header,
                                                wcsHeader=header,
                                                updateFits=True)
    assert solve['raJ2000S'].hours == 12
    assert solve['decJ2000S'].degrees == 60
    assert solve['angleS'] == 0
    assert solve['scaleS'] == 0
    assert not solve['mirroredS']

    assert header['RA'] == header['CRVAL1']
    assert header['DEC'] == header['CRVAL2']


def test_getSolutionFromWCS_5(function):
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
    solve, header = function.getSolutionFromWCS(fitsHeader=header,
                                                wcsHeader=header,
                                                updateFits=True)
    assert solve['raJ2000S'].hours == 12
    assert solve['decJ2000S'].degrees == 60
    assert solve['angleS'] == 0
    assert solve['scaleS'] == 0
    assert not solve['mirroredS']

    assert header['RA'] == header['CRVAL1']


def test_getWCSHeader_1(function):
    val = function.getWCSHeader()
    assert val is None


def test_getWCSHeader_2(function):
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    val = function.getWCSHeader(wcsHDU=hdu)
    assert val


def test_solveClear_1(function):
    function.framework = 'Test'
    suc = function.solveClear()
    assert not suc


def test_solveClear_2(function):
    function.framework = 'astap'
    function.mutexSolve.lock()
    suc = function.solveClear()
    assert suc


def test_solveThreading_1(function):
    function.framework = 'Test'
    suc = function.solveThreading()
    assert not suc


def test_solveThreading_2(function):
    function.framework = 'astap'
    suc = function.solveThreading()
    assert not suc


def test_solveThreading_3(function):
    function.framework = 'astap'
    file = 'tests/workDir/image/m51.fit'
    function.mutexSolve.lock()
    suc = function.solveThreading(fitsPath=file)
    assert not suc
    function.mutexSolve.unlock()


def test_solveThreading_4(function):
    function.framework = 'astap'
    file = 'tests/workDir/image/m51.fit'
    with mock.patch.object(function.threadPool,
                           'start'):
        suc = function.solveThreading(fitsPath=file)
        function.mutexSolve.unlock()
        assert suc


def test_abort_1(function):
    function.framework = 'test'
    suc = function.abort()
    assert not suc


def test_abort_2(function):
    function.framework = 'astap'
    with mock.patch.object(function.run['astap'],
                           'abort',
                           return_value=True):
        suc = function.abort()
        assert suc


def test_checkAvailability_1(function):
    function.framework = 'test'
    val = function.checkAvailability()
    assert val == (False, False)


def test_checkAvailability_2(function):
    function.framework = 'astap'
    with mock.patch.object(function.run['astap'],
                           'checkAvailability',
                           return_value=(True, True)):
        val = function.checkAvailability()
        assert val == (True, True)


def test_startCommunication(function):
    function.framework = 'astap'
    with mock.patch.object(function,
                           'checkAvailability',
                           return_value=(True, True)):
        suc = function.startCommunication()
        assert suc


def test_stopCommunication(function):
    function.framework = 'astrometry'
    suc = function.stopCommunication()
    assert suc
