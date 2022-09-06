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

# local imports
from base.loggerMW import setupLogging

setupLogging()
log = logging.getLogger()


def convertProfileData(data):
    """
    convertDate tries to convert data from an older or newer version of the
    config file to the actual needed one.

    :param      data: config data as dict
    :return:    data: config data as dict
    """
    if data.get('version', '0.0') in ['0.0', '4.1']:
        return data
    if 'mainW' not in data:
        return data

    log.info(f'Conversion from [{data.get("version")}] to [4.1]')
    if 'driversData' in data['mainW']:
        data['driversData'] = data['mainW']['driversData']
        data['version'] = '4.1'
        del data['mainW']['driversData']

    horizonFile = data['mainW'].get('horizonFileName', '')
    if 'hemisphereW' in data:
        data['hemisphereW']['horizonMaskFileName'] = horizonFile
    else:
        data['hemisphereW'] = {'horizonMaskFileName': horizonFile}
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
    config['version'] = '4.1'
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
    with open(fileName, 'w') as outfile:
        json.dump(config, outfile, sort_keys=True, indent=4)
    return True
