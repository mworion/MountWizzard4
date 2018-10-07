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
import PyQt5.QtCore
# local import
import mw4_main
import mw4_global


class MainTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_app = PyQt5.QtWidgets.QApplication([])

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        mw4_global.work_dir = '/Users/mw/PycharmProjects/MountWizzard4'
        mw4_global.config_dir = '/Users/mw/PycharmProjects/MountWizzard4/config'

    def tearDown(self):
        pass

    #
    #
    # testing main
    #
    #

    def test_loadConfig_ok1(self):
        filePath = '/Users/mw/PycharmProjects/MountWizzard4/config/config0.cfg'
        name = 'config'
        main = mw4_main.MountWizzard4()

        suc = main.loadConfig(filePath, name)
        self.assertEqual(True, suc)
        self.assertEqual('config', main.config['name'])
        self.assertEqual('4.0', main.config['version'])

    def test_loadConfig_not_ok1(self):
        filePath = '/Users/mw/PycharmProjects/MountWizzard4/config/config_nok1.cfg'
        name = 'config'
        main = mw4_main.MountWizzard4()

        suc = main.loadConfig(filePath, name)
        self.assertEqual(False, suc)

    def test_loadConfig_not_ok2(self):
        filePath = '/Users/mw/PycharmProjects/MountWizzard4/config/config_nok2.cfg'
        name = 'config'
        main = mw4_main.MountWizzard4()

        suc = main.loadConfig(filePath, name)
        self.assertEqual(False, suc)

    def test_loadConfig_not_ok3(self):
        filePath = '/Users/mw/PycharmProjects/MountWizzard4/config/config_nok3.cfg'
        name = 'config'
        main = mw4_main.MountWizzard4()

        suc = main.loadConfig(filePath, name)
        self.assertEqual(False, suc)

    def test_loadConfig_not_ok4(self):
        filePath = '/Users/mw/PycharmProjects/MountWizzard4/config/config_nok4.cfg'
        name = 'config'
        main = mw4_main.MountWizzard4()

        suc = main.loadConfig(filePath, name)
        self.assertEqual(False, suc)

    def test_loadConfig_not_ok5(self):
        filePath = '/Users/mw/PycharmProjects/MountWizzard4/config/config_nok5.cfg'
        name = 'config'
        main = mw4_main.MountWizzard4()

        suc = main.loadConfig(filePath, name)
        self.assertEqual(False, suc)

    def test_saveConfig(self):
        filePath = '/Users/mw/PycharmProjects/MountWizzard4/config/test.cfg'
        name = 'test'
        main = mw4_main.MountWizzard4()

        suc = main.saveConfig(filePath, name)
        self.assertEqual(True, suc)
