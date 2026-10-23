# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import logging
import yaml
from mw4.logic.profiles.config import ProfileConfig
from mw4.logic.profiles.migration import migrateConfig
from pathlib import Path
from typing import Any

log: logging.Logger = logging.getLogger("MW4")


def defaultConfig() -> ProfileConfig:
    return ProfileConfig()


def loadConfig(loadConfigPath: Path) -> ProfileConfig:
    try:
        with open(loadConfigPath, encoding="utf-8") as configFile:
            config = yaml.safe_load(configFile)
    except (OSError, yaml.YAMLError):
        return defaultConfig()

    if not config or not isinstance(config, dict):
        return defaultConfig()

    config = migrateConfig(config)
    if config is None:
        return defaultConfig()

    config["profileName"] = loadConfigPath.stem
    return ProfileConfig.fromDict(config)


def loadProfileStart(configDir: Path) -> ProfileConfig:
    config = defaultConfig()
    profilePath = configDir / "profile"
    if not profilePath.exists():
        return config

    profileName = profilePath.read_text()
    configPath = configDir / (profileName + ".yaml")
    if not configPath.exists():
        return config

    config = loadConfig(configPath)
    return config


def saveConfig(saveProfilePath: Path, config: ProfileConfig | dict[str, Any]) -> None:
    with open(saveProfilePath.parent / "profile", "w", encoding="utf-8") as profile:
        profile.writelines(saveProfilePath.stem)

    file = saveProfilePath.parent / (saveProfilePath.stem + ".yaml")
    with open(file, "w", encoding="utf-8") as outfile:
        yaml.dump(
            config.toDict() if isinstance(config, ProfileConfig) else config,
            outfile,
            default_flow_style=False,
        )
