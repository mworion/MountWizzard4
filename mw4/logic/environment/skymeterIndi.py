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


class SkymeterIndi(IndiClass):
    """
    """

    __all__ = ['SkymeterIndi']

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

        update = self.device.getNumber('POLLING_PERIOD')
        update['PERIOD_MS'] = self.updateRate
        suc = self.client.sendNewNumber(deviceName=deviceName,
                                        propertyName='POLLING_PERIOD',
                                        elements=update)
        self.log.info(f'Polling [{deviceName}] success: [{suc}]')
        return suc

    def updateNumber(self, deviceName, propertyName):
        """
        adding the data from pegasus uranus meteo sensor to dicts
        :param deviceName:
        :param propertyName:
        :return:
        """
        super().updateNumber(deviceName, propertyName)
        for element, value in self.device.getNumber(propertyName).items():
            key = propertyName + '.' + element
            key = self.convertIndigoProperty(key)
            if key == 'CLOUDS.CloudSkyTemperature':
                self.data['SKY_QUALITY.SKY_TEMPERATURE'] = float(value)
            elif key == 'SKYQUALITY.MPAS':
                self.data['SKY_QUALITY.SKY_BRIGHTNESS'] = float(value)
        return True
