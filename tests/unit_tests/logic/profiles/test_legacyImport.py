import pytest
from dataclasses import dataclass
from mw4.logic.profiles.legacyImport import (
    TARGET_PROFILE_VERSION,
    deviceSchemaFromRegistry,
    migrateLegacyConfig,
)
from types import SimpleNamespace


def schema():
    return {
        "mount": {
            "10micron": {
                "hostAddress",
                "MAC",
                "wolAddress",
                "wolPort",
                "wolAutomatic",
                "syncTimeCont",
                "syncTimeNone",
                "syncTimeNotTrack",
                "port",
            }
        },
        "camera": {
            "alpaca": {
                "apiVersion",
                "deviceName",
                "hostAddress",
                "loadConfig",
                "number",
                "port",
                "protocol",
            },
            "ascom": {"deviceName"},
        },
        "plateSolve": {"astap": {"appPath", "deviceName", "indexPath", "searchRadius", "timeout"}},
    }


def legacy(name="Old"):
    return {
        "version": "4.1",
        "profileName": name,
        "mainW": {
            "mountHost": "10.0.0.50",
            "mountMAC": "00:11:22:33:44:55",
            "port3492": True,
            "focalLength": 2563,
            "posText0": "Park East",
            "posAlt0": 0.0,
            "posAz0": 1.0,
            "buildPFileName": "DCRP3",
        },
        "hemisphereW": {
            "horizonMaskFileName": "DCRP-Meassured",
        },
        "driversData": {
            "camera": {
                "framework": "nina",
                "frameworks": {"ascom": {"deviceName": "Camera"}},
            },
            "plateSolve": {
                "framework": "astap",
                "frameworks": {
                    "astap": {
                        "appPath": "C:/ASTAP",
                        "deviceName": "ASTAP",
                        "indexPath": "C:/ASTAP",
                        "searchRadius": 20,
                        "timeout": 30,
                    }
                },
            },
        },
    }


def test_sparse_migration():
    result = migrateLegacyConfig(legacy(), schema())
    cfg = result.config
    assert cfg["version"] == TARGET_PROFILE_VERSION
    assert cfg["SettingPark"]["ParkText0"] == "Park East"
    assert cfg["WindowMain"]["buildPFileName"] == "DCRP3"
    assert cfg["WindowHemisphere"]["horizonMaskFileName"] == "DCRP-Meassured"


def test_deviceSchemaFromRegistry():
    @dataclass
    class Cfg:
        hostAddress: str = ""
        port: int = 0

    registry = {
        "camera": SimpleNamespace(
            run={
                "alpaca": SimpleNamespace(config=Cfg()),
                "none": SimpleNamespace(config=None),
                "plain": SimpleNamespace(config=object()),
            }
        ),
        "dome": SimpleNamespace(run={}),
    }
    result = deviceSchemaFromRegistry(registry)
    assert result == {"camera": {"alpaca": {"hostAddress", "port"}}}


def test_migrateLegacyConfig_wrongVersion():
    old = legacy()
    old["version"] = "3.0"
    with pytest.raises(ValueError):
        migrateLegacyConfig(old, schema())


def test_migrateLegacyConfig_edgeCases():
    old = legacy()
    old["mainW"]["relay0index"] = "bad"
    old["mainW"]["renameDir"] = "x"
    old["mainW"]["useDomeAz"] = True
    old["mainW"]["relay1buttonText"] = "Dew"
    old["topoLat"] = 48.0
    old["driversData"]["camera"]["frameworks"] = {
        "alpaca": {
            "hostAddress": "localhost",
            "deviceList": ["a"],
            "unknownKey": 1,
            "port": 11111,
        },
        "ascom": "notADict",
        "indi": {"port": 1},
    }
    result = migrateLegacyConfig(old, schema())
    cfg = result.config
    assert any("relay0index" in w for w in result.warnings)
    assert len(result.notes) == 2
    assert cfg["SettingRelay"]["RelayText1"] == "Dew"
    camera = cfg["SettingDevice"]["camera"]["alpaca"]
    assert camera["hostAddress"] == "127.0.0.1"
    assert camera["port"] == 11111
    assert "unknownKey" not in camera
