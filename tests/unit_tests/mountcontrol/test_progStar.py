############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10_micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2026 by mworion
# Licence APL2.0
#
###########################################################

import unittest
from mw4.mountcontrol.progStar import ProgStar
from skyfield.api import Angle, Star


class TestConfigData(unittest.TestCase):
    def setUp(self):
        pass

    def test_APoint_pierside_1(self):
        aPoint = ProgStar(
            Star(ra_hours=0, dec_degrees=0),
            Star(ra_hours=0, dec_degrees=0),
            Angle(hours=0),
            "e",
        )
        aPoint.pierside = "E"
        self.assertEqual("E", aPoint.pierside)

    def test_APoint_pierside_2(self):
        aPoint = ProgStar(
            Star(ra_hours=0, dec_degrees=0),
            Star(ra_hours=0, dec_degrees=0),
            Angle(hours=0),
            "e",
        )
        aPoint.pierside = "x"
        self.assertEqual("E", aPoint.pierside)
