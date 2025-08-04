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
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages

# local imports
from base.indiClass import IndiClass


class SensorWeatherIndi(IndiClass):
    """ """

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.signals = parent.signals
        self.loadConfig: bool = True

    def setUpdateConfig(self, deviceName: str) -> None:
        """ """
        update = self.device.getNumber("POLLING_PERIOD")
        update["PERIOD_MS"] = self.updateRate
        self.client.sendNewNumber(
            deviceName=deviceName, propertyName="POLLING_PERIOD", elements=update
        )
