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
import pytest
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


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    print("MODULE SETUP!!!")
    global spy
    global app

    app = mainApp.MountWizzard4(mwGlob=mwGlob)
    spy = PyQt5.QtTest.QSignalSpy(app.message)
    testdir = os.listdir(config)
    for item in testdir:
        if item.endswith('.cfg'):
            os.remove(os.path.join(config, item))
    yield
    print("MODULE TEARDOWN!!!")
    spy = None
    app = None


#
#
# testing loading config
#
#


def test_loadConfig_ok1():
    # new, no config
    app.config = {}
    suc = app.loadConfig()
    assert suc
    assert '4.0' == app.config['version']
    assert 'config' == app.config['profileName']
    assert 'filePath' in app.config


def test_loadConfig_ok2():
    # load existing basic config with filePath
    app.config = {}
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

    suc = app.loadConfig()
    assert suc
    assert '4.0' == app.config['version']
    assert 'config' == app.config['profileName']
    assert 'filePath' in app.config


def test_loadConfig_ok3():
    # load config from another file referenced
    app.config = {}
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
    suc = app.loadConfig()
    assert suc
    assert '4.0' == app.config['version']
    assert 'reference' == app.config['profileName']


def test_loadConfig_ok4():
    # load config direct from another file
    app.config = {}
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
    suc = app.loadConfig(config + '/reference.cfg')
    assert suc
    assert '4.0' == app.config['version']
    assert 'reference' == app.config['profileName']


def test_loadConfig_not_ok1():
    # load existing basic config without filePath
    app.config = {}
    basic = {
        'profileName': 'config',
        'version': '4.0',
    }
    with open(config + '/config.cfg', 'w') as outfile:
        json.dump(basic,
                  outfile,
                  sort_keys=True,
                  indent=4)

    suc = app.loadConfig()
    assert not suc
    assert '4.0' == app.config['version']
    assert 'config' == app.config['profileName']
    assert 'filePath' in app.config


def test_loadConfig_not_ok2():
    # basic config with wrong filePath
    app.config = {}
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

    suc = app.loadConfig()
    assert not suc
    assert '4.0' == app.config['version']
    assert 'config' == app.config['profileName']
    assert 'filePath' in app.config


def test_loadConfig_not_ok3():
    # basic config not readable
    app.config = {}
    with open(config + '/config.cfg', 'w') as outfile:
        outfile.write('test')

    suc = app.loadConfig()
    assert not suc
    assert '4.0' == app.config['version']
    assert 'config' == app.config['profileName']
    assert 'filePath' in app.config


def test_loadConfig_not_ok4():
    # reference config not readable
    app.config = {}
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
    with open(config + '/reference.cfg', 'w') as outfile:
        outfile.write('test')
    suc = app.loadConfig()
    assert not suc
    assert '4.0' == app.config['version']
    assert 'config' == app.config['profileName']
    assert 'filePath' in app.config


def test_loadConfig_not_ok5():
    # version not in referenced data
    app.config = {}
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
        'filePath': config + '/reference.cfg'
    }
    with open(config + '/reference.cfg', 'w') as outfile:
        json.dump(reference,
                  outfile,
                  sort_keys=True,
                  indent=4)
    suc = app.loadConfig()
    assert not suc
    assert '4.0' == app.config['version']
    assert 'config' == app.config['profileName']

#
#
# testing saving config
#
#


def test_saveConfig_ok1():
    # save default without reference
    app.config = {
        'profileName': 'config',
        'version': '4.0',
        'filePath': config + '/config.cfg'
    }
    suc = app.saveConfig()
    assert suc


def test_saveConfig_ok2():
    # save default with reference
    app.config = {
        'profileName': 'reference',
        'version': '4.0',
        'filePath': config + '/reference.cfg'
    }
    suc = app.saveConfig()
    assert suc


def test_saveConfig_ok3():
    # save to new reference
    app.config = {
        'profileName': 'reference',
        'version': '4.0',
        'filePath': config + '/reference.cfg'
    }
    suc = app.saveConfig(config + '/reference.cfg')
    assert suc
    with open(config + '/config.cfg', 'r') as inFile:
        a = json.load(inFile)
        assert a['profileName'] == 'reference'
        assert a['version'] == '4.0'
        assert a['filePath'] == config + '/reference.cfg'


def test_saveConfig_not_ok1():
    # save with default name and wrong reference
    app.config = {
        'profileName': 'config',
        'version': '4.0',
        'filePath': config + '/reference.cfg'
    }
    suc = app.saveConfig()
    assert not suc


def test_saveConfig_not_ok2():
    # save with reference name and missing file path
    app.config = {
        'profileName': 'reference',
        'version': '4.0',
    }
    suc = app.saveConfig()
    assert not suc


def test_saveConfig_not_ok3():
    # save default without reference without filePath
    app.config = {
        'profileName': 'config',
        'version': '4.0',
    }
    suc = app.saveConfig()
    assert not suc


def test_saveConfig_not_ok4():
    # save default without reference without filePath
    app.config = {
        'profileName': 'config',
        'version': '4.0',
        'filePath': None,
    }
    suc = app.saveConfig()
    assert not suc

