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
# written in python3, (c) 2019-2023 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import sys
import unittest.mock as mock
import glob
import os

# external packages
import PyQt6
from PyQt6.QtCore import QObject

# local import
from mw4 import loader


def test_main_1():
    class App:

        @staticmethod
        def exec():
            return 0

        @staticmethod
        def setWindowIcon(a):
            return 0

    class Splash:

        @staticmethod
        def showMessage(a):
            return

        @staticmethod
        def setValue(a):
            return

        @staticmethod
        def close():
            return

    files = glob.glob('tests/workDir/config/*.cfg')
    for f in files:
        os.remove(f)

    mwGlob = {'configDir': 'tests/workDir/config',
              'dataDir': 'tests/workDir/data',
              'tempDir': 'tests/workDir/temp',
              'imageDir': 'tests/workDir/image',
              'modelDir': 'tests/workDir/model',
              'workDir': 'mw4/tests/workDir',
              'modeldata': '4.0',
              }
    with mock.patch.object(PyQt6.QtCore.QBasicTimer,
                           'start'):
        with mock.patch.object(PyQt6.QtCore.QTimer,
                               'start'):
            with mock.patch.object(loader,
                                   'QIcon'):
                with mock.patch.object(loader,
                                       'MyApp',
                                       return_value=App()):
                    with mock.patch.object(loader,
                                           'SplashScreen',
                                           return_value=Splash()):
                        with mock.patch.object(loader,
                                               'MountWizzard4'):
                            with mock.patch.object(loader,
                                                   'setupWorkDirs',
                                                   return_value=mwGlob):
                                with mock.patch.object(sys,
                                                       'exit'):
                                    with mock.patch.object(sys,
                                                           'excepthook'):
                                        loader.main()
