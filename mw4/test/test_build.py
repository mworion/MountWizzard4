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
# external packages
# local import
from mw4.build import build

data = build.DataPoint(lat=48)


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
    for i, (alt, az) in enumerate(data.genGrid(minAlt=10,
                                               maxAlt=40,
                                               numbRows=4,
                                               numbCols=4)):
        val = i
    assert 15 == i


def test_genGridData1():
    for i, (alt, az) in enumerate(data.genGrid(minAlt=10,
                                               maxAlt=80,
                                               numbRows=10,
                                               numbCols=10)):
        val = i
    assert 99 == i


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
