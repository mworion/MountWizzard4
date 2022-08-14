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
# written in python3, (c) 2019-2022 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages

# local imports
from base.indiClass import IndiClass


class WeatherUPBIndi(IndiClass):
    """
    """

    __all__ = ['WeatherUPBIndi']

    def __init__(self, app=None, signals=None, data=None):
        self.signals = signals
        super().__init__(app=app, data=data)

    def setUpdateConfig(self, deviceName):
        """
        :param deviceName:
        :return: success
        """
        if not super().setUpdateConfig(deviceName):
            return False

        update = self.device.getNumber('POLLING')
        update['PERIOD'] = self.updateRate
        suc = self.client.sendNewNumber(deviceName=deviceName,
                                        propertyName='POLLING',
                                        elements=update)
        self.log.info(f'Polling [{deviceName}] success: [{suc}]')
        return suc
