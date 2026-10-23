# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import pytest
from mw4.logic.profiles.config import (
    MountParkConfig,
    ProfileConfig,
    SettingGuiConfig,
    SettingUpdateConfig,
    coerceValue,
)


def test_coerceValue():
    assert coerceValue("a", 2, 1.0) == 2
    assert coerceValue("a", 2.5, 1) == 2.5
    assert coerceValue("a", True, False) is True
    assert coerceValue("a", 3, 1) == 3
    assert coerceValue("a", "x", 1) == 1
    assert coerceValue("a", True, 1) == 1
    assert coerceValue("a", 1, False) is False
    assert coerceValue("a", True, 1.0) == 1.0


def test_section_fromDict_defaults():
    section = SettingUpdateConfig.fromDict(None)
    assert section.loglevelDebug is True
    assert section.ageDatabases == 1.0
    assert SettingUpdateConfig.fromDict("wrong") == SettingUpdateConfig()


def test_section_fromDict_valuesAndExtra():
    section = SettingGuiConfig.fromDict({"colorSet": 2, "dpi": 120, "other": 5, "scale": "x"})
    assert section.colorSet == 2
    assert section.dpi == 120.0
    assert section.scale == 1.0
    assert section.extra == {"other": 5}
    assert section.toDict() == {
        "colorSet": 2,
        "transparency": 1.0,
        "scale": 1.0,
        "dpi": 120.0,
        "other": 5,
    }


def test_section_dictAccess():
    section = MountParkConfig()
    assert section["ParkMountAfterSlew"] is False
    assert section.get("ParkMountAfterSlew", True) is False
    assert section.get("unknown", 3) == 3
    assert "ParkMountAfterSlew" in section
    assert "unknown" not in section
    section["unknown"] = 4
    assert section["unknown"] == 4
    assert "unknown" in section
    assert section.setdefault("unknown", 9) == 4
    assert section.setdefault("another", 9) == 9
    section["ParkMountAfterSlew"] = True
    assert section.pop("ParkMountAfterSlew") is True
    assert section.ParkMountAfterSlew is False
    assert section.pop("another") == 9
    assert section.pop("another", None) is None
    with pytest.raises(KeyError):
        section.pop("another")
    with pytest.raises(KeyError):
        section["another"]


def test_profile_roundTrip():
    data = {
        "profileName": "x",
        "version": "5.0",
        "topoLat": 40,
        "MountPark": {"ParkMountAfterSlew": True},
        "SettingUpdate": {"isOnline": True},
        "WindowKeypad": {"winPosX": 5},
        "loose": 1,
    }
    config = ProfileConfig.fromDict(data)
    assert config.topoLat == 40.0
    assert config.MountPark.ParkMountAfterSlew is True
    assert config["WindowKeypad"] == {"winPosX": 5}
    assert config.get("loose") == 1
    out = config.toDict()
    assert out["WindowKeypad"] == {"winPosX": 5}
    assert out["loose"] == 1
    assert out["MountPark"] == {"ParkMountAfterSlew": True}
    assert ProfileConfig.fromDict(out) == config


def test_profile_setSection():
    config = ProfileConfig()
    config["MountPark"] = {"ParkMountAfterSlew": True}
    assert isinstance(config.MountPark, MountParkConfig)
    assert config.MountPark.ParkMountAfterSlew is True
    sentinel = object()
    config["SettingGui"] = sentinel
    assert config["SettingGui"] is sentinel
    config["topoLat"] = "bad"
    assert config.topoLat == 51.47
    config["topoLat"] = 10.0
    assert config.topoLat == 10.0
    assert config.pop("topoLat") == 10.0
    assert config.topoLat == 51.47


def test_profile_typedWindowMainKeepsDynamicKeys():
    config = ProfileConfig.fromDict(
        {"WindowMain": {"targetRMS": 12.5, "winPosX": 7, "orderMain": {"index": 1}}}
    )
    assert config.WindowMain.targetRMS == 12.5
    assert config.WindowMain.altitudeMin == 30
    out = config.toDict()["WindowMain"]
    assert out["winPosX"] == 7
    assert out["orderMain"] == {"index": 1}
