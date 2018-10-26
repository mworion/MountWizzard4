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
# Python  v3.6.5
#
# Michael Würtenberger
# (c) 2018
#
# Licence APL2.0
#
###########################################################
# standard libraries
# external packages
import PyQt5.QtGui
import PyQt5.QtWidgets
# local import
from mw4 import loader

test = PyQt5.QtWidgets.QApplication([])


#
#
# testing loader imports
#
#

def test_splash_icon():
    value = PyQt5.QtGui.QPixmap(':/mw4.ico')

    assert not PyQt5.QtGui.QPixmap.isNull(value)


def test_splash_upcoming():
    value = PyQt5.QtGui.QPixmap(':/mw4.ico')
    splash = loader.SplashScreen(value, test)
    splash.showMessage('test')
    splash.setValue(10)
    splash.setValue(50)
    splash.setValue(90)
    splash.setValue(100)
