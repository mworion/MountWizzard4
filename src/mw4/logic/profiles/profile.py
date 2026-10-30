# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import json
import logging
import yaml
from mw4.deviceRegistry import DeviceRegistry
from mw4.logic.profiles.legacyImport import deviceSchemaFromRegistry, migrateLegacyConfig
from pathlib import Path
from typing import Any

log: logging.Logger = logging.getLogger("MW4")
profileVersion = "5.0"
# single place to replace by a typed configuration (review A3)
ProfileConfig = dict[str, Any]


def defaultConfig() -> ProfileConfig:
    config = {"profileName": "config", "version": profileVersion}
    return config


def loadYamlConfig(loadConfigPath: Path) -> ProfileConfig:
    try:
        with open(loadConfigPath, encoding="utf-8") as configFile:
            config = yaml.safe_load(configFile)
    except (OSError, yaml.YAMLError):
        config = {}
    return config


def loadLegacyConfig(loadConfigPath: Path, dReg: DeviceRegistry) -> ProfileConfig:
    try:
        with open(loadConfigPath, encoding="utf-8") as configFile:
            config = json.load(configFile)
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {}

    deviceSchema = deviceSchemaFromRegistry(dReg)
    try:
        migration = migrateLegacyConfig(config, deviceSchema)
    except ValueError:
        return {}
    migration.config["profileName"] = loadConfigPath.stem
    return migration.config


def loadConfig(loadConfigPath: Path, dReg) -> ProfileConfig:
    if loadConfigPath.suffix == ".yaml":
        config = loadYamlConfig(loadConfigPath)
    else:
        config = loadLegacyConfig(loadConfigPath, dReg)

    if not config:
        return defaultConfig()

    config["profileName"] = loadConfigPath.stem
    if config.get("version", "") != profileVersion:
        return defaultConfig()
    return config


def loadProfileStart(configDir: Path) -> ProfileConfig:
    config = defaultConfig()
    profilePath = configDir / "profile"
    if not profilePath.exists():
        return config

    profileName = profilePath.read_text()
    configPath = configDir / (profileName + ".yaml")
    if not configPath.exists():
        return config

    config = loadYamlConfig(configPath)
    return config


def saveConfig(saveProfilePath: Path, config: ProfileConfig) -> None:
    with open(saveProfilePath.parent / "profile", "w", encoding="utf-8") as profile:
        profile.writelines(saveProfilePath.stem)

    file = saveProfilePath.parent / (saveProfilePath.stem + ".yaml")
    with open(file, "w", encoding="utf-8") as outfile:
        yaml.dump(config, outfile, default_flow_style=False)
