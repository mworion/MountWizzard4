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
import unittest
# external packages
import PyQt5.QtGui
import PyQt5.QtWidgets
# local import
import mountwizzard4.mw4_loader


class LoaderTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_app = PyQt5.QtWidgets.QApplication([])

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    #
    #
    # testing loader imports
    #
    #

    def test_splash_icon(self):
        value = PyQt5.QtGui.QPixmap(':/mw4.ico')

        self.assertEqual(False, PyQt5.QtGui.QPixmap.isNull(value))

    def test_splash_upcoming(self):
        value = PyQt5.QtGui.QPixmap(':/mw4.ico')
        splash = mountwizzard4.mw4_loader.SplashScreen(value, self.test_app)
        splash.showMessage('test')
        splash.setValue(10)
        splash.setValue(50)
        splash.setValue(90)
        splash.setValue(100)
