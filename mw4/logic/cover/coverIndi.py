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


class CoverIndi(IndiClass):
    """
    """

    __all__ = ['CoverIndi']

    def __init__(self, app=None, signals=None, data=None):
        self.signals = signals
        super().__init__(app=app, data=data)

    def updateText(self, deviceName, propertyName):
        """
        :param deviceName:
        :param propertyName:
        :return:
        """
        if not super().updateText(deviceName, propertyName):
            return False

        for element, value in self.device.getText(propertyName).items():
            if element == 'Cover':
                value = value.strip().upper()
                if value == 'OPEN':
                    self.data['CAP_PARK.UNPARK'] = True
                    self.data['CAP_PARK.PARK'] = False

                elif value == 'CLOSED':
                    self.data['CAP_PARK.UNPARK'] = False
                    self.data['CAP_PARK.PARK'] = True

                else:
                    self.data['CAP_PARK.UNPARK'] = None
                    self.data['CAP_PARK.PARK'] = None

        return True

    def closeCover(self):
        """
        :return: success
        """
        if self.device is None:
            return False

        cover = self.device.getSwitch('CAP_PARK')

        if 'PARK' not in cover:
            return False

        cover['UNPARK'] = 'Off'
        cover['PARK'] = 'On'

        suc = self.client.sendNewSwitch(deviceName=self.deviceName,
                                        propertyName='CAP_PARK',
                                        elements=cover,
                                        )
        return suc

    def openCover(self):
        """
        :return: success
        """
        if self.device is None:
            return False

        cover = self.device.getSwitch('CAP_PARK')

        if 'UNPARK' not in cover:
            return False

        cover['UNPARK'] = 'On'
        cover['PARK'] = 'Off'

        suc = self.client.sendNewSwitch(deviceName=self.deviceName,
                                        propertyName='CAP_PARK',
                                        elements=cover,
                                        )
        return suc

    @staticmethod
    def haltCover():
        """
        :return: success
        """
        return False

    def lightOn(self):
        """
        :return:
        """
        if self.device is None:
            return False

        light = self.device.getSwitch('FLAT_LIGHT_CONTROL')

        if 'FLAT_LIGHT_ON' not in light:
            return False

        light['FLAT_LIGHT_ON'] = 'On'
        light['FLAT_LIGHT_OFF'] = 'Off'

        suc = self.client.sendNewSwitch(deviceName=self.deviceName,
                                        propertyName='FLAT_LIGHT_CONTROL',
                                        elements=light,
                                        )
        return suc

    def lightOff(self):
        """
        :return:
        """
        if self.device is None:
            return False

        light = self.device.getSwitch('FLAT_LIGHT_CONTROL')

        if 'FLAT_LIGHT_OFF' not in light:
            return False

        light['FLAT_LIGHT_ON'] = 'Off'
        light['FLAT_LIGHT_OFF'] = 'On'

        suc = self.client.sendNewSwitch(deviceName=self.deviceName,
                                        propertyName='FLAT_LIGHT_CONTROL',
                                        elements=light,
                                        )
        return suc

    def lightIntensity(self, value):
        """
        :return:
        """
        if self.device is None:
            return False

        light = self.device.getNumber('FLAT_LIGHT_INTENSITY')

        if 'FLAT_LIGHT_INTENSITY_VALUE' not in light:
            return False

        light['FLAT_LIGHT_INTENSITY_VALUE'] = value

        suc = self.client.sendNewNumber(deviceName=self.deviceName,
                                        propertyName='FLAT_LIGHT_INTENSITY',
                                        elements=light,
                                        )
        return suc
