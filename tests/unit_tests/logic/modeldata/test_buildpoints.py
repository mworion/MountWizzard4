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
import pytest
import os
import json
import binascii
import unittest.mock as mock

# external packages
import skyfield.api
from skyfield.api import Angle
import numpy as np

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from logic.modeldata.buildpoints import DataPoint
from logic.modeldata.buildpoints import HaDecToAltAz
from base import transform


@pytest.fixture(autouse=True, scope='function')
def function():
    config = 'tests/workDir/config'
    testdir = os.listdir(config)
    for item in testdir:
        if item.endswith('.bpts'):
            os.remove(os.path.join(config, item))
        if item.endswith('.hpts'):
            os.remove(os.path.join(config, item))

    func = DataPoint(app=App())
    yield func


def test_topoToAltAz1(function):
    ha = 12
    dec = 0
    alt, az = HaDecToAltAz(ha, dec, 0)

    assert alt is not None
    assert az is not None


def test_topoToAltAz2(function):
    ha = -12
    dec = 0
    alt, az = HaDecToAltAz(ha, dec, 0)

    assert alt is not None
    assert az is not None


def test_genHaDecParams1(function):
    selection = 'min'
    length = len(function.DEC_N[selection])
    for i, (a, b, c, d) in enumerate(function.genHaDecParams(selection, 50)):
        if i > length - 1:
            j = 2 * length - i - 1
        else:
            j = i
        assert a == function.DEC_N[selection][j]
        assert b == function.STEP_N[selection][j]
        assert c == function.START[selection][i]
        assert d == function.STOP[selection][i]


def test_genHaDecParams2(function):
    selection = 'norm'
    length = len(function.DEC_N[selection])
    for i, (a, b, c, d) in enumerate(function.genHaDecParams(selection, 50)):
        if i > length - 1:
            j = 2 * length - i - 1
        else:
            j = i
        assert a == function.DEC_N[selection][j]
        assert b == function.STEP_N[selection][j]
        assert c == function.START[selection][i]
        assert d == function.STOP[selection][i]


def test_genHaDecParams3(function):
    selection = 'med'
    length = len(function.DEC_N[selection])
    for i, (a, b, c, d) in enumerate(function.genHaDecParams(selection, 50)):
        if i > length - 1:
            j = 2 * length - i - 1
        else:
            j = i
        assert a == function.DEC_N[selection][j]
        assert b == function.STEP_N[selection][j]
        assert c == function.START[selection][i]
        assert d == function.STOP[selection][i]


def test_genHaDecParams4(function):
    selection = 'max'
    length = len(function.DEC_N[selection])
    for i, (a, b, c, d) in enumerate(function.genHaDecParams(selection, 50)):
        if i > length - 1:
            j = 2 * length - i - 1
        else:
            j = i
        assert a == function.DEC_N[selection][j]
        assert b == function.STEP_N[selection][j]
        assert c == function.START[selection][i]
        assert d == function.STOP[selection][i]


def test_genHaDecParams5(function):
    selection = 'test'
    val = True
    for i, (_, _, _, _) in enumerate(function.genHaDecParams(selection, 50)):
        val = False
    assert val


def test_genHaDecParams6(function):
    selection = 'max'
    length = len(function.DEC_S[selection])
    for i, (a, b, c, d) in enumerate(function.genHaDecParams(selection, -50)):
        if i > length - 1:
            j = 2 * length - i - 1
        else:
            j = i
        assert a == function.DEC_S[selection][j]
        assert b == function.STEP_S[selection][j]
        assert c == function.START[selection][i]
        assert d == function.STOP[selection][i]


def test_horizonP1(function):
    function.genGreaterCircle('max')
    function.horizonP = function.buildP
    assert len(function.horizonP) == 110
    function.genGreaterCircle('med')
    function.horizonP = function.buildP
    assert len(function.horizonP) == 92
    function.genGreaterCircle('norm')
    function.horizonP = function.buildP
    assert len(function.horizonP) == 76
    function.genGreaterCircle('min')
    function.horizonP = function.buildP
    assert len(function.horizonP) == 51


def test_horizonP2(function):
    function.horizonP = '456'
    assert len(function.horizonP) == 0


def test_horizonP3(function):
    function.horizonP = [(1, 1), (1, 1), 'test']
    assert len(function.horizonP) == 0


def test_buildP1(function):
    function.buildP = ()
    function.genGreaterCircle('max')
    assert len(function.buildP) == 110
    function.genGreaterCircle('med')
    assert len(function.buildP) == 92
    function.genGreaterCircle('norm')
    assert len(function.buildP) == 76
    function.genGreaterCircle('min')
    assert len(function.buildP) == 51


def test_buildP2(function):
    function.buildP = ()
    function.buildP = '456'
    assert len(function.buildP) == 0


def test_buildP3(function):
    function.buildP = ()
    function.buildP = [(1, 1), (1, 1), 'test']
    assert len(function.buildP) == 0


def test_genGreaterCircle1(function):
    function.lat = 48
    selection = 'min'
    function.genGreaterCircle(selection)
    i = 0
    for i, (alt, az, status) in enumerate(function.buildP):
        assert alt <= 90
        assert az <= 360
        assert alt >= 0
        assert az >= 0
        assert status
    assert i == 50


def test_genGreaterCircle2(function):
    function.lat = 48
    selection = 'norm'
    function.genGreaterCircle(selection)
    i = 0
    for i, (alt, az, status) in enumerate(function.buildP):
        assert alt <= 90
        assert az <= 360
        assert alt >= 0
        assert az >= 0
        assert status
    assert i == 75


def test_genGreaterCircle3(function):
    function.lat = 48
    selection = 'med'
    function.genGreaterCircle(selection)
    i = 0
    for i, (alt, az, status) in enumerate(function.buildP):
        assert alt <= 90
        assert az <= 360
        assert alt >= 0
        assert az >= 0
        assert status
    assert i == 91


def test_genGreaterCircle4(function):
    function.lat = 48
    selection = 'max'
    function.genGreaterCircle(selection)
    i = 0
    for i, (alt, az, status) in enumerate(function.buildP):
        assert alt <= 90
        assert az <= 360
        assert alt >= 0
        assert az >= 0
        assert status
    assert i == 109


def test_genGreaterCircle5(function):
    function.lat = 48
    temp = function.app.mount.obsSite.location
    function.app.mount.obsSite.location = None
    selection = 'max'
    suc = function.genGreaterCircle(selection)
    assert not suc
    function.app.mount.obsSite.location = temp


def test_checkFormat_1(function):
    a = [[1, 1], [1, 1]]
    suc = function.checkFormat(a)
    assert not suc


def test_checkFormat_2(function):
    a = [[1, 1], [1]]
    suc = function.checkFormat(a)
    assert not suc


def test_checkFormat_3(function):
    a = [[1, 1], (1, 1)]
    suc = function.checkFormat(a)
    assert not suc


def test_checkFormat_4(function):
    a = 'test'
    suc = function.checkFormat(a)
    assert not suc


def test_checkFormat_5(function):
    a = [(1, 1), (1, 1)]
    suc = function.checkFormat(a)
    assert suc


def test_checkFormat_6(function):
    a = [(1, 1), (1, 1, 1)]
    suc = function.checkFormat(a)
    assert not suc


def test_clearBuildP(function):
    function.buildP = ()
    function.genGreaterCircle('max')
    assert len(function.buildP) == 110
    function.clearBuildP()
    assert len(function.buildP) == 0


def test_setStatusBuildP_1(function):
    function.buildP = ()
    function.addBuildP((10, 10, True))
    function.addBuildP((10, 10, True))
    function.addBuildP((10, 10, True))
    suc = function.setStatusBuildP(-1, True)
    assert not suc


def test_setStatusBuildP_2(function):
    function.buildP = ()
    function.addBuildP((10, 10, True))
    function.addBuildP((10, 10, True))
    function.addBuildP((10, 10, True))
    suc = function.setStatusBuildP(3, True)
    assert not suc


def test_setStatusBuildP_3(function):
    function.buildP = ()
    function.addBuildP((10, 10, True))
    function.addBuildP((10, 10, True))
    function.addBuildP((10, 10, True))
    suc = function.setStatusBuildP(1, True)
    assert suc
    assert function.buildP[1][2]


def test_setStatusBuildP_4(function):
    function.buildP = ()
    function.addBuildP((10, 10, True))
    function.addBuildP((10, 10, True))
    function.addBuildP((10, 10, True))
    suc = function.setStatusBuildP(1, False)
    assert suc
    assert not function.buildP[1][2]


def test_addBuildP1(function):
    function.buildP = ()
    suc = function.addBuildP((10, 10, True))
    assert suc
    assert 1 == len(function.buildP)
    suc = function.addBuildP((10, 10, True))
    assert suc
    assert 2 == len(function.buildP)
    suc = function.addBuildP((10, 10, True))
    assert suc
    assert 3 == len(function.buildP)


def test_addBuildP2(function):
    function.buildP = ()
    suc = function.addBuildP(10)
    assert not suc
    assert 0 == len(function.buildP)
    function.app.mount.setting.horizonLimitLow = 0
    function.app.mount.setting.horizonLimitHigh = 90


def test_addBuildP3(function):
    function.buildP = ()
    suc = function.addBuildP((10, 10, 10, True))
    assert not suc
    assert 0 == len(function.buildP)


def test_addBuildP4(function):
    function.buildP = [(10, 10, True), (10, 10, True)]
    suc = function.addBuildP((10, 10, True), position=1)
    assert suc
    assert len(function.buildP) == 3


def test_addBuildP5(function):
    function.buildP = [(10, 10, True), (10, 10, True)]
    suc = function.addBuildP((10, 10, True), position=20)
    assert suc
    assert len(function.buildP) == 3


def test_addBuildP6(function):
    function.buildP = [(10, 10, True), (10, 10, True)]
    suc = function.addBuildP((10, 10, True), position=-5)
    assert suc
    assert len(function.buildP) == 3


def test_addBuildP7(function):
    function.buildP = [(10, 10, True), (10, 10, True)]
    suc = function.addBuildP(position=-5)
    assert not suc


def test_addBuildP8(function):
    function.buildP = [(10, 10, True), (10, 10, True)]
    function.app.mount.setting.horizonLimitHigh = 80
    function.app.mount.setting.horizonLimitLow = 5
    suc = function.addBuildP((10, 10, True), position='a')
    assert not suc


def test_addBuildP9(function):
    function.buildP = [(10, 10, True), (10, 10, True)]
    function.app.mount.setting.horizonLimitHigh = 80
    function.app.mount.setting.horizonLimitLow = 5
    suc = function.addBuildP((90, 10, True), position=20)
    assert not suc


def test_addBuildP10(function):
    function.buildP = [(10, 10, True), (10, 10, True)]
    function.app.mount.setting.horizonLimitHigh = 80
    function.app.mount.setting.horizonLimitLow = 5
    suc = function.addBuildP((0, 10, True), position=20)
    assert not suc


def test_addBuildP11(function):
    function.app.mount.setting.horizonLimitLow = None
    function.app.mount.setting.horizonLimitHigh = None
    function.buildP = [(10, 10, True), (10, 10, True)]
    suc = function.addBuildP((10, 10, True), position=-5)
    assert suc
    assert len(function.buildP) == 3
    function.app.mount.setting.horizonLimitLow = 5
    function.app.mount.setting.horizonLimitHigh = 80


def test_delBuildP1(function):
    function.buildP = []
    function.genGreaterCircle('max')
    assert len(function.buildP) == 108
    suc = function.delBuildP(5)
    assert suc
    assert len(function.buildP) == 107
    suc = function.delBuildP(0)
    assert suc
    assert len(function.buildP) == 106
    suc = function.delBuildP(99)
    assert suc
    assert len(function.buildP) == 105


def test_delBuildP2(function):
    function.buildP = []
    function.genGreaterCircle('max')
    assert len(function.buildP) == 108
    suc = function.delBuildP(-5)
    assert not suc
    assert len(function.buildP) == 108


def test_delBuildP3(function):
    function.buildP = []
    function.genGreaterCircle('max')
    assert len(function.buildP) == 108
    suc = function.delBuildP(170)
    assert not suc
    assert len(function.buildP) == 108


def test_delBuildP4(function):
    function.buildP = []
    function.genGreaterCircle('max')
    assert len(function.buildP) == 108
    suc = function.delBuildP('1')
    assert not suc
    assert len(function.buildP) == 108


def test_clearHorizonP(function):
    function.genGreaterCircle('max')
    function.horizonP = function.buildP
    assert len(function.horizonP) == 108
    function.clearHorizonP()
    assert len(function.horizonP) == 0


def test_isCloseHorizonLine_1(function):
    point = (45, 45)
    margin = 5
    azI = range(0, 361, 1)
    altI = np.interp(azI, [0, 90, 180, 360], [42, 42, 42, 42])
    horizonI = np.asarray([[x, y] for x, y in zip(azI, altI)])
    suc = function.isCloseHorizonLine(point, margin, horizonI)
    assert suc


def test_isCloseHorizonLine_2(function):
    point = (45, 45)
    margin = 1
    azI = range(0, 361, 1)
    altI = np.interp(azI, [0, 90, 180, 360], [42, 42, 42, 42])
    horizonI = np.asarray([[x, y] for x, y in zip(azI, altI)])
    suc = function.isCloseHorizonLine(point, margin, horizonI)
    assert not suc


def test_isAboveHorizon_1(function):
    function.clearHorizonP()
    suc = function.isAboveHorizon((10, 50))
    assert suc
    suc = function.isAboveHorizon((10, 370))
    assert suc
    suc = function.isAboveHorizon((10, -50))
    assert suc
    suc = function.isAboveHorizon((-10, 50))
    assert not suc


def test_isAboveHorizon_2(function):
    function.horizonP = [(1, 2), (2, 3)]
    suc = function.isAboveHorizon((10, 50))
    assert suc


def test_isCloseMeridian_1(function):
    function.app.mount.setting.meridianLimitSlew = None
    suc = function.isCloseMeridian((90, 45))
    assert not suc
    function.app.mount.setting.meridianLimitSlew = 3


def test_isCloseMeridian_2(function):
    function.app.mount.setting.meridianLimitSlew = 5
    function.app.mount.setting.meridianLimitTrack = 5
    suc = function.isCloseMeridian((90, 45))
    assert not suc


def test_isCloseMeridian_3(function):
    function.app.mount.setting.meridianLimitSlew = 5
    function.app.mount.setting.meridianLimitTrack = 5
    suc = function.isCloseMeridian((45, 180))
    assert suc


def test_deleteBelowHorizon1(function):
    function.clearHorizonP()
    function.buildP = [(10, 10, True), (-5, 40, True), (40, 60, True)]
    function.deleteBelowHorizon()
    assert len(function.buildP) == 2


def test_deleteBelowHorizon2(function):
    function.clearHorizonP()
    function.buildP = [(10, 10, True), (5, 40, True), (-40, 60, True)]
    function.deleteBelowHorizon()
    assert len(function.buildP) == 2


def test_deleteBelowHorizon3(function):
    function.clearHorizonP()
    function.buildP = [(-10, 10, True), (5, 40, True), (40, 60, True)]
    function.deleteBelowHorizon()
    assert len(function.buildP) == 2


def test_deleteBelowHorizon4(function):
    function.clearHorizonP()
    function.buildP = [(-10, 10, True), (-5, 40, True), (-40, 60, True)]
    function.deleteBelowHorizon()
    assert len(function.buildP) == 0


def test_deleteCloseMeridian_1(function):
    suc = function.deleteCloseMeridian()
    assert suc


def test_deleteCloseHorizonLine_1(function):
    suc = function.deleteCloseHorizonLine(0)
    assert not suc


def test_deleteCloseHorizonLine_2(function):
    function.horizonP = [(0, 10), (180, 40), (360, 60)]
    suc = function.deleteCloseHorizonLine(0)
    assert suc


def test_addHorizonP1(function):
    function.horizonP = []
    suc = function.addHorizonP((10, 10))
    assert suc
    assert len(function._horizonP) == 1

    suc = function.addHorizonP((10, 10))
    assert suc
    assert len(function._horizonP) == 2

    suc = function.addHorizonP((10, 10))
    assert suc
    assert len(function._horizonP) == 3


def test_addHorizonP2(function):
    function.horizonP = []
    suc = function.addHorizonP(10)
    assert not suc
    assert len(function.horizonP) == 0


def test_addHorizonP3(function):
    function.horizonP = []
    suc = function.addHorizonP((10, 10, 10))
    assert not suc
    assert len(function.horizonP) == 0


def test_addHorizonP4(function):
    function.horizonP = [(10, 10), (10, 10)]
    suc = function.addHorizonP((10, 10), position=1)
    assert suc
    assert len(function.horizonP) == 3


def test_addHorizonP5(function):
    function.horizonP = [(10, 10), (10, 10)]
    suc = function.addHorizonP((10, 10), position=20)
    assert suc
    assert len(function.horizonP) == 3


def test_addHorizonP6(function):
    function.horizonP = [(10, 10), (10, 10)]
    suc = function.addHorizonP((10, 10), position=-5)
    assert suc
    assert len(function.horizonP) == 3


def test_addHorizonP7(function):
    function.horizonP = [(10, 10), (10, 10)]
    suc = function.addHorizonP(position=-5)
    assert not suc


def test_addHorizonP8(function):
    function.horizonP = [(10, 10), (10, 10)]
    suc = function.addHorizonP((10, 10), position='a')
    assert not suc


def test_delHorizonP1(function):
    function.genGreaterCircle('max')
    function.horizonP = function.buildP
    assert len(function.horizonP) == 108
    suc = function.delHorizonP(5)
    assert suc
    assert len(function.horizonP) == 107
    suc = function.delHorizonP(1)
    assert suc
    assert len(function.horizonP) == 106
    suc = function.delHorizonP(10)
    assert suc
    assert len(function.horizonP) == 105


def test_delHorizonP2(function):
    function.genGreaterCircle('max')
    function.horizonP = function.buildP
    assert len(function.horizonP) == 108

    suc = function.delHorizonP(-5)
    assert not suc
    assert len(function.horizonP) == len(function.buildP)


def test_delHorizonP3(function):
    function.genGreaterCircle('max')
    function.horizonP = function.buildP
    assert len(function.horizonP) == len(function.buildP)

    suc = function.delHorizonP(170)
    assert not suc
    assert len(function.horizonP) == len(function.buildP)


def test_delHorizonP4(function):
    function.genGreaterCircle('max')
    function.horizonP = function.buildP
    assert len(function.horizonP) == len(function.buildP)

    suc = function.delHorizonP('1')
    assert not suc
    assert len(function.horizonP) == len(function.buildP)


def test_delHorizonP5(function):
    function.horizonP = [(1, 1), (3, 3), (10, 10)]
    suc = function.delHorizonP(position=0)
    assert suc

    suc = function.delHorizonP(154)
    assert not suc


def test_loadModel_1(function):
    val = function.loadModel('')
    assert val is None


def test_loadModel_2(function):
    with open('tests/workDir/config/test.model', 'w') as outfile:
        outfile.writelines('[test, ]],[]}')

    val = function.loadModel('tests/workDir/config/test.model')
    assert val is None


def test_loadModel_3(function):
    with open('tests/workDir/config/test.model', 'wb') as outfile:
        outfile.write(binascii.unhexlify('9f'))

    val = function.loadModel('tests/workDir/config/test.model')
    assert val is None


def test_loadModel_4(function):
    values = [{'azimuth': 1, 'altitude': 1}, {'azimuth': 2, 'altitude': 2}]
    with open('tests/workDir/config/test.model', 'w') as outfile:
        json.dump(values,
                  outfile,
                  indent=4)

    val = function.loadModel('tests/workDir/config/test.model')
    assert val == [(1, 1), (2, 2)]


def test_loadJSON_1(function):
    val = function.loadJSON('')
    assert val is None


def test_loadJSON_2(function):
    with open('tests/workDir/config/test.bpts', 'w') as outfile:
        outfile.writelines('[test, ]],[]}')

    val = function.loadJSON('tests/workDir/config/test.bpts')
    assert val is None


def test_loadJSON_3(function):
    with open('tests/workDir/config/test.bpts', 'wb') as outfile:
        outfile.write(binascii.unhexlify('9f'))

    val = function.loadJSON('tests/workDir/config/test.bpts')
    assert val is None


def test_loadJSON_4(function):
    values = [(1, 1), (2, 2)]
    with open('tests/workDir/config/test.bpts', 'w') as outfile:
        json.dump(values,
                  outfile,
                  indent=4)

    val = function.loadJSON('tests/workDir/config/test.bpts')
    assert val == [(1, 1), (2, 2)]


def test_loadCSV_1(function):
    val = function.loadCSV('')
    assert val is None


def test_loadCSV_2(function):
    with open('tests/workDir/config/test.csv', 'w') as outfile:
        outfile.writelines('[test, ]],[]}\n')

    val = function.loadCSV('tests/workDir/config/test.csv')
    assert val is None


def test_loadCSV_3(function):
    with open('tests/workDir/config/test.csv', 'w') as outfile:
        outfile.writelines('1, 1\n')
        outfile.writelines('2, 2\n')

    val = function.loadCSV('tests/workDir/config/test.csv')
    assert val == [(1, 1), (2, 2)]


def test_loadCSV_4(function):
    with open('tests/workDir/config/test.csv', 'w') as outfile:
        outfile.writelines('1; 1\n')
        outfile.writelines('2; 2\n')

    val = function.loadCSV('tests/workDir/config/test.csv')
    assert val == [(1, 1), (2, 2)]


def test_loadBuildP_1(function):
    # wrong fileName given
    suc = function.loadBuildP()
    assert not suc


def test_loadBuildP_2(function):
    # path with not existent file given
    suc = function.loadBuildP('test_file_not_there')
    assert not suc


def test_loadBuildP_3(function):
    # load file with path
    function.buildPFile = ''
    fileName = 'tests/workDir/config/test.bpts'
    values = [(1, 1), (2, 2)]
    with open(fileName, 'w') as outfile:
        json.dump(values,
                  outfile,
                  indent=4)
    suc = function.loadBuildP('tests/workDir/config/test.bpts')
    assert suc
    assert function.buildP == [(1, 1, True), (2, 2, True)]


def test_loadBuildP_4(function):
    # load file without path
    fileName = 'tests/workDir/config/test.bpts'
    function.buildPFile = 'test'
    values = [(1, 1), (2, 2)]
    with open(fileName, 'w') as outfile:
        json.dump(values,
                  outfile,
                  indent=4)
    with mock.patch.object(function,
                           'checkFormat',
                           return_value=False):
        suc = function.loadBuildP('tests/workDir/config/test.bpts')
        assert not suc


def test_loadBuildP_5(function):
    # load file with path
    function.buildPFile = ''
    fileName = 'tests/workDir/config/test.csv'
    with open(fileName, 'w') as outfile:
        outfile.write('1, 1\n')
        outfile.write('2, 2\n')
    suc = function.loadBuildP('tests/workDir/config/test.csv', ext='.csv', keep=True)
    assert suc


def test_loadBuildP_6(function):
    # load file with path
    function.buildPFile = ''
    values = [{'azimuth': 1, 'altitude': 1}, {'azimuth': 2, 'altitude': 2}]
    with open('tests/workDir/config/test.model', 'w') as outfile:
        json.dump(values,
                  outfile,
                  indent=4)
    suc = function.loadBuildP('tests/workDir/config/test.model', ext='.model', keep=True)
    assert suc


def test_saveBuildP_11(function):
    function.genGreaterCircle('min')
    suc = function.saveBuildP()
    assert not suc


def test_saveBuildP_12(function):
    fileName = 'tests/workDir/config/save_test.bpts'
    function.genGreaterCircle('min')
    suc = function.saveBuildP('save_test')
    assert suc
    assert os.path.isfile(fileName)


def test_loadHorizonP_1(function):
    # no fileName given
    suc = function.loadHorizonP()
    assert not suc


def test_loadHorizonP_2(function):
    # wrong fileName given
    suc = function.loadHorizonP('format_not_ok')
    assert not suc


def test_loadHorizonP_3(function):
    # path with not existent file given
    fileName = 'tests/workDir/config/test_load_horizon.hpts'
    suc = function.loadHorizonP(fileName, '.hpts')
    assert not suc


def test_loadHorizonP_4(function):
    # load file with path
    fileName = 'tests/workDir/config/test_horizon_2.hpts'
    values = [(1, 1), (2, 2)]
    with open(fileName, 'w') as outfile:
        json.dump(values,
                  outfile,
                  indent=4)
    suc = function.loadHorizonP('test_horizon_2', '.hpts')
    assert suc
    assert function.horizonP == values


def test_loadHorizonP_5(function):
    # load with wrong content
    function.horizonPFile = ''
    fileName = 'tests/workDir/config/test_horizon_2.hpts'
    with open(fileName, 'wb') as outfile:
        outfile.write(binascii.unhexlify('9f'))
    suc = function.loadHorizonP('test_horizon_2', '.hpts')
    assert not suc
    assert function.horizonP == []


def test_loadHorizonP_6(function):
    # load with wrong content 2
    function.horizonPFile = ''
    fileName = 'tests/workDir/config/test_horizon_2.hpts'
    with open(fileName, 'w') as outfile:
        outfile.writelines('[test, ]],[]}')
    suc = function.loadHorizonP('test_horizon_2', '.hpts')
    assert not suc
    assert function.horizonP == []


def test_loadHorizonP_7(function):
    # load file with path
    fileName = 'tests/workDir/config/test_horizon_2.csv'
    values = [(1.0, 1.0), (2.0, 2.0)]
    with open(fileName, 'w') as outfile:
        outfile.write('1,1\n2,2\n')

    suc = function.loadHorizonP('test_horizon_2', '.csv')
    assert suc
    assert function.horizonP == values


def test_saveHorizonP_10(function):
    function._horizonP = [(0, 1), (0, 2)]
    suc = function.saveHorizonP(fileName='test_save_horizon')
    assert suc


def test_saveHorizonP_11(function):
    function._horizonP = [(0, 1), (0, 2)]
    suc = function.saveHorizonP()
    assert not suc


def test_saveHorizonP_12(function):
    function._horizonP = [(0, 1), (0, 2)]
    suc = function.saveHorizonP(fileName='test_horizon_1')
    assert suc
    fileName = 'tests/workDir/config/' + 'test_horizon_1' + '.hpts'
    with open(fileName, 'r') as infile:
        value = json.load(infile)
        assert value[0] == [0, 1]
        assert value[-1] == [0, 2]


def test_genGrid1(function):
    suc = function.genGrid(minAlt=10,
                           maxAlt=80,
                           numbRows=4,
                           numbCols=4)
    assert suc


def test_genGrid2(function):
    suc = function.genGrid(minAlt=0,
                           maxAlt=80,
                           numbRows=4,
                           numbCols=4)
    assert not suc


def test_genGrid3(function):
    suc = function.genGrid(minAlt=10,
                           maxAlt=90,
                           numbRows=4,
                           numbCols=4)
    assert not suc


def test_genGrid4(function):
    suc = function.genGrid(minAlt=50,
                           maxAlt=40,
                           numbRows=4,
                           numbCols=3)
    assert not suc


def test_genGrid5(function):
    suc = function.genGrid(minAlt=10,
                           maxAlt=40,
                           numbRows=4,
                           numbCols=4)
    assert suc


def test_genGrid6(function):
    suc = function.genGrid(minAlt=10,
                           maxAlt=90,
                           numbRows=4,
                           numbCols=3)
    assert not suc


def test_genGrid7(function):
    suc = function.genGrid(minAlt=10,
                           maxAlt=80,
                           numbRows=4,
                           numbCols=3)
    assert not suc


def test_genGridData1(function):
    function.genGrid(minAlt=10,
                     maxAlt=40,
                     numbRows=4,
                     numbCols=4)
    assert 16 == len(function.buildP)


def test_genGridData2(function):
    function.genGrid(minAlt=5,
                     maxAlt=85,
                     numbRows=4,
                     numbCols=4)
    assert 12 == len(function.buildP)


def test_genGridData3(function):
    function.genGrid(minAlt=5,
                     maxAlt=85,
                     numbRows=8,
                     numbCols=8)
    assert 56 == len(function.buildP)


def test_genGridData4(function):
    function.genGrid(minAlt=10,
                     maxAlt=40,
                     numbRows=6,
                     numbCols=6)
    assert 36 == len(function.buildP)


def test_genGridData5(function):
    function.genGrid(minAlt=10,
                     maxAlt=40,
                     numbRows=6,
                     numbCols=12)
    assert 72 == len(function.buildP)


def test_genGridData6(function):
    function.genGrid(minAlt=10,
                     maxAlt=40,
                     numbRows=1,
                     numbCols=12)
    assert 0 == len(function.buildP)


def test_genGridData7(function):
    function.genGrid(minAlt=10,
                     maxAlt=40,
                     numbRows=5,
                     numbCols=1)
    assert 0 == len(function.buildP)


def test_genGridData8(function):
    function.genGrid(minAlt=10,
                     maxAlt=40,
                     numbRows=10,
                     numbCols=12)
    assert 0 == len(function.buildP)


def test_genGridData9(function):
    function.genGrid(minAlt=10,
                     maxAlt=40,
                     numbRows=6,
                     numbCols=20)
    assert 0 == len(function.buildP)


def test_genAlign1(function):
    suc = function.genAlign(altBase=30,
                            azBase=30,
                            numberBase=5,
                            )
    assert suc
    assert 5 == len(function.buildP)


def test_genAlign2(function):
    suc = function.genAlign(altBase=0,
                            azBase=30,
                            numberBase=5,
                            )
    assert not suc
    assert 0 == len(function.buildP)


def test_genAlign3(function):
    suc = function.genAlign(altBase=30,
                            azBase=-10,
                            numberBase=5,
                            )
    assert not suc
    assert 0 == len(function.buildP)


def test_genAlign4(function):
    suc = function.genAlign(altBase=30,
                            azBase=30,
                            numberBase=2,
                            )
    assert not suc
    assert 0 == len(function.buildP)


def test_genAlign5(function):
    suc = function.genAlign(altBase=30,
                            azBase=30,
                            numberBase=30,
                            )
    assert not suc
    assert 0 == len(function.buildP)


def test_sort_1(function):
    values = [(10, 10, True), (20, 20, True), (30, 90, True), (40, 190, True), (50, 290, True)]
    result = [(30, 90, True), (20, 20, True), (10, 10, True), (50, 290, True), (40, 190, True)]
    suc = function.sort(values, eastwest=True)
    assert suc
    assert function.buildP == result


def test_sort_2(function):
    values = [(10, 10, True), (20, 20, True), (30, 90, True), (40, 190, True), (50, 290, True)]
    result = [(30, 90, True), (20, 20, True), (10, 10, True), (50, 290, True), (40, 190, True)]
    suc = function.sort(values, highlow=True)
    assert suc
    assert function.buildP == result


def test_sort_3(function):
    values = [(30, 90, True), (50, 290, True), (20, 20, True), (10, 10, True), (40, 190, True)]
    result = [(30, 90, True), (20, 20, True), (10, 10, True), (50, 290, True), (40, 190, True)]
    suc = function.sort(values, eastwest=True)
    assert suc
    assert function.buildP == result


def test_sort_4(function):
    values = [(30, 90, True), (50, 290, True), (20, 20, True), (10, 10, True), (40, 190, True)]
    result = [(30, 90, True), (20, 20, True), (10, 10, True), (50, 290, True), (40, 190, True)]
    suc = function.sort(values, highlow=True)
    assert suc
    assert function.buildP == result


def test_sort_5(function):
    values = [(30, 90, True), (50, 290, True), (20, 20, True), (10, 10, True), (40, 190, True)]
    result = [(50, 290, True), (40, 190, True), (30, 90, True), (20, 20, True), (10, 10, True)]
    suc = function.sort(values, highlow=True, pierside='E')
    assert suc
    assert function.buildP == result


def test_sort_6(function):
    values = [(30, 90, True), (50, 290, True), (20, 20, True), (10, 10, True), (40, 190, True)]
    result = [(30, 90, True), (20, 20, True), (10, 10, True), (50, 290, True), (40, 190, True)]
    suc = function.sort(values, highlow=True, pierside='W')
    assert suc
    assert function.buildP == result


def test_sort_7(function):
    values = [(30, 90, True, 3), (20, 20, True, 2), (50, 290, True, 1)]
    result = [(30, 90, True, 3), (20, 20, True, 2), (50, 290, True, 1)]
    suc = function.sort(values, sortDomeAz=True)
    assert suc
    assert function.buildP == result


def test_generateCelestialEquator_1(function):
    value = function.generateCelestialEquator()
    assert len(value) == 1728


def test_generateCelestialEquator_2(function):
    temp = function.app.mount.obsSite.location
    function.app.mount.obsSite.location = None
    value = function.generateCelestialEquator()
    assert value == []
    function.app.mount.obsSite.location = temp


def test_generateDSOPath_1(function):
    ra = skyfield.api.Angle(hours=0)
    dec = skyfield.api.Angle(degrees=0)
    suc = function.generateDSOPath(ha=ra,
                                   dec=dec,
                                   numberPoints=0)
    assert not suc


def test_generateDSOPath_2(function):
    temp = function.app.mount.obsSite.location
    function.app.mount.obsSite.location = None
    ra = skyfield.api.Angle(hours=0)
    dec = skyfield.api.Angle(degrees=0)
    suc = function.generateDSOPath(ha=ra,
                                   dec=dec,
                                   numberPoints=1)
    assert not suc
    function.app.mount.obsSite.location = temp


def test_generateDSOPath_3(function):
    ra = skyfield.api.Angle(hours=0)
    dec = skyfield.api.Angle(degrees=0)
    loc = function.app.mount.obsSite.location
    timeJD = function.app.mount.obsSite.ts.tt_jd(2459580.5)
    with mock.patch.object(function,
                           'clearBuildP'):
        suc = function.generateDSOPath(ha=ra,
                                       dec=dec,
                                       timeJD=timeJD,
                                       location=loc,
                                       numberPoints=1,
                                       keep=False)
        assert suc


def test_generateDSOPath_4(function):
    ra = skyfield.api.Angle(hours=0)
    dec = skyfield.api.Angle(degrees=0)
    with mock.patch.object(skyfield.almanac,
                           'find_discrete',
                           return_value=([], [])):
        suc = function.generateDSOPath(ha=ra,
                                       dec=dec,
                                       timeJD=function.app.mount.obsSite.timeJD,
                                       location=function.app.mount.obsSite.location,
                                       numberPoints=1,
                                       keep=True)
        assert suc


def test_generateDSOPath_5(function):
    ra = skyfield.api.Angle(hours=0)
    dec = skyfield.api.Angle(degrees=0)
    ts = function.app.mount.obsSite.ts
    ti = ts.tt_jd(2459580.5)
    with mock.patch.object(skyfield.almanac,
                           'find_discrete',
                           return_value=([ti, ti], [1, 0])):
        with mock.patch.object(function,
                               'calcPath',
                               return_value=[(0, 0), (0, 0), (0, 0)]):
            suc = function.generateDSOPath(ha=ra,
                                           dec=dec,
                                           numberPoints=1,
                                           timeJD=function.app.mount.obsSite.timeJD,
                                           location=function.app.mount.obsSite.location,
                                           keep=True)
            assert suc


def test_generateGoldenSpiral_1(function):
    suc = function.generateGoldenSpiral(200)
    assert suc


def test_ditherPoints(function):
    function.buildP = [(10, 10, True)]
    function.ditherPoints()
    assert function.buildP[0][0] != 10
    assert function.buildP[0][1] != 10
