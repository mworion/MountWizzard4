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
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
import os

# external packages
from skyfield.api import Angle, wgs84
import numpy as np

# local imports
from mountcontrol.mount import Mount
from base.loggerMW import setupLogging
setupLogging()


@pytest.fixture(autouse=True, scope='function')
def function():
    m = Mount(host='192.168.2.15',
              pathToData=os.getcwd() + '/data',
              verbose=True)
    m.obsSite.location = wgs84.latlon(latitude_degrees=90,
                                      longitude_degrees=11,
                                      elevation_m=500)
    yield m


def test_properties_1(function):
    function.geometry.initializeGeometry('10micron GM1000HPS')
    function.geometry.offVertGEM = 0.10
    function.geometry.offNorthGEM = 0.10
    function.geometry.offEastGEM = 0.10
    function.geometry.offVert = 0.10
    function.geometry.offEast = 0.10
    function.geometry.offNorth = 0.10
    assert function.geometry.offVertGEM == 0
    assert function.geometry.offNorthGEM == 0
    assert function.geometry.offEastGEM == 0


def test_properties_2(function):
    function.geometry.initializeGeometry('10micron GM1000HPS')
    function.geometry.offVert = 0.10
    function.geometry.offEast = 0.10
    function.geometry.offNorth = 0.10
    function.geometry.offVertGEM = 0.10
    function.geometry.offNorthGEM = 0.10
    function.geometry.offEastGEM = 0.10
    assert function.geometry.offVert == 0
    assert function.geometry.offNorth == 0
    assert function.geometry.offEast == 0


def test_properties_3(function):
    function.geometry.initializeGeometry('10micron GM1000HPS')
    function.geometry.offGEM = 0.10
    val = function.geometry.offPlateOTA
    assert val == 0.1 - function.geometry.offGemPlate


def test_properties_4(function):
    function.geometry.initializeGeometry('10micron GM1000HPS')
    function.geometry.offPlateOTA = 0.10
    val = function.geometry.offGEM
    assert val == 0.1 + function.geometry.offGemPlate


def test_initializeGeometry_1(function):
    suc = function.geometry.initializeGeometry('')
    assert not suc


def test_initializeGeometry_2(function):
    suc = function.geometry.initializeGeometry('10micron GM1000HPS')
    assert suc


def test_transformRotX_1(function):
    function.geometry.transformRotX(90, degrees=True)


def test_transformRotX_2(function):
    function.geometry.transformRotX(np.pi)


def test_transformRotX_3(function):
    function.geometry.transformRotX(Angle(degrees=90))


def test_transformRotY_1(function):
    function.geometry.transformRotY(90, degrees=True)


def test_transformRotY_2(function):
    function.geometry.transformRotY(np.pi)


def test_transformRotY_3(function):
    function.geometry.transformRotY(Angle(degrees=90))


def test_transformRotZ_1(function):
    function.geometry.transformRotZ(90, degrees=True)


def test_transformRotZ_2(function):
    function.geometry.transformRotZ(np.pi)


def test_transformRotZ_3(function):
    function.geometry.transformRotZ(Angle(degrees=90))


def test_transformTranslate(function):
    function.geometry.transformTranslate([1, 2, 3])


def test_geometry_1(function):
    suc = function.geometry.initializeGeometry('10micron GM1000HPS')
    function.geometry.offNorth = 0.1
    function.geometry.offEast = 0.2
    function.geometry.offVert = 0.3
    function.geometry.offGEM = 0.1
    function.geometry.offLAT = 0.2
    function.geometry.domeRadius = 1.5

    assert suc

    testValues = [[0, 0, 'E'],
                  [0, 6, 'E'],
                  [0, 12, 'E'],
                  [0, 18, 'E'],
                  [45, 0, 'E'],
                  [45, 6, 'E'],
                  [45, 12, 'E'],
                  [45, 18, 'E'],
                  [0, 0, 'W'],
                  [0, 6, 'W'],
                  [0, 12, 'W'],
                  [0, 18, 'W'],
                  [45, 0, 'W'],
                  [45, 6, 'W'],
                  [45, 12, 'W'],
                  [45, 18, 'W']]

    results = [
        [81.42689500055411, 26.565051177077958, 0.2000000000000001, -0.09999999999999992,
         1.4832396974191326],
        [3.8225537292743446, 277.6794427904114, 0.2000000000000001, 1.4832396974191326, 0.1],
        [-81.4268950005541, 333.434948822922, 0.2000000000000001, 0.10000000000000009,
         -1.4832396974191326],
        [-3.822553729274351, 82.32055720958864, 0.2000000000000001, -1.4832396974191326,
         -0.10000000000000019],
        [37.223444738231244, 4.8025610547841895, 1.1902302044074613, -0.09999999999999996,
         0.9073874919328418],
        [3.8225537292743446, 322.6794427904114, 1.1902302044074613, 0.9073874919328418, 0.1],
        [-37.223444738231244, 355.19743894521577, 1.1902302044074613, 0.10000000000000005,
         -0.9073874919328418],
        [-3.8225537292743486, 37.320557209588635, 1.1902302044074613, -0.9073874919328418,
         -0.10000000000000012],
        [81.42689500055411, 206.5650511770781, -0.19999999999999993, 0.10000000000000027,
         1.4832396974191326],
        [-3.822553729274351, 262.3205572095886, -0.19999999999999993, 1.4832396974191326,
         -0.10000000000000019],
        [-81.42689500055411, 153.43494882292197, -0.19999999999999993, -0.10000000000000009,
         -1.4832396974191326],
        [3.8225537292743446, 97.67944279041136, -0.19999999999999993, -1.4832396974191326,
         0.1],
        [52.51256311391629, 353.71101162190206, 0.907387491932842, 0.10000000000000021,
         1.1902302044074609],
        [-3.8225537292743508, 307.3205572095886, 0.907387491932842, 1.1902302044074609,
         -0.10000000000000014],
        [-52.51256311391629, 6.288988378097951, 0.907387491932842, -0.10000000000000007,
         -1.1902302044074609],
        [3.822553729274345, 52.67944279041136, 0.907387491932842, -1.1902302044074609, 0.1],
    ]

    for t, r in zip(testValues, results):
        val = function.geometry.calcTransformationMatrices(dec=Angle(degrees=t[0]),
                                                           ha=Angle(hours=t[1]),
                                                           lat=Angle(degrees=50),
                                                           pierside=t[2])
        alt, az, inter, _, _ = val
        assert pytest.approx(alt.degrees, 0.001) == r[0]
        assert pytest.approx(az.degrees, 0.001) == r[1]
        assert pytest.approx(inter[0], 0.001) == r[2]
        assert pytest.approx(inter[1], 0.001) == r[3]
        assert pytest.approx(inter[2], 0.001) == r[4]


def test_geometry_2(function):
    suc = function.geometry.initializeGeometry('10micron GM2000HPS')
    function.geometry.offNorth = 0.1
    function.geometry.offEast = 0.2
    function.geometry.offVert = 0.3
    function.geometry.offGEM = 0.1
    function.geometry.offLAT = 0.2
    function.geometry.domeRadius = 1.5

    assert suc

    testValues = [[0, 0, 'E'],
                  [0, 6, 'E'],
                  [0, 12, 'E'],
                  [0, 18, 'E'],
                  [45, 0, 'E'],
                  [45, 6, 'E'],
                  [45, 12, 'E'],
                  [45, 18, 'E'],
                  [0, 0, 'W'],
                  [0, 6, 'W'],
                  [0, 12, 'W'],
                  [0, 18, 'W'],
                  [45, 0, 'W'],
                  [45, 6, 'W'],
                  [45, 12, 'W'],
                  [45, 18, 'W']]

    results = [
        [81.42689500055411, 26.565051177077958, 0.2000000000000001, -0.09999999999999992,
         1.4832396974191326],
        [3.8225537292743446, 277.6794427904114, 0.2000000000000001, 1.4832396974191326, 0.1],
        [-81.4268950005541, 333.434948822922, 0.2000000000000001, 0.10000000000000009,
         -1.4832396974191326],
        [-3.822553729274351, 82.32055720958864, 0.2000000000000001, -1.4832396974191326,
         -0.10000000000000019],
        [37.223444738231244, 4.8025610547841895, 1.1902302044074613, -0.09999999999999996,
         0.9073874919328418],
        [3.8225537292743446, 322.6794427904114, 1.1902302044074613, 0.9073874919328418, 0.1],
        [-37.223444738231244, 355.19743894521577, 1.1902302044074613, 0.10000000000000005,
         -0.9073874919328418],
        [-3.8225537292743486, 37.320557209588635, 1.1902302044074613, -0.9073874919328418,
         -0.10000000000000012],
        [81.42689500055411, 206.5650511770781, -0.19999999999999993, 0.10000000000000027,
         1.4832396974191326],
        [-3.822553729274351, 262.3205572095886, -0.19999999999999993, 1.4832396974191326,
         -0.10000000000000019],
        [-81.42689500055411, 153.43494882292197, -0.19999999999999993, -0.10000000000000009,
         -1.4832396974191326],
        [3.8225537292743446, 97.67944279041136, -0.19999999999999993, -1.4832396974191326,
         0.1],
        [52.51256311391629, 353.71101162190206, 0.907387491932842, 0.10000000000000021,
         1.1902302044074609],
        [-3.8225537292743508, 307.3205572095886, 0.907387491932842, 1.1902302044074609,
         -0.10000000000000014],
        [-52.51256311391629, 6.288988378097951, 0.907387491932842, -0.10000000000000007,
         -1.1902302044074609],
        [3.822553729274345, 52.67944279041136, 0.907387491932842, -1.1902302044074609, 0.1],
    ]

    for t, r in zip(testValues, results):
        val = function.geometry.calcTransformationMatrices(dec=Angle(degrees=t[0]),
                                                           ha=Angle(hours=t[1]),
                                                           lat=Angle(degrees=50),
                                                           pierside=t[2])
        alt, az, inter, _, _ = val
        assert pytest.approx(alt.degrees, 0.001) == r[0]
        assert pytest.approx(az.degrees, 0.001) == r[1]
        assert pytest.approx(inter[0], 0.001) == r[2]
        assert pytest.approx(inter[1], 0.001) == r[3]
        assert pytest.approx(inter[2], 0.001) == r[4]


def test_geometry_3(function):
    suc = function.geometry.initializeGeometry('10micron GM3000HPS')
    function.geometry.offNorth = 0.1
    function.geometry.offEast = 0.2
    function.geometry.offVert = 0.3
    function.geometry.offGEM = 0.1
    function.geometry.offLAT = 0.2
    function.geometry.domeRadius = 1.5

    assert suc

    testValues = [[0, 0, 'E'],
                  [0, 6, 'E'],
                  [0, 12, 'E'],
                  [0, 18, 'E'],
                  [45, 0, 'E'],
                  [45, 6, 'E'],
                  [45, 12, 'E'],
                  [45, 18, 'E'],
                  [0, 0, 'W'],
                  [0, 6, 'W'],
                  [0, 12, 'W'],
                  [0, 18, 'W'],
                  [45, 0, 'W'],
                  [45, 6, 'W'],
                  [45, 12, 'W'],
                  [45, 18, 'W']]

    results = [
        [81.42689500055411, 26.565051177077958, 0.2000000000000001, -0.09999999999999992,
         1.4832396974191326],
        [3.8225537292743446, 277.6794427904114, 0.2000000000000001, 1.4832396974191326, 0.1],
        [-81.4268950005541, 333.434948822922, 0.2000000000000001, 0.10000000000000009,
         -1.4832396974191326],
        [-3.822553729274351, 82.32055720958864, 0.2000000000000001, -1.4832396974191326,
         -0.10000000000000019],
        [37.223444738231244, 4.8025610547841895, 1.1902302044074613, -0.09999999999999996,
         0.9073874919328418],
        [3.8225537292743446, 322.6794427904114, 1.1902302044074613, 0.9073874919328418, 0.1],
        [-37.223444738231244, 355.19743894521577, 1.1902302044074613, 0.10000000000000005,
         -0.9073874919328418],
        [-3.8225537292743486, 37.320557209588635, 1.1902302044074613, -0.9073874919328418,
         -0.10000000000000012],
        [81.42689500055411, 206.5650511770781, -0.19999999999999993, 0.10000000000000027,
         1.4832396974191326],
        [-3.822553729274351, 262.3205572095886, -0.19999999999999993, 1.4832396974191326,
         -0.10000000000000019],
        [-81.42689500055411, 153.43494882292197, -0.19999999999999993, -0.10000000000000009,
         -1.4832396974191326],
        [3.8225537292743446, 97.67944279041136, -0.19999999999999993, -1.4832396974191326,
         0.1],
        [52.51256311391629, 353.71101162190206, 0.907387491932842, 0.10000000000000021,
         1.1902302044074609],
        [-3.8225537292743508, 307.3205572095886, 0.907387491932842, 1.1902302044074609,
         -0.10000000000000014],
        [-52.51256311391629, 6.288988378097951, 0.907387491932842, -0.10000000000000007,
         -1.1902302044074609],
        [3.822553729274345, 52.67944279041136, 0.907387491932842, -1.1902302044074609, 0.1],
    ]

    for t, r in zip(testValues, results):
        val = function.geometry.calcTransformationMatrices(dec=Angle(degrees=t[0]),
                                                           ha=Angle(hours=t[1]),
                                                           lat=Angle(degrees=50),
                                                           pierside=t[2])
        alt, az, inter, _, _ = val

        assert pytest.approx(alt.degrees, 0.001) == r[0]
        assert pytest.approx(az.degrees, 0.001) == r[1]
        assert pytest.approx(inter[0], 0.001) == r[2]
        assert pytest.approx(inter[1], 0.001) == r[3]
        assert pytest.approx(inter[2], 0.001) == r[4]


def test_geometry_4(function):
    suc = function.geometry.initializeGeometry('10micron GM4000HPS')
    function.geometry.offNorth = 0.1
    function.geometry.offEast = 0.2
    function.geometry.offVert = 0.3
    function.geometry.offGEM = 0.1
    function.geometry.offLAT = 0.2
    function.geometry.domeRadius = 1.5

    assert suc

    testValues = [[0, 0, 'E'],
                  [0, 6, 'E'],
                  [0, 12, 'E'],
                  [0, 18, 'E'],
                  [45, 0, 'E'],
                  [45, 6, 'E'],
                  [45, 12, 'E'],
                  [45, 18, 'E'],
                  [0, 0, 'W'],
                  [0, 6, 'W'],
                  [0, 12, 'W'],
                  [0, 18, 'W'],
                  [45, 0, 'W'],
                  [45, 6, 'W'],
                  [45, 12, 'W'],
                  [45, 18, 'W']]

    results = [
        [81.42689500055411, 26.565051177077958, 0.2000000000000001, -0.09999999999999992,
         1.4832396974191326],
        [3.8225537292743446, 277.6794427904114, 0.2000000000000001, 1.4832396974191326, 0.1],
        [-81.4268950005541, 333.434948822922, 0.2000000000000001, 0.10000000000000009,
         -1.4832396974191326],
        [-3.822553729274351, 82.32055720958864, 0.2000000000000001, -1.4832396974191326,
         -0.10000000000000019],
        [37.223444738231244, 4.8025610547841895, 1.1902302044074613, -0.09999999999999996,
         0.9073874919328418],
        [3.8225537292743446, 322.6794427904114, 1.1902302044074613, 0.9073874919328418, 0.1],
        [-37.223444738231244, 355.19743894521577, 1.1902302044074613, 0.10000000000000005,
         -0.9073874919328418],
        [-3.8225537292743486, 37.320557209588635, 1.1902302044074613, -0.9073874919328418,
         -0.10000000000000012],
        [81.42689500055411, 206.5650511770781, -0.19999999999999993, 0.10000000000000027,
         1.4832396974191326],
        [-3.822553729274351, 262.3205572095886, -0.19999999999999993, 1.4832396974191326,
         -0.10000000000000019],
        [-81.42689500055411, 153.43494882292197, -0.19999999999999993, -0.10000000000000009,
         -1.4832396974191326],
        [3.8225537292743446, 97.67944279041136, -0.19999999999999993, -1.4832396974191326,
         0.1],
        [52.51256311391629, 353.71101162190206, 0.907387491932842, 0.10000000000000021,
         1.1902302044074609],
        [-3.8225537292743508, 307.3205572095886, 0.907387491932842, 1.1902302044074609,
         -0.10000000000000014],
        [-52.51256311391629, 6.288988378097951, 0.907387491932842, -0.10000000000000007,
         -1.1902302044074609],
        [3.822553729274345, 52.67944279041136, 0.907387491932842, -1.1902302044074609, 0.1],
    ]

    for t, r in zip(testValues, results):
        val = function.geometry.calcTransformationMatrices(dec=Angle(degrees=t[0]),
                                                           ha=Angle(hours=t[1]),
                                                           lat=Angle(degrees=50),
                                                           pierside=t[2])
        alt, az, inter, _, _ = val
        assert pytest.approx(alt.degrees, 0.001) == r[0]
        assert pytest.approx(az.degrees, 0.001) == r[1]
        assert pytest.approx(inter[0], 0.001) == r[2]
        assert pytest.approx(inter[1], 0.001) == r[3]
        assert pytest.approx(inter[2], 0.001) == r[4]


def test_geometry_5(function):
    suc = function.geometry.initializeGeometry('10micron GM1000HPS')
    assert suc
    function.geometry.offNorth = 0.1
    function.geometry.offEast = 0.2
    function.geometry.offVert = 0.3
    function.geometry.offGEM = 0.1
    function.geometry.offLAT = 0.2
    function.geometry.domeRadius = 1.5

    val = function.geometry.calcTransformationMatrices(ha=None,
                                                       dec=None,
                                                       lat=None,
                                                       pierside='E')
    alt, az, inter, PB, PD = val
    assert alt is None
    assert az is None
    assert inter is None
    assert PB is None
    assert PD is None


def test_geometry_6(function):
    suc = function.geometry.initializeGeometry('10micron GM1000HPS')
    assert suc
    function.geometry.offNorth = 0.1
    function.geometry.offEast = 0.2
    function.geometry.offVert = 0.3
    function.geometry.offGEM = 0.1
    function.geometry.offLAT = 0.2
    function.geometry.domeRadius = 1.5

    val = function.geometry.calcTransformationMatrices(ha=Angle(hours=1),
                                                       dec=None,
                                                       lat=None,
                                                       pierside='E')
    alt, az, inter, PB, PD = val
    assert alt is None
    assert az is None
    assert inter is None
    assert PB is None
    assert PD is None


def test_geometry_7(function):
    suc = function.geometry.initializeGeometry('10micron GM1000HPS')
    assert suc
    function.geometry.offNorth = 0.1
    function.geometry.offEast = 0.2
    function.geometry.offVert = 0.3
    function.geometry.offGEM = 0.1
    function.geometry.offLAT = 0.2
    function.geometry.domeRadius = 1.5

    val = function.geometry.calcTransformationMatrices(ha=Angle(hours=1),
                                                       dec=Angle(degrees=1),
                                                       lat=None,
                                                       pierside='E')
    alt, az, inter, PB, PD = val
    assert alt is None
    assert az is None
    assert inter is None
    assert PB is None
    assert PD is None


def test_geometry_8(function):
    suc = function.geometry.initializeGeometry('10micron GM1000HPS')
    assert suc
    function.geometry.offNorth = 0
    function.geometry.offEast = 0
    function.geometry.offVert = 0
    function.geometry.offGEM = 0
    function.geometry.offLAT = 0.5
    function.geometry.domeRadius = 0.25

    val = function.geometry.calcTransformationMatrices(ha=Angle(hours=1),
                                                       dec=Angle(degrees=1),
                                                       lat=Angle(degrees=49),
                                                       pierside='E')
    alt, az, inter, PB, PD = val
    assert alt is None
    assert az is None
    assert inter is None
    assert PB is None
    assert PD is None


def test_geometry_9(function):
    suc = function.geometry.initializeGeometry('10micron GM1000HPS')
    assert suc
    function.geometry.offNorth = 0.1
    function.geometry.offEast = 0.2
    function.geometry.offVert = 0.3
    function.geometry.offGEM = 0.1
    function.geometry.offLAT = 0.2
    function.geometry.domeRadius = 1.5

    val = function.geometry.calcTransformationMatrices(dec=Angle(degrees=10),
                                                       ha=Angle(hours=5),
                                                       lat=Angle(degrees=-50),
                                                       pierside='E')
    alt, az, inter, _, _ = val
