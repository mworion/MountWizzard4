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
import PyQt5
# external packages
# local import
from mw4 import mainApp


def setupQt():
    # global app, spy, mwGlob, test
    mwGlob = {'workDir': '.',
              'configDir': './mw4/test/config',
              'dataDir': './mw4/test/config',
              'tempDir': './mw4/test/temp',
              'modeldata': 'test',
              }

    test = PyQt5.QtWidgets.QApplication([])
    app = mainApp.MountWizzard4(mwGlob=mwGlob)
    spy = PyQt5.QtTest.QSignalSpy(app.message)
    app.mainW.timerGui.stop()
    app.mainW.timerTask.stop()
    return app, spy, mwGlob, test
