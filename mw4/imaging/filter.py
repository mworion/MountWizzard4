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


class Filter(indiClass.IndiClass):
    """
    the class Filter inherits all information and handling of the FilterWheel device

        >>> f = Filter(app=None)
    """

    __all__ = ['Filter',
               ]

    logger = logging.getLogger(__name__)

    # update rate to 1 seconds for setting indi server
    UPDATE_RATE = 1

    def __init__(self, app=None):
        super().__init__(app=app)

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
