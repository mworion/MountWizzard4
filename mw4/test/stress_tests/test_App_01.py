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
# Python  v3.7.5
#
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
# standard libraries
import sys
import unittest.mock as mock
import faulthandler

# external packages
import pytest
import PyQt5
from PyQt5.QtTest import QTest

# local import
from mw4.mainApp import MountWizzard4


mwglob = {'dataDir': 'mw4/test/data',
          'configDir': 'mw4/test/config',
          'workDir': 'mw4/test',
          'imageDir': 'mw4/test/image',
          'tempDir': 'mw4/test/temp',
          'modelDir': 'mw4/test/model',
          'modelData': '4.0'
          }


@pytest.fixture(autouse=True, scope='function')
def mw4():

    testArgv = ['run', 'test']
    faulthandler.enable()

    with mock.patch.object(sys,
                           'argv',
                           testArgv):
        mw4 = MountWizzard4(mwGlob=mwglob)
        yield mw4


def test_1(qtbot, mw4):

    qtbot.add_widget(mw4.mainW)
    QTest.qWait(1000)
    # qtbot.mouseClick(mw4.mainW.ui.saveConfigQuit, PyQt5.QtCore.Qt.LeftButton)
    QTest.qWait(10000)
