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
    for i, (a, b, c, d) in enumerate(data.genHaDecParams(selection=selection)):
        assert a == data.DEC[selection][i]
        assert b == data.STEP[selection][i]
        assert c == data.START[i]
        assert d == data.STOP[i]


def test_genHaDecParams2():
    selection = 'norm'
    for i, (a, b, c, d) in enumerate(data.genHaDecParams(selection=selection)):
        assert a == data.DEC[selection][i]
        assert b == data.STEP[selection][i]
        assert c == data.START[i]
        assert d == data.STOP[i]


def test_genHaDecParams3():
    selection = 'med'
    for i, (a, b, c, d) in enumerate(data.genHaDecParams(selection=selection)):
        assert a == data.DEC[selection][i]
        assert b == data.STEP[selection][i]
        assert c == data.START[i]
        assert d == data.STOP[i]


def test_genHaDecParams4():
    selection = 'max'
    for i, (a, b, c, d) in enumerate(data.genHaDecParams(selection=selection)):
        assert a == data.DEC[selection][i]
        assert b == data.STEP[selection][i]
        assert c == data.START[i]
        assert d == data.STOP[i]


def test_genHaDecParams5():
    selection = 'test'
    val = False
    for i, (a, b, c, d) in enumerate(data.genHaDecParams(selection=selection)):
        val = True
    assert not val


def test_genGreaterCircle1():
    data.lat = 48
    selection = 'min'
    for i, (alt, az) in enumerate(data.genGreaterCircle(selection)):
        assert alt <= 90
        assert az <= 360
        assert alt >= 0
        assert az >= 0
    assert 44 == i


def test_genGreaterCircle2():
    data.lat = 48
    selection = 'norm'
    for i, (alt, az) in enumerate(data.genGreaterCircle(selection)):
        assert alt <= 90
        assert az <= 360
        assert alt >= 0
        assert az >= 0
    assert 67 == i


def test_genGreaterCircle3():
    data.lat = 48
    selection = 'med'
    for i, (alt, az) in enumerate(data.genGreaterCircle(selection)):
        assert alt <= 90
        assert az <= 360
        assert alt >= 0
        assert az >= 0
    assert 136 == i


def test_genGreaterCircle4():
    data.lat = 48
    selection = 'max'
    for i, (alt, az) in enumerate(data.genGreaterCircle(selection)):
        assert alt <= 90
        assert az <= 360
        assert alt >= 0
        assert az >= 0
    assert 167 == i


def test_buildP1():
    data.buildP = ()
    data.buildP = list(data.genGreaterCircle('max'))
    assert len(data.buildP) == 168
    data.buildP = list(data.genGreaterCircle('med'))
    assert len(data.buildP) == 137
    data.buildP = list(data.genGreaterCircle('norm'))
    assert len(data.buildP) == 68
    data.buildP = list(data.genGreaterCircle('min'))
    assert len(data.buildP) == 45


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


def test_delBuildP1():
    data.buildP = ()
    data.buildP = list(data.genGreaterCircle('max'))
    assert len(data.buildP) == 168
    suc = data.delBuildP(5)
    assert suc
    assert len(data.buildP) == 167
    suc = data.delBuildP(0)
    assert suc
    assert len(data.buildP) == 166
    suc = data.delBuildP(165)
    assert suc
    assert len(data.buildP) == 165


def test_delBuildP2():
    data.buildP = ()
    data.buildP = list(data.genGreaterCircle('max'))
    assert len(data.buildP) == 168
    suc = data.delBuildP(-5)
    assert not suc
    assert len(data.buildP) == 168


def test_delBuildP3():
    data.buildP = ()
    data.buildP = list(data.genGreaterCircle('max'))
    assert len(data.buildP) == 168
    suc = data.delBuildP(170)
    assert not suc
    assert len(data.buildP) == 168


def test_delBuildP4():
    data.buildP = ()
    data.buildP = list(data.genGreaterCircle('max'))
    assert len(data.buildP) == 168
    suc = data.delBuildP('1')
    assert not suc
    assert len(data.buildP) == 168
