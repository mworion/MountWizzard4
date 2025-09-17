############################################################
# -*- coding: utf-8 -*-
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PySide for python
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
import json
from pathlib import Path

# external libraries
from ndicts import NestedDict
from packaging.utils import Version

# local imports
from base.loggerMW import setupLogging

setupLogging()
log = logging.getLogger()
profileVersion = "4.2"


def replaceKeys(oldDict: dict, keyDict: dict) -> dict:
    """ """
    newDict = {}
    for key in oldDict.keys():
        newKey = keyDict.get(key, key)
        if isinstance(oldDict[key], dict):
            newDict[newKey] = replaceKeys(oldDict[key], keyDict)
        else:
            newDict[newKey] = oldDict[key]
    return newDict


def convertKeyData(data: dict) -> dict:
    """ """
    keyDict = {
        "checkASCOMAutoConnect": "autoConnectASCOM",
        "checkAutoDeleteHorizon": "autoDeleteHorizon",
        "checkAutoDeleteMeridian": "autoDeleteMeridian",
        "checkAutomaticTelescope": "automaticTelescope",
        "checkAvoidFlip": "avoidFlip",
        "checkIncludeSubdirs": "includeSubdirs",
        "checkJ2000": "coordsJ2000",
        "checkJNow": "coordsJNow",
        "checkKeepImages": "keepModelImages",
        "checkRefracCont": "refracCont",
        "checkRefracNoTrack": "refracNoTrack",
        "checkRefracNone": "refracManual",
        "checkSafetyMarginHorizon": "useSafetyMargin",
        "checkSortEW": "sortEW",
        "checkSortHL": "sortHL",
        "checkSortNothing": "sortNothing",
        "safetyMarginHorizon": "safetyMarginValue",
        "syncNotTracking": "syncTimeNotTrack",
        "checkShowAlignStar": "showAlignStar",
        "checkShowCelestial": "showCelestial",
        "checkShowMeridian": "showMeridian",
        "checkShowSlewPath": "showSlewPath",
        "checkUseHorizon": "showHorizon",
        "useTerrain": "showTerrain",
        "checkAutoSolve": "autoSolve",
        "checkEmbedData": "embedData",
        "checkShowCrosshair": "showCrosshair",
    }
    data = replaceKeys(data, keyDict)
    return data


def convertProfileData40to41(data: dict) -> dict:
    """ """
    actVer = Version(data.get("version", "0.0"))
    if actVer >= Version("4.1"):
        return data
    if "mainW" not in data:
        return data

    log.info(f"Conversion from [{data.get('version')}] to [4.1]")
    watney = {
        "deviceName": "Watney",
        "deviceList": ["Watney"],
        "searchRadius": 10,
        "timeout": 30,
        "appPath": Path(""),
        "indexPath": Path(""),
    }
    d = NestedDict(data)
    try:
        d["driversData"] = d["mainW", "driversData"]
        del d["mainW"]["driversData"]

        d["driversData", "plateSolve"] = d["driversData", "astrometry"]
        del d["driversData"]["astrometry"]

        d["driversData", "plateSolve", "frameworks", "watney"] = watney
        d["hemisphereW", "horizonMaskFileName"] = d["mainW", "horizonFileName"]
        del d["mainW"]["horizonFileName"]

        t = d["driversData", "directWeather", "frameworks", "internal"]
        d["driversData", "directWeather", "frameworks", "directWeather"] = t
        del d["driversData"]["directWeather"]["frameworks"]["internal"]

        d["driversData", "directWeather", "frameworks", "directWeather", "deviceName"] = (
            "On Mount"
        )
        d["version"] = "4.1"

    except Exception as e:
        log.error(f"Failed conversion, keep old structure: {e}")
    else:
        data = d.to_dict()
    return data


def convertProfileData41to42(data: dict) -> dict:
    """ """
    actVer = Version(data.get("version", "0.0"))
    if actVer >= Version("4.2"):
        return data

    log.info(f"Conversion from [{data.get('version')}] to [4.2]")
    d = NestedDict(data)
    try:
        if "sensorWeather" in d["driversData"]:
            d["driversData", "sensor1Weather"] = d["driversData", "sensorWeather"]
            del d["driversData"]["sensorWeather"]
        if "powerWeather" in d["driversData"]:
            d["driversData", "sensor2Weather"] = d["driversData", "powerWeather"]
            del d["driversData"]["powerWeather"]
        if "skymeter" in d["driversData"]:
            d["driversData", "sensor3Weather"] = d["driversData", "skymeter"]
            del d["driversData"]["skymeter"]
        d["version"] = "4.2"

    except Exception as e:
        log.error(f"Failed conversion, keep old structure: {e}")
    else:
        data = d.to_dict()
    return data


def blendProfile(config, configAdd):
    """ """
    return config


def defaultConfig() -> dict:
    """ """
    config = dict()
    config["profileName"] = "config"
    config["version"] = profileVersion
    return config


def checkResetTabOrder(profile: dict) -> dict:
    """ """
    newDict = {}
    for key in profile.keys():
        if key.startswith("order"):
            continue
        if isinstance(profile[key], dict):
            newDict[key] = checkResetTabOrder(profile[key])
        else:
            newDict[key] = profile[key]
    return newDict


def loadProfile(loadProfilePath: Path) -> dict:
    """ """
    try:
        with open(loadProfilePath, "r") as configFile:
            configData = json.load(configFile)
    except Exception as e:
        log.critical(f"Cannot parse: {loadProfilePath.name}, error: {e}")
        return defaultConfig()

    configData["profileName"] = loadProfilePath.stem
    profile = convertProfileData40to41(configData)
    profile = convertProfileData41to42(profile)
    mainW = profile.get("mainW", {})
    resetOrder = mainW.get("resetTabOrder", False)
    if resetOrder:
        log.info("Resetting tab order upon start")
        profile = checkResetTabOrder(profile)
    return profile


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
