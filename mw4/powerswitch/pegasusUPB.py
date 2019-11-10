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
# Python  v3.7.4
#
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
from datetime import datetime
# external packages
import numpy as np
# local imports
from mw4.base import indiClass


class PegasusUPB(indiClass.IndiClass):
    """
    the class PegasusUPB inherits all information and handling of the PegasusUPB device

        >>> fw = PegasusUPB(
        >>>                  host=host
        >>>                  name=''
        >>>                 )
    """

    __all__ = ['PegasusUPB',
               ]

    version = '0.100.0'
    logger = logging.getLogger(__name__)

    # update rate to 1000 milli seconds for setting indi server
    UPDATE_RATE = 1000

    def __init__(self,
                 app=None,
                 host=None,
                 name='',
                 ):
        super().__init__(host=host,
                         name=name
                         )
        self.app = app

    def setUpdateConfig(self, deviceName):
        """
        _setUpdateRate corrects the update rate of weather devices to get an defined
        setting regardless, what is setup in server side.

        :param deviceName:
        :return: success
        """

        if deviceName != self.name:
            return False

        if self.device is None:
            return False

        # setting polling updates in driver

        update = self.device.getNumber('POLLING')

        if 'PERIOD' not in update:
            return False

        if update.get('PERIOD', 0) == self.UPDATE_RATE:
            return True

        update['PERIOD'] = self.UPDATE_RATE
        suc = self.client.sendNewNumber(deviceName=deviceName,
                                        propertyName='POLLING',
                                        elements=update,
                                        )

        return suc

    def updateNumber(self, deviceName, propertyName):
        """
        updateNumber is called whenever a new number is received in client. it runs
        through the device list and writes the number data to the according locations.

        :param deviceName:
        :param propertyName:
        :return:
        """

        if self.device is None:
            return False
        if deviceName != self.name:
            return False

        for element, value in self.device.getNumber(propertyName).items():
            self.data[element] = value
            # print(propertyName, element, value)

        return True

    def updateSwitch(self, deviceName, propertyName):
        """
        updateSwitch is called whenever a new number is received in client. it runs
        through the device list and writes the number data to the according locations.

        :param deviceName:
        :param propertyName:
        :return:
        """

        if self.device is None:
            return False
        if deviceName != self.name:
            return False

        for element, value in self.device.getSwitch(propertyName).items():
            self.data[element] = value
            # print(propertyName, element, value)

        return True

    def togglePowerPort(self, port=None):
        """
        togglePowerPort

        :param port:
        :return: true fot test purpose
        """

        if port is None:
            return False

        if self.device is None:
            return False

        power = self.device.getSwitch('POWER_CONTROL')
        portName = f'POWER_CONTROL_{port:1.0f}'
        if portName not in power:
            return False

        power[portName] = not power[portName]
        self.client.sendNewSwitch(deviceName=self.name,
                                  propertyName='POWER_CONTROL',
                                  elements=power,
                                  )
        return True

    def togglePowerPortBoot(self, port=None):
        """
        togglePowerPortBoot

        :param port:
        :return: true fot test purpose
        """

        if port is None:
            return False

        if self.device is None:
            return False

        power = self.device.getSwitch('POWER_ON_BOOT')
        portName = f'POWER_PORT_{port:1.0f}'
        if portName not in power:
            return False

        power[portName] = not power[portName]
        self.client.sendNewSwitch(deviceName=self.name,
                                  propertyName='POWER_ON_BOOT',
                                  elements=power,
                                  )
        return True

    def toggleHubUSB(self):
        """
        toggleHubUSB

        :return: true fot test purpose
        """

        if self.device is None:
            return False

        usb = self.device.getSwitch('USB_HUB_CONTROL')
        if 'ENABLED' not in usb:
            return False
        if 'DISABLED' not in usb:
            return False

        usb['ENABLED'] = not usb['ENABLED']
        usb['DISABLED'] = not usb['DISABLED']
        self.client.sendNewSwitch(deviceName=self.name,
                                  propertyName='USB_HUB_CONTROL',
                                  elements=usb,
                                  )
        return True

    def sendAutoDew(self, value=False):
        """
        sendAutoDew

        :param value:
        :return: true fot test purpose
        """

        if self.device is None:
            return False

        autoDew = self.device.getSwitch('AUTO_DEW')
        autoDew['AUTO_DEW_ENABLED'] = value
        autoDew['AUTO_DEW_DISABLED'] = not value
        self.client.sendNewSwitch(deviceName=self.name,
                                  propertyName='AUTO_DEW',
                                  elements=autoDew,
                                  )
        return True
