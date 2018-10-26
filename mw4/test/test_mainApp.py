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
import unittest
import locale
import shutil
# external packages
import PyQt5.QtCore
# local import
from mw4 import mainApp
from mw4 import glob


test = PyQt5.QtWidgets.QApplication([])
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

glob.work_dir = '.'
glob.config_dir = './mw4/test/config'

test_app = mainApp.MountWizzard4()


#
#
# testing main
#
#

def test_loadConfig_ok1():
    filePath = './mw4/test/config/config_ok.cfg'

    suc = test_app.loadConfig(filePath=filePath)
    assert suc
    assert '4.0' == test_app.config['version']


def test_loadConfig_ok2():
    filePath = './mw4/test/config/config_ok.cfg'

    suc = test_app.loadConfig(filePath=filePath)
    assert suc
    assert '4.0' == test_app.config['version']


def test_loadConfig_ok3():

    suc = test_app.loadConfig()
    assert suc


def test_loadConfig_not_ok1():
    filePath = './mw4/test/config/config_nok1.cfg'

    suc = test_app.loadConfig(filePath=filePath)
    assert suc


def test_loadConfig_not_ok2():
    filePath = './mw4/test/config/config_nok2.cfg'

    suc = test_app.loadConfig(filePath=filePath)
    assert not suc


def test_loadConfig_not_ok3():
    filePath = './mw4/test/config/config_nok3.cfg'

    suc = test_app.loadConfig(filePath=filePath)
    assert not suc


def test_loadConfig_not_ok4():
    filePath = './mw4/test/config/config_nok4.cfg'

    suc = test_app.loadConfig(filePath=filePath)
    assert not suc


def test_loadConfig_not_ok5():
    filePath = './mw4/test/config/config_nok5.cfg'

    suc = test_app.loadConfig(filePath=filePath)
    assert not suc


def test_saveConfig_ok1():
    filePath = './mw4/test/config/test.cfg'

    suc = test_app.saveConfig(filePath=filePath)
    assert suc
