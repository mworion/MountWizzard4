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
# GUI with PyQT5 for python
#
# written in python3, (c) 2019-2022 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
import os
import json

# external libraries
from ndicts.ndicts import NestedDict
from packaging.utils import Version

# local imports
from base.loggerMW import setupLogging

setupLogging()
log = logging.getLogger()
profileVersion = '4.1'


def replaceKeys(oldDict, keyDict):
    """
    :param oldDict:
    :param keyDict:
    :return:
    """
    newDict = {}
    for key in oldDict.keys():
        newKey = keyDict.get(key, key)
        if isinstance(oldDict[key], dict):
            newDict[newKey] = replaceKeys(oldDict[key], keyDict)
        else:
            newDict[newKey] = oldDict[key]
    return newDict


def convertKeyData(data):
    """
    :param data:
    :return:
    """
    keyDict = {
        'checkASCOMAutoConnect': 'autoConnectASCOM',
        'checkAutoDeleteHorizon': 'autoDeleteHorizon',
        'checkAutoDeleteMeridian': 'autoDeleteMeridian',
        'checkAutomaticTelescope': 'automaticTelescope',
        'checkAvoidFlip': 'avoidFlip',
        'checkFastDownload': 'fastDownload',
        'checkIncludeSubdirs': 'includeSubdirs',
        'checkJ2000': 'coordsJ2000',
        'checkJNow': 'coordsJNow',
        'checkKeepImages': 'keepModelImages',
        'checkRefracCont': 'refracCont',
        'checkRefracNoTrack': 'refracNoTrack',
        'checkRefracNone': 'refracManual',
        'checkSafetyMarginHorizon': 'useSafetyMargin',
        'checkSortEW': 'sortEW',
        'checkSortHL': 'sortHL',
        'checkSortNothing': 'sortNothing',
        'safetyMarginHorizon': 'safetyMarginValue',
        'syncNotTracking': 'syncTimeNotTrack',
        'checkShowAlignStar': 'showAlignStar',
        'checkShowCelestial': 'showCelestial',
        'checkShowMeridian': 'showMeridian',
        'checkShowSlewPath': 'showSlewPath',
        'checkUseHorizon': 'showHorizon',
        'useTerrain': 'showTerrain',
        'checkAutoSolve': 'autoSolve',
        'checkEmbedData': 'embedData',
        'checkShowCrosshair': 'showCrosshair',
    }
    data = replaceKeys(data, keyDict)
    return data


def convertProfileData(data):
    """
    convertDate tries to convert data from an older or newer version of the
    config file to the actual needed one.

    :param      data: config data as dict
    :return:    data: config data as dict
    """
    actVer = Version(data.get('version', '0.0'))
    if actVer >= Version(profileVersion):
        return data
    if 'mainW' not in data:
        return data

    log.info(f'Conversion from [{data.get("version")}] to [{profileVersion}]')
    data = NestedDict(data)
    data['driversData'] = data['mainW', 'driversData']
    del data['mainW']['driversData']
    data['driversData', 'plateSolve'] = data['driversData', 'astrometry']
    del data['driversData']['astrometry']
    data['hemisphereW', 'horizonMaskFileName'] = data['mainW', 'horizonFileName']
    del data['mainW']['horizonFileName']
    t = data['driversData', 'directWeather', 'frameworks', 'internal']
    data['driversData', 'directWeather', 'frameworks', 'directWeather'] = t
    del data['driversData']['directWeather']['frameworks']['internal']
    data['driversData', 'directWeather', 'frameworks', 'directWeather',
         'deviceName'] = 'On Mount'
    data['version'] = profileVersion
    data = data.to_dict()
    return data


def blendProfile(config, configAdd):
    """
    :param config:
    :param configAdd:
    :return:
    """
    return config


def defaultConfig(config=None):
    """
    :param config:
    :return:
    """
    if config is None:
        config = dict()

    config['profileName'] = 'config'
    config['version'] = profileVersion
    return config


def loadProfile(configDir=None, name=None):
    """
    :param      configDir:   name of the config dir
    :param      name:   name of the config file
    :return:    success if file could be loaded
    """
    if name is None:
        profileFile = f'{configDir}/profile'
        if os.path.isfile(profileFile):
            with open(profileFile, 'r') as profile:
                name = profile.readline().strip()
        else:
            name = 'config'

    fileName = f'{configDir}/{name}.cfg'

    if not os.path.isfile(fileName):
        log.info(f'Config file {fileName} not existing')
        return defaultConfig()

    try:
        with open(fileName, 'r') as configFile:
            configData = json.load(configFile)
    except Exception as e:
        log.critical(f'Cannot parse: {fileName}, error: {e}')
        return defaultConfig()
    else:
        configData['profileName'] = name
        return convertProfileData(configData)


def saveProfile(configDir=None, name=None, config={}):
    """
    :param      configDir:   name of the config dir
    :param      name:   name of the config file
    :param      config:   data
    :return:    success
    """
    if name is None:
        name = config['profileName']

    profileFile = f'{configDir}/profile'
    with open(profileFile, 'w') as profile:
        profile.writelines(f'{name}')

    fileName = configDir + '/' + name + '.cfg'
    config['version'] = profileVersion
    with open(fileName, 'w') as outfile:
        json.dump(config, outfile, sort_keys=True, indent=4)
    return True
