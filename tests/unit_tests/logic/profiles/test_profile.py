# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import glob
import mw4.logic.profiles
import os
import pytest
import yaml
from mw4.logic.profiles.profile import (
    defaultConfig,
    loadConfig,
    loadProfileStart,
    saveConfig,
)
from pathlib import Path
from unittest import mock


@pytest.fixture(autouse=True, scope="module")
def setup():
    cleanConfigFiles()


@pytest.fixture(autouse=True)
def resetConfigFiles():
    cleanConfigFiles()


def cleanConfigFiles():
    files = glob.glob("tests/work/config/*.yaml")
    for f in files:
        os.remove(f)
    f = "tests/work/config/profile"
    if os.path.isfile(f):
        os.remove(f)


def test_loadProfile_osError():
    val = loadConfig(Path("tests/work/config/nonexistent_file.yaml"))
    assert val == defaultConfig()


def test_loadProfile_yamlError():
    with (
        mock.patch("builtins.open", mock.mock_open(read_data="data")),
        mock.patch.object(yaml, "safe_load", side_effect=yaml.YAMLError),
    ):
        val = loadConfig(Path("tests/work/config/config.yaml"))
    assert val == defaultConfig()


def test_defaultConfig():
    val = defaultConfig()
    assert val["profileName"] == "config"
    assert val["version"] == "5.0"


def test_loadProfile_1():
    config = defaultConfig()
    config["WindowKeypad"] = {}
    config["WindowKeypad"]["resetTabOrder"] = True
    config["WindowKeypad"]["orderMain"] = {
        "00": "Environ",
        "index": 0,
    }
    with open("tests/work/config/config.yaml", "w") as outfile:
        yaml.dump(config.toDict(), outfile)

    with mock.patch.object(yaml, "safe_load", return_value={}):
        val = loadConfig(Path("tests/work/config/config.yaml"))
        assert val == defaultConfig()


def test_loadProfile_2():
    config = defaultConfig()
    config["WindowKeypad"] = {}
    config["WindowKeypad"]["resetTabOrder"] = True
    config["WindowKeypad"]["orderMain"] = {
        "00": "Environ",
        "index": 0,
    }
    with open("tests/work/config/config.yaml", "w") as outfile:
        yaml.dump(config.toDict(), outfile)

    val = loadConfig(Path("tests/work/config/config.yaml"))
    assert "orderMain" in val["WindowKeypad"]


def test_loadProfile_3():
    config = defaultConfig()
    config["WindowKeypad"] = {}
    config["WindowKeypad"]["resetTabOrder"] = True
    config["WindowKeypad"]["orderMain"] = {
        "00": "Environ",
        "index": 0,
    }
    config["version"] = "0.0"
    with open("tests/work/config/config.yaml", "w") as outfile:
        yaml.dump(config.toDict(), outfile)

    val = loadConfig(Path("tests/work/config/config.yaml"))
    assert "WindowKeypad" not in val


def test_loadProfileStart_1():
    val = loadProfileStart(Path("tests/work/config"))
    assert val == defaultConfig()


def test_loadProfileStart_2():
    with open("tests/work/config/profile", "w") as outfile:
        outfile.write("test")

    config = defaultConfig()
    config["WindowKeypad"] = {}
    with open("tests/work/config/config.yaml", "w") as outfile:
        yaml.dump(config.toDict(), outfile)

    val = loadProfileStart(Path("tests/work/config"))
    assert val == defaultConfig()


def test_loadProfileStart_3():
    with open("tests/work/config/profile", "w") as outfile:
        outfile.write("config")

    config = defaultConfig()
    config["WindowKeypad"] = {}
    with open("tests/work/config/config.yaml", "w") as outfile:
        yaml.dump(config.toDict(), outfile)

    with mock.patch.object(mw4.logic.profiles.profile, "loadConfig", return_value=defaultConfig()):
        val = loadProfileStart(Path("tests/work/config"))
    assert val == defaultConfig()


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


def test_loadProfile_notDict():
    with open("tests/work/config/config.yaml", "w") as outfile:
        outfile.write("- a\n- b\n")
    val = loadConfig(Path("tests/work/config/config.yaml"))
    assert val == defaultConfig()


def test_saveLoad_roundTrip():
    config = defaultConfig()
    config["WindowKeypad"] = {"winPosX": 3}
    config.SettingGui.dpi = 120.0
    saveConfig(Path("tests/work/config/rt.yaml"), config)
    val = loadConfig(Path("tests/work/config/rt.yaml"))
    assert val["WindowKeypad"] == {"winPosX": 3}
    assert val.SettingGui.dpi == 120.0
    assert val.profileName == "rt"
