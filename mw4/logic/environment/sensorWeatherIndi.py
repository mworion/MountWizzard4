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
#
# written in python3, (c) 2019-2023 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages

# local imports
from base.indiClass import IndiClass


class SensorWeatherIndi(IndiClass):
    """
    """

    __all__ = ['SensorWeatherIndi']

    def __init__(self, app=None, signals=None, data=None):
        self.signals = signals
        super().__init__(app=app, data=data)

    def setUpdateConfig(self, deviceName):
        """
        setUpdateRate corrects the update rate of weather devices to get a defined
        setting regardless, what is set up in server side.

        :param deviceName:
        :return: success
        """
        if not super().setUpdateConfig(deviceName):
            return False

        update = self.device.getNumber('POLLING_PERIOD')
        update['PERIOD_MS'] = self.updateRate
        suc = self.client.sendNewNumber(deviceName=deviceName,
                                        propertyName='POLLING_PERIOD',
                                        elements=update)
        self.log.info(f'Polling [{deviceName}] success: [{suc}]')
        return suc
