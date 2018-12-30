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
# Python  v3.6.7
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
import skyfield.api
# local import
from mw4 import mainApp


test = PyQt5.QtWidgets.QApplication([])


mwGlob = {'workDir': '.',
          'configDir': './mw4/test/config',
          'dataDir': './mw4/test/config',
          'modeldata': 'test',
          }
config = mwGlob['configDir']
app = mainApp.MountWizzard4(mwGlob=mwGlob)


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    testdir = os.listdir(config)
    for item in testdir:
        if item.endswith('.cfg'):
            os.remove(os.path.join(config, item))
    yield

#
#
# testing loading config
#
#


def test_loadConfig_1():
    # new, no config
    app.config = {}
    suc = app.loadConfig()
    assert suc
    assert app.config['version'] == '4.0'
    assert app.config['profileName'] == 'config'
    assert 'filePath' in app.config


def test_loadConfig_2():
    # load existing basic config without reference
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
    assert app.config['version'] == '4.0'
    assert app.config['profileName'] == 'config'
    assert app.config['filePath'] == config + '/config.cfg'


def test_loadConfig_3():
    # load existing basic config with defect file
    app.config = {}
    with open(config + '/config.cfg', 'w') as outfile:
        outfile.writelines('dummy test')
    suc = app.loadConfig()
    assert not suc
    assert app.config['version'] == '4.0'
    assert app.config['profileName'] == 'config'
    assert app.config['filePath'] == config + '/config.cfg'


def test_loadConfig_4():
    # load existing basic config with error missing filePath
    # -> auto correcting this issue
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
    assert suc
    assert app.config['version'] == '4.0'
    assert app.config['profileName'] == 'config'
    assert app.config['filePath'] == config + '/config.cfg'


def test_loadConfig_5():
    # load existing config from another file referenced
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
    assert app.config['version'] == '4.0'
    assert app.config['profileName'] == 'reference'
    assert app.config['filePath'] == config + '/reference.cfg'


def test_loadConfig_6():
    # load existing config from another file referenced with error in filepath in reference
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
    }
    with open(config + '/reference.cfg', 'w') as outfile:
        json.dump(reference,
                  outfile,
                  sort_keys=True,
                  indent=4)
    suc = app.loadConfig()
    assert not suc
    assert app.config['version'] == '4.0'
    assert app.config['profileName'] == 'config'
    assert app.config['filePath'] == config + '/config.cfg'


def test_loadConfig_7():
    # load config direct from referenced file
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
    assert app.config['version'] == '4.0'
    assert app.config['profileName'] == 'reference'
    assert app.config['filePath'] == config + '/reference.cfg'


def test_loadConfig_8():
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
    assert suc
    assert '4.0' == app.config['version']
    assert 'config' == app.config['profileName']
    assert 'filePath' in app.config


def test_loadConfig_9():
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


def test_loadConfig_10():
    # basic config with wrong profileName
    app.config = {}
    basic = {
        'profileName': 'test',
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


#
#
# testing saving config
#
#


def test_saveConfig_1():
    # save default without reference
    app.config = {
        'profileName': 'config',
        'version': '4.0',
        'filePath': config + '/config.cfg'
    }
    suc = app.saveConfig()
    with open(config + '/config.cfg', 'r') as infile:
        res = json.load(infile)
    assert suc
    assert res['profileName'] == 'config'
    assert res['version'] == '4.0'
    assert res['filePath'] == config + '/config.cfg'


def test_saveConfig_2():
    # save default with reference
    app.config = {
        'profileName': 'reference',
        'version': '4.0',
        'filePath': config + '/reference.cfg'
    }
    suc = app.saveConfig()
    with open(config + '/config.cfg', 'r') as infile:
        res = json.load(infile)
    assert suc
    assert res['profileName'] == 'reference'
    assert res['version'] == '4.0'
    assert res['filePath'] == config + '/reference.cfg'
    with open(config + '/reference.cfg', 'r') as infile:
        res = json.load(infile)
    assert suc
    assert res['profileName'] == 'reference'
    assert res['version'] == '4.0'
    assert res['filePath'] == config + '/reference.cfg'


def test_saveConfig_3():
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
    with open(config + '/reference.cfg', 'r') as infile:
        res = json.load(infile)
    assert suc
    assert res['profileName'] == 'reference'
    assert res['version'] == '4.0'
    assert res['filePath'] == config + '/reference.cfg'


def test_saveConfig_4():
    # save to new reference
    app.config = {
        'profileName': 'reference',
        'version': '4.0',
        'filePath': config + '/config.cfg'
    }
    suc = app.saveConfig(config + '/reference.cfg')
    assert suc
    with open(config + '/config.cfg', 'r') as inFile:
        a = json.load(inFile)
    assert a['profileName'] == 'reference'
    assert a['version'] == '4.0'
    assert a['filePath'] == config + '/reference.cfg'
    with open(config + '/reference.cfg', 'r') as infile:
        res = json.load(infile)
    assert suc
    assert res['profileName'] == 'reference'
    assert res['version'] == '4.0'
    assert res['filePath'] == config + '/reference.cfg'


def test_saveConfig_5():
    # save with default name and wrong reference
    # -> path should be added automatically as default path
    app.config = {
        'profileName': 'config',
        'version': '4.0',
        'filePath': config + '/reference.cfg'
    }
    suc = app.saveConfig()
    assert suc
    with open(config + '/config.cfg', 'r') as inFile:
        a = json.load(inFile)
    assert a['profileName'] == 'config'
    assert a['version'] == '4.0'
    assert a['filePath'] == config + '/config.cfg'


def test_saveConfig_6():
    # save with reference name and missing file path
    # -> path should be added automatically as default path
    app.config = {
        'profileName': 'reference',
        'version': '4.0',
    }
    suc = app.saveConfig()
    assert suc

    with open(config + '/config.cfg', 'r') as inFile:
        a = json.load(inFile)
    assert a['profileName'] == 'config'
    assert a['version'] == '4.0'
    assert a['filePath'] == config + '/config.cfg'


def test_saveConfig_7():
    # save default without reference without filePath
    # -> path should be added automatically
    app.config = {
        'profileName': 'config',
        'version': '4.0',
    }
    suc = app.saveConfig()
    assert suc
    with open(config + '/config.cfg', 'r') as inFile:
        a = json.load(inFile)
    assert a['profileName'] == 'config'
    assert a['version'] == '4.0'
    assert a['filePath'] == config + '/config.cfg'


def test_saveConfig_8():
    # save default without reference with wrong filePath
    # -> path should be repaired automatically
    app.config = {
        'profileName': 'config',
        'version': '4.0',
        'filePath': None,
    }
    suc = app.saveConfig()
    assert suc
    with open(config + '/config.cfg', 'r') as inFile:
        a = json.load(inFile)
    assert a['profileName'] == 'config'
    assert a['version'] == '4.0'
    assert a['filePath'] == config + '/config.cfg'


def test_storeConfig_1():
    app.mount.obsSite.location = skyfield.toposlib.Topos(latitude_degrees=20,
                                                         longitude_degrees=10,
                                                         elevation_m=500)
    suc = app.storeConfig()
    assert suc
    assert app.config['topoLat'] == 20
