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
        pass

    def tearDown(self):
        pass

    #
    #
    # testing main
    #
    #

    def test_loadConfig_ok1(self):
        filePath = '/Users/mw/PycharmProjects/MountWizzard4/config/config.cfg'
        name = 'config'
        mw4_global.work_dir = '/Users/mw/PycharmProjects/MountWizzard4'

        main = mw4_main.MountWizzard4()

        suc = main.loadConfig(filePath, name)
        self.assertEqual(True, suc)
        self.assertEqual('config', main.config['name'])

    def test_saveConfig(self):
        pass
