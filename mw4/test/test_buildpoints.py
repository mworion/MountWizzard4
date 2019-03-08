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
import pytest
import os
import json
import binascii
import unittest.mock as mock
# external packages
import PyQt5
import skyfield.api
# local import
from mw4 import mainApp
from mw4.modeldata import buildpoints
from mw4.test.test_setupQt import setupQt

app, spy, mwGlob, test = setupQt()


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    global data
    config = mwGlob['configDir']
    testdir = os.listdir(config)
    for item in testdir:
        if item.endswith('.bpts'):
            os.remove(os.path.join(config, item))
        if item.endswith('.hpts'):
            os.remove(os.path.join(config, item))

    data = buildpoints.DataPoint(mwGlob=mwGlob,
                                 app=app,
                                 )
    yield


def test_topoToAltAz1():
    ha = 12
    dec = 0
    alt, az = buildpoints.HaDecToAltAz(ha, dec, 0)

    assert alt is not None
    assert az is not None


def test_topoToAltAz2():
    ha = -12
    dec = 0
    alt, az = buildpoints.HaDecToAltAz(ha, dec, 0)

    assert alt is not None
    assert az is not None


def test_genHaDecParams1():
    selection = 'min'
    length = len(data.DEC[selection])
    for i, (a, b, c, d) in enumerate(data.genHaDecParams(selection=selection)):
        if i > length - 1:
            j = 2 * length - i - 1
        else:
            j = i
        assert a == data.DEC[selection][j]
        assert b == data.STEP[selection][j]
        assert c == data.START[selection][i]
        assert d == data.STOP[selection][i]


def test_genHaDecParams2():
    selection = 'norm'
    length = len(data.DEC[selection])
    for i, (a, b, c, d) in enumerate(data.genHaDecParams(selection=selection)):
        if i > length - 1:
            j = 2 * length - i - 1
        else:
            j = i
        assert a == data.DEC[selection][j]
        assert b == data.STEP[selection][j]
        assert c == data.START[selection][i]
        assert d == data.STOP[selection][i]


def test_genHaDecParams3():
    selection = 'med'
    length = len(data.DEC[selection])
    for i, (a, b, c, d) in enumerate(data.genHaDecParams(selection=selection)):
        if i > length - 1:
            j = 2 * length - i - 1
        else:
            j = i
        assert a == data.DEC[selection][j]
        assert b == data.STEP[selection][j]
        assert c == data.START[selection][i]
        assert d == data.STOP[selection][i]


def test_genHaDecParams4():
    selection = 'max'
    length = len(data.DEC[selection])
    for i, (a, b, c, d) in enumerate(data.genHaDecParams(selection=selection)):
        if i > length - 1:
            j = 2 * length - i - 1
        else:
            j = i
        assert a == data.DEC[selection][j]
        assert b == data.STEP[selection][j]
        assert c == data.START[selection][i]
        assert d == data.STOP[selection][i]


def test_genHaDecParams5():
    selection = 'test'
    val = True
    for i, (_, _, _, _) in enumerate(data.genHaDecParams(selection=selection)):
        val = False
    assert val


def test_genGreaterCircle1():
    data.lat = 48
    selection = 'min'
    data.genGreaterCircle(selection)
    i = 0
    for i, (alt, az) in enumerate(data.buildP):
        assert alt <= 90
        assert az <= 360
        assert alt >= 0
        assert az >= 0
    assert i == 60


def test_genGreaterCircle2():
    data.lat = 48
    selection = 'norm'
    data.genGreaterCircle(selection)
    i = 0
    for i, (alt, az) in enumerate(data.buildP):
        assert alt <= 90
        assert az <= 360
        assert alt >= 0
        assert az >= 0
    assert i == 91


def test_genGreaterCircle3():
    data.lat = 48
    selection = 'med'
    data.genGreaterCircle(selection)
    i = 0
    for i, (alt, az) in enumerate(data.buildP):
        assert alt <= 90
        assert az <= 360
        assert alt >= 0
        assert az >= 0
    assert i == 112


def test_genGreaterCircle4():
    data.lat = 48
    selection = 'max'
    data.genGreaterCircle(selection)
    i = 0
    for i, (alt, az) in enumerate(data.buildP):
        assert alt <= 90
        assert az <= 360
        assert alt >= 0
        assert az >= 0
    assert i == 156


def test_checkFormat_1():
    a = [[1, 1], [1, 1]]
    suc = data.checkFormat(a)
    assert suc


def test_checkFormat_2():
    a = [[1, 1], [1]]
    suc = data.checkFormat(a)
    assert not suc


def test_checkFormat_3():
    a = [[1, 1], (1, 1)]
    suc = data.checkFormat(a)
    assert not suc


def test_checkFormat_4():
    a = 'test'
    suc = data.checkFormat(a)
    assert not suc


def test_buildP1():
    data.buildP = ()
    data.genGreaterCircle('max')
    assert len(data.buildP) == 157
    data.genGreaterCircle('med')
    assert len(data.buildP) == 113
    data.genGreaterCircle('norm')
    assert len(data.buildP) == 92
    data.genGreaterCircle('min')
    assert len(data.buildP) == 61


def test_buildP2():
    data.buildP = ()
    data.buildP = '456'
    assert len(data.buildP) == 0


def test_buildP3():
    data.buildP = ()
    data.buildP = [(1, 1), (1, 1), 'test']
    assert len(data.buildP) == 0


def test_clearBuildP():
    data.buildP = ()
    data.genGreaterCircle('max')
    assert len(data.buildP) == 157
    data.clearBuildP()
    assert len(data.buildP) == 0


def test_addBuildP1():
    data.buildP = ()
    suc = data.addBuildP((10, 10))
    assert suc
    assert 1 == len(data.buildP)
    suc = data.addBuildP((10, 10))
    assert suc
    assert 2 == len(data.buildP)
    suc = data.addBuildP((10, 10))
    assert suc
    assert 3 == len(data.buildP)


def test_addBuildP2():
    data.buildP = ()
    suc = data.addBuildP(10)
    assert not suc
    assert 0 == len(data.buildP)


def test_addBuildP3():
    data.buildP = ()
    suc = data.addBuildP((10, 10, 10))
    assert not suc
    assert 0 == len(data.buildP)


def test_addBuildP4():
    data.buildP = [(10, 10), (10, 10)]
    suc = data.addBuildP((10, 10), position=1)
    assert suc
    assert len(data.buildP) == 3


def test_addBuildP5():
    data.buildP = [(10, 10), (10, 10)]
    suc = data.addBuildP((10, 10), position=20)
    assert suc
    assert len(data.buildP) == 3


def test_addBuildP6():
    data.buildP = [(10, 10), (10, 10)]
    suc = data.addBuildP((10, 10), position=-5)
    assert suc
    assert len(data.buildP) == 3


def test_addBuildP7():
    data.buildP = [(10, 10), (10, 10)]
    suc = data.addBuildP(position=-5)
    assert not suc


def test_delBuildP1():
    data.buildP = ()
    data.genGreaterCircle('max')
    assert len(data.buildP) == 157
    suc = data.delBuildP(5)
    assert suc
    assert len(data.buildP) == 156
    suc = data.delBuildP(0)
    assert suc
    assert len(data.buildP) == 155
    suc = data.delBuildP(150)
    assert suc
    assert len(data.buildP) == 154


def test_delBuildP2():
    data.buildP = ()
    data.genGreaterCircle('max')
    assert len(data.buildP) == 157
    suc = data.delBuildP(-5)
    assert not suc
    assert len(data.buildP) == 157


def test_delBuildP3():
    data.buildP = ()
    data.genGreaterCircle('max')
    assert len(data.buildP) == 157
    suc = data.delBuildP(170)
    assert not suc
    assert len(data.buildP) == 157


def test_delBuildP4():
    data.buildP = ()
    data.genGreaterCircle('max')
    assert len(data.buildP) == 157
    suc = data.delBuildP('1')
    assert not suc
    assert len(data.buildP) == 157


def test_horizonP1():
    data.clearHorizonP()
    data.genGreaterCircle('max')
    data.horizonP = data.buildP
    assert len(data.horizonP) == 159
    data.genGreaterCircle('med')
    data.horizonP = data.buildP
    assert len(data.horizonP) == 115
    data.genGreaterCircle('norm')
    data.horizonP = data.buildP
    assert len(data.horizonP) == 94
    data.genGreaterCircle('min')
    data.horizonP = data.buildP
    assert len(data.horizonP) == 63


def test_horizonP2():
    data.horizonP = ()
    data.horizonP = '456'
    assert len(data.horizonP) == 2


def test_horizonP3():
    data.horizonP = ()
    data.horizonP = [(1, 1), (1, 1), 'test']
    assert len(data.horizonP) == 2


def test_clearHorizonP():
    data.horizonP = ()
    data.genGreaterCircle('max')
    data.horizonP = data.buildP
    assert len(data.horizonP) == 159
    data.clearHorizonP()
    assert len(data.horizonP) == 2


def test_addHorizonP1():
    data.horizonP = ()
    suc = data.addHorizonP((10, 10))
    assert suc
    assert len(data.horizonP) == 3
    suc = data.addHorizonP((10, 10))
    assert suc
    assert len(data.horizonP) == 4
    suc = data.addHorizonP((10, 10))
    assert suc
    assert len(data.horizonP) == 5


def test_addHorizonP2():
    data.horizonP = ()
    suc = data.addHorizonP(10)
    assert not suc
    assert len(data.horizonP) == 2


def test_addHorizonP3():
    data.horizonP = ()
    suc = data.addHorizonP((10, 10, 10))
    assert not suc
    assert len(data.horizonP) == 2


def test_addHorizonP4():
    data.horizonP = [(10, 10), (10, 10)]
    suc = data.addHorizonP((10, 10), position=1)
    assert suc
    assert len(data.horizonP) == 5


def test_addHorizonP5():
    data.horizonP = [(10, 10), (10, 10)]
    suc = data.addHorizonP((10, 10), position=20)
    assert suc
    assert len(data.horizonP) == 5


def test_addHorizonP6():
    data.horizonP = [(10, 10), (10, 10)]
    suc = data.addHorizonP((10, 10), position=-5)
    assert suc
    assert len(data.horizonP) == 5


def test_addHorizonP7():
    data.horizonP = [(10, 10), (10, 10)]
    suc = data.addHorizonP(position=-5)
    assert not suc


def test_delHorizonP1():
    data.horizonP = ()
    data.genGreaterCircle('max')
    data.horizonP = data.buildP
    assert len(data.horizonP) == 159
    suc = data.delHorizonP(5)
    assert suc
    assert len(data.horizonP) == 158
    suc = data.delHorizonP(1)
    assert suc
    assert len(data.horizonP) == 157
    suc = data.delHorizonP(150)
    assert suc
    assert len(data.horizonP) == 156


def test_delHorizonP2():
    data.horizonP = ()
    data.genGreaterCircle('max')
    data.horizonP = data.buildP
    assert len(data.horizonP) == 159
    suc = data.delHorizonP(-5)
    assert not suc
    assert len(data.horizonP) == 159


def test_delHorizonP3():
    data.horizonP = ()
    data.genGreaterCircle('max')
    data.horizonP = data.buildP
    assert len(data.horizonP) == 159
    suc = data.delHorizonP(170)
    assert not suc
    assert len(data.horizonP) == 159


def test_delHorizonP4():
    data.horizonP = ()
    data.genGreaterCircle('max')
    data.horizonP = data.buildP
    assert len(data.horizonP) == 159
    suc = data.delHorizonP('1')
    assert not suc
    assert len(data.horizonP) == 159


def test_delHorizonP5():
    data.horizonP = [(1, 1), (3, 3), (10, 10)]
    suc = data.delHorizonP(position=0)
    assert not suc
    suc = data.delHorizonP(154)
    assert not suc


def test_saveBuildP_11():
    data.genGreaterCircle('min')
    suc = data.saveBuildP()
    assert not suc


def test_saveBuildP_12():
    fileName = mwGlob['configDir'] + '/save_test.bpts'
    data.genGreaterCircle('min')
    suc = data.saveBuildP('save_test')
    assert suc
    assert os.path.isfile(fileName)


def test_loadBuildP_11():
    # wrong fileName given
    suc = data.loadBuildP()
    assert not suc


def test_loadBuildP_12():
    # path with not existent file given
    suc = data.loadBuildP(fileName='test_file_not_there')
    assert not suc


def test_loadBuildP_13():
    # load file with path
    data.buildPFile = ''
    fileName = mwGlob['configDir'] + '/test.bpts'
    values = [(1, 1), (2, 2)]
    with open(fileName, 'w') as outfile:
        json.dump(values,
                  outfile,
                  indent=4)
    suc = data.loadBuildP(fileName='test')
    assert suc
    assert data.buildP == values


def test_loadBuildP_14():
    # load with wrong content
    data.buildPFile = ''
    fileName = mwGlob['configDir'] + '/test.bpts'
    with open(fileName, 'wb') as outfile:
        outfile.write(binascii.unhexlify('9f'))
    suc = data.loadBuildP(fileName='test')
    assert not suc
    assert data.buildP == []


def test_loadBuildP_15():
    # load with wrong content 2
    data.buildPFile = ''
    fileName = mwGlob['configDir'] + '/test.bpts'
    with open(fileName, 'w') as outfile:
        outfile.writelines('[test, ]],[]}')
    suc = data.loadBuildP(fileName='test')
    assert not suc
    assert data.buildP == []


def test_loadBuildP_16():
    # load file without path
    fileName = mwGlob['configDir'] + '/test.bpts'
    data.buildPFile = 'test'
    values = [(1, 1), (2, 2)]
    with open(fileName, 'w') as outfile:
        json.dump(values,
                  outfile,
                  indent=4)
    with mock.patch.object(data,
                           'checkFormat',
                           return_value=False):
        suc = data.loadBuildP()
        assert not suc


def test_checkBoundaries_1():
    points = [(0, 0), (0, 1), (0, 2), (0, 360)]
    pointsRet = [(0, 1), (0, 2)]
    value = data.checkBoundaries(points)
    assert pointsRet == value


def test_checkBoundaries_2():
    points = [(0, 1), (0, 2), (0, 360)]
    pointsRet = [(0, 1), (0, 2)]
    value = data.checkBoundaries(points)
    assert pointsRet == value


def test_checkBoundaries_3():
    points = [(0, 0), (0, 1), (0, 2)]
    pointsRet = [(0, 1), (0, 2)]
    value = data.checkBoundaries(points)
    assert pointsRet == value


def test_saveHorizonP_10():
    data._horizonP = [(0, 1), (0, 2)]
    suc = data.saveHorizonP(fileName='test_save_horizon')
    assert suc


def test_saveHorizonP_11():
    data._horizonP = [(0, 1), (0, 2)]
    suc = data.saveHorizonP()
    assert not suc


def test_saveHorizonP_12():
    data._horizonP = [(0, 0), (0, 1), (0, 2), (0, 360)]
    suc = data.saveHorizonP(fileName='test_horizon_1')
    assert suc
    fileName = mwGlob['configDir'] + '/' + 'test_horizon_1' + '.hpts'
    with open(fileName, 'r') as infile:
        value = json.load(infile)
        assert value[0] != [0, 0]
        assert value[-1] != [0, 360]


def test_loadHorizonP_10():
    # no fileName given
    suc = data.loadHorizonP()
    assert not suc


def test_loadHorizonP_11():
    # wrong fileName given
    suc = data.loadHorizonP(fileName='format_not_ok')
    assert not suc


def test_loadHorizonP_12():
    # path with not existent file given
    fileName = mwGlob['configDir'] + '/test_load_horizon.hpts'
    suc = data.loadHorizonP(fileName=fileName)
    assert not suc


def test_loadHorizonP_13():
    # load file with path
    fileName = mwGlob['configDir'] + '/test_horizon_2.hpts'
    values = [(1, 1), (2, 2)]
    with open(fileName, 'w') as outfile:
        json.dump(values,
                  outfile,
                  indent=4)
    suc = data.loadHorizonP(fileName='test_horizon_2')
    assert suc
    assert data.horizonP == [(0, 0)] + values + [(0, 360)]


def test_loadHorizonP_14():
    # load with wrong content
    data.horizonPFile = ''
    fileName = mwGlob['configDir'] + '/test_horizon_2.hpts'
    with open(fileName, 'wb') as outfile:
        outfile.write(binascii.unhexlify('9f'))
    suc = data.loadHorizonP(fileName='test_horizon_2')
    assert not suc
    assert data.horizonP == [(0, 0), (0, 360)]


def test_loadHorizonP_15():
    # load with wrong content 2
    data.horizonPFile = ''
    fileName = mwGlob['configDir'] + '/test_horizon_2.hpts'
    with open(fileName, 'w') as outfile:
        outfile.writelines('[test, ]],[]}')
    suc = data.loadHorizonP(fileName='test_horizon_2')
    assert not suc
    assert data.horizonP == [(0, 0), (0, 360)]


def test_genGrid1():
    suc = data.genGrid(minAlt=10,
                       maxAlt=80,
                       numbRows=4,
                       numbCols=4)
    assert suc


def test_genGrid2():
    suc = data.genGrid(minAlt=0,
                       maxAlt=80,
                       numbRows=4,
                       numbCols=4)
    assert not suc


def test_genGrid3():
    suc = data.genGrid(minAlt=10,
                       maxAlt=90,
                       numbRows=4,
                       numbCols=4)
    assert not suc


def test_genGrid4():
    suc = data.genGrid(minAlt=50,
                       maxAlt=40,
                       numbRows=4,
                       numbCols=3)
    assert not suc


def test_genGrid5():
    suc = data.genGrid(minAlt=10,
                       maxAlt=40,
                       numbRows=4,
                       numbCols=4)
    assert suc


def test_genGrid6():
    suc = data.genGrid(minAlt=10,
                       maxAlt=90,
                       numbRows=4,
                       numbCols=3)
    assert not suc


def test_genGrid7():
    suc = data.genGrid(minAlt=10,
                       maxAlt=80,
                       numbRows=4,
                       numbCols=3)
    assert not suc


def test_genGridData1():
    data.genGrid(minAlt=10,
                 maxAlt=40,
                 numbRows=4,
                 numbCols=4)
    assert 16 == len(data.buildP)


def test_genGridData2():
    data.genGrid(minAlt=5,
                 maxAlt=85,
                 numbRows=4,
                 numbCols=4)
    assert 16 == len(data.buildP)


def test_genGridData3():
    data.genGrid(minAlt=5,
                 maxAlt=85,
                 numbRows=8,
                 numbCols=8)
    assert 64 == len(data.buildP)


def test_genGridData4():
    data.genGrid(minAlt=10,
                 maxAlt=40,
                 numbRows=6,
                 numbCols=6)
    assert 36 == len(data.buildP)


def test_genGridData5():
    data.genGrid(minAlt=10,
                 maxAlt=40,
                 numbRows=6,
                 numbCols=12)
    assert 72 == len(data.buildP)


def test_genGridData6():
    data.genGrid(minAlt=10,
                 maxAlt=40,
                 numbRows=1,
                 numbCols=12)
    assert 0 == len(data.buildP)


def test_genGridData7():
    data.genGrid(minAlt=10,
                 maxAlt=40,
                 numbRows=5,
                 numbCols=1)
    assert 0 == len(data.buildP)


def test_genGridData8():
    data.genGrid(minAlt=10,
                 maxAlt=40,
                 numbRows=10,
                 numbCols=12)
    assert 0 == len(data.buildP)


def test_genGridData9():
    data.genGrid(minAlt=10,
                 maxAlt=40,
                 numbRows=6,
                 numbCols=20)
    assert 0 == len(data.buildP)


def test_genAlign1():
    suc = data.genAlign(altBase=30,
                        azBase=30,
                        numberBase=5,
                        )
    assert suc
    assert 5 == len(data.buildP)


def test_genAlign2():
    suc = data.genAlign(altBase=0,
                        azBase=30,
                        numberBase=5,
                        )
    assert not suc
    assert 0 == len(data.buildP)


def test_genAlign3():
    suc = data.genAlign(altBase=30,
                        azBase=-10,
                        numberBase=5,
                        )
    assert not suc
    assert 0 == len(data.buildP)


def test_genAlign4():
    suc = data.genAlign(altBase=30,
                        azBase=30,
                        numberBase=2,
                        )
    assert not suc
    assert 0 == len(data.buildP)


def test_genAlign5():
    suc = data.genAlign(altBase=30,
                        azBase=30,
                        numberBase=30,
                        )
    assert not suc
    assert 0 == len(data.buildP)


def test_isAboveHorizon():
    data.clearHorizonP()
    suc = data.isAboveHorizon((10, 50))
    assert suc
    suc = data.isAboveHorizon((10, 370))
    assert suc
    suc = data.isAboveHorizon((10, -50))
    assert suc
    suc = data.isAboveHorizon((-10, 50))
    assert not suc


def test_deleteBelowHorizon1():
    data.clearHorizonP()
    data.buildP = [(10, 10), (-5, 40), (40, 60)]
    data.deleteBelowHorizon()
    assert len(data.buildP) == 2


def test_deleteBelowHorizon2():
    data.clearHorizonP()
    data.buildP = [(10, 10), (5, 40), (-40, 60)]
    data.deleteBelowHorizon()
    assert len(data.buildP) == 2


def test_deleteBelowHorizon3():
    data.clearHorizonP()
    data.buildP = [(-10, 10), (5, 40), (40, 60)]
    data.deleteBelowHorizon()
    assert len(data.buildP) == 2


def test_deleteBelowHorizon4():
    data.clearHorizonP()
    data.buildP = [(-10, 10), (-5, 40), (-40, 60)]
    data.deleteBelowHorizon()
    assert len(data.buildP) == 0


def test_sort_1():
    values = [(10, 10), (20, 20), (30, 90), (40, 190), (50, 290)]
    data._buildP = values
    suc = data.sort()
    assert not suc
    assert data.buildP == values


def test_sort_2():
    values = [(10, 10), (20, 20), (30, 90), (40, 190), (50, 290)]
    data._buildP = values
    suc = data.sort(eastwest=True, highlow=True)
    assert not suc
    assert data.buildP == values


def test_sort_3():
    values = [(10, 10), (20, 20), (30, 90), (40, 190), (50, 290)]
    result = [(30, 90), (20, 20), (10, 10), (50, 290), (40, 190)]
    data._buildP = values
    suc = data.sort(eastwest=True, highlow=False)
    assert suc
    assert data.buildP == result


def test_sort_4():
    values = [(10, 10), (20, 20), (30, 90), (40, 190), (50, 290)]
    result = [(30, 90), (20, 20), (10, 10), (50, 290), (40, 190)]
    data._buildP = values
    suc = data.sort(eastwest=False, highlow=True)
    assert suc
    assert data.buildP == result


def test_sort_5():
    values = [(30, 90), (50, 290), (20, 20), (10, 10), (40, 190)]
    result = [(30, 90), (20, 20), (10, 10), (50, 290), (40, 190)]
    data._buildP = values
    suc = data.sort(eastwest=True, highlow=False)
    assert suc
    assert data.buildP == result


def test_sort_6():
    values = [(30, 90), (50, 290), (20, 20), (10, 10), (40, 190)]
    result = [(30, 90), (20, 20), (10, 10), (50, 290), (40, 190)]
    data._buildP = values
    suc = data.sort(eastwest=False, highlow=True)
    assert suc
    assert data.buildP == result


def test_generateCelestialEquator():
    value = data.generateCelestialEquator()
    assert len(value) == 560
