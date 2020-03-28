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

# external packages
import pytest
from PyQt5.QtWidgets import QWidget

# local import
from mw4.mainApp import MountWizzard4
from mw4.gui.widget import MWidget
from mw4.gui.mainW import Ui_MainWindow


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown(qtbot):
    global app, ui

    mwGlob = {'configDir': 'mw4/test/config',
              'dataDir': 'mw4/test/data',
              'tempDir': 'mw4/test/temp',
              'imageDir': 'mw4/test/image',
              'modelDir': 'mw4/test/model',
              'workDir': 'mw4/test',
              }

    widget = QWidget()
    ui = Ui_MainWindow()
    ui.setupUi(widget)

    app = MountWizzard4(mwGlob=mwGlob)
    app.close = MWidget().close
    app.deleteLater = MWidget().deleteLater
    qtbot.addWidget(app)

    yield

    app.close()
    del app


def test_toggleWindow_1():
    def Sender():
        return ui.cameraSetup

    app.sender = Sender

    app.toggleWindow()


def test_toggleWindow_2():
    def Sender():
        return ui.openMessageW

    app.sender = Sender

    app.toggleWindow()


def test_toggleWindow_3():
    def Sender():
        return None

    app.sender = Sender

    app.toggleWindow('showMessageW')

