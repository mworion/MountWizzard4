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
# License APL2.0
#
###########################################################
import pytest
from mw4.logic.driverHandling.driverHandling import DriverHandling
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture
def function():
    """Provide a DriverHandling instance with initialized app and DeviceRegistry."""
    app = App()
    driversData = {}
    handl = DriverHandling(app.dReg, driversData)
    handl.app = app
    return handl
