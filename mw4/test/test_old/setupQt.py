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
    mwGlob = {'workDir': 'mw4/test',
              'configDir': 'mw4/test/config',
              'dataDir': 'mw4/test/data',
              'tempDir': 'mw4/test/temp',
              'imageDir': 'mw4/test/image',
              'modelDir': 'mw4/test/model',
              }

    test = PyQt5.QtWidgets.QApplication(sys.argv)
    loader.extractDataFiles(mwGlob=mwGlob)
    app = mainApp.MountWizzard4(mwGlob=mwGlob)
    spy = PyQt5.QtTest.QSignalSpy(app.message)
    app.mount.stopTimers()
    app.measure.timerTask.stop()
    app.relay.timerTask.stop()
    return app, spy, mwGlob, test
