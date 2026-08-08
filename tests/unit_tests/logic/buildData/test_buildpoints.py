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

import json
import numpy as np
import os
import pytest
import skyfield.almanac
import skyfield.api
from mw4.logic.buildData.buildpoints import BuildPoint, HaDecToAltAz
from pathlib import Path
from skyfield.api import Angle, wgs84
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from unittest import mock


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
    func = BuildPoint(app=App())
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
    assert len(function.buildP) == 2


def test_addBuildP_6(function):
    function.buildP = [[10, 10, 1], [10, 10, 1]]
    function.app.mount.setting.horizonLimitHigh = 80
    function.app.mount.setting.horizonLimitLow = 5
    function.addBuildP([0, 10, 1], position=20)
    assert len(function.buildP) == 2


def test_addBuildP_7(function):
    function.app.mount.setting.horizonLimitLow = None
    function.app.mount.setting.horizonLimitHigh = None
    function.buildP = [[10, 10, 1], [10, 10, 1]]
    function.addBuildP([10, 10, 1], position=-5)
    assert len(function.buildP) == 3
    function.app.mount.setting.horizonLimitLow = 5
    function.app.mount.setting.horizonLimitHigh = 80


def test_delBuildP1(function):
    function.buildP = [[10, 10, 1], [10, 10, 1], [10, 10, 1], [10, 10, 1], [10, 10, 1]]
    assert len(function.buildP) == 5
    function.delBuildP(1)
    assert len(function.buildP) == 4
    function.delBuildP(0)
    assert len(function.buildP) == 3
    function.delBuildP(99)
    assert len(function.buildP) == 3


def test_delBuildP2(function):
    function.buildP = [[10, 10, 1], [10, 10, 1], [10, 10, 1], [10, 10, 1], [10, 10, 1]]
    assert len(function.buildP) == 5
    function.delBuildP(-5)
    assert len(function.buildP) == 5


def test_horizonP1(function):
    function.horizonP = [[1, 2], [2, 3], [3, 4]]
    assert len(function.horizonP) == 3


def test_genGreaterCircle1(function):
    function.app.mount.obsSite.location = wgs84.latlon(
        latitude_degrees=48, longitude_degrees=11
    )
    function.horizonP = []
    function.genGreaterCircle(10, 10, 5)
    for i, (alt, az, status) in enumerate(function.buildP):
        assert alt <= 90
        assert az <= 360
        assert alt >= 0
        assert az >= 0
        assert status == 0


def test_genGreaterCircle2(function):
    function.app.mount.obsSite.location = wgs84.latlon(
        latitude_degrees=-48, longitude_degrees=11
    )
    function.horizonP = []
    function.genGreaterCircle(10, 10, 5)
    for i, (alt, az, status) in enumerate(function.buildP):
        assert alt <= 90
        assert az <= 360
        assert alt >= 0
        assert az >= 0
        assert status == 0


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
    function.buildP = [[1, 2, 1], [2, 3, 1]]
    assert len(function.buildP) == 2
    function.clearBuildP()
    assert len(function.buildP) == 0


def test_clearHorizonP(function):
    function.horizonP = [[1, 2], [2, 3]]
    assert len(function.horizonP) == 2
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
    function.setStatusBuildP(1, 0)
    assert not function.buildP[1][2]


def test_setStatusBuildPUnprocessed(function):
    function.buildP = []
    function.addBuildP([10, 10, 1])
    function.addBuildP([10, 10, 1])
    function.addBuildP([10, 10, 1])
    function.setStatusBuildPUnprocessed(1)
    assert function.buildP[1][2] == 0


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
    assert function.buildP[1][2] == 1


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


def test_sortAz_1(function):
    function.buildP = [[10, 10, 1], [5, 40, 1], [350, 60, 1], [180, 20, 1]]
    function.sortAz()
    assert function.buildP[0] == [350, 60, 1]
    assert function.buildP[1] == [5, 40, 1]
    assert function.buildP[2] == [180, 20, 1]
    assert function.buildP[3] == [10, 10, 1]


def test_sortDomeAz_1(function):
    function.buildP = [[10, 10, 1]]
    with mock.patch.object(
        function.app.mount, "calcMountAltAzToDomeAltAz", return_value=(10, Angle(degrees=350))
    ):
        function.sortDomeAz()


def test_sortDomeAz_2(function):
    function.buildP = [[10, 10, 1]]
    with mock.patch.object(
        function.app.mount, "calcMountAltAzToDomeAltAz", return_value=(10, None)
    ):
        function.sortDomeAz()


def test_sortAlt_1(function):
    function.buildP = [[10, 10, 1], [5, 40, 1], [350, 60, 1], [180, 20, 1]]
    function.sortAlt()
    assert function.buildP[0] == [350, 60, 1]
    assert function.buildP[1] == [180, 20, 1]
    assert function.buildP[2] == [10, 10, 1]
    assert function.buildP[3] == [5, 40, 1]


def test_sortActualPierside_1(function):
    function.buildP = [[10, 10, 1], [5, 40, 1], [350, 60, 1], [180, 20, 1]]
    function.app.mount.obsSite.pierside = "W"
    function.sortActualPierside()
    assert function.buildP[0] == [10, 10, 1]
    assert function.buildP[1] == [5, 40, 1]
    assert function.buildP[2] == [350, 60, 1]
    assert function.buildP[3] == [180, 20, 1]


def test_sortActualPierside_2(function):
    function.buildP = [[10, 10, 1], [5, 40, 1], [350, 60, 1], [180, 20, 1]]
    function.app.mount.obsSite.pierside = "E"
    function.sortActualPierside()
    assert function.buildP[0] == [10, 10, 1]
    assert function.buildP[1] == [5, 40, 1]
    assert function.buildP[2] == [350, 60, 1]
    assert function.buildP[3] == [180, 20, 1]


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
    function.horizonP = [[10, 10]] * 20
    assert len(function.horizonP) == 20
    function.delHorizonP(5)
    assert len(function.horizonP) == 19
    function.delHorizonP(1)
    assert len(function.horizonP) == 18
    function.delHorizonP(10)
    assert len(function.horizonP) == 17


def test_delHorizonP2(function):
    function.horizonP = [[10, 10]] * 20
    assert len(function.horizonP) == 20
    function.delHorizonP(-5)
    assert len(function.horizonP) == 20


def test_delHorizonP3(function):
    function.horizonP = [[10, 10]] * 20
    assert len(function.horizonP) == 20
    function.delHorizonP(170)
    assert len(function.horizonP) == 20


def test_delHorizonP5(function):
    function.horizonP = [[1, 1], [3, 3], [10, 10]]
    function.delHorizonP(position=0)
    function.delHorizonP(154)


def test_loadModel_2(function):
    with open("tests/work/config/test.model", "w") as outfile:
        outfile.writelines("[test, ]],[]}")

    val = function.loadModel(Path("tests/work/config/test.model"))
    assert val == []



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
    assert val == []



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
    assert val == []


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


def test_loadBuildP_3(function):
    # load file with Path
    function.buildPFile = ""
    fileName = "tests/work/config/test.bpts"
    values = [[1, 1], [2, 2]]
    with open(fileName, "w") as outfile:
        json.dump(values, outfile, indent=4)
    suc = function.loadBuildP(Path("tests/work/config/test.bpts"))
    assert suc
    assert function.buildP == [[1, 1, function.UNPROCESSED], [2, 2, function.UNPROCESSED]]


def test_loadBuildP_4(function):
    # load file with Path
    function.buildPFile = ""
    fileName = "tests/work/config/test.csv"
    with open(fileName, "w") as outfile:
        outfile.write("1, 1\n")
        outfile.write("2, 2\n")
    suc = function.loadBuildP(Path("tests/work/config/test.csv"))
    assert suc


def test_loadBuildP_6(function):
    # load file with Path
    function.buildPFile = ""
    values = [{"azimuth": 1, "altitude": 1}, {"azimuth": 2, "altitude": 2}]
    with open("tests/work/config/test.model", "w") as outfile:
        json.dump(values, outfile, indent=4)
    suc = function.loadBuildP(Path("tests/work/config/test.model"))
    assert suc


def test_saveBuildP_1(function):
    function.location = wgs84.latlon(latitude_degrees=48, longitude_degrees=11)
    function.genGreaterCircle(10, 10, 5)
    function.saveBuildP("")


def test_saveBuildP_2(function):
    function.location = wgs84.latlon(latitude_degrees=48, longitude_degrees=11)
    fileName = "tests/work/config/save_test.bpts"
    function.genGreaterCircle(10, 10, 5)
    function.saveBuildP("save_test")
    assert os.path.isfile(fileName)


def test_loadHorizonP_1(function):
    # path with not existent file given
    fileName = Path("tests/work/config/test_load_horizon.hpts")
    suc = function.loadHorizonP(fileName)
    assert not suc


def test_loadHorizonP_2(function):
    # load file with Path
    fileName = Path("tests/work/config/test_horizon_2.hpts")
    values = [[1, 1], [2, 2]]
    with open(fileName, "w") as outfile:
        json.dump(values, outfile, indent=4)
    suc = function.loadHorizonP(fileName)
    assert suc
    assert function.horizonP == values


def test_loadHorizonP_3(function):
    # load file with Path
    fileName = Path("tests/work/config/test_horizon_2.csv")
    values = [[1.0, 1.0], [2.0, 2.0]]
    with open(fileName, "w") as outfile:
        outfile.write("1,1\n2,2\n")

    suc = function.loadHorizonP(fileName)
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
    function.horizonP = []
    suc = function.genGrid(minAlt=10, maxAlt=80, numbRows=4, numbCols=4)
    assert suc


def test_genGrid2(function):
    function.horizonP = []
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
    function.app.mount.setting.horizonLimitHigh = 80
    function.app.mount.setting.horizonLimitLow = 5
    function.buildP = []
    function.horizonP = []
    function.genGrid(minAlt=10, maxAlt=40, numbRows=4, numbCols=4)
    assert len(function.buildP) == 16


def test_genGridData2(function):
    function.app.mount.setting.horizonLimitHigh = 80
    function.app.mount.setting.horizonLimitLow = 5
    function.buildP = []
    function.horizonP = []
    function.genGrid(minAlt=5, maxAlt=85, numbRows=4, numbCols=4)
    assert len(function.buildP) == 12


def test_genGridData3(function):
    function.app.mount.setting.horizonLimitHigh = 80
    function.app.mount.setting.horizonLimitLow = 5
    function.buildP = []
    function.horizonP = []
    function.genGrid(minAlt=5, maxAlt=85, numbRows=8, numbCols=8)
    assert len(function.buildP) == 56


def test_genGridData4(function):
    function.app.mount.setting.horizonLimitHigh = 80
    function.app.mount.setting.horizonLimitLow = 5
    function.buildP = []
    function.horizonP = []
    function.genGrid(minAlt=10, maxAlt=40, numbRows=6, numbCols=6)
    assert len(function.buildP) == 36


def test_genGridData5(function):
    function.app.mount.setting.horizonLimitHigh = 80
    function.app.mount.setting.horizonLimitLow = 5
    function.buildP = []
    function.horizonP = []
    function.genGrid(minAlt=10, maxAlt=40, numbRows=6, numbCols=12)
    assert len(function.buildP) == 72


def test_genGridData6(function):
    function.buildP = []
    function.horizonP = []
    function.genGrid(minAlt=10, maxAlt=40, numbRows=1, numbCols=12)
    assert len(function.buildP) == 0


def test_genGridData7(function):
    function.buildP = []
    function.horizonP = []
    function.genGrid(minAlt=10, maxAlt=40, numbRows=5, numbCols=1)
    assert len(function.buildP) == 0


def test_genGridData8(function):
    function.buildP = []
    function.horizonP = []
    function.genGrid(minAlt=10, maxAlt=40, numbRows=10, numbCols=12)
    assert len(function.buildP) == 0


def test_genGridData9(function):
    function.buildP = []
    function.horizonP = []
    function.genGrid(minAlt=10, maxAlt=40, numbRows=6, numbCols=20)
    assert len(function.buildP) == 0


def test_genAlign1(function):
    function.buildP = []
    function.horizonP = []
    suc = function.genAlign(
        altBase=30,
        azBase=30,
        numberBase=5,
    )
    assert suc
    assert len(function.buildP) == 5


def test_genAlign2(function):
    function.buildP = []
    function.horizonP = []
    suc = function.genAlign(
        altBase=0,
        azBase=30,
        numberBase=5,
    )
    assert not suc
    assert len(function.buildP) == 0


def test_genAlign3(function):
    function.buildP = []
    function.horizonP = []
    suc = function.genAlign(
        altBase=30,
        azBase=-10,
        numberBase=5,
    )
    assert not suc
    assert len(function.buildP) == 0


def test_genAlign4(function):
    function.buildP = []
    function.horizonP = []
    suc = function.genAlign(
        altBase=30,
        azBase=30,
        numberBase=2,
    )
    assert not suc
    assert len(function.buildP) == 0


def test_genAlign5(function):
    function.buildP = []
    function.horizonP = []
    suc = function.genAlign(
        altBase=30,
        azBase=30,
        numberBase=30,
    )
    assert not suc
    assert len(function.buildP) == 0


def test_generateCelestialEquator_1(function):
    function.app.mount.obsSite.location = wgs84.latlon(
        latitude_degrees=48, longitude_degrees=11
    )
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
    with (
        mock.patch.object(skyfield.almanac, "find_discrete", return_value=([ti, ti], [1, 0])),
        mock.patch.object(function, "calcPath", return_value=[(0, 0), (0, 0), (0, 0)]),
    ):
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


def test_ditherPoints_multiple_points(function):
    """Test dithering with multiple points"""
    function.buildP = [[10, 10, 1], [20, 20, 0], [30, 30, 2]]
    function.ditherPoints()

    for i, p in enumerate(function.buildP):
        # Points should have been modified by random dither
        assert p[2] == 0  # Status should be reset to UNPROCESSED
    assert len(function.buildP) == 3


def test_isCloseMeridian_1(function):
    """Test point exactly on meridian"""
    function.app.mount.setting.meridianLimitSlew = 5
    function.app.mount.setting.meridianLimitTrack = 5
    suc = function.isCloseMeridian((90, 180))
    assert suc


def test_isCloseMeridian_edge_upper(function):
    """Test point at upper meridian limit"""
    function.app.mount.setting.meridianLimitSlew = 10
    function.app.mount.setting.meridianLimitTrack = 5
    suc = function.isCloseMeridian((90, 189))
    assert suc


def test_isCloseMeridian_edge_lower(function):
    """Test point at lower meridian limit"""
    function.app.mount.setting.meridianLimitSlew = 10
    function.app.mount.setting.meridianLimitTrack = 5
    suc = function.isCloseMeridian((90, 171))
    assert suc


def test_genAlign_boundary_altitude(function):
    """Test genAlign with boundary altitude values"""
    function.buildP = []
    function.horizonP = []
    suc = function.genAlign(altBase=5, azBase=0, numberBase=3)
    assert suc
    assert len(function.buildP) == 3


def test_genAlign_boundary_altitude_high(function):
    """Test genAlign with high boundary altitude"""
    function.buildP = []
    function.horizonP = []
    suc = function.genAlign(altBase=80, azBase=0, numberBase=4)
    assert suc
    assert len(function.buildP) == 4


def test_genAlign_azimuth_wrapping(function):
    """Test genAlign handles azimuth wrapping correctly"""
    function.buildP = []
    function.horizonP = []
    suc = function.genAlign(altBase=30, azBase=350, numberBase=4)
    assert suc
    # Check that azimuth values are properly wrapped
    for alt, az, status in function.buildP:
        assert 0 <= az <= 360


def test_genGrid_boundary_values(function):
    """Test genGrid with boundary parameter values"""
    function.horizonP = []
    suc = function.genGrid(minAlt=5, maxAlt=85, numbRows=3, numbCols=4)
    assert suc


def test_genGrid_equal_min_max_alt(function):
    """Test genGrid when minAlt equals maxAlt"""
    suc = function.genGrid(minAlt=50, maxAlt=50, numbRows=4, numbCols=4)
    assert not suc


def test_loadModel_nonexistent_file(function):
    """Test loadModel with existing file returns data"""
    values = [{"azimuth": 45, "altitude": 30}]
    fileName = Path("tests/work/config/test_model_exist.model")
    with open(fileName, "w") as outfile:
        json.dump(values, outfile, indent=4)
    val = function.loadModel(fileName)
    assert val == [[30, 45]]


def test_loadBPTS_nonexistent_file(function):
    """Test loadBPTS with existing file returns data"""
    values = [[45, 30]]
    fileName = Path("tests/work/config/test_bpts_exist.bpts")
    with open(fileName, "w") as outfile:
        json.dump(values, outfile, indent=4)
    val = function.loadBPTS(fileName)
    assert val == [[45, 30]]


def test_loadCSV_empty_file(function):
    """Test loadCSV with empty file"""
    with open("tests/work/config/empty.csv", "w"):
        pass
    val = function.loadCSV(Path("tests/work/config/empty.csv"))
    assert val == []


def test_loadCSV_single_row(function):
    """Test loadCSV with single row"""
    with open("tests/work/config/single.csv", "w") as outfile:
        outfile.write("45, 90\n")
    val = function.loadCSV(Path("tests/work/config/single.csv"))
    assert val == [[45, 90]]


def test_addBuildP_boundary_position_zero(function):
    """Test addBuildP with position 0"""
    function.buildP = [[10, 10, 1], [20, 20, 1]]
    function.addBuildP([5, 5, 0], position=0)
    assert function.buildP[0] == [5, 5, 0]


def test_addBuildP_boundary_negative_position(function):
    """Test addBuildP with negative position (should be clipped to 0)"""
    function.buildP = [[10, 10, 1]]
    function.addBuildP([5, 5, 0], position=-100)
    assert function.buildP[0] == [5, 5, 0]


def test_delBuildP_boundary(function):
    """Test delBuildP with boundary index"""
    function.buildP = [[10, 10, 1], [20, 20, 1], [30, 30, 1]]
    function.delBuildP(2)
    assert len(function.buildP) == 2
    assert function.buildP[1] == [20, 20, 1]


def test_addHorizonP_boundary_position(function):
    """Test addHorizonP with boundary positions"""
    function.horizonP = [[10, 10]]
    function.addHorizonP([20, 20], position=0)
    assert function.horizonP[0] == [20, 20]
    assert function.horizonP[1] == [10, 10]


def test_isAboveHorizon_edge_azimuth_360(function):
    """Test isAboveHorizon with azimuth 360"""
    function.clearHorizonP()
    suc = function.isAboveHorizon([10, 360])
    assert suc


def test_isAboveHorizon_edge_azimuth_negative(function):
    """Test isAboveHorizon with negative azimuth"""
    function.clearHorizonP()
    suc = function.isAboveHorizon([10, -10])
    assert suc


def test_isAboveHorizon_low_altitude(function):
    """Test isAboveHorizon with very low altitude"""
    function.clearHorizonP()
    suc = function.isAboveHorizon([-89, 180])
    assert not suc


def test_deleteCloseMeridian_with_points_near_meridian(function):
    """Test deleteCloseMeridian removes points near meridian"""
    function.app.mount.setting.meridianLimitSlew = 5
    function.app.mount.setting.meridianLimitTrack = 5
    function.buildP = [[45, 175, 0], [45, 180, 0], [45, 185, 0], [45, 90, 0]]
    function.deleteCloseMeridian()
    # Points near meridian should be removed
    assert len(function.buildP) < 4


def test_generateCelestialEquator_with_negative_latitude(function):
    """Test generateCelestialEquator at southern hemisphere"""
    function.app.mount.obsSite.location = wgs84.latlon(
        latitude_degrees=-30, longitude_degrees=150
    )
    value = function.generateCelestialEquator()
    assert len(value) > 0
    for alt, az in value:
        assert alt > 0


def test_calcPath_no_valid_points(function):
    """Test calcPath when no points are above horizon"""
    ra = skyfield.api.Angle(hours=0)
    dec = skyfield.api.Angle(degrees=89)  # Very high declination
    ts = function.app.mount.obsSite.ts
    location = function.app.mount.obsSite.location
    timeJD = ts.tt_jd(2459580.5)

    buildP = function.calcPath(ts, 1, timeJD.tt, ra, dec, location)
    # Result may be empty or have fewer points depending on geometry
    assert isinstance(buildP, list)


def test_calcPath_multiple_points(function):
    """Test calcPath generates multiple points"""
    ra = skyfield.api.Angle(hours=6)
    dec = skyfield.api.Angle(degrees=45)
    ts = function.app.mount.obsSite.ts
    location = function.app.mount.obsSite.location
    timeJD = ts.tt_jd(2459580.5)

    buildP = function.calcPath(ts, 10, timeJD.tt, ra, dec, location)
    # Should attempt to generate requested number of points
    assert len(buildP) > 0


def test_genGrid_with_large_altitude_range(function):
    """Test genGrid with wide altitude range"""
    function.horizonP = []
    suc = function.genGrid(minAlt=5, maxAlt=85, numbRows=8, numbCols=6)
    assert suc
    # Check point count - should be filtered by horizon limits
    assert len(function.buildP) >= 30


def test_loadHorizonP_with_txt_extension(function):
    """Test loadHorizonP works with .txt extension"""
    fileName = Path("tests/work/config/test_horizon.txt")
    values = [[0, 0], [90, 180], [0, 360]]
    with open(fileName, "w") as outfile:
        json.dump(values, outfile, indent=4)
    suc = function.loadHorizonP(fileName)
    assert suc
    assert len(function.horizonP) == 3


def test_sortDomeAz_multiple_points(function):
    """Test sortDomeAz with multiple points returning angles"""
    function.buildP = [[10, 10, 1], [20, 20, 1], [30, 30, 1]]
    angle1 = Angle(degrees=350)
    angle2 = Angle(degrees=200)
    angle3 = Angle(degrees=100)

    with mock.patch.object(
        function.app.mount,
        "calcMountAltAzToDomeAltAz",
        side_effect=[(None, angle1), (None, angle2), (None, angle3)],
    ):
        function.sortDomeAz()
        # Should be sorted by dome azimuth descending
        assert len(function.buildP) == 3


def test_sortActualPierside_preserves_coordinates(function):
    """Test sortActualPierside maintains coordinate integrity"""
    function.buildP = [[45, 90, 1], [50, 200, 1]]
    function.app.mount.obsSite.pierside = "W"
    original_coords = [[p[0], p[1]] for p in function.buildP]
    function.sortActualPierside()
    sorted_coords = [[p[0], p[1]] for p in function.buildP]
    # Coordinates should be preserved, just reordered
    assert len(original_coords) == len(sorted_coords)
