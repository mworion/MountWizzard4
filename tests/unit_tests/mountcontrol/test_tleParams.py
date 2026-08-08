############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10_micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2026 by mworion
# License APL2.0
#
###########################################################

from mw4.mountcontrol.tleParams import TLEParams
from skyfield.api import Angle, load


class ObsSite:
    UTC2TT = 69
    ts = load.timescale()


def testAzimuth():
    tleParams = TLEParams(ObsSite())
    tleParams.azimuth = Angle(degrees=10)
    assert tleParams.azimuth.degrees == 10


def testAltitude():
    tleParams = TLEParams(ObsSite())
    tleParams.altitude = Angle(degrees=10)
    assert tleParams.altitude.degrees == 10


def testRa():
    tleParams = TLEParams(ObsSite())
    tleParams.ra = Angle(hours=10)
    assert tleParams.ra.hours == 10


def testDec():
    tleParams = TLEParams(ObsSite())
    tleParams.dec = Angle(degrees=10)
    assert tleParams.dec.degrees == 10


def testFlip():
    tleParams = TLEParams(ObsSite())
    tleParams.flip = True
    assert tleParams.flip


def testMessage():
    tleParams = TLEParams(ObsSite())
    tleParams.message = "test"
    assert tleParams.message == "test"


def testL0():
    tleParams = TLEParams(ObsSite())
    tleParams.l0 = "test"
    assert tleParams.l0 == "test"


def testL1():
    tleParams = TLEParams(ObsSite())
    tleParams.l1 = "test"
    assert tleParams.l1 == "test"


def testL2():
    tleParams = TLEParams(ObsSite())
    tleParams.l2 = "test"
    assert tleParams.l2 == "test"


def testName():
    tleParams = TLEParams(ObsSite())
    tleParams.name = "test"
    assert tleParams.name == "test"
