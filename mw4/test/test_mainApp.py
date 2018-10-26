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
import locale
import shutil
# external packages
import PyQt5.QtCore
# local import
from mw4 import mainApp
from mw4 import glob


class MainTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_app = PyQt5.QtWidgets.QApplication([])
        locale.setlocale(locale.LC_ALL, 'en_US')


    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        glob.work_dir = '.'
        glob.config_dir = './config'
        shutil.copy(glob.work_dir + '/mw4/test/config_nok1.cfg', glob.config_dir)
        shutil.copy(glob.work_dir + '/mw4/test/config_nok2.cfg', glob.config_dir)
        shutil.copy(glob.work_dir + '/mw4/test/config_nok3.cfg', glob.config_dir)
        shutil.copy(glob.work_dir + '/mw4/test/config_nok4.cfg', glob.config_dir)
        shutil.copy(glob.work_dir + '/mw4/test/config_nok5.cfg', glob.config_dir)
        shutil.copy(glob.work_dir + '/mw4/test/config_ok.cfg', glob.config_dir)

        self.main = mainApp.MountWizzard4()

    def tearDown(self):
        pass

    #
    #
    # testing main
    #
    #

    def test_loadConfig_ok1(self):
        filePath = 'config/config_ok.cfg'

        suc = self.main.loadConfig(filePath=filePath)
        self.assertEqual(True, suc)
        self.assertEqual('4.0', self.main.config['version'])

    def test_loadConfig_ok2(self):
        filePath = 'config/config_ok.cfg'

        suc = self.main.loadConfig(filePath=filePath)
        self.assertEqual(True, suc)
        self.assertEqual('4.0', self.main.config['version'])

    def test_loadConfig_ok3(self):

        suc = self.main.loadConfig()
        self.assertEqual(True, suc)

    def test_loadConfig_not_ok1(self):
        filePath = 'config/config_nok1.cfg'

        suc = self.main.loadConfig(filePath=filePath)
        self.assertEqual(True, suc)

    def test_loadConfig_not_ok2(self):
        filePath = 'config/config_nok2.cfg'

        suc = self.main.loadConfig(filePath=filePath)
        self.assertEqual(False, suc)

    def test_loadConfig_not_ok3(self):
        filePath = 'config/config_nok3.cfg'

        suc = self.main.loadConfig(filePath=filePath)
        self.assertEqual(False, suc)

    def test_loadConfig_not_ok4(self):
        filePath = 'config/config_nok4.cfg'

        suc = self.main.loadConfig(filePath=filePath)
        self.assertEqual(False, suc)

    def test_loadConfig_not_ok5(self):
        filePath = 'config/config_nok5.cfg'

        suc = self.main.loadConfig(filePath=filePath)
        self.assertEqual(False, suc)

    def test_saveConfig_ok1(self):
        filePath = 'config/test.cfg'

        suc = self.main.saveConfig(filePath=filePath)
        self.assertEqual(True, suc)
