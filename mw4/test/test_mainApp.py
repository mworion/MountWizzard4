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
# Python  v3.6.5
#
# Michael Würtenberger
# (c) 2018
#
# Licence APL2.0
#
###########################################################
# standard libraries
import os
import json
# external packages
import PyQt5.QtCore
# local import
from mw4 import mainApp


test = PyQt5.QtWidgets.QApplication([])


mwGlob = {'workDir': '.',
          'configDir': './mw4/test/config',
          'build': 'test',
          }
config = mwGlob['configDir']

test_app = mainApp.MountWizzard4(mwGlob=mwGlob)

test = os.listdir(config)
for item in test:
    if item.endswith('.cfg'):
        os.remove(os.path.join(config, item))

#
#
# testing main
#
#


def test_loadConfig_ok1():
    # new, no config
    test_app.config = {}
    suc = test_app.loadConfig()
    assert suc
    assert '4.0' == test_app.config['version']
    assert 'config' == test_app.config['profileName']
    assert 'filePath' in test_app.config


def test_loadConfig_ok2():
    # load existing basic config with filePath
    test_app.config = {}
    basic = {
        'profileName': 'config',
        'version': '4.0',
        'filePath': config + '/config.cfg',
    }
    with open(config + '/config.cfg', 'w') as outfile:
        json.dump(basic,
                  outfile,
                  sort_keys=True,
                  indent=4)

    suc = test_app.loadConfig()
    assert suc
    assert '4.0' == test_app.config['version']
    assert 'config' == test_app.config['profileName']
    assert 'filePath' in test_app.config


def test_loadConfig_ok3():
    # load config from another file referenced
    test_app.config = {}
    basic = {
        'profileName': 'reference',
        'version': '4.0',
        'filePath': config + '/reference.cfg'
    }
    with open(config + '/config.cfg', 'w') as outfile:
        json.dump(basic,
                  outfile,
                  sort_keys=True,
                  indent=4)
    reference = {
        'profileName': 'reference',
        'version': '4.0',
        'filePath': config + '/reference.cfg'
    }
    with open(config + '/reference.cfg', 'w') as outfile:
        json.dump(reference,
                  outfile,
                  sort_keys=True,
                  indent=4)

    suc = test_app.loadConfig()
    assert suc
    assert '4.0' == test_app.config['version']
    assert 'reference' == test_app.config['profileName']


def test_loadConfig_not_ok1():
    # load existing basic config without filePath
    test_app.config = {}
    basic = {
        'profileName': 'config',
        'version': '4.0',
    }
    with open(config + '/config.cfg', 'w') as outfile:
        json.dump(basic,
                  outfile,
                  sort_keys=True,
                  indent=4)

    suc = test_app.loadConfig()
    assert not suc
    assert '4.0' == test_app.config['version']
    assert 'config' == test_app.config['profileName']
    assert 'filePath' in test_app.config


def test_loadConfig_not_ok2():
    # basic config with wrong filePath
    test_app.config = {}
    basic = {
        'profileName': 'config',
        'version': '4.0',
        'filePath': config + '/test.cfg',
    }
    with open(config + '/config.cfg', 'w') as outfile:
        json.dump(basic,
                  outfile,
                  sort_keys=True,
                  indent=4)

    suc = test_app.loadConfig()
    assert not suc
    assert '4.0' == test_app.config['version']
    assert 'config' == test_app.config['profileName']
    assert 'filePath' in test_app.config
