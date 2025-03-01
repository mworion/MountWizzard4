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
# GUI with PySide for python
#
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages

# local imports
from base.indiClass import IndiClass


class SensorWeatherIndi(IndiClass):
    """ """

    def __init__(self, app=None, signals=None, data=None):
        self.signals = signals
        super().__init__(app=app, data=data)

    def setUpdateConfig(self, deviceName: str) -> None:
        """
        """
        update = self.device.getNumber("POLLING_PERIOD")
        update["PERIOD_MS"] = self.updateRate
        self.client.sendNewNumber(
            deviceName=deviceName, propertyName="POLLING_PERIOD", elements=update
        )
