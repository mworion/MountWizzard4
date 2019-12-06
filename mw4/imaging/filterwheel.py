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
# Python  v3.7.5
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


class FilterWheel(indiClass.IndiClass):
    """
    the class FilterWheel inherits all information and handling of the FilterWheel device

        >>> FilterWheel(host=None,
        >>>          name=''
        >>>          )
    """

    __all__ = ['FilterWheel',
               ]

    logger = logging.getLogger(__name__)

    # update rate to 1 seconds for setting indi server
    UPDATE_RATE = 1

    def __init__(self,
                 app=None,
                 host=None,
                 name='',
                 ):

        super().__init__(host=host,
                         name=name,
                         app=app,
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

        update = self.device.getNumber('PERIOD_MS')

        if 'PERIOD' not in update:
            return False

        if update.get('PERIOD', 0) == self.UPDATE_RATE:
            return True

        update['PERIOD'] = self.UPDATE_RATE
        suc = self.client.sendNewNumber(deviceName=deviceName,
                                        propertyName='PERIOD_MS',
                                        elements=update)
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
            key = propertyName + '.' + element
            self.data[key] = value
            # print('number', propertyName, element, value)

        return True

    def updateText(self, deviceName, propertyName):
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

        for element, value in self.device.getText(propertyName).items():
            key = propertyName + '.' + element
            self.data[key] = value
            # print('text', propertyName, element, value)

        return True

    def updateSwitch(self, deviceName, propertyName):
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

        for element, value in self.device.getSwitch(propertyName).items():
            key = propertyName + '.' + element
            self.data[key] = value
            # print('switch', propertyName, element, value)

        return True

    def updateLight(self, deviceName, propertyName):
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

        for element, value in self.device.getLight(propertyName).items():
            key = propertyName + '.' + element
            self.data[key] = value
            # print('light', propertyName, element, value)

        return True

    def sendFilterNumber(self, filterNumber=1):
        """
        sendFilterNumber send the desired filter number

        :param filterNumber:
        :return: success
        """

        # setting fast mode:
        filterNo = self.device.getNumber('FILTER_SLOT')
        filterNo['FILTER_SLOT_VALUE'] = filterNumber
        suc = self.client.sendNewNumber(deviceName=self.name,
                                        propertyName='FILTER_SLOT',
                                        elements=filterNo,
                                        )

        return suc
