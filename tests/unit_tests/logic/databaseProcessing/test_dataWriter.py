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
# GUI with PySide
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
import unittest.mock as mock
import os
import json
import shutil
from pathlib import Path

# external packages
from skyfield.api import EarthSatellite

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from logic.databaseProcessing.dataWriter import DataWriter


@pytest.fixture(autouse=True, scope="function")
def function(qapp):
    for file in ["CDFLeapSeconds.txt", "finals.data", "tai-utc.dat"]:
        path = "tests/work/data/" + file
        if os.path.isfile(path):
            os.remove(path)

    window = DataWriter(app=App())
    yield window


def test_writeEarthRotationData_1(function):
    suc = function.writeEarthRotationData(dataFilePath=Path("tests/work/data"))
    assert not suc


def test_writeEarthRotationData_2(function):
    suc = function.writeEarthRotationData(dataFilePath=Path("tests/work/temp"))
    assert not suc


def test_writeEarthRotationData_3(function):
    shutil.copy("tests/testData/CDFLeapSeconds.txt", "tests/work/data/CDFLeapSeconds.txt")
    suc = function.writeEarthRotationData(dataFilePath=Path("tests/work/temp"))
    assert not suc


def test_writeEarthRotationData_4(function):
    shutil.copy("tests/testData/CDFLeapSeconds.txt", "tests/work/data/CDFLeapSeconds.txt")
    shutil.copy("tests/testData/finals.data", "tests/work/data/finals.data")
    suc = function.writeEarthRotationData(dataFilePath=Path("tests/work/temp"))
    assert suc


def test_writeCometMPC_1(function):
    with open("tests/testData/mpc_comet_test.json") as f:
        data = json.load(f)

    testData = [data[0]]
    function.writeCometMPC(datas=testData, dataFilePath=Path("tests/work/temp"))


def test_writeCometMPC_2(function):
    with open("tests/testData/mpc_comet_test.json") as f:
        data = json.load(f)

    testData = [data[0]]
    function.writeCometMPC(datas=testData, dataFilePath=Path("tests/work/temp"))

    with open("tests/work/temp/comets.mpc") as f:
        testLine = f.readline()
    with open("tests/testData/mpc_comet_test.txt") as f:
        refLine = f.readline()
    assert testLine == refLine


def test_writeCometMPC_3(function):
    data = [{"test": "test"}]

    function.writeCometMPC(datas=data, dataFilePath=Path("tests/work/temp"))
    assert os.path.isfile("tests/work/temp/comets.mpc")


def test_generateCycleCountPackedText(function):
    cycles = [
        0,
        1,
        13,
        108,
        127,
        162,
        193,
        360,
        418,
    ]
    texts = ["00", "01", "13", "A8", "C7", "G2", "J3", "a0", "f8"]
    for cycle, text in zip(cycles, texts):
        val = function.generateCycleCountTextPacked(cycle)
        assert val == text


def test_generatePackedDesignation_1(function):
    designations = [
        "1995 XA",
        "1995 XL1",
        "1995 FB13",
        "1998 SQ108",
        "1998 SV127",
        "1998 SS162",
        "2099 AZ193",
        "2008 AA360",
        "2007 TA418",
    ]
    results = [
        "J95X00A",
        "J95X01L",
        "J95F13B",
        "J98SA8Q",
        "J98SC7V",
        "J98SG2S",
        "K99AJ3Z",
        "K08Aa0A",
        "K07Tf8A",
    ]

    for desig, res in zip(designations, results):
        val = function.generateDesignationPacked(desig)
        assert val == res


def test_convertDatePacked(function):
    values = ["01", "10", "30", "01", "22", "99"]
    results = ["1", "A", "U", "1", "M", " "]

    for value, result in zip(values, results):
        val = function.convertDatePacked(value)
        assert val == result


def test_generateDatePacked(function):
    months = ["01", "01", "09", "10", "10"]
    days = ["01", "10", "30", "01", "22"]
    results = ["11", "1A", "9U", "A1", "AM"]

    for mon, day, result in zip(months, days, results):
        val = function.generateDatePacked(mon, day)
        assert val == result


def test_generateEpochPacked(function):
    epoch = 2458600.5
    epochPackedText = "K194R"
    val = function.generateEpochPacked(epoch)
    assert val == epochPackedText


def test_generateOldDesignationPacked_1(function):
    numberTexts = ["(1)", "(100)", "(5986)", "(12345)", "(123456)"]
    results = ["00001  ", "00100  ", "05986  ", "12345  ", "C3456  "]

    for numberText, result in zip(numberTexts, results):
        val = function.generateOldDesignationPacked(numberText)
        assert val == result


def test_generateOldDesignationPacked_2(function):
    val = function.generateOldDesignationPacked("")
    assert val == "xxxxxxx"


def test_writeAsteroidMPC_1(function):
    with open("tests/testData/mpc_asteroid_test.json") as f:
        data = json.load(f)

    testData = [data[0]]
    function.writeAsteroidMPC(datas=testData, dataFilePath=Path("tests/work/temp"))


def test_writeAsteroidMPC_2(function):
    with open("tests/testData/mpc_asteroid_test.json") as f:
        data = json.load(f)

    testData = [data[0]]
    function.writeAsteroidMPC(datas=testData, dataFilePath=Path("tests/work/temp"))

    with open("tests/work/temp/asteroids.mpc") as f:
        testLine = f.readline()
    with open("tests/testData/mpc_asteroid_test.txt") as f:
        refLine = f.readline()
    assert testLine[:202] == refLine[:202]


def test_writeAsteroidMPC_3(function):
    with open("tests/testData/mpc_asteroid_test.json") as f:
        data = json.load(f)

    function.writeAsteroidMPC(datas=data, dataFilePath=Path("tests/work/temp"))

    with open("tests/work/temp/asteroids.mpc") as f:
        testLines = f.readlines()
    with open("tests/testData/mpc_asteroid_test.txt") as f:
        refLines = f.readlines()
    for test, ref in zip(testLines, refLines):
        assert test[0:8] == ref[0:8]
        assert test[14:202] == ref[14:202]


def test_writeAsteroidMPC_4(function):
    with open("tests/testData/nea_extended_test.json") as f:
        data = json.load(f)

    testData = [data[0]]
    function.writeAsteroidMPC(datas=testData, dataFilePath=Path("tests/work/temp"))

    with open("tests/work/temp/asteroids.mpc") as f:
        testLine = f.readline()
    with open("tests/testData/nea_extended_test.txt") as f:
        refLine = f.readline()
    assert testLine[:202] == refLine[:202]


def test_writeAsteroidMPC_5(function):
    with open("tests/testData/nea_extended_test.json") as f:
        data = json.load(f)

    with mock.patch.object(function, "generateEpochPacked", return_value=" 1985"):
        function.writeAsteroidMPC(datas=data, dataFilePath=Path("tests/work/temp"))

    with open("tests/work/temp/asteroids.mpc") as f:
        testLines = f.readlines()
    with open("tests/testData/nea_extended_test.txt") as f:
        refLines = f.readlines()
    for test, ref in zip(testLines, refLines):
        if ref[0:3] in ["PLS"]:
            continue
        assert test[0:7] == ref[0:7]
        assert test[21:140] == ref[21:140]
        assert test[142:167] == ref[142:167]


def test_writeAsteroidMPC_6(function):
    data = [{}]

    function.writeAsteroidMPC(datas=data, dataFilePath=Path("tests/work/temp"))
    assert os.path.isfile("tests/work/temp/asteroids.mpc")


def test_writeSatelliteTLE_1(function):
    tle = [
        "NOAA 8",
        "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
        "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954",
    ]
    data = [EarthSatellite(tle[1], tle[2], name=tle[0])]
    function.writeSatelliteTLE(datas=data, dataFilePath=Path("tests/work/temp"))

    with open("tests/work/temp/satellites.tle") as f:
        refLines = f.readlines()

    assert tle[0] == refLines[0].strip("\n")
    assert tle[1] == refLines[1].strip("\n")
    assert tle[2] == refLines[2].strip("\n")


def t_writeSatelliteTLE_2(function):
    tle = [
        "BEIDOU-3 M23",
        "1 44542U 19061A   21180.78220369 -.00000015  00000-0 -66561+1 0  9997",
        "2 44542  54.7025 244.1098 0007981 318.8601 283.5781  1.86231125 12011",
    ]
    data = [EarthSatellite(tle[1], tle[2], name=tle[0])]
    function.writeSatelliteTLE(datas=data, dataFilePath=Path("tests/work/temp"))

    with open("tests/work/temp/satellites.tle") as f:
        refLines = f.readlines()

    assert tle[0] == refLines[0].strip("\n")
    assert tle[1] == refLines[1].strip("\n")
    assert tle[2] == refLines[2].strip("\n")
