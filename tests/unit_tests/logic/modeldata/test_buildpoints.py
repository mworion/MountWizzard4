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
#
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
from skyfield.api import wgs84
from mountcontrol.mount import Mount
import numpy as np

# local import
from logic.modeldata.buildpoints import DataPoint
from logic.modeldata.buildpoints import HaDecToAltAz
from base import transform


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    class Test():
        mount = Mount(host='localhost', MAC='00:00:00:00:00:00', verbose=False,
                      pathToData='tests/workDir/data')
        mount.obsSite.location = wgs84.latlon(latitude_degrees=20,
                                              longitude_degrees=10,
                                              elevation_m=500)
        mwGlob = {'configDir': 'tests/workDir/config'}

    global app

    config = 'tests/workDir/config'
    testdir = os.listdir(config)
    for item in testdir:
        if item.endswith('.bpts'):
            os.remove(os.path.join(config, item))
        if item.endswith('.hpts'):
            os.remove(os.path.join(config, item))

    app = DataPoint(app=Test())
    yield


def test_topoToAltAz1():
    ha = 12
    dec = 0
    alt, az = HaDecToAltAz(ha, dec, 0)

    assert alt is not None
    assert az is not None


def test_topoToAltAz2():
    ha = -12
    dec = 0
    alt, az = HaDecToAltAz(ha, dec, 0)

    assert alt is not None
    assert az is not None


def test_genHaDecParams1():
    selection = 'min'
    length = len(app.DEC_N[selection])
    for i, (a, b, c, d) in enumerate(app.genHaDecParams(selection, 50)):
        if i > length - 1:
            j = 2 * length - i - 1
        else:
            j = i
        assert a == app.DEC_N[selection][j]
        assert b == app.STEP_N[selection][j]
        assert c == app.START[selection][i]
        assert d == app.STOP[selection][i]


def test_genHaDecParams2():
    selection = 'norm'
    length = len(app.DEC_N[selection])
    for i, (a, b, c, d) in enumerate(app.genHaDecParams(selection, 50)):
        if i > length - 1:
            j = 2 * length - i - 1
        else:
            j = i
        assert a == app.DEC_N[selection][j]
        assert b == app.STEP_N[selection][j]
        assert c == app.START[selection][i]
        assert d == app.STOP[selection][i]


def test_genHaDecParams3():
    selection = 'med'
    length = len(app.DEC_N[selection])
    for i, (a, b, c, d) in enumerate(app.genHaDecParams(selection, 50)):
        if i > length - 1:
            j = 2 * length - i - 1
        else:
            j = i
        assert a == app.DEC_N[selection][j]
        assert b == app.STEP_N[selection][j]
        assert c == app.START[selection][i]
        assert d == app.STOP[selection][i]


def test_genHaDecParams4():
    selection = 'max'
    length = len(app.DEC_N[selection])
    for i, (a, b, c, d) in enumerate(app.genHaDecParams(selection, 50)):
        if i > length - 1:
            j = 2 * length - i - 1
        else:
            j = i
        assert a == app.DEC_N[selection][j]
        assert b == app.STEP_N[selection][j]
        assert c == app.START[selection][i]
        assert d == app.STOP[selection][i]


def test_genHaDecParams5():
    selection = 'test'
    val = True
    for i, (_, _, _, _) in enumerate(app.genHaDecParams(selection, 50)):
        val = False
    assert val


def test_genHaDecParams6():
    selection = 'max'
    length = len(app.DEC_S[selection])
    for i, (a, b, c, d) in enumerate(app.genHaDecParams(selection, -50)):
        if i > length - 1:
            j = 2 * length - i - 1
        else:
            j = i
        assert a == app.DEC_S[selection][j]
        assert b == app.STEP_S[selection][j]
        assert c == app.START[selection][i]
        assert d == app.STOP[selection][i]


def test_horizonP1():
    app.genGreaterCircle('max')
    app.horizonP = app.buildP
    assert len(app.horizonP) == 110
    app.genGreaterCircle('med')
    app.horizonP = app.buildP
    assert len(app.horizonP) == 82
    app.genGreaterCircle('norm')
    app.horizonP = app.buildP
    assert len(app.horizonP) == 76
    app.genGreaterCircle('min')
    app.horizonP = app.buildP
    assert len(app.horizonP) == 51


def test_horizonP2():
    app.horizonP = '456'
    assert len(app.horizonP) == 0


def test_horizonP3():
    app.horizonP = [(1, 1), (1, 1), 'test']
    assert len(app.horizonP) == 0


def test_buildP1():
    app.buildP = ()
    app.genGreaterCircle('max')
    assert len(app.buildP) == 110
    app.genGreaterCircle('med')
    assert len(app.buildP) == 82
    app.genGreaterCircle('norm')
    assert len(app.buildP) == 76
    app.genGreaterCircle('min')
    assert len(app.buildP) == 51


def test_buildP2():
    app.buildP = ()
    app.buildP = '456'
    assert len(app.buildP) == 0


def test_buildP3():
    app.buildP = ()
    app.buildP = [(1, 1), (1, 1), 'test']
    assert len(app.buildP) == 0


def test_genGreaterCircle1():
    app.lat = 48
    selection = 'min'
    app.genGreaterCircle(selection)
    i = 0
    for i, (alt, az, status) in enumerate(app.buildP):
        assert alt <= 90
        assert az <= 360
        assert alt >= 0
        assert az >= 0
        assert status
    assert i == 50


def test_genGreaterCircle2():
    app.lat = 48
    selection = 'norm'
    app.genGreaterCircle(selection)
    i = 0
    for i, (alt, az, status) in enumerate(app.buildP):
        assert alt <= 90
        assert az <= 360
        assert alt >= 0
        assert az >= 0
        assert status
    assert i == 75


def test_genGreaterCircle3():
    app.lat = 48
    selection = 'med'
    app.genGreaterCircle(selection)
    i = 0
    for i, (alt, az, status) in enumerate(app.buildP):
        assert alt <= 90
        assert az <= 360
        assert alt >= 0
        assert az >= 0
        assert status
    assert i == 81


def test_genGreaterCircle4():
    app.lat = 48
    selection = 'max'
    app.genGreaterCircle(selection)
    i = 0
    for i, (alt, az, status) in enumerate(app.buildP):
        assert alt <= 90
        assert az <= 360
        assert alt >= 0
        assert az >= 0
        assert status
    assert i == 109


def test_genGreaterCircle5():
    app.lat = 48
    app.app.mount.obsSite.location = None
    selection = 'max'
    suc = app.genGreaterCircle(selection)
    assert not suc


def test_checkFormat_1():
    a = [[1, 1], [1, 1]]
    suc = app.checkFormat(a)
    assert not suc


def test_checkFormat_2():
    a = [[1, 1], [1]]
    suc = app.checkFormat(a)
    assert not suc


def test_checkFormat_3():
    a = [[1, 1], (1, 1)]
    suc = app.checkFormat(a)
    assert not suc


def test_checkFormat_4():
    a = 'test'
    suc = app.checkFormat(a)
    assert not suc


def test_checkFormat_5():
    a = [(1, 1), (1, 1)]
    suc = app.checkFormat(a)
    assert suc


def test_checkFormat_6():
    a = [(1, 1), (1, 1, 1)]
    suc = app.checkFormat(a)
    assert not suc


def test_clearBuildP():
    app.buildP = ()
    app.genGreaterCircle('max')
    assert len(app.buildP) == 110
    app.clearBuildP()
    assert len(app.buildP) == 0


def test_setStatusBuildP_1():
    app.buildP = ()
    app.addBuildP((10, 10, True))
    app.addBuildP((10, 10, True))
    app.addBuildP((10, 10, True))
    suc = app.setStatusBuildP(-1, True)
    assert not suc


def test_setStatusBuildP_2():
    app.buildP = ()
    app.addBuildP((10, 10, True))
    app.addBuildP((10, 10, True))
    app.addBuildP((10, 10, True))
    suc = app.setStatusBuildP(3, True)
    assert not suc


def test_setStatusBuildP_3():
    app.buildP = ()
    app.addBuildP((10, 10, True))
    app.addBuildP((10, 10, True))
    app.addBuildP((10, 10, True))
    suc = app.setStatusBuildP(1, True)
    assert suc
    assert app.buildP[1][2]


def test_setStatusBuildP_4():
    app.buildP = ()
    app.addBuildP((10, 10, True))
    app.addBuildP((10, 10, True))
    app.addBuildP((10, 10, True))
    suc = app.setStatusBuildP(1, False)
    assert suc
    assert not app.buildP[1][2]


def test_addBuildP1():
    app.buildP = ()
    suc = app.addBuildP((10, 10, True))
    assert suc
    assert 1 == len(app.buildP)
    suc = app.addBuildP((10, 10, True))
    assert suc
    assert 2 == len(app.buildP)
    suc = app.addBuildP((10, 10, True))
    assert suc
    assert 3 == len(app.buildP)


def test_addBuildP2():
    app.buildP = ()
    suc = app.addBuildP(10)
    assert not suc
    assert 0 == len(app.buildP)


def test_addBuildP3():
    app.buildP = ()
    suc = app.addBuildP((10, 10, 10, True))
    assert not suc
    assert 0 == len(app.buildP)


def test_addBuildP4():
    app.buildP = [(10, 10, True), (10, 10, True)]
    suc = app.addBuildP((10, 10, True), position=1)
    assert suc
    assert len(app.buildP) == 3


def test_addBuildP5():
    app.buildP = [(10, 10, True), (10, 10, True)]
    suc = app.addBuildP((10, 10, True), position=20)
    assert suc
    assert len(app.buildP) == 3


def test_addBuildP6():
    app.buildP = [(10, 10, True), (10, 10, True)]
    suc = app.addBuildP((10, 10, True), position=-5)
    assert suc
    assert len(app.buildP) == 3


def test_addBuildP7():
    app.buildP = [(10, 10, True), (10, 10, True)]
    suc = app.addBuildP(position=-5)
    assert not suc


def test_addBuildP8():
    app.buildP = [(10, 10, True), (10, 10, True)]
    app.app.mount.setting.horizonLimitHigh = 80
    app.app.mount.setting.horizonLimitLow = 5
    suc = app.addBuildP((10, 10, True), position='a')
    assert not suc


def test_addBuildP9():
    app.buildP = [(10, 10, True), (10, 10, True)]
    app.app.mount.setting.horizonLimitHigh = 80
    app.app.mount.setting.horizonLimitLow = 5
    suc = app.addBuildP((90, 10, True), position=20)
    assert not suc


def test_addBuildP10():
    app.buildP = [(10, 10, True), (10, 10, True)]
    app.app.mount.setting.horizonLimitHigh = 80
    app.app.mount.setting.horizonLimitLow = 5
    suc = app.addBuildP((0, 10, True), position=20)
    assert not suc


def test_delBuildP1():
    app.buildP = []
    app.genGreaterCircle('max')
    assert len(app.buildP) == 110
    suc = app.delBuildP(5)
    assert suc
    assert len(app.buildP) == 109
    suc = app.delBuildP(0)
    assert suc
    assert len(app.buildP) == 108
    suc = app.delBuildP(99)
    assert suc
    assert len(app.buildP) == 107


def test_delBuildP2():
    app.buildP = []
    app.genGreaterCircle('max')
    assert len(app.buildP) == 110
    suc = app.delBuildP(-5)
    assert not suc
    assert len(app.buildP) == 110


def test_delBuildP3():
    app.buildP = []
    app.genGreaterCircle('max')
    assert len(app.buildP) == 110
    suc = app.delBuildP(170)
    assert not suc
    assert len(app.buildP) == 110


def test_delBuildP4():
    app.buildP = []
    app.genGreaterCircle('max')
    assert len(app.buildP) == 110
    suc = app.delBuildP('1')
    assert not suc
    assert len(app.buildP) == 110


def test_clearHorizonP():
    app.genGreaterCircle('max')
    app.horizonP = app.buildP
    assert len(app.horizonP) == 110
    app.clearHorizonP()
    assert len(app.horizonP) == 0


def test_isCloseHorizonLine_1():
    point = (45, 45)
    margin = 5
    azI = range(0, 361, 1)
    altI = np.interp(azI, [0, 90, 180, 360], [42, 42, 42, 42])
    horizonI = np.asarray([[x, y] for x, y in zip(azI, altI)])
    suc = app.isCloseHorizonLine(point, margin, horizonI)
    assert suc


def test_isCloseHorizonLine_2():
    point = (45, 45)
    margin = 1
    azI = range(0, 361, 1)
    altI = np.interp(azI, [0, 90, 180, 360], [42, 42, 42, 42])
    horizonI = np.asarray([[x, y] for x, y in zip(azI, altI)])
    suc = app.isCloseHorizonLine(point, margin, horizonI)
    assert not suc


def test_isAboveHorizon_1():
    app.clearHorizonP()
    suc = app.isAboveHorizon((10, 50))
    assert suc
    suc = app.isAboveHorizon((10, 370))
    assert suc
    suc = app.isAboveHorizon((10, -50))
    assert suc
    suc = app.isAboveHorizon((-10, 50))
    assert not suc


def test_isAboveHorizon_2():
    app.horizonP = [(1, 2), (2, 3)]
    suc = app.isAboveHorizon((10, 50))
    assert suc


def test_isCloseMeridian_1():
    suc = app.isCloseMeridian((90, 45))
    assert not suc


def test_isCloseMeridian_2():
    app.app.mount.setting.meridianLimitSlew = 5
    app.app.mount.setting.meridianLimitTrack = 5
    suc = app.isCloseMeridian((90, 45))
    assert not suc


def test_isCloseMeridian_3():
    app.app.mount.setting.meridianLimitSlew = 5
    app.app.mount.setting.meridianLimitTrack = 5
    suc = app.isCloseMeridian((45, 180))
    assert suc


def test_deleteBelowHorizon1():
    app.clearHorizonP()
    app.buildP = [(10, 10, True), (-5, 40, True), (40, 60, True)]
    app.deleteBelowHorizon()
    assert len(app.buildP) == 2


def test_deleteBelowHorizon2():
    app.clearHorizonP()
    app.buildP = [(10, 10, True), (5, 40, True), (-40, 60, True)]
    app.deleteBelowHorizon()
    assert len(app.buildP) == 2


def test_deleteBelowHorizon3():
    app.clearHorizonP()
    app.buildP = [(-10, 10, True), (5, 40, True), (40, 60, True)]
    app.deleteBelowHorizon()
    assert len(app.buildP) == 2


def test_deleteBelowHorizon4():
    app.clearHorizonP()
    app.buildP = [(-10, 10, True), (-5, 40, True), (-40, 60, True)]
    app.deleteBelowHorizon()
    assert len(app.buildP) == 0


def test_deleteCloseMeridian_1():
    suc = app.deleteCloseMeridian()
    assert suc


def test_deleteCloseHorizonLine_1():
    suc = app.deleteCloseHorizonLine(0)
    assert not suc


def test_deleteCloseHorizonLine_2():
    app.horizonP = [(0, 10), (180, 40), (360, 60)]
    suc = app.deleteCloseHorizonLine(0)
    assert suc


def test_addHorizonP1():
    app.horizonP = []
    suc = app.addHorizonP((10, 10))
    assert suc
    assert len(app._horizonP) == 1

    suc = app.addHorizonP((10, 10))
    assert suc
    assert len(app._horizonP) == 2

    suc = app.addHorizonP((10, 10))
    assert suc
    assert len(app._horizonP) == 3


def test_addHorizonP2():
    app.horizonP = []
    suc = app.addHorizonP(10)
    assert not suc
    assert len(app.horizonP) == 0


def test_addHorizonP3():
    app.horizonP = []
    suc = app.addHorizonP((10, 10, 10))
    assert not suc
    assert len(app.horizonP) == 0


def test_addHorizonP4():
    app.horizonP = [(10, 10), (10, 10)]
    suc = app.addHorizonP((10, 10), position=1)
    assert suc
    assert len(app.horizonP) == 3


def test_addHorizonP5():
    app.horizonP = [(10, 10), (10, 10)]
    suc = app.addHorizonP((10, 10), position=20)
    assert suc
    assert len(app.horizonP) == 3


def test_addHorizonP6():
    app.horizonP = [(10, 10), (10, 10)]
    suc = app.addHorizonP((10, 10), position=-5)
    assert suc
    assert len(app.horizonP) == 3


def test_addHorizonP7():
    app.horizonP = [(10, 10), (10, 10)]
    suc = app.addHorizonP(position=-5)
    assert not suc


def test_addHorizonP8():
    app.horizonP = [(10, 10), (10, 10)]
    suc = app.addHorizonP((10, 10), position='a')
    assert not suc


def test_delHorizonP1():
    app.genGreaterCircle('max')
    app.horizonP = app.buildP
    assert len(app.horizonP) == 110
    suc = app.delHorizonP(5)
    assert suc
    assert len(app.horizonP) == 109
    suc = app.delHorizonP(1)
    assert suc
    assert len(app.horizonP) == 108
    suc = app.delHorizonP(10)
    assert suc
    assert len(app.horizonP) == 107


def test_delHorizonP2():
    app.genGreaterCircle('max')
    app.horizonP = app.buildP
    assert len(app.horizonP) == 110

    suc = app.delHorizonP(-5)
    assert not suc
    assert len(app.horizonP) == len(app.buildP)


def test_delHorizonP3():
    app.genGreaterCircle('max')
    app.horizonP = app.buildP
    assert len(app.horizonP) == len(app.buildP)

    suc = app.delHorizonP(170)
    assert not suc
    assert len(app.horizonP) == len(app.buildP)


def test_delHorizonP4():
    app.genGreaterCircle('max')
    app.horizonP = app.buildP
    assert len(app.horizonP) == len(app.buildP)

    suc = app.delHorizonP('1')
    assert not suc
    assert len(app.horizonP) == len(app.buildP)


def test_delHorizonP5():
    app.horizonP = [(1, 1), (3, 3), (10, 10)]
    suc = app.delHorizonP(position=0)
    assert suc

    suc = app.delHorizonP(154)
    assert not suc


def test_loadJSON_1():
    val = app.loadJSON('', '')
    assert val is None


def test_loadJSON_2():
    with open('tests/workDir/config/test.bpts', 'w') as outfile:
        outfile.writelines('[test, ]],[]}')

    val = app.loadJSON('test', '.bpts')
    assert val is None


def test_loadJSON_3():
    with open('tests/workDir/config/test.bpts', 'wb') as outfile:
        outfile.write(binascii.unhexlify('9f'))

    val = app.loadJSON('test', '.bpts')
    assert val is None


def test_loadJSON_4():
    values = [(1, 1), (2, 2)]
    with open('tests/workDir/config/test.bpts', 'w') as outfile:
        json.dump(values,
                  outfile,
                  indent=4)

    val = app.loadJSON('test', '.bpts')
    assert val == [(1, 1), (2, 2)]


def test_loadCSV_1():
    val = app.loadCSV('', '.csv')
    assert val is None


def test_loadCSV_2():
    with open('tests/workDir/config/test.csv', 'w') as outfile:
        outfile.writelines('[test, ]],[]}\n')

    val = app.loadCSV('test', '.csv')
    assert val is None


def test_loadCSV_3():
    with open('tests/workDir/config/test.csv', 'w') as outfile:
        outfile.writelines('1, 1\n')
        outfile.writelines('2, 2\n')

    val = app.loadCSV('test', '.csv')
    assert val == [(1, 1), (2, 2)]


def test_loadCSV_4():
    with open('tests/workDir/config/test.csv', 'w') as outfile:
        outfile.writelines('1; 1\n')
        outfile.writelines('2; 2\n')

    val = app.loadCSV('test', '.csv')
    assert val == [(1, 1), (2, 2)]


def test_loadBuildP_1():
    # wrong fileName given
    suc = app.loadBuildP()
    assert not suc


def test_loadBuildP_2():
    # path with not existent file given
    suc = app.loadBuildP('test_file_not_there', '')
    assert not suc


def test_loadBuildP_3():
    # load file with path
    app.buildPFile = ''
    fileName = 'tests/workDir/config/test.bpts'
    values = [(1, 1), (2, 2)]
    with open(fileName, 'w') as outfile:
        json.dump(values,
                  outfile,
                  indent=4)
    suc = app.loadBuildP('test', '.bpts')
    assert suc
    assert app.buildP == [(1, 1, True), (2, 2, True)]


def test_loadBuildP_4():
    # load file without path
    fileName = 'tests/workDir/config/test.bpts'
    app.buildPFile = 'test'
    values = [(1, 1), (2, 2)]
    with open(fileName, 'w') as outfile:
        json.dump(values,
                  outfile,
                  indent=4)
    with mock.patch.object(app,
                           'checkFormat',
                           return_value=False):
        suc = app.loadBuildP('test', '.bpts')
        assert not suc


def test_loadBuildP_5():
    # load file with path
    app.buildPFile = ''
    fileName = 'tests/workDir/config/test.csv'
    with open(fileName, 'w') as outfile:
        outfile.write('1, 1\n')
        outfile.write('2, 2\n')
    suc = app.loadBuildP('test', '.csv')
    assert suc
    assert app.buildP == [(1, 1, True), (2, 2, True)]


def test_saveBuildP_11():
    app.genGreaterCircle('min')
    suc = app.saveBuildP()
    assert not suc


def test_saveBuildP_12():
    fileName = 'tests/workDir/config/save_test.bpts'
    app.genGreaterCircle('min')
    suc = app.saveBuildP('save_test')
    assert suc
    assert os.path.isfile(fileName)


def test_loadHorizonP_1():
    # no fileName given
    suc = app.loadHorizonP()
    assert not suc


def test_loadHorizonP_2():
    # wrong fileName given
    suc = app.loadHorizonP('format_not_ok')
    assert not suc


def test_loadHorizonP_3():
    # path with not existent file given
    fileName = 'tests/workDir/config/test_load_horizon.hpts'
    suc = app.loadHorizonP(fileName, '.hpts')
    assert not suc


def test_loadHorizonP_4():
    # load file with path
    fileName = 'tests/workDir/config/test_horizon_2.hpts'
    values = [(1, 1), (2, 2)]
    with open(fileName, 'w') as outfile:
        json.dump(values,
                  outfile,
                  indent=4)
    suc = app.loadHorizonP('test_horizon_2', '.hpts')
    assert suc
    assert app.horizonP == values


def test_loadHorizonP_5():
    # load with wrong content
    app.horizonPFile = ''
    fileName = 'tests/workDir/config/test_horizon_2.hpts'
    with open(fileName, 'wb') as outfile:
        outfile.write(binascii.unhexlify('9f'))
    suc = app.loadHorizonP('test_horizon_2', '.hpts')
    assert not suc
    assert app.horizonP == []


def test_loadHorizonP_6():
    # load with wrong content 2
    app.horizonPFile = ''
    fileName = 'tests/workDir/config/test_horizon_2.hpts'
    with open(fileName, 'w') as outfile:
        outfile.writelines('[test, ]],[]}')
    suc = app.loadHorizonP('test_horizon_2', '.hpts')
    assert not suc
    assert app.horizonP == []


def test_loadHorizonP_7():
    # load file with path
    fileName = 'tests/workDir/config/test_horizon_2.csv'
    values = [(1.0, 1.0), (2.0, 2.0)]
    with open(fileName, 'w') as outfile:
        outfile.write('1,1\n2,2\n')

    suc = app.loadHorizonP('test_horizon_2', '.csv')
    assert suc
    assert app.horizonP == values


def test_saveHorizonP_10():
    app._horizonP = [(0, 1), (0, 2)]
    suc = app.saveHorizonP(fileName='test_save_horizon')
    assert suc


def test_saveHorizonP_11():
    app._horizonP = [(0, 1), (0, 2)]
    suc = app.saveHorizonP()
    assert not suc


def test_saveHorizonP_12():
    app._horizonP = [(0, 1), (0, 2)]
    suc = app.saveHorizonP(fileName='test_horizon_1')
    assert suc
    fileName = 'tests/workDir/config/' + 'test_horizon_1' + '.hpts'
    with open(fileName, 'r') as infile:
        value = json.load(infile)
        assert value[0] == [0, 1]
        assert value[-1] == [0, 2]


def test_genGrid1():
    suc = app.genGrid(minAlt=10,
                      maxAlt=80,
                      numbRows=4,
                      numbCols=4)
    assert suc


def test_genGrid2():
    suc = app.genGrid(minAlt=0,
                      maxAlt=80,
                      numbRows=4,
                      numbCols=4)
    assert not suc


def test_genGrid3():
    suc = app.genGrid(minAlt=10,
                      maxAlt=90,
                      numbRows=4,
                      numbCols=4)
    assert not suc


def test_genGrid4():
    suc = app.genGrid(minAlt=50,
                      maxAlt=40,
                      numbRows=4,
                      numbCols=3)
    assert not suc


def test_genGrid5():
    suc = app.genGrid(minAlt=10,
                      maxAlt=40,
                      numbRows=4,
                      numbCols=4)
    assert suc


def test_genGrid6():
    suc = app.genGrid(minAlt=10,
                      maxAlt=90,
                      numbRows=4,
                      numbCols=3)
    assert not suc


def test_genGrid7():
    suc = app.genGrid(minAlt=10,
                      maxAlt=80,
                      numbRows=4,
                      numbCols=3)
    assert not suc


def test_genGridData1():
    app.genGrid(minAlt=10,
                maxAlt=40,
                numbRows=4,
                numbCols=4)
    assert 16 == len(app.buildP)


def test_genGridData2():
    app.genGrid(minAlt=5,
                maxAlt=85,
                numbRows=4,
                numbCols=4)
    assert 16 == len(app.buildP)


def test_genGridData3():
    app.genGrid(minAlt=5,
                maxAlt=85,
                numbRows=8,
                numbCols=8)
    assert 64 == len(app.buildP)


def test_genGridData4():
    app.genGrid(minAlt=10,
                maxAlt=40,
                numbRows=6,
                numbCols=6)
    assert 36 == len(app.buildP)


def test_genGridData5():
    app.genGrid(minAlt=10,
                maxAlt=40,
                numbRows=6,
                numbCols=12)
    assert 72 == len(app.buildP)


def test_genGridData6():
    app.genGrid(minAlt=10,
                maxAlt=40,
                numbRows=1,
                numbCols=12)
    assert 0 == len(app.buildP)


def test_genGridData7():
    app.genGrid(minAlt=10,
                maxAlt=40,
                numbRows=5,
                numbCols=1)
    assert 0 == len(app.buildP)


def test_genGridData8():
    app.genGrid(minAlt=10,
                maxAlt=40,
                numbRows=10,
                numbCols=12)
    assert 0 == len(app.buildP)


def test_genGridData9():
    app.genGrid(minAlt=10,
                maxAlt=40,
                numbRows=6,
                numbCols=20)
    assert 0 == len(app.buildP)


def test_genAlign1():
    suc = app.genAlign(altBase=30,
                       azBase=30,
                       numberBase=5,
                       )
    assert suc
    assert 5 == len(app.buildP)


def test_genAlign2():
    suc = app.genAlign(altBase=0,
                       azBase=30,
                       numberBase=5,
                       )
    assert not suc
    assert 0 == len(app.buildP)


def test_genAlign3():
    suc = app.genAlign(altBase=30,
                       azBase=-10,
                       numberBase=5,
                       )
    assert not suc
    assert 0 == len(app.buildP)


def test_genAlign4():
    suc = app.genAlign(altBase=30,
                       azBase=30,
                       numberBase=2,
                       )
    assert not suc
    assert 0 == len(app.buildP)


def test_genAlign5():
    suc = app.genAlign(altBase=30,
                       azBase=30,
                       numberBase=30,
                       )
    assert not suc
    assert 0 == len(app.buildP)


def test_sort_1():
    values = [(10, 10, True), (20, 20, True), (30, 90, True), (40, 190, True), (50, 290, True)]
    result = [(30, 90, True), (20, 20, True), (10, 10, True), (50, 290, True), (40, 190, True)]
    app._buildP = values
    suc = app.sort(eastwest=True)
    assert suc
    assert app.buildP == result


def test_sort_2():
    values = [(10, 10, True), (20, 20, True), (30, 90, True), (40, 190, True), (50, 290, True)]
    result = [(30, 90, True), (20, 20, True), (10, 10, True), (50, 290, True), (40, 190, True)]
    app._buildP = values
    suc = app.sort(highlow=True)
    assert suc
    assert app.buildP == result


def test_sort_3():
    values = [(30, 90, True), (50, 290, True), (20, 20, True), (10, 10, True), (40, 190, True)]
    result = [(30, 90, True), (20, 20, True), (10, 10, True), (50, 290, True), (40, 190, True)]
    app._buildP = values
    suc = app.sort(eastwest=True)
    assert suc
    assert app.buildP == result


def test_sort_4():
    values = [(30, 90, True), (50, 290, True), (20, 20, True), (10, 10, True), (40, 190, True)]
    result = [(30, 90, True), (20, 20, True), (10, 10, True), (50, 290, True), (40, 190, True)]
    app._buildP = values
    suc = app.sort(highlow=True)
    assert suc
    assert app.buildP == result


def test_sort_5():
    values = [(30, 90, True), (50, 290, True), (20, 20, True), (10, 10, True), (40, 190, True)]
    result = [(50, 290, True), (40, 190, True), (30, 90, True), (20, 20, True), (10, 10, True)]
    app._buildP = values
    suc = app.sort(highlow=True, pierside='E')
    assert suc
    assert app.buildP == result


def test_sort_6():
    values = [(30, 90, True), (50, 290, True), (20, 20, True), (10, 10, True), (40, 190, True)]
    result = [(30, 90, True), (20, 20, True), (10, 10, True), (50, 290, True), (40, 190, True)]
    app._buildP = values
    suc = app.sort(highlow=True, pierside='W')
    assert suc
    assert app.buildP == result


def test_generateCelestialEquator_1():
    value = app.generateCelestialEquator()
    assert len(value) == 3480


def test_generateCelestialEquator_2():
    app.app.mount.obsSite.location = None
    value = app.generateCelestialEquator()
    assert value == []


def test_generateDSOPath_1():
    ra = skyfield.api.Angle(hours=0)
    dec = skyfield.api.Angle(degrees=0)
    suc = app.generateDSOPath(ra=ra,
                              dec=dec,
                              numberPoints=0,
                              duration=1,
                              timeShift=0,
                              )
    assert not suc


def test_generateDSOPath_2():
    ra = skyfield.api.Angle(hours=0)
    dec = skyfield.api.Angle(degrees=0)
    suc = app.generateDSOPath(ra=ra,
                              dec=dec,
                              numberPoints=1,
                              duration=0,
                              timeShift=0,
                              )
    assert not suc


def test_generateDSOPath_3():
    ra = skyfield.api.Angle(hours=0)
    dec = skyfield.api.Angle(degrees=0)
    suc = app.generateDSOPath(ra=ra,
                              dec=dec,
                              numberPoints=1,
                              duration=1,
                              timeShift=0,
                              )
    assert not suc


def test_generateDSOPath_4():
    ra = skyfield.api.Angle(hours=0)
    dec = skyfield.api.Angle(degrees=0)
    with mock.patch.object(transform,
                           'J2000ToAltAz',
                           return_value=(Angle(degrees=10), Angle(degrees=10))):
        suc = app.generateDSOPath(ra=ra,
                                  dec=dec,
                                  numberPoints=1,
                                  duration=1,
                                  timeShift=0,
                                  timeJD=app.app.mount.obsSite.timeJD,
                                  location=app.app.mount.obsSite.location,
                                  )
        assert suc


def test_generateGoldenSpiral_1():
    suc = app.generateGoldenSpiral(0)
    assert not suc


def test_generateGoldenSpiral_2():
    suc = app.generateGoldenSpiral(200)
    assert suc
