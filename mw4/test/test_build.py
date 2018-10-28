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
import numpy as np
# local import
from mw4.build import build

build = build.Data()


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


def test_convertPoint():
    for alt, az in build.convertPoint(build.genDecMin):
        print(alt, az)
