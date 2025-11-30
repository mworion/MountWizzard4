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
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import binascii
import json
import os
import unittest.mock as mock
from pathlib import Path

import numpy as np
import pytest

# external packages
import skyfield.api
from skyfield.api import wgs84
import skyfield.almanac

from mw4.logic.buildData.buildpoints import DataPoint, HaDecToAltAz

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="module")
def function():
    config = Path("tests/work/config")
    testdir = os.listdir(config)
    for item in testdir:
        if item.endswith(".bpts"):
            os.remove(os.path.join(config, item))
        if item.endswith(".hpts"):
            os.remove(os.path.join(config, item))

    app = App()
    app.mount.obsSite.location = wgs84.latlon(latitude_degrees=48, longitude_degrees=11)
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


def test_addBuildP_1(function):
    function.buildP = []
    function.addBuildP([10, 10, 1], 1)
    assert len(function.buildP) == 1


def test_addBuildP_2(function):
    function.buildP = [[10, 10, 1], [10, 10, 1]]
    function.addBuildP([10, 10, 1], position=1)
    assert len(function.buildP) == 3


def test_addBuildP_3(function):
    function.buildP = [[10, 10, 1], [10, 10, 1]]
    function.addBuildP([10, 10, 1], position=20)
    assert len(function.buildP) == 3


def test_addBuildP_4(function):
    function.buildP = [[10, 10, 1], [10, 10, 1]]
    function.addBuildP([10, 10, 1], position=-5)
    assert len(function.buildP) == 3


def test_addBuildP_5(function):
    function.buildP = [[10, 10, 1], [10, 10, 1]]
    function.app.mount.setting.horizonLimitHigh = 80
    function.app.mount.setting.horizonLimitLow = 5
    function.addBuildP([90, 10, 1], position=20)


def test_addBuildP_6(function):
    function.buildP = [[10, 10, 1], [10, 10, 1]]
    function.app.mount.setting.horizonLimitHigh = 80
    function.app.mount.setting.horizonLimitLow = 5
    function.addBuildP([0, 10, 1], position=20)


def test_addBuildP_7(function):
    function.app.mount.setting.horizonLimitLow = None
    function.app.mount.setting.horizonLimitHigh = None
    function.buildP = [[10, 10, 1], [10, 10, 1]]
    function.addBuildP([10, 10, 1], position=-5)
    assert len(function.buildP) == 3
    function.app.mount.setting.horizonLimitLow = 5
    function.app.mount.setting.horizonLimitHigh = 80


def test_delBuildP1(function):
    function.buildP = []
    function.genGreaterCircle("max")
    assert len(function.buildP) == 127
    function.delBuildP(5)
    assert len(function.buildP) == 126
    function.delBuildP(0)
    assert len(function.buildP) == 125
    function.delBuildP(99)
    assert len(function.buildP) == 124


def test_delBuildP2(function):
    function.buildP = []
    function.genGreaterCircle("max")
    assert len(function.buildP) == 127
    function.delBuildP(-5)
    assert len(function.buildP) == 127


def test_delBuildP3(function):
    function.buildP = []
    function.genGreaterCircle("max")
    assert len(function.buildP) == 127
    function.delBuildP(170)
    assert len(function.buildP) == 127


def test_genHaDecParams1(function):
    selection = "min"
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
    selection = "norm"
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
    selection = "med"
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
    selection = "max"
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
    selection = "test"
    val = True
    for i, (_, _, _, _) in enumerate(function.genHaDecParams(selection, 50)):
        val = False
    assert val


def test_genHaDecParams6(function):
    selection = "max"
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
    function.horizonP = []
    function.genGreaterCircle("max")
    function.horizonP = function.buildP
    assert len(function.horizonP) == 127
    function.horizonP = []
    function.genGreaterCircle("med")
    function.horizonP = function.buildP
    assert len(function.horizonP) == 102
    function.horizonP = []
    function.genGreaterCircle("norm")
    function.horizonP = function.buildP
    assert len(function.horizonP) == 89
    function.horizonP = []
    function.genGreaterCircle("min")
    function.horizonP = function.buildP
    assert len(function.horizonP) == 58


def test_horizonP2(function):
    function.horizonP = "456"
    assert len(function.horizonP) == 0


def test_horizonP3(function):
    function.horizonP = [(1, 1), (1, 1), "test"]
    assert len(function.horizonP) == 0


def test_buildP1(function):
    function.horizonP = []
    function.genGreaterCircle("max")
    function.genGreaterCircle("med")
    function.genGreaterCircle("norm")
    function.genGreaterCircle("min")


def test_buildP2(function):
    function.buildP = "456"
    assert len(function.buildP) == 0


def test_buildP3(function):
    function.buildP = [(1, 1), (1, 1), "test"]
    assert len(function.buildP) == 0


def test_genGreaterCircle1(function):
    function.horizonP = []
    selection = "min"
    function.genGreaterCircle(selection)
    for i, (alt, az, status) in enumerate(function.buildP):
        assert alt <= 90
        assert az <= 360
        assert alt >= 0
        assert az >= 0
        assert status


def test_genGreaterCircle2(function):
    function.horizonP = []
    selection = "norm"
    function.genGreaterCircle(selection)
    for i, (alt, az, status) in enumerate(function.buildP):
        assert alt <= 90
        assert az <= 360
        assert alt >= 0
        assert az >= 0
        assert status


def test_genGreaterCircle3(function):
    function.horizonP = []
    selection = "med"
    function.genGreaterCircle(selection)
    for i, (alt, az, status) in enumerate(function.buildP):
        assert alt <= 90
        assert az <= 360
        assert alt >= 0
        assert az >= 0
        assert status


def test_genGreaterCircle4(function):
    function.horizonP = []
    selection = "max"
    function.genGreaterCircle(selection)
    for i, (alt, az, status) in enumerate(function.buildP):
        assert alt <= 90
        assert az <= 360
        assert alt >= 0
        assert az >= 0
        assert status


def test_genGreaterCircle5(function):
    function.horizonP = []
    temp = function.app.mount.obsSite.location
    function.app.mount.obsSite.location = None
    selection = "max"
    suc = function.genGreaterCircle(selection)
    assert not suc
    function.app.mount.obsSite.location = temp


def test_checkFormat_1(function):
    a = [(1, 1), (1, 1)]
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
    a = "test"
    suc = function.checkFormat(a)
    assert not suc


def test_checkFormat_5(function):
    a = [[1, 1], [1, 1]]
    suc = function.checkFormat(a)
    assert suc


def test_checkFormat_6(function):
    a = [(1, 1), (1, 1, 1)]
    suc = function.checkFormat(a)
    assert not suc


def test_clearBuildP(function):
    function.genGreaterCircle("max")
    assert len(function.buildP) == 127
    function.clearBuildP()
    assert len(function.buildP) == 0


def test_clearHorizonP(function):
    function.genGreaterCircle("max")
    function.horizonP = function.buildP
    assert len(function.horizonP) == 127
    function.clearHorizonP()
    assert len(function.horizonP) == 0


def test_setStatusBuildP_1(function):
    function.buildP = []
    function.addBuildP([10, 10, 1])
    function.addBuildP([10, 10, 1])
    function.addBuildP([10, 10, 1])
    function.setStatusBuildP(-1, 1)


def test_setStatusBuildP_2(function):
    function.buildP = []
    function.addBuildP([10, 10, 1])
    function.addBuildP([10, 10, 1])
    function.addBuildP([10, 10, 1])
    function.setStatusBuildP(3, 1)


def test_setStatusBuildP_3(function):
    function.buildP = []
    function.addBuildP([10, 10, 1])
    function.addBuildP([10, 10, 1])
    function.addBuildP([10, 10, 1])
    function.setStatusBuildP(1, 1)
    assert function.buildP[1][2]


def test_setStatusBuildP_4(function):
    function.buildP = []
    function.addBuildP([10, 10, 1])
    function.addBuildP([10, 10, 1])
    function.addBuildP([10, 10, 1])
    function.setStatusBuildP(1, False)
    assert not function.buildP[1][2]


def test_setStatusBuildPSolved(function):
    function.buildP = []
    function.addBuildP([10, 10, 1])
    function.addBuildP([10, 10, 1])
    function.addBuildP([10, 10, 1])
    function.setStatusBuildPSolved(1)
    assert function.buildP[1][2] == 2


def test_setStatusBuildPFailed(function):
    function.buildP = []
    function.addBuildP([10, 10, 1])
    function.addBuildP([10, 10, 1])
    function.addBuildP([10, 10, 1])
    function.setStatusBuildPFailed(1)
    assert function.buildP[1][2] == 0


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
    suc = function.isAboveHorizon([10, 50])
    assert suc
    suc = function.isAboveHorizon([10, 370])
    assert suc
    suc = function.isAboveHorizon([10, -50])
    assert suc
    suc = function.isAboveHorizon([-10, 50])
    assert not suc


def test_isAboveHorizon_2(function):
    function.horizonP = [[1, 2], [2, 3]]
    suc = function.isAboveHorizon([10, 50])
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
    function.buildP = [[10, 10, 1], [-5, 40, 1], [40, 60, 1]]
    function.deleteBelowHorizon()
    assert len(function.buildP) == 2


def test_deleteBelowHorizon2(function):
    function.clearHorizonP()
    function.buildP = [[10, 10, 1], [-5, 40, 1], [40, 60, 1]]
    function.deleteBelowHorizon()
    assert len(function.buildP) == 2


def test_deleteBelowHorizon3(function):
    function.clearHorizonP()
    function.buildP = [[10, 10, 1], [-5, 40, 1], [40, 60, 1]]
    function.deleteBelowHorizon()
    assert len(function.buildP) == 2


def test_deleteBelowHorizon4(function):
    function.clearHorizonP()
    function.buildP = [[-10, 10, 1], [-5, 40, 1], [-40, 60, 1]]
    function.deleteBelowHorizon()
    assert len(function.buildP) == 0


def test_deleteCloseMeridian_1(function):
    function.deleteCloseMeridian()


def test_deleteCloseHorizonLine_1(function):
    function.deleteCloseHorizonLine(0)


def test_deleteCloseHorizonLine_2(function):
    function.buildP = [[10, 10, 1], [5, 40, 1], [-40, 60, 1]]
    function.horizonP = [[0, 10], [180, 40], [360, 60]]
    function.deleteCloseHorizonLine(0)


def test_addHorizonP1(function):
    function.horizonP = []
    function.addHorizonP([10, 10])
    assert len(function._horizonP) == 1

    function.addHorizonP([10, 10])
    assert len(function._horizonP) == 2

    function.addHorizonP([10, 10])
    assert len(function._horizonP) == 3


def test_addHorizonP4(function):
    function.horizonP = [[10, 10], [10, 10]]
    function.addHorizonP([10, 10], position=1)
    assert len(function.horizonP) == 3


def test_addHorizonP5(function):
    function.horizonP = [[10, 10], [10, 10]]
    function.addHorizonP([10, 10], position=20)
    assert len(function.horizonP) == 3


def test_addHorizonP6(function):
    function.horizonP = [[10, 10], [10, 10]]
    function.addHorizonP([10, 10], position=-5)
    assert len(function.horizonP) == 3


def test_delHorizonP1(function):
    function.genGreaterCircle("max")
    function.horizonP = function.buildP
    assert len(function.horizonP) == 127
    function.delHorizonP(5)
    assert len(function.horizonP) == 126
    function.delHorizonP(1)
    assert len(function.horizonP) == 125
    function.delHorizonP(10)
    assert len(function.horizonP) == 124


def test_delHorizonP2(function):
    function.genGreaterCircle("max")
    function.horizonP = function.buildP
    assert len(function.horizonP) == 127

    function.delHorizonP(-5)
    assert len(function.horizonP) == len(function.buildP)


def test_delHorizonP3(function):
    function.genGreaterCircle("max")
    function.horizonP = function.buildP
    assert len(function.horizonP) == len(function.buildP)

    function.delHorizonP(170)
    assert len(function.horizonP) == len(function.buildP)


def test_delHorizonP4(function):
    function.genGreaterCircle("max")
    function.horizonP = function.buildP
    assert len(function.horizonP) == len(function.buildP)


def test_delHorizonP5(function):
    function.horizonP = [[1, 1], [3, 3], [10, 10]]
    function.delHorizonP(position=0)
    function.delHorizonP(154)


def test_loadModel_2(function):
    with open("tests/work/config/test.model", "w") as outfile:
        outfile.writelines("[test, ]],[]}")

    val = function.loadModel(Path("tests/work/config/test.model"))
    assert val is None


def test_loadModel_3(function):
    with open("tests/work/config/test.model", "wb") as outfile:
        outfile.write(binascii.unhexlify("9f"))

    val = function.loadModel(Path("tests/work/config/test.model"))
    assert val is None


def test_loadModel_4(function):
    values = [{"azimuth": 1, "altitude": 1}, {"azimuth": 2, "altitude": 2}]
    with open("tests/work/config/test.model", "w") as outfile:
        json.dump(values, outfile, indent=4)

    val = function.loadModel(Path("tests/work/config/test.model"))
    assert val == [[1, 1], [2, 2]]


def test_loadBPTS_2(function):
    with open("tests/work/config/test.bpts", "w") as outfile:
        outfile.writelines("[test, ]],[]}")

    val = function.loadBPTS(Path("tests/work/config/test.bpts"))
    assert val is None


def test_loadBPTS_3(function):
    with open("tests/work/config/test.bpts", "wb") as outfile:
        outfile.write(binascii.unhexlify("9f"))

    val = function.loadBPTS(Path("tests/work/config/test.bpts"))
    assert val is None


def test_loadBPTS_4(function):
    values = [[1, 1], [2, 2]]
    with open("tests/work/config/test.bpts", "w") as outfile:
        json.dump(values, outfile, indent=4)

    val = function.loadBPTS(Path("tests/work/config/test.bpts"))
    assert val == [[1, 1], [2, 2]]


def test_loadCSV_1(function):
    with open("tests/work/config/test.csv", "w") as outfile:
        outfile.writelines("[test, ]],[]}\n")

    val = function.loadCSV(Path("tests/work/config/test.csv"))
    assert val is None


def test_loadCSV_2(function):
    with open("tests/work/config/test.csv", "w") as outfile:
        outfile.writelines("1, 1\n")
        outfile.writelines("2, 2\n")

    val = function.loadCSV(Path("tests/work/config/test.csv"))
    assert val == [[1, 1], [2, 2]]


def test_loadCSV_3(function):
    with open("tests/work/config/test.csv", "w") as outfile:
        outfile.writelines("1; 1\n")
        outfile.writelines("2; 2\n")

    val = function.loadCSV(Path("tests/work/config/test.csv"))
    assert val == [[1, 1], [2, 2]]


def test_loadBuildP_1(function):
    # path with not existent file given
    suc = function.loadBuildP(Path("test_file_not_there"))
    assert not suc


def test_loadBuildP_2(function):
    # path with not existent file given
    with mock.patch.object(Path, "is_file", return_value=True):
        with mock.patch.object(function, "loadBPTS", return_value=None):
            suc = function.loadBuildP(Path("tests/work/config/test.bpts"))
            assert not suc


def test_loadBuildP_3(function):
    # load file with Path
    function.buildPFile = ""
    fileName = "tests/work/config/test.bpts"
    values = [[1, 1], [2, 2]]
    with open(fileName, "w") as outfile:
        json.dump(values, outfile, indent=4)
    suc = function.loadBuildP(Path("tests/work/config/test.bpts"))
    assert suc
    assert function.buildP == [(1, 1, 1), (2, 2, 1)]


def test_loadBuildP_4(function):
    # load file with Path
    function.buildPFile = ""
    fileName = "tests/work/config/test.csv"
    with open(fileName, "w") as outfile:
        outfile.write("1, 1\n")
        outfile.write("2, 2\n")
    suc = function.loadBuildP(Path("tests/work/config/test.csv"), ext=".csv", keep=True)
    assert suc


def test_loadBuildP_6(function):
    # load file with Path
    function.buildPFile = ""
    values = [{"azimuth": 1, "altitude": 1}, {"azimuth": 2, "altitude": 2}]
    with open("tests/work/config/test.model", "w") as outfile:
        json.dump(values, outfile, indent=4)
    suc = function.loadBuildP(Path("tests/work/config/test.model"), ext=".model", keep=True)
    assert suc


def test_saveBuildP_1(function):
    function.genGreaterCircle("min")
    function.saveBuildP("")


def test_saveBuildP_2(function):
    fileName = "tests/work/config/save_test.bpts"
    function.genGreaterCircle("min")
    function.saveBuildP("save_test")
    assert os.path.isfile(fileName)


def test_loadHorizonP_1(function):
    # path with not existent file given
    fileName = "tests/work/config/test_load_horizon.hpts"
    suc = function.loadHorizonP(fileName, ".hpts")
    assert not suc


def test_loadHorizonP_2(function):
    # load file with Path
    fileName = "tests/work/config/test_horizon_2.hpts"
    values = [[1, 1], [2, 2]]
    with open(fileName, "w") as outfile:
        json.dump(values, outfile, indent=4)
    suc = function.loadHorizonP("test_horizon_2", ".hpts")
    assert suc
    assert function.horizonP == values


def test_loadHorizonP_3(function):
    # load with wrong content
    function.horizonPFile = ""
    function.horizonP = []
    fileName = "tests/work/config/test_horizon_2.hpts"
    with open(fileName, "wb") as outfile:
        outfile.write(binascii.unhexlify("9f"))
    suc = function.loadHorizonP("test_horizon_2", ".hpts")
    assert not suc
    assert function.horizonP == []


def test_loadHorizonP_4(function):
    # load with wrong content 2
    function.horizonPFile = ""
    function.horizonP = []
    fileName = "tests/work/config/test_horizon_2.hpts"
    with open(fileName, "w") as outfile:
        outfile.writelines("[test, ]],[]}")
    suc = function.loadHorizonP("test_horizon_2", ".hpts")
    assert not suc
    assert function.horizonP == []


def test_loadHorizonP_5(function):
    # load file with Path
    fileName = "tests/work/config/test_horizon_2.csv"
    values = [[1.0, 1.0], [2.0, 2.0]]
    with open(fileName, "w") as outfile:
        outfile.write("1,1\n2,2\n")

    suc = function.loadHorizonP("test_horizon_2", ".csv")
    assert suc
    assert function.horizonP == values


def test_saveHorizonP_1(function):
    function._horizonP = [(0, 1), (0, 2)]
    function.saveHorizonP(fileName="test_horizon_1")
    fileName = "tests/work/config/" + "test_horizon_1" + ".hpts"
    with open(fileName) as infile:
        value = json.load(infile)
        assert value[0] == [0, 1]
        assert value[1] == [0, 2]


def test_genGrid1(function):
    suc = function.genGrid(minAlt=10, maxAlt=80, numbRows=4, numbCols=4)
    assert suc


def test_genGrid2(function):
    suc = function.genGrid(minAlt=0, maxAlt=80, numbRows=4, numbCols=4)
    assert not suc


def test_genGrid3(function):
    suc = function.genGrid(minAlt=10, maxAlt=90, numbRows=4, numbCols=4)
    assert not suc


def test_genGrid4(function):
    suc = function.genGrid(minAlt=50, maxAlt=40, numbRows=4, numbCols=3)
    assert not suc


def test_genGrid5(function):
    suc = function.genGrid(minAlt=10, maxAlt=40, numbRows=4, numbCols=4)
    assert suc


def test_genGrid6(function):
    suc = function.genGrid(minAlt=10, maxAlt=90, numbRows=4, numbCols=3)
    assert not suc


def test_genGrid7(function):
    suc = function.genGrid(minAlt=10, maxAlt=80, numbRows=4, numbCols=3)
    assert not suc


def test_genGridData1(function):
    function.genGrid(minAlt=10, maxAlt=40, numbRows=4, numbCols=4)
    assert len(function.buildP) == 16


def test_genGridData2(function):
    function.genGrid(minAlt=5, maxAlt=85, numbRows=4, numbCols=4)
    assert len(function.buildP) == 12


def test_genGridData3(function):
    function.genGrid(minAlt=5, maxAlt=85, numbRows=8, numbCols=8)
    assert len(function.buildP) == 56


def test_genGridData4(function):
    function.genGrid(minAlt=10, maxAlt=40, numbRows=6, numbCols=6)
    assert len(function.buildP) == 36


def test_genGridData5(function):
    function.genGrid(minAlt=10, maxAlt=40, numbRows=6, numbCols=12)
    assert len(function.buildP) == 72


def test_genGridData6(function):
    function.genGrid(minAlt=10, maxAlt=40, numbRows=1, numbCols=12)
    assert len(function.buildP) == 72


def test_genGridData7(function):
    function.genGrid(minAlt=10, maxAlt=40, numbRows=5, numbCols=1)
    assert len(function.buildP) == 72


def test_genGridData8(function):
    function.genGrid(minAlt=10, maxAlt=40, numbRows=10, numbCols=12)
    assert len(function.buildP) == 72


def test_genGridData9(function):
    function.genGrid(minAlt=10, maxAlt=40, numbRows=6, numbCols=20)
    assert len(function.buildP) == 72


def test_genAlign1(function):
    suc = function.genAlign(
        altBase=30,
        azBase=30,
        numberBase=5,
    )
    assert suc
    assert len(function.buildP) == 5


def test_genAlign2(function):
    suc = function.genAlign(
        altBase=0,
        azBase=30,
        numberBase=5,
    )
    assert not suc
    assert len(function.buildP) == 5


def test_genAlign3(function):
    suc = function.genAlign(
        altBase=30,
        azBase=-10,
        numberBase=5,
    )
    assert not suc
    assert len(function.buildP) == 5


def test_genAlign4(function):
    suc = function.genAlign(
        altBase=30,
        azBase=30,
        numberBase=2,
    )
    assert not suc
    assert len(function.buildP) == 5


def test_genAlign5(function):
    suc = function.genAlign(
        altBase=30,
        azBase=30,
        numberBase=30,
    )
    assert not suc
    assert len(function.buildP) == 5


def test_sort_1(function):
    values = [
        [10, 10, 1],
        [20, 20, 1],
        [30, 90, 1],
        [40, 190, 1],
        [50, 290, 1],
    ]
    result = [
        [30, 90, 1],
        [20, 20, 1],
        [10, 10, 1],
        [50, 290, 1],
        [40, 190, 1],
    ]
    suc = function.sort(values, eastwest=True)
    assert suc
    assert function.buildP == result


def test_sort_2(function):
    values = [
        [10, 10, 1],
        [20, 20, 1],
        [30, 90, 1],
        [40, 190, 1],
        [50, 290, 1],
    ]
    result = [
        [30, 90, 1],
        [20, 20, 1],
        [10, 10, 1],
        [50, 290, 1],
        [40, 190, 1],
    ]
    suc = function.sort(values, highlow=True)
    assert suc
    assert function.buildP == result


def test_sort_3(function):
    values = [
        [30, 90, 1],
        [50, 290, 1],
        [20, 20, 1],
        [10, 10, 1],
        [40, 190, 1],
    ]
    result = [
        [30, 90, 1],
        [20, 20, 1],
        [10, 10, 1],
        [50, 290, 1],
        [40, 190, 1],
    ]
    suc = function.sort(values, eastwest=True)
    assert suc
    assert function.buildP == result


def test_sort_4(function):
    values = [
        [30, 90, 1],
        [50, 290, 1],
        [20, 20, 1],
        [10, 10, 1],
        [40, 190, 1],
    ]
    result = [
        [30, 90, 1],
        [20, 20, 1],
        [10, 10, 1],
        [50, 290, 1],
        [40, 190, 1],
    ]
    suc = function.sort(values, highlow=True)
    assert suc
    assert function.buildP == result


def test_sort_5(function):
    values = [
        [30, 90, 1],
        [50, 290, 1],
        [20, 20, 1],
        [10, 10, 1],
        [40, 190, 1],
    ]
    result = [
        [50, 290, 1],
        [40, 190, 1],
        [30, 90, 1],
        [20, 20, 1],
        [10, 10, 1],
    ]
    suc = function.sort(values, highlow=True, pierside="E")
    assert suc
    assert function.buildP == result


def test_sort_6(function):
    values = [
        [30, 90, 1],
        [50, 290, 1],
        [20, 20, 1],
        [10, 10, 1],
        [40, 190, 1],
    ]
    result = [
        [30, 90, 1],
        [20, 20, 1],
        [10, 10, 1],
        [50, 290, 1],
        [40, 190, 1],
    ]
    suc = function.sort(values, highlow=True, pierside="W")
    assert suc
    assert function.buildP == result


def test_sort_7(function):
    values = [[30, 90, 1, 3], [20, 20, 1, 2], [50, 290, 1, 1]]
    result = [[30, 90, 1, 3], [20, 20, 1, 2], [50, 290, 1, 1]]
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
    loc = function.app.mount.obsSite.location
    timeJD = function.app.mount.obsSite.ts.tt_jd(2459580.5)
    with mock.patch.object(function, "clearBuildP"):
        function.generateDSOPath(
            ha=ra, dec=dec, timeJD=timeJD, location=loc, numberPoints=1, keep=False
        )


def test_generateDSOPath_2(function):
    ra = skyfield.api.Angle(hours=0)
    dec = skyfield.api.Angle(degrees=0)
    with mock.patch.object(skyfield.almanac, "find_discrete", return_value=([], [])):
        function.generateDSOPath(
            ha=ra,
            dec=dec,
            timeJD=function.app.mount.obsSite.timeJD,
            location=function.app.mount.obsSite.location,
            numberPoints=1,
            keep=True,
        )


def test_generateDSOPath_3(function):
    ra = skyfield.api.Angle(hours=0)
    dec = skyfield.api.Angle(degrees=0)
    ts = function.app.mount.obsSite.ts
    ti = ts.tt_jd(2459580.5)
    with mock.patch.object(skyfield.almanac, "find_discrete", return_value=([ti, ti], [1, 0])):
        with mock.patch.object(function, "calcPath", return_value=[(0, 0), (0, 0), (0, 0)]):
            function.generateDSOPath(
                ha=ra,
                dec=dec,
                numberPoints=1,
                timeJD=function.app.mount.obsSite.timeJD,
                location=function.app.mount.obsSite.location,
                keep=True,
            )


def test_generateGoldenSpiral_1(function):
    function.generateGoldenSpiral(200)


def test_ditherPoints(function):
    function.buildP = [[10, 10, 1]]
    function.ditherPoints()
    assert function.buildP[0][0] != 10
    assert function.buildP[0][1] != 10
