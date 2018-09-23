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
    # testing mainW gui fw
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

    #
    #
    # testing mainW gui model name
    #
    #

    def test_setNameList(self):
        value = ['Test1', 'test2', 'test3', 'test4']
        self.mount.model.nameList = value
        self.mainW.setNameList()
        self.assertEqual(4, self.mainW.ui.nameList.count())
        value = None
        self.mount.model.nameList = value
        self.mainW.setNameList()
        self.assertEqual(0, self.mainW.ui.nameList.count())

    #
    #
    # testing mainW gui pointing
    #
    #

    def test_updatePointGui_alt(self):
        value = '45'
        self.mount.obsSite.Alt = value
        self.mainW.updatePointGUI()
        self.assertEqual('45.00', self.mainW.ui.ALT.text())
        value = None
        self.mount.obsSite.Alt = value
        self.mainW.updatePointGUI()
        self.assertEqual('-', self.mainW.ui.ALT.text())

    def test_updatePointGui_az(self):
        value = '45'
        self.mount.obsSite.Az = value
        self.mainW.updatePointGUI()
        self.assertEqual('45.00', self.mainW.ui.AZ.text())
        value = None
        self.mount.obsSite.Az = value
        self.mainW.updatePointGUI()
        self.assertEqual('-', self.mainW.ui.AZ.text())

    def test_updatePointGui_ra(self):
        value = '45'
        self.mount.obsSite.raJNow = value
        self.mainW.updatePointGUI()
        self.assertEqual('45:00:00', self.mainW.ui.RA.text())
        value = None
        self.mount.obsSite.raJNow = value
        self.mainW.updatePointGUI()
        self.assertEqual('-', self.mainW.ui.RA.text())

    def test_updatePointGui_dec(self):
        value = '45'
        self.mount.obsSite.decJNow = value
        self.mainW.updatePointGUI()
        self.assertEqual('+45:00:00', self.mainW.ui.DEC.text())
        value = None
        self.mount.obsSite.decJNow = value
        self.mainW.updatePointGUI()
        self.assertEqual('-', self.mainW.ui.DEC.text())
