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
# Python  v3.6.7
#
# Michael Würtenberger
# (c) 2018
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
from astropy.io import fits

# external packages
# local import
from mw4.astrometry import astrometryKstars
from mw4.test.test_setupQt import setupQt
app, spy, mwGlob, test = setupQt()

tempDir = mwGlob['tempDir']
threadPool = ''


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    global app
    app = astrometryKstars.AstrometryKstars(tempDir=tempDir,
                                            threadPool=threadPool)
    yield


def test_init_1():
    home = os.environ.get('HOME')
    binSolve = '/Applications/kstars.app/Contents/MacOS/astrometry/bin/solve-field'
    binImage = '/Applications/kstars.app/Contents/MacOS/astrometry/bin/image2xy'
    index = home + '/Library/Application Support/Astrometry'
    with mock.patch.object(platform,
                           'system',
                           return_value='Darwin'):

        assert app.binPathSolveField == binSolve
        assert app.binPathImage2xy == binImage
        assert app.indexPath == index
        assert os.path.isfile(tempDir + '/astrometry.cfg')


def test_init_2():
    binSolve = '/usr/bin/solve-field'
    binImage = '/usr/bin/image2xy'
    index = '/usr/share/astrometry'
    with mock.patch.object(platform,
                           'system',
                           return_value='Linux'):
        app = astrometryKstars.AstrometryKstars(tempDir=tempDir,
                                                threadPool=threadPool)
        assert app.binPathSolveField == binSolve
        assert app.binPathImage2xy == binImage
        assert app.indexPath == index
        assert os.path.isfile(tempDir + '/astrometry.cfg')


def test_init_3():
    with mock.patch.object(platform,
                           'system',
                           return_value='Windows'):
        app = astrometryKstars.AstrometryKstars(tempDir=tempDir,
                                                threadPool=threadPool)
        assert app.binPathSolveField == ''
        assert app.binPathImage2xy == ''
        assert app.indexPath == ''
        assert os.path.isfile(tempDir + '/astrometry.cfg')


app = astrometryKstars.AstrometryKstars(tempDir=tempDir,
                                        threadPool=threadPool)


def test_convertToHMS_1():
    value = 180.0
    ret = app.convertToHMS(value)
    assert ret == '12:00:00'


def test_convertToHMS_2():
    value = -180.0
    ret = app.convertToHMS(value)
    assert ret == '12:00:00'


def test_convertToHMS_3():
    value = '12 00 34'
    ret = app.convertToHMS(value)
    assert ret == '12:00:34'


def test_convertToHMS_4():
    value = '12 00 34 34'
    ret = app.convertToHMS(value)
    assert ret is None


def test_convertToHMS_5():
    value = '12:00:34'
    ret = app.convertToHMS(value)
    assert ret == '12:00:34'


def test_convertToHMS_6():
    value = '12:00:34.356'
    ret = app.convertToHMS(value)
    assert ret == '12:00:34'


def test_convertToDMS_1():
    value = 90.0
    ret = app.convertToDMS(value)
    assert ret == '+90:00:00'


def test_convertToDMS_2():
    value = -90.0
    ret = app.convertToDMS(value)
    assert ret == '-90:00:00'


def test_convertToDMS_3():
    value = '45 45 45'
    ret = app.convertToDMS(value)
    assert ret == '+45:45:45'


def test_convertToDMS_4():
    value = '45 45 45 50'
    ret = app.convertToDMS(value)
    assert ret is None


def test_convertToDMS_5():
    value = '45:45:45'
    ret = app.convertToDMS(value)
    assert ret == '+45:45:45'


def test_convertToDMS_6():
    value = '45 45 45.345'
    ret = app.convertToDMS(value)
    assert ret == '+45:45:45'


def test_convertToDMS_7():
    value = '++45 45 45'
    ret = app.convertToDMS(value)
    assert ret is None


def test_convertToDMS_8():
    value = '-45 45 45.345'
    ret = app.convertToDMS(value)
    assert ret == '-45:45:45'


def test_checkAvailability_1():
    suc = app.checkAvailability()
    assert suc


def test_checkAvailability_2():
    app.indexPath = ''
    app.binPathImage2xy = ''
    app.binPathSolveField = ''
    suc = app.checkAvailability()
    assert not suc


def test_checkAvailability_3():
    app.indexPath = ''
    app.binPathImage2xy = ''
    suc = app.checkAvailability()
    assert not suc


def test_checkAvailability_4():
    app.indexPath = ''
    suc = app.checkAvailability()
    assert not suc


def test_readFitsData_1():
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    header = hdu[0].header
    header.set('OBJCTRA', '12 30 00.00')
    header.set('OBJCTDEC', '-60 30 00.00')
    header.set('SCALE', 1.3)
    value = app.readFitsData(fitsHDU=hdu)
    assert value[0] == '--scale-low'
    assert value[1] == '1.1818181818181817'
    assert value[2] == '--scale-high'
    assert value[3] == '1.4300000000000002'
    assert value[4] == '--ra'
    assert value[5] == '12:30:00'
    assert value[6] == '--dec'
    assert value[7] == '-60:30:00'
    assert value[8] == '--radius'
    assert value[9] == '1'


def test_readFitsData_2():
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    header = hdu[0].header
    header.set('OBJCTRA', 180.0)
    header.set('OBJCTDEC', 60.0)
    header.set('SCALE', 1.0)
    value = app.readFitsData(fitsHDU=hdu)
    assert value[0] == '--scale-low'
    assert value[1] == '0.9090909090909091'
    assert value[2] == '--scale-high'
    assert value[3] == '1.1'
    assert value[4] == '--ra'
    assert value[5] == '12:00:00'
    assert value[6] == '--dec'
    assert value[7] == '+60:00:00'
    assert value[8] == '--radius'
    assert value[9] == '1'


def test_readFitsData_3():
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    header = hdu[0].header
    header.set('OBJCTRA', 180.0)
    header.set('OBJCTDEC', 60.0)
    header.set('SCALE', 1.0)
    value = app.readFitsData(fitsHDU=hdu, searchRatio=2)
    assert value[0] == '--scale-low'
    assert value[1] == '0.5'
    assert value[2] == '--scale-high'
    assert value[3] == '2.0'
    assert value[4] == '--ra'
    assert value[5] == '12:00:00'
    assert value[6] == '--dec'
    assert value[7] == '+60:00:00'
    assert value[8] == '--radius'
    assert value[9] == '1'


def test_readFitsData_4():
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    value = app.readFitsData(fitsHDU=hdu)
    assert value == ''


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
    ra, dec, angle, scale, flipped = app.getSolutionFromWCS(wcsHeader=header)
    assert ra == 180
    assert dec == 60
    assert angle == 0
    assert scale == 0
    assert not flipped


def test_updateFitsWithWCSData_1():
    hdu1 = fits.HDUList()
    hdu1.append(fits.PrimaryHDU())
    header1 = hdu1[0].header
    header1.set('OBJCTRA', 180.0)
    header1.set('OBJCTDEC', 60.0)

    hdu2 = fits.HDUList()
    hdu2.append(fits.PrimaryHDU())
    header2 = hdu2[0].header
    header2.set('CRVAL1', 180.0)
    header2.set('CRVAL2', 60.0)
    suc = app.updateFitsWithWCSData(fitsHeader=header1, wcsHeader=header2)
    assert suc
    assert header1['RA'] == header2['CRVAL1']
    assert header1['DEC'] == header2['CRVAL2']
    assert header1['ANGLE'] == 0
    assert header1['SCALE'] == 0


def test_runImage2xy():
    suc = app.runImage2xy()
    assert not suc


def test_runSolveField():
    suc = app.runSolveField()
    assert not suc


def test_solve():
    suc, res = app.solve()
    assert not suc


def test_solveDone():
    app.solveDone()


def test_solveResult():
    app.solveResult('')


def test_solveClear():
    app.mutexSolve.lock()
    app.solveClear()


def test_solveThreading():
    suc = app.solveThreading()
    assert not suc
