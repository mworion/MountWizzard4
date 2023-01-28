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
# written in python3, (c) 2019-2023 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import os
import json
import pytest
import glob
import unittest.mock as mock

# external packages

# local import
from logic.profiles.profile import convertProfileData, blendProfile, defaultConfig
from logic.profiles.profile import loadProfile, saveProfile
from logic.profiles.profile import convertKeyData, replaceKeys, checkResetTabOrder


@pytest.fixture(autouse=True, scope='function')
def setup():
    files = glob.glob('tests/workDir/config/*.cfg')
    for f in files:
        os.remove(f)
    f = 'tests/workDir/config/profile'
    if os.path.isfile(f):
        os.remove(f)


def test_replaceKeys():
    keyDict = {'old': 'new'}
    data = {'test': {
        'out': {
            'old': 10,
        }
    }}
    val = replaceKeys(data, keyDict)
    assert 'new' in val['test']['out']


def test_convertKeyData():
    i = {'checkASCOMAutoConnect': 'test'}
    r = convertKeyData(i)
    assert 'checkASCOMAutoConnect' not in r
    assert 'autoConnectASCOM' in r


def test_convertProfileData_0():
    data = {}
    val = convertProfileData(data)
    assert 'version' not in val


def test_convertProfileData_1():
    data = {
        'version': '4.1'
    }
    val = convertProfileData(data)
    assert val['version'] == '4.1'


def test_convertProfileData_2():
    data = {
        'version': '4.0'
    }
    val = convertProfileData(data)
    assert val['version'] == '4.0'


def test_convertProfileData_3():
    data = {
        'version': '4.0',
        'hemisphereW': {},
        'mainW': {
            'horizonFileName': 'test',
            'driversData': {
                'astrometry': {
                    'test1': 1,
                    'test2': 2
                },
                'directWeather': {
                    'frameworks': {
                        'internal': {
                            'deviceName': 'Direct'
                        }
                    }
                }
            }
        },
    }
    val = convertProfileData(data)
    assert val['version'] == '4.1'
    assert 'driversData' in val
    assert 'driversData' not in val['mainW']
    assert 'astrometry' not in val['driversData']
    assert 'plateSolve' in val['driversData']
    assert 'directWeather' in val['driversData']['directWeather']['frameworks']
    assert 'internal' not in val['driversData']['directWeather']['frameworks']
    t = val['driversData']['directWeather']['frameworks']
    assert 'On Mount' in t['directWeather']['deviceName']
    assert 'Direct' not in t['directWeather']['deviceName']


def test_convertProfileData_4():
    data = {
        'mainW': '4.0'
    }
    val = convertProfileData(data)
    assert val['mainW'] == '4.0'


def test_blendProfile():
    conf = blendProfile({}, {})
    assert conf == {}


def test_defaultConfig():
    val = defaultConfig()
    assert val['profileName'] == 'config'
    assert val['version'] == '4.1'


def test_checkResetTabOrder_1():
    test = {
        'order': {},
    }
    val = checkResetTabOrder(test)
    assert val == {}


def test_checkResetTabOrder_2():
    test = {
        'test': {
            'order': {},
        },
    }
    val = checkResetTabOrder(test)
    assert val == {'test': {}}


def test_loadProfile_1():
    val = loadProfile(configDir='tests/workDir/config')
    assert val == {'profileName': 'config', 'version': '4.1'}


def test_loadProfile_2():
    with open('tests/workDir/config/profile', 'w') as outfile:
        outfile.write('config')

    config = defaultConfig()
    config['mainW'] = {}
    with open('tests/workDir/config/config.cfg', 'w') as outfile:
        json.dump(config, outfile)

    val = loadProfile(configDir='tests/workDir/config')
    assert val == {'profileName': 'config', 'version': '4.1', 'mainW': {}}


def test_loadProfile_3():
    with open('tests/workDir/config/profile', 'w') as outfile:
        outfile.write('config')

    val = loadProfile(configDir='tests/workDir/config', name='config')
    assert val == {'profileName': 'config', 'version': '4.1'}


def test_loadProfile_4():
    with open('tests/workDir/config/profile', 'w') as outfile:
        outfile.write('config')
    config = defaultConfig()

    with open('tests/workDir/config/config.cfg', 'w') as outfile:
        json.dump(config, outfile)

    with mock.patch.object(json,
                           'load',
                           side_effect=Exception()):
        val = loadProfile(configDir='tests/workDir/config', name='config')
        assert val == {'profileName': 'config', 'version': '4.1'}


def test_loadProfile_5():
    with open('tests/workDir/config/profile', 'w') as outfile:
        outfile.write('config')
    config = defaultConfig()
    config['mainW'] = {}
    config['mainW']['resetTabOrder'] = True
    config['mainW']['orderMain'] = {
        '00': 'Environ',
        'index': 0,
    }

    with open('tests/workDir/config/config.cfg', 'w') as outfile:
        json.dump(config, outfile)

    val = loadProfile(configDir='tests/workDir/config', name='config')
    assert 'oderMain' not in list(val['mainW'].keys())


def test_saveProfile_1():
    config = {'profileName': 'config'}

    suc = saveProfile(configDir='tests/workDir/config', config=config)
    assert suc
    assert os.path.isfile('tests/workDir/config/config.cfg')
    assert os.path.isfile('tests/workDir/config/profile')
    with open('tests/workDir/config/profile', 'r') as infile:
        name = infile.readline().strip()
    assert name == 'config'


def test_saveProfile_2():
    config = {'profileName': 'config'}

    suc = saveProfile(configDir='tests/workDir/config', config=config, name='config')
    assert suc
    assert os.path.isfile('tests/workDir/config/config.cfg')
    assert os.path.isfile('tests/workDir/config/profile')
    with open('tests/workDir/config/profile', 'r') as infile:
        name = infile.readline().strip()
    assert name == 'config'


def test_saveProfile_3():
    config = {'profileName': 'new'}

    suc = saveProfile(configDir='tests/workDir/config', config=config, name='new')
    assert suc
    assert os.path.isfile('tests/workDir/config/new.cfg')
    assert os.path.isfile('tests/workDir/config/profile')
    with open('tests/workDir/config/profile', 'r') as infile:
        name = infile.readline().strip()
    assert name == 'new'


def test_saveProfile_4():
    config = {'profileName': 'new'}

    suc = saveProfile(configDir='tests/workDir/config', config=config)
    assert suc
    assert os.path.isfile('tests/workDir/config/new.cfg')
    assert os.path.isfile('tests/workDir/config/profile')
    with open('tests/workDir/config/profile', 'r') as infile:
        name = infile.readline().strip()
    assert name == 'new'
    

def test_saveProfile_5():
    suc = saveProfile(configDir='tests/workDir/config')
    assert suc
    assert os.path.isfile('tests/workDir/config/config.cfg')
    assert os.path.isfile('tests/workDir/config/profile')
    with open('tests/workDir/config/profile', 'r') as infile:
        name = infile.readline().strip()
    assert name == 'config'

