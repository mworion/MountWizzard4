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
# external packages
import PyQt5
# local import
from mw4 import mainApp
from mw4 import loader


def setupQt():
    mwGlob = {'workDir': '.',
              'configDir': 'mw4/test/test_units/config',
              'dataDir': 'mw4/test/test_units/data',
              'tempDir': 'mw4/test/test_units/temp',
              'imageDir': 'mw4/test/test_units/image',
              'modelDir': 'mw4/test/test_units/model',
              }

    test = PyQt5.QtWidgets.QApplication(sys.argv)
    loader.extractDataFiles(mwGlob=mwGlob)
    app = mainApp.MountWizzard4(mwGlob=mwGlob)
    spy = PyQt5.QtTest.QSignalSpy(app.message)
    app.mount.stopTimers()
    app.measure.timerTask.stop()
    app.relay.timerTask.stop()
    return app, spy, mwGlob, test
