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
# Python  v3.6.5
#
# Michael Würtenberger
# (c) 2018
#
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock
import pytest
# external packages
# local import

from mw4.build import build

mwGlob = {'workDir': '.',
          'configDir': './mw4/test/config/',
          'build': 'test',
          }


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    print("MODULE SETUP!!!")
    global data

    data = build.DataPoint(mwGlob=mwGlob, lat=48)
    yield
    print("MODULE TEARDOWN!!!")
    data = None

def test_topoToAzAlt1():
    ha = 12
    dec = 0
    alt, az = data.topoToAzAlt(ha, dec, 0)

    assert alt is not None
    assert az is not None


def test_topoToAzAlt2():
    ha = -12
    dec = 0
    alt, az = data.topoToAzAlt(ha, dec, 0)

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
        assert c == data.START[i]
        assert d == data.STOP[i]


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
        assert c == data.START[i]
        assert d == data.STOP[i]


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
        assert c == data.START[i]
        assert d == data.STOP[i]


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
        assert c == data.START[i]
        assert d == data.STOP[i]


def test_genHaDecParams5():
    selection = 'test'
    val = True
    for i, (a, b, c, d) in enumerate(data.genHaDecParams(selection=selection)):
        val = False
    assert val


def test_genGreaterCircle1():
    data.lat = 48
    selection = 'min'
    for i, (alt, az) in enumerate(data.genGreaterCircle(selection)):
        assert alt <= 90
        assert az <= 360
        assert alt >= 0
        assert az >= 0
    assert 39 == i


def test_genGreaterCircle2():
    data.lat = 48
    selection = 'norm'
    for i, (alt, az) in enumerate(data.genGreaterCircle(selection)):
        assert alt <= 90
        assert az <= 360
        assert alt >= 0
        assert az >= 0
    assert 60 == i


def test_genGreaterCircle3():
    data.lat = 48
    selection = 'med'
    for i, (alt, az) in enumerate(data.genGreaterCircle(selection)):
        assert alt <= 90
        assert az <= 360
        assert alt >= 0
        assert az >= 0
    assert 105 == i


def test_genGreaterCircle4():
    data.lat = 48
    selection = 'max'
    for i, (alt, az) in enumerate(data.genGreaterCircle(selection)):
        assert alt <= 90
        assert az <= 360
        assert alt >= 0
        assert az >= 0
    assert 156 == i


def test_buildP1():
    data.buildP = ()
    data.buildP = list(data.genGreaterCircle('max'))
    assert len(data.buildP) == 157
    data.buildP = list(data.genGreaterCircle('med'))
    assert len(data.buildP) == 106
    data.buildP = list(data.genGreaterCircle('norm'))
    assert len(data.buildP) == 61
    data.buildP = list(data.genGreaterCircle('min'))
    assert len(data.buildP) == 40


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
    data.buildP = list(data.genGreaterCircle('max'))
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


def test_delBuildP1():
    data.buildP = ()
    data.buildP = list(data.genGreaterCircle('max'))
    assert len(data.buildP) == 157
    suc = data.delBuildP(5)
    assert suc
    assert len(data.buildP) == 156
    suc = data.delBuildP(0)
    assert suc
    assert len(data.buildP) == 155
    suc = data.delBuildP(154)
    assert suc
    assert len(data.buildP) == 154


def test_delBuildP2():
    data.buildP = ()
    data.buildP = list(data.genGreaterCircle('max'))
    assert len(data.buildP) == 157
    suc = data.delBuildP(-5)
    assert not suc
    assert len(data.buildP) == 157


def test_delBuildP3():
    data.buildP = ()
    data.buildP = list(data.genGreaterCircle('max'))
    assert len(data.buildP) == 157
    suc = data.delBuildP(170)
    assert not suc
    assert len(data.buildP) == 157


def test_delBuildP4():
    data.buildP = ()
    data.buildP = list(data.genGreaterCircle('max'))
    assert len(data.buildP) == 157
    suc = data.delBuildP('1')
    assert not suc
    assert len(data.buildP) == 157


def test_horizonP1():
    data.horizonP = ()
    data.horizonP = list(data.genGreaterCircle('max'))
    assert len(data.horizonP) == 157
    data.horizonP = list(data.genGreaterCircle('med'))
    assert len(data.horizonP) == 106
    data.horizonP = list(data.genGreaterCircle('norm'))
    assert len(data.horizonP) == 61
    data.horizonP = list(data.genGreaterCircle('min'))
    assert len(data.horizonP) == 40


def test_horizonP2():
    data.horizonP = ()
    data.horizonP = '456'
    assert len(data.horizonP) == 0


def test_horizonP3():
    data.horizonP = ()
    data.horizonP = [(1, 1), (1, 1), 'test']
    assert len(data.horizonP) == 0


def test_clearHorizonP():
    data.horizonP = ()
    data.horizonP = list(data.genGreaterCircle('max'))
    assert len(data.horizonP) == 157
    data.clearHorizonP()
    assert len(data.horizonP) == 0


def test_addHorizonP1():
    data.horizonP = ()
    suc = data.addHorizonP((10, 10))
    assert suc
    assert 1 == len(data.horizonP)
    suc = data.addHorizonP((10, 10))
    assert suc
    assert 2 == len(data.horizonP)
    suc = data.addHorizonP((10, 10))
    assert suc
    assert 3 == len(data.horizonP)


def test_addHorizonP2():
    data.horizonP = ()
    suc = data.addHorizonP(10)
    assert not suc
    assert 0 == len(data.horizonP)


def test_addHorizonP3():
    data.horizonP = ()
    suc = data.addHorizonP((10, 10, 10))
    assert not suc
    assert 0 == len(data.horizonP)


def test_delHorizonP1():
    data.horizonP = ()
    data.horizonP = list(data.genGreaterCircle('max'))
    assert len(data.horizonP) == 157
    suc = data.delHorizonP(5)
    assert suc
    assert len(data.horizonP) == 156
    suc = data.delHorizonP(0)
    assert suc
    assert len(data.horizonP) == 155
    suc = data.delHorizonP(154)
    assert suc
    assert len(data.horizonP) == 154


def test_delHorizonP2():
    data.horizonP = ()
    data.horizonP = list(data.genGreaterCircle('max'))
    assert len(data.horizonP) == 157
    suc = data.delHorizonP(-5)
    assert not suc
    assert len(data.horizonP) == 157


def test_delHorizonP3():
    data.horizonP = ()
    data.horizonP = list(data.genGreaterCircle('max'))
    assert len(data.horizonP) == 157
    suc = data.delHorizonP(170)
    assert not suc
    assert len(data.horizonP) == 157


def test_delHorizonP4():
    data.horizonP = ()
    data.horizonP = list(data.genGreaterCircle('max'))
    assert len(data.horizonP) == 157
    suc = data.delHorizonP('1')
    assert not suc
    assert len(data.horizonP) == 157


def test_saveBuildP():
    data.buildPFile = 'test'
    data.buildP = list(data.genGreaterCircle('min'))
    suc = data.saveBuildP()
    assert suc


def test_loadBuildP1():
    data.buildPFile = 'test'
    data.buildP = list(data.genGreaterCircle('min'))
    suc = data.saveBuildP()
    assert suc
    suc = data.loadBuildP()
    assert suc
    for i, (alt, az) in enumerate(data.genGreaterCircle('min')):
        assert data.buildP[i][0] == alt
        assert data.buildP[i][1] == az


def test_loadBuildP2():
    data.buildPFile = 'test'
    data.buildP = list(data.genGreaterCircle('min'))
    suc = data.saveBuildP()
    assert suc
    data.buildPFile = 'test1'
    suc = data.loadBuildP()
    assert not suc


def test_loadBuildP3():
    data.buildPFile = 'format_nok'
    suc = data.loadBuildP()
    assert not suc


def test_saveHorizonP():
    data.horizonPFile = 'test'
    data.horizonP = list(data.genGreaterCircle('min'))
    suc = data.saveHorizonP()
    assert suc


def test_loadHorizonP1():
    data.horizonPFile = 'test'
    data.horizonP = list(data.genGreaterCircle('min'))
    suc = data.saveHorizonP()
    assert suc
    suc = data.loadHorizonP()
    assert suc
    for i, (alt, az) in enumerate(data.genGreaterCircle('min')):
        assert data.horizonP[i][0] == alt
        assert data.horizonP[i][1] == az


def test_loadHorizonP2():
    data.horizonPFile = 'test'
    data.horizonP = list(data.genGreaterCircle('min'))
    suc = data.saveHorizonP()
    assert suc
    data.horizonPFile = 'test1'
    suc = data.loadHorizonP()
    assert not suc


def test_loadHorizonP3():
    data.horizonPFile = 'format_nok'
    suc = data.loadHorizonP()
    assert not suc


def test_genGrid1():
    val = True
    for i, (alt, az) in enumerate(data.genGrid(minAlt=10,
                                               maxAlt=80,
                                               numbRows=4,
                                               numbCols=3)):
        val = False
    assert val


def test_genGrid2():
    val = True
    for i, (alt, az) in enumerate(data.genGrid(minAlt=0,
                                               maxAlt=80,
                                               numbRows=4,
                                               numbCols=3)):
        val = False
    assert val


def test_genGrid3():
    val = True
    for i, (alt, az) in enumerate(data.genGrid(minAlt=10,
                                               maxAlt=90,
                                               numbRows=4,
                                               numbCols=3)):
        val = False
    assert val


def test_genGrid4():
    val = True
    for i, (alt, az) in enumerate(data.genGrid(minAlt=50,
                                               maxAlt=40,
                                               numbRows=4,
                                               numbCols=3)):
        val = False
    assert val


def test_genGrid5():
    val = True
    for i, (alt, az) in enumerate(data.genGrid(minAlt=10,
                                               maxAlt=40,
                                               numbRows=4,
                                               numbCols=4)):
        val = False
    assert not val


def test_genGrid6():
    val = True
    for i, (alt, az) in enumerate(data.genGrid(minAlt=10,
                                               maxAlt=90,
                                               numbRows=4,
                                               numbCols=4)):
        val = False
    assert val


def test_genGridData1():
    val = list(data.genGrid(minAlt=10,
                            maxAlt=40,
                            numbRows=4,
                            numbCols=4))
    assert 16 == len(val)


def test_genGridData2():
    val = list(data.genGrid(minAlt=5,
                            maxAlt=85,
                            numbRows=4,
                            numbCols=4))
    assert 16 == len(val)


def test_genGridData3():
    val = list(data.genGrid(minAlt=5,
                            maxAlt=85,
                            numbRows=8,
                            numbCols=8))
    assert 64 == len(val)


def test_genGridData4():
    val = list(data.genGrid(minAlt=10,
                            maxAlt=40,
                            numbRows=6,
                            numbCols=6))
    assert 36 == len(val)


def test_genGridData5():
    val = list(data.genGrid(minAlt=10,
                            maxAlt=40,
                            numbRows=6,
                            numbCols=12))
    assert 72 == len(val)


def test_genGridData6():
    val = list(data.genGrid(minAlt=10,
                            maxAlt=40,
                            numbRows=1,
                            numbCols=12))
    assert 0 == len(val)


def test_genGridData7():
    val = list(data.genGrid(minAlt=10,
                            maxAlt=40,
                            numbRows=5,
                            numbCols=1))
    assert 0 == len(val)


def test_genGridData8():
    val = list(data.genGrid(minAlt=10,
                            maxAlt=40,
                            numbRows=10,
                            numbCols=12))
    assert 0 == len(val)


def test_genGridData9():
    val = list(data.genGrid(minAlt=10,
                            maxAlt=40,
                            numbRows=6,
                            numbCols=20))
    assert 0 == len(val)


def test_genInitial1():
    val = True
    for i, (alt, az) in enumerate(data.genInitial(alt=30,
                                                  azStart=30,
                                                  numb=5,
                                                  )):
        val = False
    assert not val


def test_genInitial2():
    val = True
    for i, (alt, az) in enumerate(data.genInitial(alt=0,
                                                  azStart=30,
                                                  numb=5,
                                                  )):
        val = False
    assert val


def test_genInitial3():
    val = True
    for i, (alt, az) in enumerate(data.genInitial(alt=30,
                                                  azStart=-10,
                                                  numb=5,
                                                  )):
        val = False
    assert val


def test_genInitial4():
    val = True
    for i, (alt, az) in enumerate(data.genInitial(alt=30,
                                                  azStart=30,
                                                  numb=2,
                                                  )):
        val = False
    assert val


def test_genInitial5():
    val = True
    for i, (alt, az) in enumerate(data.genInitial(alt=30,
                                                  azStart=30,
                                                  numb=30,
                                                  )):
        val = False
    assert val
