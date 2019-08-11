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


appMain, spy, mwGlob, test = setupQt()

tempDir = mwGlob['tempDir']
threadPool = ''


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    global app
    app = astrometry.Astrometry(appMain,
                                tempDir=tempDir,
                                threadPool=threadPool)
    yield


def test_init_1():
    home = os.environ.get('HOME')
    binSolve = '/Applications/KStars300.app/Contents/MacOS/astrometry/bin'
    index = home + '/Library/Application Support/Astrometry'
    with mock.patch.object(platform,
                           'system',
                           return_value='Darwin'):

        assert app.binPath['KStars300'] == binSolve
        assert app.indexPath == index
        assert os.path.isfile(tempDir + '/astrometry.cfg')


def test_init_2():
    binSolve = '/usr/bin'
    index = '/usr/share/astrometry'
    with mock.patch.object(platform,
                           'system',
                           return_value='Linux'):
        app = astrometry.Astrometry(appMain,
                                    tempDir=tempDir,
                                    threadPool=threadPool)
        assert app.binPath['astrometry-glob'] == binSolve
        assert app.indexPath == index
        assert os.path.isfile(tempDir + '/astrometry.cfg')


def test_init_3():
    with mock.patch.object(platform,
                           'system',
                           return_value='Windows'):
        app = astrometry.Astrometry(appMain,
                                    tempDir=tempDir,
                                    threadPool=threadPool)
        assert app.binPath == {}
        assert app.indexPath == ''
        assert os.path.isfile(tempDir + '/astrometry.cfg')


app = astrometry.Astrometry(appMain,
                            tempDir=tempDir,
                            threadPool=threadPool)


def test_checkAvailability_1():
    app.indexPath = ''
    app.binPath = {}
    suc = app.checkAvailability()
    assert suc
    assert app.available == {}


def test_checkAvailability_2():
    app.indexPath = '/usr/share/astrometry'
    app.binPath = {'KStars': '/Applications/KStars300.app/Contents/MacOS/astrometry/bin'}
    with mock.patch.object(platform,
                           'system',
                           return_value='Linux'):
        suc = app.checkAvailability()
        assert suc
        assert app.available == {}


def test_checkAvailability_3():
    app.indexPath = '/usr/share/astrometry'
    app.binPath = {'KStars': '/Applications/KStars300.app/Contents/MacOS/astrometry/bin'}
    with mock.patch.object(platform,
                           'system',
                           return_value='Darwin'):
        suc = app.checkAvailability()
        assert suc
        assert app.available == {}


def test_checkAvailability_4():
    app.indexPath = '/Users/mw/Library/Application Support/Astrometry'
    app.binPath = {'KStars': '/Applications/KStars300.app/Contents/MacOS/astrometry/bin'}
    with mock.patch.object(platform,
                           'system',
                           return_value='Darwin'):
        suc = app.checkAvailability()
        assert suc
        assert 'KStars' in app.available


def test_getWCSHeader():
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    value = app.getWCSHeader(wcsHDU=hdu)
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
        angle, scale, flip = app.calcAngleScaleFromWCS(wcsHeader=header)
        assert np.round(scale, 0) == scaleX * 3600
        assert np.round(angle, 3) == np.round(angleX, 3)


def test_calcAngleScaleFromWCS_2():
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    header = hdu[0].header
    angle, scale, flip = app.calcAngleScaleFromWCS(wcsHeader=header)
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
    (ra, dec, angle, scale, error, flipped), header = app.getSolutionFromWCS(fitsHeader=header,
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
    (ra, dec, angle, scale, error, flipped), header = app.getSolutionFromWCS(fitsHeader=header,
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
    suc = app.runImage2xy()
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
        suc = app.runImage2xy()
    assert not suc


def test_runSolveField_1():
    suc = app.runSolveField()
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
        suc = app.runSolveField()
    assert not suc


def test_abort_1():
    class Test:
        @staticmethod
        def kill():
            return

    app.process = Test()
    suc = app.abort()
    assert suc


def test_abort_2():
    class Test:
        @staticmethod
        def kill():
            return

    app.process = None
    suc = app.abort()
    assert not suc


def test_solve_1():
    suc = app.solve()
    assert not suc


def test_solve_2():
    with mock.patch.object(app,
                           'runImage2xy',
                           return_value=False):
        with mock.patch.object(app,
                               'runSolveField',
                               return_value=False):
            suc = app.solve(app='KStars300',
                            fitsPath=mwGlob['imageDir'] + '/nonsolve.fits',
                            timeout=5,
                            )
        assert not suc


def test_solve_3():
    with mock.patch.object(app,
                           'runImage2xy',
                           return_value=True):
        with mock.patch.object(app,
                               'runSolveField',
                               return_value=False):
            suc = app.solve(app='KStars300',
                            fitsPath=mwGlob['imageDir'] + '/nonsolve.fits',
                            timeout=5,
                            )
        assert not suc


def test_solve_4():
    with mock.patch.object(app,
                           'runImage2xy',
                           return_value=True):
        with mock.patch.object(app,
                               'runSolveField',
                               return_value=True):
            suc = app.solve(app='KStars300',
                            fitsPath=mwGlob['imageDir'] + '/nonsolve.fits',
                            timeout=5,
                            )
        assert suc


def test_solveClear():
    app.mutexSolve.lock()
    app.solveClear()


def test_solveThreading():
    suc = app.solveThreading()
    assert not suc
