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


def test_updatePointGui_alt():
    value = '45'
    app.mount.obsSite.Alt = value
    app.mainW.updatePointGUI()
    assert '45.00' == app.mainW.ui.ALT.text()
    value = None
    app.mount.obsSite.Alt = value
    app.mainW.updatePointGUI()
    assert '-' == app.mainW.ui.ALT.text()


def test_updatePointGui_az():
    value = '45'
    app.mount.obsSite.Az = value
    app.mainW.updatePointGUI()
    assert '45.00' == app.mainW.ui.AZ.text()
    value = None
    app.mount.obsSite.Az = value
    app.mainW.updatePointGUI()
    assert '-' == app.mainW.ui.AZ.text()


def test_updatePointGui_ra():
    value = '45'
    app.mount.obsSite.raJNow = value
    app.mainW.updatePointGUI()
    assert '45:00:00' == app.mainW.ui.RA.text()
    value = None
    app.mount.obsSite.raJNow = value
    app.mainW.updatePointGUI()
    assert '-' == app.mainW.ui.RA.text()


def test_updatePointGui_dec():
    value = '45'
    app.mount.obsSite.decJNow = value
    app.mainW.updatePointGUI()
    assert '+45:00:00' == app.mainW.ui.DEC.text()
    value = None
    app.mount.obsSite.decJNow = value
    app.mainW.updatePointGUI()
    assert '-' == app.mainW.ui.DEC.text()


def test_updatePointGui_jd1():
    value = '2451544.5'
    app.mount.obsSite.utc_ut1 = '0'
    app.mount.obsSite.timeJD = value
    app.mainW.updatePointGUI()
    assert '00:00:00' == app.mainW.ui.timeJD.text()


def test_updatePointGui_jd2():
    value = None
    app.mount.obsSite.timeJD = value
    app.mainW.updatePointGUI()
    assert '-' != app.mainW.ui.timeJD.text()


def test_updatePointGui_pierside():
    value = 'W'
    app.mount.obsSite.pierside = value
    app.mainW.updatePointGUI()
    assert 'WEST' == app.mainW.ui.pierside.text()
    value = None
    app.mount.obsSite.pierside = value
    app.mainW.updatePointGUI()
    assert '-' == app.mainW.ui.pierside.text()


def test_updatePointGui_sidereal():
    value = '45:45:45'
    app.mount.obsSite.timeSidereal = value
    app.mainW.updatePointGUI()
    assert '45:45:45' == app.mainW.ui.timeSidereal.text()
    value = None
    app.mount.obsSite.timeSidereal = value
    app.mainW.updatePointGUI()
    assert '-' == app.mainW.ui.timeSidereal.text()


def test_updateStatusGui_statusText():
    app.mount.obsSite.status = 6
    app.mainW.updateStatusGUI()
    assert 'Slewing or going to stop' == app.mainW.ui.statusText.text()
    app.mount.obsSite.status = None
    app.mainW.updateStatusGUI()
    assert '-' == app.mainW.ui.statusText.text()

