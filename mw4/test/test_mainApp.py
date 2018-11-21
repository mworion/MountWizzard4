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
import shutil
# external packages
import PyQt5.QtCore
# local import
from mw4 import mainApp


test = PyQt5.QtWidgets.QApplication([])


mwGlob = {'workDir': '.',
          'configDir': './mw4/test/config',
          'build': 'test',
          }
config = mwGlob['configDir'] + '/config'
if os.path.isdir(config):
    os.remove(config)
test_app = mainApp.MountWizzard4(mwGlob=mwGlob)

#
#
# testing main
#
#


def test_loadConfig_ok1():
    # new, no config
    config = mwGlob['configDir'] + '/config.cfg'
    if os.path.isdir(config):
        os.remove(config)
    suc = test_app.loadConfig()
    assert suc
    assert '4.0' == test_app.config['version']
    assert 'config' == test_app.config['profileName']
    assert test_app.config['filePath']


def test_loadConfig_ok2():
    # load existing basic config without filePath
    configTest = './mw4/test/config/config_ok.cfg'
    config = mwGlob['configDir'] + '/config.cfg'
    if os.path.isdir(config):
        os.remove(config)
    shutil.copy(configTest, config)

    suc = test_app.loadConfig()
    assert suc
    assert '4.0' == test_app.config['version']
    assert 'config' == test_app.config['profileName']


def test_loadConfig_ok3():
    # load config from another file referenced
    configTest = './mw4/test/config/config_ok_link.cfg'
    config = mwGlob['configDir'] + '/config.cfg'
    if os.path.isdir(config):
        os.remove(config)
    shutil.copy(configTest, config)

    suc = test_app.loadConfig()
    assert suc
    assert '4.0' == test_app.config['version']
    assert 'link' == test_app.config['profileName']


def test_loadConfig_ok4():
    configFilePath = './mw4/test/config/config_nok2.cfg'

    suc = test_app.loadConfig(configFilePath=configFilePath)
    assert not suc


def test_loadConfig_not_ok1():
    configFilePath = './mw4/test/config/config_nok1.cfg'

    suc = test_app.loadConfig(configFilePath=configFilePath)
    assert suc


def test_loadConfig_not_ok3():
    configFilePath = './mw4/test/config/config_nok3.cfg'

    suc = test_app.loadConfig(configFilePath=configFilePath)
    assert not suc


def test_loadConfig_not_ok4():
    configFilePath = './mw4/test/config/config_nok4.cfg'

    suc = test_app.loadConfig(configFilePath=configFilePath)
    assert not suc


def test_loadConfig_not_ok5():
    configFilePath = './mw4/test/config/config_nok5.cfg'

    suc = test_app.loadConfig(configFilePath=configFilePath)
    assert not suc


def test_saveConfig_ok1():
    configFilePath = './mw4/test/config/test1.cfg'

    suc = test_app.saveConfig(configFilePath=configFilePath)
    assert suc
