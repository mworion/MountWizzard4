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

# external packages
# local import
from mw4.astrometry import astrometry
from mw4.test.test_units.setupQt import setupQt


@pytest.fixture(autouse=True, scope='module')
def module_setup_teardown():
    global app, spy, mwGlob, test
    app, spy, mwGlob, test = setupQt()
    yield


def test_getWCSHeader():
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    value = app.astrometry.getWCSHeader(wcsHDU=hdu)
    assert value == hdu[0].header


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
    (ra, dec, angle, scale, error, flipped, path), header \
        = app.astrometry.getSolutionFromWCS(fitsHeader=header,
                                            wcsHeader=header)
    assert ra.hours == 12
    assert dec.degrees == 60
    assert angle == 0
    assert scale == 0
    assert not flipped

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
    (ra, dec, angle, scale, error, flipped, path), header \
        = app.astrometry.getSolutionFromWCS(fitsHeader=header,
                                            wcsHeader=header,
                                            updateFits=True)
    assert ra.hours == 12
    assert dec.degrees == 60
    assert angle == 0
    assert scale == 0
    assert not flipped

    assert header['RA'] == header['CRVAL1']
    assert header['DEC'] == header['CRVAL2']


def test_runImage2xy_1():
    suc = app.astrometry.runImage2xy()
    assert not suc


def test_runImage2xy_2():
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
        suc = app.astrometry.runImage2xy()
    assert not suc


def test_runSolveField_1():
    suc = app.astrometry.runSolveField()
    assert not suc


def test_runSolveField_2():
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
        suc = app.astrometry.runSolveField()
    assert not suc


def test_solveNet_1():
    suc = app.astrometry.solveNET()
    assert not suc


def test_solveNet_2():
    with mock.patch.object(app.astrometry,
                           'runImage2xy',
                           return_value=False):
        with mock.patch.object(app.astrometry,
                               'runSolveField',
                               return_value=False):
            suc = app.astrometry.solveNET(app='KStars',
                                          fitsPath=mwGlob['imageDir'] + '/nonsolve.fits',
                                          timeout=5,
                                          )
        assert not suc


def test_solveNet_3():
    with mock.patch.object(app.astrometry,
                           'runImage2xy',
                           return_value=True):
        with mock.patch.object(app.astrometry,
                               'runSolveField',
                               return_value=False):
            suc = app.astrometry.solveNET(app='KStars',
                                          fitsPath=mwGlob['imageDir'] + '/nonsolve.fits',
                                          timeout=5,
                                          )
        assert not suc


def test_solveNet_4():
    home = os.environ.get('HOME')
    app.astrometry.solveApp = {
        'KStars': {
            'programPath': '/Applications/Astrometry.app/Contents/MacOS',
            'indexPath': home + '/Library/Application Support/Astrometry',
            'solve': app.astrometry.solveNET,
            'abort': app.astrometry.abortNET,
        }
    }
    with mock.patch.object(app.astrometry,
                           'runImage2xy',
                           return_value=True):
        with mock.patch.object(app.astrometry,
                               'runSolveField',
                               return_value=True):
            suc = app.astrometry.solveNET(app='KStars',
                                          fitsPath=mwGlob['imageDir'] + '/m51.fits',
                                          timeout=5,
                                          )
        assert suc


def test_abortNet_1():
    app.astrometry.process = None
    suc = app.astrometry.abortNET()
    assert not suc


def test_abortNet_2():
    class Test:
        @staticmethod
        def kill():
            return True
    app.astrometry.process = Test()
    suc = app.astrometry.abortNET()
    assert suc
