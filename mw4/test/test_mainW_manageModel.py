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
import unittest.mock as mock
import logging
import pytest
# external packages
import PyQt5.QtGui
import PyQt5.QtWidgets
import PyQt5.uic
import PyQt5.QtTest
import PyQt5.QtCore
# local import
from mw4 import mainApp

test = PyQt5.QtWidgets.QApplication([])
mwGlob = {'workDir': '.',
          'configDir': './mw4/test/config',
          'dataDir': './mw4/test/config',
          'modeldata': 'test',
          }

'''
@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    global spy
    global app

    app = mainApp.MountWizzard4(mwGlob=mwGlob)
    spy = PyQt5.QtTest.QSignalSpy(app.message)
    yield
    spy = None
    app = None
'''
app = mainApp.MountWizzard4(mwGlob=mwGlob)
spy = PyQt5.QtTest.QSignalSpy(app.message)


def test_setNameList():
    value = ['Test1', 'test2', 'test3', 'test4']
    app.mount.model.nameList = value
    app.mainW.setNameList()
    assert 4 == app.mainW.ui.nameList.count()
    value = None
    app.mount.model.nameList = value
    app.mainW.setNameList()
    assert 0 == app.mainW.ui.nameList.count()


def test_showModelPolar1():
    app.mount.obsSite.location = ['49:00:00', '11:00:00', '580']
    app.mount.model._parseStars(['21:52:58.95,+08*56:10.1,   5.7,201',
                                 '21:06:10.79,+45*20:52.8,  12.1,329',
                                 '23:13:58.02,+38*48:18.8,  31.0,162',
                                 '17:43:41.26,+59*15:30.7,   8.4,005',
                                 ],
                                4)
    app.mainW.ui.checkShowErrorValues.setChecked(True)
    suc = app.mainW.showModelPolar()
    assert suc


def test_showModelPolar2():
    app = mainApp.MountWizzard4(mwGlob=mwGlob)
    app.mount.obsSite.location = ['49:00:00', '11:00:00', '580']
    app.mainW.ui.checkShowErrorValues.setChecked(True)
    suc = app.mainW.showModelPolar()
    assert not suc


def test_showModelPolar3():
    app = mainApp.MountWizzard4(mwGlob=mwGlob)
    app.mainW.ui.checkShowErrorValues.setChecked(True)
    suc = app.mainW.showModelPolar()
    assert not suc

