# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import glob
import json
import mw4.logic.profiles
import os
import pytest
import yaml
from mw4.logic.profiles.profile import (
    defaultConfig,
    loadConfig,
    loadLegacyConfig,
    loadProfileStart,
    loadYamlConfig,
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
    val = loadConfig(Path("tests/work/config/nonexistent_file.yaml"), None)
    assert val == defaultConfig()


def test_loadProfile_yamlError():
    with (
        mock.patch("builtins.open", mock.mock_open(read_data="data")),
        mock.patch.object(yaml, "safe_load", side_effect=yaml.YAMLError),
    ):
        val = loadConfig(Path("tests/work/config/config.yaml"), None)
    assert val == defaultConfig()


def test_loadYamlConfig_osError():
    assert loadYamlConfig(Path("tests/work/config/nonexistent_file.yaml")) == {}


def test_loadLegacyConfig_osError():
    val = loadLegacyConfig(Path("tests/work/config/nonexistent_file.cfg"), None)
    assert val == {}


def test_loadLegacyConfig_jsonError():
    with open("tests/work/config/bad.cfg", "w") as outfile:
        outfile.write("no json")
    assert loadLegacyConfig(Path("tests/work/config/bad.cfg"), None) == {}
    os.remove("tests/work/config/bad.cfg")


def test_loadLegacyConfig_wrongVersion():
    with open("tests/work/config/old.cfg", "w") as outfile:
        json.dump({"version": "3.0"}, outfile)
    with mock.patch.object(mw4.logic.profiles.profile, "deviceSchemaFromRegistry", return_value={}):
        val = loadLegacyConfig(Path("tests/work/config/old.cfg"), None)
    os.remove("tests/work/config/old.cfg")
    assert val == {}


def test_loadLegacyConfig_valid():
    with open("tests/work/config/old.cfg", "w") as outfile:
        json.dump({"version": "4.1", "profileName": "x"}, outfile)
    with mock.patch.object(mw4.logic.profiles.profile, "deviceSchemaFromRegistry", return_value={}):
        val = loadLegacyConfig(Path("tests/work/config/old.cfg"), None)
    os.remove("tests/work/config/old.cfg")
    assert val["version"] == "5.0"
    assert val["profileName"] == "old"


def test_loadConfig_legacy():
    with mock.patch.object(
        mw4.logic.profiles.profile,
        "loadLegacyConfig",
        return_value={"version": "5.0"},
    ):
        val = loadConfig(Path("tests/work/config/old.cfg"), None)
    assert val == {"version": "5.0", "profileName": "old"}


def test_defaultConfig():
    val = defaultConfig()
    assert val["profileName"] == "config"
    assert val["version"] == "5.0"


def test_loadProfile_1():
    config = defaultConfig()
    config["WindowMain"] = {}
    config["WindowMain"]["resetTabOrder"] = True
    config["WindowMain"]["orderMain"] = {
        "00": "Environ",
        "index": 0,
    }
    with open("tests/work/config/config.yaml", "w") as outfile:
        yaml.dump(config, outfile)

    with mock.patch.object(yaml, "safe_load", return_value={}):
        val = loadConfig(Path("tests/work/config/config.yaml"), None)
        assert val == defaultConfig()


def test_loadProfile_2():
    config = defaultConfig()
    config["WindowMain"] = {}
    config["WindowMain"]["resetTabOrder"] = True
    config["WindowMain"]["orderMain"] = {
        "00": "Environ",
        "index": 0,
    }
    with open("tests/work/config/config.yaml", "w") as outfile:
        yaml.dump(config, outfile)

    val = loadConfig(Path("tests/work/config/config.yaml"), None)
    assert "orderMain" in val["WindowMain"]


def test_loadProfile_3():
    config = defaultConfig()
    config["WindowMain"] = {}
    config["WindowMain"]["resetTabOrder"] = True
    config["WindowMain"]["orderMain"] = {
        "00": "Environ",
        "index": 0,
    }
    config["version"] = "0.0"
    with open("tests/work/config/config.yaml", "w") as outfile:
        yaml.dump(config, outfile)

    val = loadConfig(Path("tests/work/config/config.yaml"), None)
    assert "WindowMain" not in val


def test_loadProfileStart_1():
    val = loadProfileStart(Path("tests/work/config"))
    assert val == defaultConfig()


def test_loadProfileStart_2():
    with open("tests/work/config/profile", "w") as outfile:
        outfile.write("test")

    config = defaultConfig()
    config["WindowMain"] = {}
    with open("tests/work/config/config.yaml", "w") as outfile:
        yaml.dump(config, outfile)

    val = loadProfileStart(Path("tests/work/config"))
    assert val == {"profileName": "config", "version": "5.0"}


def test_loadProfileStart_3():
    with open("tests/work/config/profile", "w") as outfile:
        outfile.write("config")

    config = defaultConfig()
    config["WindowMain"] = {}
    with open("tests/work/config/config.yaml", "w") as outfile:
        yaml.dump(config, outfile)

    with mock.patch.object(
        mw4.logic.profiles.profile, "loadYamlConfig", return_value={"profileName": "config"}
    ):
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
