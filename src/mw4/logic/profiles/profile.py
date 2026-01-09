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
import json
import logging
from mw4.base.loggerMW import setupLogging
from pathlib import Path

setupLogging()
log = logging.getLogger()
profileVersion = "4.3"


def defaultConfig() -> dict:
    """ """
    config = {"profileName": "config", "version": profileVersion}
    return config


def loadProfile(loadProfilePath: Path) -> dict:
    """ """
    try:
        with open(loadProfilePath) as configFile:
            configData = json.load(configFile)
    except Exception as e:
        log.critical(f"Cannot parse: {loadProfilePath.name}, error: {e}")
        return defaultConfig()

    configData["profileName"] = loadProfilePath.stem
    if configData.get('version', '') != profileVersion:
        return defaultConfig()
    return configData


def loadProfileStart(configDir: Path) -> dict:
    """ """
    profile = defaultConfig()
    profilePath = configDir / "profile"
    if not profilePath.exists():
        return profile

    profileName = profilePath.read_text()
    profilePath = configDir / (profileName + ".cfg")
    if not profilePath.exists():
        return profile

    profile = loadProfile(profilePath)
    return profile


def saveProfile(saveProfilePath: Path, config: dict) -> None:
    """ """
    with open(saveProfilePath.parent / "profile", "w") as profile:
        profile.writelines(saveProfilePath.stem)

    file = saveProfilePath.parent / (saveProfilePath.stem + ".cfg")
    config["version"] = profileVersion
    with open(file, "w") as outfile:
        json.dump(config, outfile, sort_keys=True, indent=4)
