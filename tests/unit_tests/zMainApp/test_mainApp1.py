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
#
# written in python3, (c) 2019-2021 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
import sys
import unittest.mock as mock
import logging

# external packages
import PyQt5

# local import
from mainApp import MountWizzard4
from base.loggerMW import addLoggingLevel

addLoggingLevel('TRACE', 5)


def test_start_parameters_1(qapp):
    mwGlob = {'configDir': 'tests/config',
              'dataDir': 'tests/data',
              'tempDir': 'tests/temp',
              'imageDir': 'tests/image',
              'modelDir': 'tests/model',
              'workDir': 'mw4/test',
              }
    with mock.patch.object(PyQt5.QtWidgets.QWidget,
                           'show'):
        with mock.patch.object(PyQt5.QtCore.QTimer,
                               'start'):
            with mock.patch.object(PyQt5.QtCore.QBasicTimer,
                                   'start'):
                with mock.patch.object(MountWizzard4,
                                       'checkAndSetAutomation',
                                       return_value=None):
                    with mock.patch.object(sys,
                                           'argv',
                                           return_value=['test']):
                        MountWizzard4(mwGlob=mwGlob, application=qapp)
