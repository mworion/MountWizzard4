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

import glob
import json
import os
import pytest
import unittest.mock as mock
from mw4.logic.profiles.profile import (
    blendProfile,
    checkResetTabOrder,
    convertKeyData,
    convertProfileData40to41,
    convertProfileData41to42,
    defaultConfig,
    loadProfile,
    loadProfileStart,
    replaceKeys,
    saveProfile,
)
from pathlib import Path


@pytest.fixture(autouse=True, scope="function")
def setup():
    files = glob.glob("tests/work/config/*.cfg")
    for f in files:
        os.remove(f)
    f = "tests/work/config/profile"
    if os.path.isfile(f):
        os.remove(f)


def test_replaceKeys():
    keyDict = {"old": "new"}
    data = {
        "test": {
            "out": {
                "old": 10,
            }
        }
    }
    val = replaceKeys(data, keyDict)
    assert "new" in val["test"]["out"]


def test_convertKeyData():
    i = {"checkASCOMAutoConnect": "test"}
    r = convertKeyData(i)
    assert "checkASCOMAutoConnect" not in r
    assert "autoConnectASCOM" in r


def test_convertProfileData40to41_1():
    data = {"version": "4.1"}
    val = convertProfileData40to41(data)
    assert val["version"] == "4.1"


def test_convertProfileData40to41_2():
    data = {"version": "4.0"}
    val = convertProfileData40to41(data)
    assert val["version"] == "4.0"


def test_convertProfileData40to41_3():
    data = {
        "version": "4.0",
        "hemisphereW": {},
        "mainW": {
            "horizonFileName": "test",
            "driversData": {
                "astrometry": {"test1": 1, "test2": 2},
                "directWeather": {"frameworks": {"internal": {"deviceName": "Direct"}}},
            },
        },
    }
    val = convertProfileData40to41(data)
    assert val["version"] == "4.1"
    assert "driversData" in val
    assert "driversData" not in val["mainW"]
    assert "astrometry" not in val["driversData"]
    assert "plateSolve" in val["driversData"]
    assert "directWeather" in val["driversData"]["directWeather"]["frameworks"]
    assert "internal" not in val["driversData"]["directWeather"]["frameworks"]
    t = val["driversData"]["directWeather"]["frameworks"]
    assert "On Mount" in t["directWeather"]["deviceName"]
    assert "Direct" not in t["directWeather"]["deviceName"]


def test_convertProfileData41to42_1():
    data = {"version": "4.2"}
    val = convertProfileData41to42(data)
    assert val["version"] == "4.2"


def test_convertProfileData41to42_2():
    data = {"version": "4.1"}
    val = convertProfileData41to42(data)
    assert val["version"] == "4.1"


def test_convertProfileData41to42_3():
    data = {
        "version": "4.1",
        "driversData": {
            "sensorWeather": {"frameworks": {"internal": {"deviceName": "Direct"}}},
            "powerWeather": {"frameworks": {"internal": {"deviceName": "Direct"}}},
            "skymeter": {"frameworks": {"internal": {"deviceName": "Direct"}}},
        },
    }
    val = convertProfileData41to42(data)
    assert val["version"] == "4.2"
    assert "sensorWeather" not in val["driversData"]
    assert "powerWeather" not in val["driversData"]
    assert "skymeter" not in val["driversData"]
    assert "sensor1Weather" in val["driversData"]
    assert "sensor2Weather" in val["driversData"]
    assert "sensor3Weather" in val["driversData"]


def test_convertProfileData40to41_4():
    data = {"mainW": "4.0"}
    val = convertProfileData40to41(data)
    assert val["mainW"] == "4.0"


def test_blendProfile():
    conf = blendProfile({}, {})
    assert conf == {}


def test_defaultConfig():
    val = defaultConfig()
    assert val["profileName"] == "config"
    assert val["version"] == "4.2"


def test_checkResetTabOrder_1():
    test = {
        "order": {},
    }
    val = checkResetTabOrder(test)
    assert val == {}


def test_checkResetTabOrder_2():
    test = {
        "test": {
            "order": {},
        },
    }
    val = checkResetTabOrder(test)
    assert val == {"test": {}}


def test_loadProfile_1():
    val = loadProfile(Path("tests/work/config"))
    assert val == {"profileName": "config", "version": "4.2"}


def test_loadProfile_2():
    with open("tests/work/config/profile", "w") as outfile:
        outfile.write("config")

    config = defaultConfig()
    config["mainW"] = {}
    with open("tests/work/config/config.cfg", "w") as outfile:
        json.dump(config, outfile)

    val = loadProfile(Path("tests/work/config/config.cfg"))
    assert val == {"profileName": "config", "version": "4.2", "mainW": {}}


def test_loadProfile_3():
    with open("tests/work/config/profile", "w") as outfile:
        outfile.write("config")

    val = loadProfile(Path("tests/work/config/config.cfg"))
    assert val == {"profileName": "config", "version": "4.2"}


def test_loadProfile_4():
    with open("tests/work/config/profile", "w") as outfile:
        outfile.write("config")
    config = defaultConfig()

    with open("tests/work/config/config.cfg", "w") as outfile:
        json.dump(config, outfile)

    with mock.patch.object(json, "load", side_effect=Exception()):
        val = loadProfile(Path("tests/work/config/config.cfg"))
        assert val == {"profileName": "config", "version": "4.2"}


def test_loadProfile_5():
    with open("tests/work/config/profile", "w") as outfile:
        outfile.write("config")
    config = defaultConfig()
    config["mainW"] = {}
    config["mainW"]["resetTabOrder"] = True
    config["mainW"]["orderMain"] = {
        "00": "Environ",
        "index": 0,
    }

    with open("tests/work/config/config.cfg", "w") as outfile:
        json.dump(config, outfile)

    val = loadProfile(Path("tests/work/config/config.cfg"))
    assert "oderMain" not in list(val["mainW"].keys())


def test_loadProfileStart_1():
    val = loadProfileStart(Path("tests/work/config"))
    assert val == defaultConfig()


def test_loadProfileStart_2():
    with open("tests/work/config/profile", "w") as outfile:
        outfile.write("test")

    config = defaultConfig()
    config["mainW"] = {}
    with open("tests/work/config/config.cfg", "w") as outfile:
        json.dump(config, outfile)

    val = loadProfileStart(Path("tests/work/config"))
    assert val == {"profileName": "config", "version": "4.2"}


def test_loadProfileStart_3():
    with open("tests/work/config/profile", "w") as outfile:
        outfile.write("config")

    config = defaultConfig()
    config["mainW"] = {}
    with open("tests/work/config/config.cfg", "w") as outfile:
        json.dump(config, outfile)

    val = loadProfileStart(Path("tests/work/config"))
    assert val == {"profileName": "config", "version": "4.2", "mainW": {}}


def test_saveProfile_1():
    config = {"profileName": "config"}

    saveProfile(Path("tests/work/config/config.cfg"), config)
    assert os.path.isfile("tests/work/config/config.cfg")
    assert os.path.isfile("tests/work/config/profile")
    with open("tests/work/config/profile") as infile:
        name = infile.readline().strip()
    assert name == "config"


def test_saveProfile_2():
    config = {"profileName": "config"}

    saveProfile(Path("tests/work/config/config.cfg"), config)
    assert os.path.isfile("tests/work/config/config.cfg")
    assert os.path.isfile("tests/work/config/profile")
    with open("tests/work/config/profile") as infile:
        name = infile.readline().strip()
    assert name == "config"


def test_saveProfile_3():
    config = {"profileName": "new"}

    saveProfile(Path("tests/work/config/new.cfg"), config)
    assert os.path.isfile("tests/work/config/new.cfg")
    assert os.path.isfile("tests/work/config/profile")
    with open("tests/work/config/profile") as infile:
        name = infile.readline().strip()
    assert name == "new"


def test_saveProfile_4():
    saveProfile(Path("tests/work/config/config.cfg"), defaultConfig())
    assert os.path.isfile("tests/work/config/config.cfg")
    assert os.path.isfile("tests/work/config/profile")
    with open("tests/work/config/profile") as infile:
        name = infile.readline().strip()
    assert name == "config"


def test_saveProfile_5():
    saveProfile(Path("tests/work/config/new.cfg"), defaultConfig())
    assert os.path.isfile("tests/work/config/new.cfg")
    assert os.path.isfile("tests/work/config/profile")
    with open("tests/work/config/profile") as infile:
        name = infile.readline().strip()
    assert name == "new"
