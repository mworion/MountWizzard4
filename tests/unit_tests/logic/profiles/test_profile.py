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
import os
import json
import pytest
import glob
import unittest.mock as mock

# external packages

# local import
from logic.profiles.profile import convertProfileData, blendProfile, defaultConfig
from logic.profiles.profile import loadProfile, saveProfile


@pytest.fixture(autouse=True, scope='function')
def setup():
    files = glob.glob('tests/workDir/config/*.cfg')
    for f in files:
        os.remove(f)
    f = 'tests/workDir/config/profile'
    if os.path.isfile(f):
        os.remove(f)


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
        'mainW': {},
    }
    val = convertProfileData(data)
    assert val['version'] == '4.0'


def test_convertProfileData_4():
    data = {
        'version': '4.0',
        'hemisphereW': {},
        'mainW': {
            'driversData': 'test'
        },
    }
    val = convertProfileData(data)
    assert val['version'] == '4.1'
    assert 'driversData' in val
    assert 'driversData' not in val['mainW']


def test_blendProfile():
    conf = blendProfile({}, {})
    assert conf == {}


def test_defaultConfig():
    val = defaultConfig()
    assert val['profileName'] == 'config'
    assert val['version'] == '4.1'


def test_loadConfig_1():
    val = loadProfile(configDir='tests/workDir/config')
    assert val == {'profileName': 'config', 'version': '4.1'}


def test_loadConfig_2():
    with open('tests/workDir/config/profile', 'w') as outfile:
        outfile.write('config')

    config = defaultConfig()
    with open('tests/workDir/config/config.cfg', 'w') as outfile:
        json.dump(config, outfile)

    val = loadProfile(configDir='tests/workDir/config')
    assert val == {'profileName': 'config', 'version': '4.1'}


def test_loadConfig_3():
    with open('tests/workDir/config/profile', 'w') as outfile:
        outfile.write('config')

    val = loadProfile(configDir='tests/workDir/config', name='config')
    assert val == {'profileName': 'config', 'version': '4.1'}


def test_loadConfig_4():
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


def test_saveConfig_1():
    config = {'profileName': 'config'}

    suc = saveProfile(configDir='tests/workDir/config', config=config)
    assert suc
    assert os.path.isfile('tests/workDir/config/config.cfg')
    assert os.path.isfile('tests/workDir/config/profile')
    with open('tests/workDir/config/profile', 'r') as infile:
        name = infile.readline().strip()
    assert name == 'config'


def test_saveConfig_2():
    config = {'profileName': 'config'}

    suc = saveProfile(configDir='tests/workDir/config', config=config, name='config')
    assert suc
    assert os.path.isfile('tests/workDir/config/config.cfg')
    assert os.path.isfile('tests/workDir/config/profile')
    with open('tests/workDir/config/profile', 'r') as infile:
        name = infile.readline().strip()
    assert name == 'config'


def test_saveConfig_3():
    config = {'profileName': 'new'}

    suc = saveProfile(configDir='tests/workDir/config', config=config, name='new')
    assert suc
    assert os.path.isfile('tests/workDir/config/new.cfg')
    assert os.path.isfile('tests/workDir/config/profile')
    with open('tests/workDir/config/profile', 'r') as infile:
        name = infile.readline().strip()
    assert name == 'new'


def test_saveConfig_4():
    config = {'profileName': 'new'}

    suc = saveProfile(configDir='tests/workDir/config', config=config)
    assert suc
    assert os.path.isfile('tests/workDir/config/new.cfg')
    assert os.path.isfile('tests/workDir/config/profile')
    with open('tests/workDir/config/profile', 'r') as infile:
        name = infile.readline().strip()
    assert name == 'new'
