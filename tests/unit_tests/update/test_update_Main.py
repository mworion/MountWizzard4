############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock

from base.loggerMW import setupLogging

# external packages
# local import
from mw4 import update

setupLogging()


@mock.patch("sys.argv", ["python", "1", "10", "10", "0"])
def test_main_2():
    class Test:
        def __init__(self, runnable=None, version=None, x=0, y=0, colorSet=0):
            pass

        @staticmethod
        def run():
            return

    update.UpdateGUI = Test
    update.main()
