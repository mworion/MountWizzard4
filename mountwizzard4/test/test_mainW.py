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
import os
# external packages
import PyQt5.QtTest
import PyQt5.QtGui
import PyQt5.QtWidgets
import PyQt5.uic
# local import
import mountwizzard4.gui.mainW
import mountwizzard4.mw4_global
import mountcontrol.qtmount


class MainWindowTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = PyQt5.QtWidgets.QApplication([])

    @classmethod
    def tearDownClass(cls):
        pass

    def quit(self):
        pass

    def setUp(self):
        mountwizzard4.mw4_global.work_dir = '/Users/mw/PycharmProjects/MountWizzard4'
        self.mount = mountcontrol.qtmount.Mount()
        self.mainW = mountwizzard4.gui.mainW.MainWindow(self)

    #
    #
    # testing mainW gui
    #
    #

    def test_updateFwGui_productName(self):
        value = 'Test1234'
        self.mount.fw.productName = value
        self.mainW.updateFwGui()
        self.assertEqual(value, self.mainW.ui.productName.text())
        value = None
        self.mount.fw.productName = value
        self.mainW.updateFwGui()
        self.assertEqual('-', self.mainW.ui.productName.text())

    def test_updateFwGui_hwVersion(self):
        value = 'Test1234'
        self.mount.fw.hwVersion = value
        self.mainW.updateFwGui()
        self.assertEqual(value, self.mainW.ui.hwVersion.text())
        value = None
        self.mount.fw.hwVersion = value
        self.mainW.updateFwGui()
        self.assertEqual('-', self.mainW.ui.hwVersion.text())

    def test_updateFwGui_numberString(self):
        value = '2.15.18'
        self.mount.fw.numberString = value
        self.mainW.updateFwGui()
        self.assertEqual(value, self.mainW.ui.numberString.text())
        value = None
        self.mount.fw.numberString = value
        self.mainW.updateFwGui()
        self.assertEqual('-', self.mainW.ui.numberString.text())

    def test_updateFwGui_fwdate(self):
        value = 'Test1234'
        self.mount.fw.fwdate = value
        self.mainW.updateFwGui()
        self.assertEqual(value, self.mainW.ui.fwdate.text())
        value = None
        self.mount.fw.fwdate = value
        self.mainW.updateFwGui()
        self.assertEqual('-', self.mainW.ui.fwdate.text())

    def test_updateFwGui_fwtime(self):
        value = 'Test1234'
        self.mount.fw.fwtime = value
        self.mainW.updateFwGui()
        self.assertEqual(value, self.mainW.ui.fwtime.text())
        value = None
        self.mount.fw.fwtime = value
        self.mainW.updateFwGui()
        self.assertEqual('-', self.mainW.ui.fwtime.text())



