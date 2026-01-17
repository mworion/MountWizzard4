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
import yaml
import os
import pytest
import unittest.mock as mock
from mw4.logic.profiles.profile import (
    defaultConfig,
    loadConfig,
    loadProfileStart,
    saveConfig,
)
import mw4.logic.profiles
from pathlib import Path


@pytest.fixture(autouse=True, scope="function")
def setup():
    files = glob.glob("tests/work/config/*.yaml")
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
    config = defaultConfig()
    config["mainW"] = {}
    config["mainW"]["resetTabOrder"] = True
    config["mainW"]["orderMain"] = {
        "00": "Environ",
        "index": 0,
    }
    with open("tests/work/config/config.yaml", "w") as outfile:
        yaml.dump(config, outfile)

    with mock.patch.object(yaml, "safe_load", return_value={}):
        val = loadConfig(Path("tests/work/config/config.yaml"))
        assert val == defaultConfig()


def test_loadProfile_2():
    config = defaultConfig()
    config["mainW"] = {}
    config["mainW"]["resetTabOrder"] = True
    config["mainW"]["orderMain"] = {
        "00": "Environ",
        "index": 0,
    }
    with open("tests/work/config/config.yaml", "w") as outfile:
        yaml.dump(config, outfile)

    val = loadConfig(Path("tests/work/config/config.yaml"))
    assert 'orderMain' in val['mainW']


def test_loadProfile_3():
    config = defaultConfig()
    config["mainW"] = {}
    config["mainW"]["resetTabOrder"] = True
    config["mainW"]["orderMain"] = {
        "00": "Environ",
        "index": 0,
    }
    config["version"] = "0.0"
    with open("tests/work/config/config.yaml", "w") as outfile:
        yaml.dump(config, outfile)

    val = loadConfig(Path("tests/work/config/config.yaml"))
    assert 'mainW' not in val


def test_loadProfileStart_1():
    val = loadProfileStart(Path("tests/work/config"))
    assert val == defaultConfig()


def test_loadProfileStart_2():
    with open("tests/work/config/profile", "w") as outfile:
        outfile.write("test")

    config = defaultConfig()
    config["mainW"] = {}
    with open("tests/work/config/config.yaml", "w") as outfile:
        yaml.dump(config, outfile)

    val = loadProfileStart(Path("tests/work/config"))
    assert val == {"profileName": "config", "version": "4.3"}


def test_loadProfileStart_3():
    with open("tests/work/config/profile", "w") as outfile:
        outfile.write("config")

    config = defaultConfig()
    config["mainW"] = {}
    with open("tests/work/config/config.yaml", "w") as outfile:
        yaml.dump(config, outfile)

    with mock.patch.object(mw4.logic.profiles.profile, "loadConfig", return_value={"profileName": "config"}):
        val = loadProfileStart(Path("tests/work/config"))
    assert val == {"profileName": "config"}


def test_saveProfile_1():
    config = {"profileName": "config"}

    saveConfig(Path("tests/work/config/config.yaml"), config)
    assert os.path.isfile("tests/work/config/config.yaml")
    assert os.path.isfile("tests/work/config/profile")
    with open("tests/work/config/profile") as infile:
        name = infile.readline().strip()
    assert name == "config"


def test_saveProfile_2():
    config = {"profileName": "config"}

    saveConfig(Path("tests/work/config/config.yaml"), config)
    assert os.path.isfile("tests/work/config/config.yaml")
    assert os.path.isfile("tests/work/config/profile")
    with open("tests/work/config/profile") as infile:
        name = infile.readline().strip()
    assert name == "config"


def test_saveProfile_3():
    config = {"profileName": "new"}

    saveConfig(Path("tests/work/config/new.yaml"), config)
    assert os.path.isfile("tests/work/config/new.yaml")
    assert os.path.isfile("tests/work/config/profile")
    with open("tests/work/config/profile") as infile:
        name = infile.readline().strip()
    assert name == "new"


def test_saveProfile_4():
    saveConfig(Path("tests/work/config/config.yaml"), defaultConfig())
    assert os.path.isfile("tests/work/config/config.yaml")
    assert os.path.isfile("tests/work/config/profile")
    with open("tests/work/config/profile") as infile:
        name = infile.readline().strip()
    assert name == "config"


def test_saveProfile_5():
    saveConfig(Path("tests/work/config/new.yaml"), defaultConfig())
    assert os.path.isfile("tests/work/config/new.yaml")
    assert os.path.isfile("tests/work/config/profile")
    with open("tests/work/config/profile") as infile:
        name = infile.readline().strip()
    assert name == "new"
