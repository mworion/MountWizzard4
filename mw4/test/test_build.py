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
import skyfield.starlib
# local import
from mw4.build import build

build = build.Data()


def test_topoToAzAlt1():
    ra = 12
    dec = 0
    star = skyfield.starlib.Star(ra_hours=ra, dec_degrees=dec)
    alt, az = build.topoToAzAlt(star, 0)

    assert alt is not None
    assert az is not None


def test_topoToAzAlt2():
    ra = 12
    dec = 0
    star = skyfield.starlib.Star(ra_hours=ra, dec_degrees=dec)
    alt, az = build.topoToAzAlt(1, 0)

    assert alt is None
    assert az is None


def test_topoToAzAlt3():
    ra = -12
    dec = 0
    star = skyfield.starlib.Star(ra_hours=ra, dec_degrees=dec)
    alt, az = build.topoToAzAlt(star, 0)

    assert alt is not None
    assert az is not None


def test_topoToAzAlt4():
    ra = 12
    dec = -450
    star = skyfield.starlib.Star(ra_hours=ra, dec_degrees=dec)
    alt, az = build.topoToAzAlt(star, 0)

    assert alt is not None
    assert az is not None


def test_genDecMin():
    for a, b, c in build.genDecMin():
        print(a, b, c)


def test_genDecNorm():
    for a, b, c in build.genDecNorm():
        print(a, b, c)


def test_genDecMax():
    for a, b, c in build.genDecMax():
        print(a, b, c)


def test_genHaDec1():
    for a, b in build.genHaDec(build.genDecMin):
        print(a, b)


def test_genHaDec2():
    for a, b in build.genHaDec(build.genDecNorm):
        print(a, b)


def test_genHaDec3():
    for a, b in build.genHaDec(build.genDecMax):
        print(a, b)
