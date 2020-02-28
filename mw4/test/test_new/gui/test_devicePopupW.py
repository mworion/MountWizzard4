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
import unittest.mock as mock
import pytest
import sys
import platform
import os

# external packages
import PyQt5.QtWidgets
import PyQt5.QtTest
import PyQt5.QtCore

# local import
from mw4.gui.devicePopupW import DevicePopup

test = PyQt5.QtWidgets.QApplication(sys.argv)


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    global app
    data = {}
    geometry = [100, 100, 100, 100]
    framework = {'indi'}
    app = DevicePopup(geometry=geometry,
                      data=data,
                      framework=framework,
                      driver='telescope',
                      deviceType='telescope')


def test_initConfig_1():
    suc = app.initConfig()
    assert suc
