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

# external packages
# local import
from mw4.astrometry import astrometryKstars
from mw4.test.test_setupQt import setupQt
app, spy, mwGlob, test = setupQt()

tempDir = mwGlob['tempDir']
threadPool = ''


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    yield


def test_init_1():
    home = os.environ.get('HOME')
    binSolve = '/Applications/kstars.app/Contents/MacOS/astrometry/bin/solve-field'
    binImage = '/Applications/kstars.app/Contents/MacOS/astrometry/bin/image2xy'
    index = home + '/Library/Application Support/Astrometry'
    with mock.patch.object(platform,
                           'system',
                           return_value='Darwin'):
        app = astrometryKstars.AstrometryKstars(tempDir=tempDir,
                                                threadPool=threadPool)
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


def test_convertToHMS_1():
    app = astrometryKstars.AstrometryKstars(tempDir=tempDir,
                                            threadPool=threadPool)
    value = 180.0
    ret = app.convertToHMS(value)
    assert ret == '12:00:00'


def test_convertToHMS_2():
    app = astrometryKstars.AstrometryKstars(tempDir=tempDir,
                                            threadPool=threadPool)
    value = -180.0
    ret = app.convertToHMS(value)
    assert ret == '12:00:00'


def test_convertToHMS_3():
    app = astrometryKstars.AstrometryKstars(tempDir=tempDir,
                                            threadPool=threadPool)
    value = '12 00 34'
    ret = app.convertToHMS(value)
    assert ret == '12:00:34'


def test_convertToHMS_4():
    app = astrometryKstars.AstrometryKstars(tempDir=tempDir,
                                            threadPool=threadPool)
    value = '12 00 34 34'
    ret = app.convertToHMS(value)
    assert ret is None


def test_convertToHMS_5():
    app = astrometryKstars.AstrometryKstars(tempDir=tempDir,
                                            threadPool=threadPool)
    value = '12:00:34'
    ret = app.convertToHMS(value)
    assert ret == '12:00:34'


def test_convertToHMS_6():
    app = astrometryKstars.AstrometryKstars(tempDir=tempDir,
                                            threadPool=threadPool)
    value = '12:00:34.356'
    ret = app.convertToHMS(value)
    assert ret == '12:00:34'


def test_convertToDMS_1():
    app = astrometryKstars.AstrometryKstars(tempDir=tempDir,
                                            threadPool=threadPool)
    value = 90.0
    ret = app.convertToDMS(value)
    assert ret == '+90:00:00'


def test_convertToDMS_2():
    app = astrometryKstars.AstrometryKstars(tempDir=tempDir,
                                            threadPool=threadPool)
    value = -90.0
    ret = app.convertToDMS(value)
    assert ret == '-90:00:00'


def test_convertToDMS_3():
    app = astrometryKstars.AstrometryKstars(tempDir=tempDir,
                                            threadPool=threadPool)
    value = '45 45 45'
    ret = app.convertToDMS(value)
    assert ret == '+45:45:45'


def test_convertToDMS_4():
    app = astrometryKstars.AstrometryKstars(tempDir=tempDir,
                                            threadPool=threadPool)
    value = '45 45 45 50'
    ret = app.convertToDMS(value)
    assert ret is None


def test_convertToDMS_5():
    app = astrometryKstars.AstrometryKstars(tempDir=tempDir,
                                            threadPool=threadPool)
    value = '45:45:45'
    ret = app.convertToDMS(value)
    assert ret == '+45:45:45'


def test_convertToDMS_6():
    app = astrometryKstars.AstrometryKstars(tempDir=tempDir,
                                            threadPool=threadPool)
    value = '45 45 45.345'
    ret = app.convertToDMS(value)
    assert ret == '+45:45:45'


def test_convertToDMS_7():
    app = astrometryKstars.AstrometryKstars(tempDir=tempDir,
                                            threadPool=threadPool)
    value = '++45 45 45'
    ret = app.convertToDMS(value)
    assert ret is None


def test_convertToDMS_8():
    app = astrometryKstars.AstrometryKstars(tempDir=tempDir,
                                            threadPool=threadPool)
    value = '-45 45 45.345'
    ret = app.convertToDMS(value)
    assert ret == '-45:45:45'


def test_checkAvailability_1():
    app = astrometryKstars.AstrometryKstars(tempDir=tempDir,
                                            threadPool=threadPool)
    suc = app.checkAvailability()
    assert suc


def test_checkAvailability_2():
    app = astrometryKstars.AstrometryKstars(tempDir=tempDir,
                                            threadPool=threadPool)
    app.indexPath = ''
    app.binPathImage2xy = ''
    app.binPathSolveField = ''
    suc = app.checkAvailability()
    assert not suc


def test_checkAvailability_3():
    app = astrometryKstars.AstrometryKstars(tempDir=tempDir,
                                            threadPool=threadPool)
    app.indexPath = ''
    app.binPathImage2xy = ''
    suc = app.checkAvailability()
    assert not suc


def test_checkAvailability_4():
    app = astrometryKstars.AstrometryKstars(tempDir=tempDir,
                                            threadPool=threadPool)
    app.indexPath = ''
    suc = app.checkAvailability()
    assert not suc


def test_angle_concept():
    for angle1 in range(-180, 180, 1):
        phi = np.radians(angle1)
        CD11 = np.cos(phi)
        CD12 = np.sin(phi)
        CD21 = -np.sin(phi)
        CD22 = np.cos(phi)

        angle = np.degrees(np.arctan(CD12 / CD11))
        if CD11 > 0 and CD12 > 0:
            # quadrant 1
            pass
        elif CD11 > 0 and CD12 <= 0:
            # quadrant 4
            pass
        elif CD11 < 0 and CD12 > 0:
            # quadrant 2
            angle += 180
        elif CD11 < 0 and CD12 <= 0:
            # quadrant 3
            angle -= 180

        angle = np.round(angle, 0)
        angle1 = np.round(angle1, 0)
        assert angle == angle1



