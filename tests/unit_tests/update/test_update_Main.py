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

# external packages
# local import
import mw4.update
from mw4.base.loggerMW import setupLogging

setupLogging()


@mock.patch("sys.argv", ["python", "1", "10", "10", "0"])
def test_main_2():
    class Test:
        def __init__(self, runnable=None, version=None, x=0, y=0, colorSet=0):
            pass

        @staticmethod
        def run():
            return

    mw4.update.UpdateGUI = Test
    mw4.update.main()
