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
#
# written in python3, (c) 2019-2023 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
import unittest.mock as mock
import os
import json
import shutil

# external packages
from skyfield.api import EarthSatellite

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from logic.databaseProcessing.dataWriter import DataWriter


@pytest.fixture(autouse=True, scope='function')
def function(qapp):
    for file in ['CDFLeapSeconds.txt', 'finals.data', 'tai-utc.dat']:
        path = 'tests/workDir/data/' + file
        if os.path.isfile(path):
            os.remove(path)

    window = DataWriter(app=App())
    yield window


def test_writeEarthRotationData_1(function):
    suc = function.writeEarthRotationData(installPath='tests/workDir/data')
    assert not suc


def test_writeEarthRotationData_2(function):
    suc = function.writeEarthRotationData(installPath='tests/workDir/temp')
    assert not suc


def test_writeEarthRotationData_3(function):
    shutil.copy('tests/testData/CDFLeapSeconds.txt', 'tests/workDir/data/CDFLeapSeconds.txt')
    suc = function.writeEarthRotationData(installPath='tests/workDir/temp')
    assert not suc


def test_writeEarthRotationData_4(function):
    shutil.copy('tests/testData/CDFLeapSeconds.txt', 'tests/workDir/data/CDFLeapSeconds.txt')
    shutil.copy('tests/testData/finals.data', 'tests/workDir/data/finals.data')
    suc = function.writeEarthRotationData(installPath='tests/workDir/temp')
    assert not suc


def test_writeEarthRotationData_5(function):
    shutil.copy('tests/testData/CDFLeapSeconds.txt', 'tests/workDir/data/CDFLeapSeconds.txt')
    shutil.copy('tests/testData/tai-utc.dat', 'tests/workDir/data/tai-utc.dat')
    shutil.copy('tests/testData/finals.data', 'tests/workDir/data/finals.data')
    suc = function.writeEarthRotationData(installPath='tests/workDir/temp',
                                          updaterApp='tenmicron_v2.exe')
    assert suc


def test_writeEarthRotationData_6(function):
    shutil.copy('tests/testData/CDFLeapSeconds.txt', 'tests/workDir/data/CDFLeapSeconds.txt')
    shutil.copy('tests/testData/tai-utc.dat', 'tests/workDir/data/tai-utc.dat')
    shutil.copy('tests/testData/finals.data', 'tests/workDir/data/finals.data')
    suc = function.writeEarthRotationData(installPath='tests/workDir/temp')
    assert suc


def test_writeCometMPC_1(function):
    suc = function.writeCometMPC()
    assert not suc


def test_writeCometMPC_2(function):
    data = {'test': 'test'}

    suc = function.writeCometMPC(datas=data, installPath='tests/workDir/temp')
    assert not suc


def test_writeCometMPC_3(function):
    data = [{'test': 'test'}]

    suc = function.writeCometMPC(datas=data, installPath='tests/workDir/temp')
    assert suc
    assert os.path.isfile('tests/workDir/temp/minorPlanets.mpc')


def test_writeCometMPC_4(function):
    with open('tests/testData/mpc_comet_test.json') as f:
        data = json.load(f)

    testData = [data[0]]

    suc = function.writeCometMPC(datas=testData, installPath='tests/workDir/temp')
    assert suc


def test_writeCometMPC_5(function):
    with open('tests/testData/mpc_comet_test.json') as f:
        data = json.load(f)

    testData = [data[0]]

    suc = function.writeCometMPC(datas=testData, installPath='tests/workDir/temp')
    assert suc

    with open('tests/workDir/temp/minorPlanets.mpc', 'r') as f:
        testLine = f.readline()

    with open('tests/testData/mpc_comet_test.txt', 'r') as f:
        refLine = f.readline()

    assert testLine == refLine


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
    texts = [
        '00',
        '01',
        '13',
        'A8',
        'C7',
        'G2',
        'J3',
        'a0',
        'f8'
    ]
    for cycle, text in zip(cycles, texts):
        val = function.generateCycleCountTextPacked(cycle)
        assert val == text


def test_generatePackedDesignation_1(function):
    designations = [
        '1995 XA',
        '1995 XL1',
        '1995 FB13',
        '1998 SQ108',
        '1998 SV127',
        '1998 SS162',
        '2099 AZ193',
        '2008 AA360',
        '2007 TA418'
    ]
    results = [
        'J95X00A',
        'J95X01L',
        'J95F13B',
        'J98SA8Q',
        'J98SC7V',
        'J98SG2S',
        'K99AJ3Z',
        'K08Aa0A',
        'K07Tf8A'
    ]

    for desig, res in zip(designations, results):
        val = function.generateDesignationPacked(desig)
        assert val == res


def test_convertDatePacked(function):
    values = ['01', '10', '30', '01', '22', '99']
    results = ['1', 'A', 'U', '1', 'M', ' ']

    for value, result in zip(values, results):
        val = function.convertDatePacked(value)
        assert val == result


def test_generateDatePacked(function):

    months = ['01', '01', '09', '10', '10']
    days = ['01', '10', '30', '01', '22']
    results = ['11', '1A', '9U', 'A1', 'AM']

    for mon, day, result in zip(months, days, results):
        val = function.generateDatePacked(mon, day)
        assert val == result


def test_generateEpochPacked(function):
    epoch = 2458600.5
    epochPackedText = 'K194R'
    val = function.generateEpochPacked(epoch)
    assert val == epochPackedText


def test_generateOldDesignationPacked_1(function):
    numberTexts = ['(1)', '(100)', '(5986)', '(12345)', '(123456)']
    results = ['00001  ', '00100  ', '05986  ', '12345  ', 'C3456  ']

    for numberText, result in zip(numberTexts, results):
        val = function.generateOldDesignationPacked(numberText)
        assert val == result


def test_generateOldDesignationPacked_2(function):
    val = function.generateOldDesignationPacked('')
    assert val == 'xxxxxxx'


def test_writeAsteroidMPC_1(function):
    suc = function.writeAsteroidMPC()
    assert not suc


def test_writeAsteroidMPC_2(function):
    data = {'Principal_desig': '2016 NU22'}

    suc = function.writeAsteroidMPC(datas=data, installPath='tests/workDir/temp')
    assert not suc


def test_writeAsteroidMPC_3(function):
    data = [{}]

    suc = function.writeAsteroidMPC(datas=data, installPath='tests/workDir/temp')
    assert suc
    assert os.path.isfile('tests/workDir/temp/minorPlanets.mpc')


def test_writeAsteroidMPC_4(function):
    with open('tests/testData/mpc_asteroid_test.json') as f:
        data = json.load(f)

    testData = [data[0]]

    suc = function.writeAsteroidMPC(datas=testData, installPath='tests/workDir/temp')
    assert suc


def test_writeAsteroidMPC_5(function):
    with open('tests/testData/mpc_asteroid_test.json') as f:
        data = json.load(f)

    testData = [data[0]]

    suc = function.writeAsteroidMPC(datas=testData, installPath='tests/workDir/temp')
    assert suc

    with open('tests/workDir/temp/minorPlanets.mpc', 'r') as f:
        testLine = f.readline()

    with open('tests/testData/mpc_asteroid_test.txt', 'r') as f:
        refLine = f.readline()

    assert testLine[:202] == refLine[:202]


def test_writeAsteroidMPC_6(function):
    with open('tests/testData/mpc_asteroid_test.json') as f:
        data = json.load(f)

    suc = function.writeAsteroidMPC(datas=data, installPath='tests/workDir/temp')
    assert suc

    with open('tests/workDir/temp/minorPlanets.mpc', 'r') as f:
        testLines = f.readlines()

    with open('tests/testData/mpc_asteroid_test.txt', 'r') as f:
        refLines = f.readlines()

    for test, ref in zip(testLines, refLines):
        assert test[0:8] == ref[0:8]
        assert test[14:202] == ref[14:202]


def test_writeAsteroidMPC_7(function):
    with open('tests/testData/nea_extended_test.json') as f:
        data = json.load(f)

    testData = [data[0]]

    suc = function.writeAsteroidMPC(datas=testData, installPath='tests/workDir/temp')
    assert suc

    with open('tests/workDir/temp/minorPlanets.mpc', 'r') as f:
        testLine = f.readline()

    with open('tests/testData/nea_extended_test.txt', 'r') as f:
        refLine = f.readline()

    assert testLine[:202] == refLine[:202]


def test_writeAsteroidMPC_8(function):
    with open('tests/testData/nea_extended_test.json') as f:
        data = json.load(f)

    with mock.patch.object(function,
                           'generateEpochPacked',
                           return_value=' 1985'):
        suc = function.writeAsteroidMPC(datas=data, installPath='tests/workDir/temp')
        assert suc

    with open('tests/workDir/temp/minorPlanets.mpc', 'r') as f:
        testLines = f.readlines()

    with open('tests/testData/nea_extended_test.txt', 'r') as f:
        refLines = f.readlines()

    for test, ref in zip(testLines, refLines):
        if ref[0:3] in ['PLS']:
            continue

        assert test[0:7] == ref[0:7]
        assert test[21:140] == ref[21:140]
        assert test[142:167] == ref[142:167]


def test_writeSatelliteTLE_1(function):
    data = None
    suc = function.writeSatelliteTLE(datas=data, installPath='tests/workDir/temp')
    assert not suc


def test_writeSatelliteTLE_2(function):
    data = 'test'
    suc = function.writeSatelliteTLE(datas=data, installPath='tests/workDir/temp')
    assert not suc


def test_writeSatelliteTLE_3(function):
    tle = ["NOAA 8",
           "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
           "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954"]
    data = {'NOAA 8': EarthSatellite(tle[1], tle[2],  name=tle[0])}
    suc = function.writeSatelliteTLE(datas=data, installPath='tests/workDir/temp')
    assert suc

    with open('tests/workDir/temp/satellites.tle', 'r') as f:
        refLines = f.readlines()

    assert tle[0] == refLines[0].strip('\n')
    assert tle[1] == refLines[1].strip('\n')
    assert tle[2] == refLines[2].strip('\n')


def t_writeSatelliteTLE_4(function):
    tle = ["BEIDOU-3 M23",
           "1 44542U 19061A   21180.78220369 -.00000015  00000-0 -66561+1 0  9997",
           "2 44542  54.7025 244.1098 0007981 318.8601 283.5781  1.86231125 12011"]
    data = {'BEIDOU-3 M23': EarthSatellite(tle[1], tle[2],  name=tle[0])}
    suc = function.writeSatelliteTLE(datas=data, installPath='tests/workDir/temp')
    assert suc

    with open('tests/workDir/temp/satellites.tle', 'r') as f:
        refLines = f.readlines()

    assert tle[0] == refLines[0].strip('\n')
    assert tle[1] == refLines[1].strip('\n')
    assert tle[2] == refLines[2].strip('\n')
