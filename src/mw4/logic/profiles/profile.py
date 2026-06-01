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
# License APL2.0
#
###########################################################
import logging
import yaml
from pathlib import Path

log: logging.Logger = logging.getLogger("MW4")
profileVersion = "4.3"


def defaultConfig() -> dict[str, str]:
    config = {"profileName": "config", "version": profileVersion}
    return config


def loadConfig(loadConfigPath: Path) -> dict[str, str]:
    try:
        with open(loadConfigPath, encoding="utf-8") as configFile:
            config = yaml.safe_load(configFile)
    except (OSError, yaml.YAMLError):
        return defaultConfig()

    if not config:
        return defaultConfig()

    config["profileName"] = loadConfigPath.stem
    if config.get("version", "") != profileVersion:
        return defaultConfig()
    return config


def loadProfileStart(configDir: Path) -> dict[str, str]:
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


def saveConfig(saveProfilePath: Path, config: dict) -> None:
    with open(saveProfilePath.parent / "profile", "w", encoding="utf-8") as profile:
        profile.writelines(saveProfilePath.stem)

    file = saveProfilePath.parent / (saveProfilePath.stem + ".yaml")
    with open(file, "w", encoding="utf-8") as outfile:
        yaml.dump(config, outfile, default_flow_style=False)
