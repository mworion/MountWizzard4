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
import glob
import os
import faulthandler
faulthandler.enable()

# external packages
import pytest
from PyQt5.QtCore import QObject

# local import
from mw4 import loader
from mw4 import mainApp


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown(qtbot):
    files = glob.glob('mw4/test/config/*.cfg')
    for f in files:
        os.remove(f)

    yield


def test_main_1(qtbot):
    class Test(QObject):
        @staticmethod
        def installEventFilter(a):
            return

        @staticmethod
        def exec_():
            return 0

        @staticmethod
        def setWindowIcon(a):
            return 0

    mwGlob = {'configDir': 'mw4/test/config',
              'dataDir': 'mw4/test/data',
              'tempDir': 'mw4/test/temp',
              'imageDir': 'mw4/test/image',
              'modelDir': 'mw4/test/model',
              'workDir': 'mw4/test',
              'modeldata': '4.0',
              }

    with mock.patch.object(mainApp,
                           'MountWizzard4'):
        with mock.patch.object(loader,
                               'MyApp',
                               return_value=Test()):
            with mock.patch.object(loader,
                                   'setupWorkDirs',
                                   return_value=mwGlob):
                with mock.patch.object(sys,
                                       'exit'):
                    loader.main()
