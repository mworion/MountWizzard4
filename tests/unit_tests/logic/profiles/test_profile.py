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
# Licence APL2.0
#
###########################################################
import glob
import json
import os
import pytest
import unittest.mock as mock

from mw4.logic.profiles.profile import (
    defaultConfig,
    loadProfile,
    loadProfileStart,
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


def test_defaultConfig():
    val = defaultConfig()
    assert val["profileName"] == "config"
    assert val["version"] == "4.3"


def test_loadProfile_1():
    val = loadProfile(Path("tests/work/config"))
    assert val == {"profileName": "config", "version": "4.3"}


def test_loadProfile_2():
    with open("tests/work/config/profile", "w") as outfile:
        outfile.write("config")

    config = defaultConfig()
    config["mainW"] = {}
    config["version"] = "4.0"
    with open("tests/work/config/config.cfg", "w") as outfile:
        json.dump(config, outfile)

    val = loadProfile(Path("tests/work/config/config.cfg"))
    assert val == {"profileName": "config", "version": "4.3"}


def test_loadProfile_3():
    with open("tests/work/config/profile", "w") as outfile:
        outfile.write("config")

    val = loadProfile(Path("tests/work/config/config.cfg"))
    assert val == {"profileName": "config", "version": "4.3"}


def test_loadProfile_4():
    with open("tests/work/config/profile", "w") as outfile:
        outfile.write("config")
    config = defaultConfig()

    with open("tests/work/config/config.cfg", "w") as outfile:
        json.dump(config, outfile)

    with mock.patch.object(json, "load", side_effect=Exception()):
        val = loadProfile(Path("tests/work/config/config.cfg"))
        assert val == {"profileName": "config", "version": "4.3"}


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
    assert val == {"profileName": "config", "version": "4.3"}


def test_loadProfileStart_3():
    with open("tests/work/config/profile", "w") as outfile:
        outfile.write("config")

    config = defaultConfig()
    config["mainW"] = {}
    with open("tests/work/config/config.cfg", "w") as outfile:
        json.dump(config, outfile)

    val = loadProfileStart(Path("tests/work/config"))
    assert val == {"profileName": "config", "version": "4.3", "mainW": {}}


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
