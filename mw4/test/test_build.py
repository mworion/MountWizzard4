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

build = build.Data(lat=48)


def test_topoToAzAlt1():
    ha = 12
    dec = 0
    alt, az = build.topoToAzAlt(ha, dec, 0)

    assert alt is not None
    assert az is not None


def test_topoToAzAlt2():
    ha = -12
    dec = 0
    alt, az = build.topoToAzAlt(ha, dec, 0)

    assert alt is not None
    assert az is not None


def test_genHaDecParams1():
    selection = 'min'
    for i, (a, b, c, d) in enumerate(build.genHaDecParams(selection=selection)):
        assert a == build.DEC[selection][i]
        assert b == build.STEP[selection][i]
        assert c == build.START[i]
        assert d == build.STOP[i]


def test_genHaDecParams2():
    selection = 'norm'
    for i, (a, b, c, d) in enumerate(build.genHaDecParams(selection=selection)):
        assert a == build.DEC[selection][i]
        assert b == build.STEP[selection][i]
        assert c == build.START[i]
        assert d == build.STOP[i]


def test_genHaDecParams3():
    selection = 'med'
    for i, (a, b, c, d) in enumerate(build.genHaDecParams(selection=selection)):
        assert a == build.DEC[selection][i]
        assert b == build.STEP[selection][i]
        assert c == build.START[i]
        assert d == build.STOP[i]


def test_genHaDecParams4():
    selection = 'max'
    for i, (a, b, c, d) in enumerate(build.genHaDecParams(selection=selection)):
        assert a == build.DEC[selection][i]
        assert b == build.STEP[selection][i]
        assert c == build.START[i]
        assert d == build.STOP[i]


def test_genHaDecParams5():
    selection = 'test'
    val = False
    for i, (a, b, c, d) in enumerate(build.genHaDecParams(selection=selection)):
        val = True
    assert not val


def test_genGreaterCircle1():
    build.lat = 48
    selection = 'min'
    for i, (alt, az) in enumerate(build.genGreaterCircle(selection)):
        assert alt <= 90
        assert az <= 360
        assert alt >= 0
        assert az >= 0
    assert 44 == i


def test_genGreaterCircle2():
    build.lat = 48
    selection = 'norm'
    for i, (alt, az) in enumerate(build.genGreaterCircle(selection)):
        assert alt <= 90
        assert az <= 360
        assert alt >= 0
        assert az >= 0
    assert 67 == i


def test_genGreaterCircle3():
    build.lat = 48
    selection = 'med'
    for i, (alt, az) in enumerate(build.genGreaterCircle(selection)):
        assert alt <= 90
        assert az <= 360
        assert alt >= 0
        assert az >= 0
    assert 136 == i


def test_genGreaterCircle4():
    build.lat = 48
    selection = 'max'
    for i, (alt, az) in enumerate(build.genGreaterCircle(selection)):
        assert alt <= 90
        assert az <= 360
        assert alt >= 0
        assert az >= 0
    assert 167 == i


def test_buildP1():
    build.buildP = ()
    build.buildP = list(build.genGreaterCircle('max'))
    assert len(build.buildP) == 168
    build.buildP = list(build.genGreaterCircle('med'))
    assert len(build.buildP) == 137
    build.buildP = list(build.genGreaterCircle('norm'))
    assert len(build.buildP) == 68
    build.buildP = list(build.genGreaterCircle('min'))
    assert len(build.buildP) == 45


def test_addBuildP1():
    build.buildP = ()
    suc = build.addBuildP((10, 10))
    assert suc
    assert 1 == len(build.buildP)
    suc = build.addBuildP((10, 10))
    assert suc
    assert 2 == len(build.buildP)
    suc = build.addBuildP((10, 10))
    assert suc
    assert 3 == len(build.buildP)


def test_delBuildP1():
    build.buildP = ()
    build.buildP = list(build.genGreaterCircle('max'))
    assert len(build.buildP) == 168
    suc = build.delBuildP(5)
    assert suc
    assert len(build.buildP) == 167
    suc = build.delBuildP(0)
    assert suc
    assert len(build.buildP) == 166
    suc = build.delBuildP(165)
    assert suc
    assert len(build.buildP) == 165


def test_delBuildP2():
    build.buildP = ()
    build.buildP = list(build.genGreaterCircle('max'))
    assert len(build.buildP) == 168
    suc = build.delBuildP(-5)
    assert not suc
    assert len(build.buildP) == 168


def test_delBuildP3():
    build.buildP = ()
    build.buildP = list(build.genGreaterCircle('max'))
    assert len(build.buildP) == 168
    suc = build.delBuildP(170)
    assert not suc
    assert len(build.buildP) == 168


def test_delBuildP4():
    build.buildP = ()
    build.buildP = list(build.genGreaterCircle('max'))
    assert len(build.buildP) == 168
    suc = build.delBuildP('1')
    assert not suc
    assert len(build.buildP) == 168
