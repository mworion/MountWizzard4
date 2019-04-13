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
# Python  v3.6.7
#
# Michael Würtenberger
# (c) 2018
#
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
from datetime import datetime
# external packages
import PyQt5
import numpy as np
# local imports
from mw4.base import indiClass


class DomeSignals(PyQt5.QtCore.QObject):
    """
    The DomeSignals class offers a list of signals to be used and instantiated by
    the Mount class to get signals for triggers for finished tasks to
    enable a gui to update their values transferred to the caller back.

    This has to be done in a separate class as the signals have to be subclassed from
    QObject and the Mount class itself is subclassed from object
    """

    __all__ = ['DomeSignals']
    version = '0.1'

    azimuth = PyQt5.QtCore.pyqtSignal()
    slewFinished = PyQt5.QtCore.pyqtSignal()


class Dome(indiClass.IndiClass):
    """
    the class PegasusUPB inherits all information and handling of the PegasusUPB device

        >>> fw = Dome(
        >>>           host=host
        >>>           name=''
        >>>          )
    """

    __all__ = ['Dome',
               ]

    version = '0.1'
    logger = logging.getLogger(__name__)

    # update rate to 1000 milli seconds for setting indi server
    UPDATE_RATE = 1000

    def __init__(self,
                 host=None,
                 name='',
                 ):
        super().__init__(host=host,
                         name=name
                         )

        self.signals = DomeSignals()

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

        update = self.device.getNumber('POLLING_PERIOD')

        if 'PERIOD_MS' not in update:
            return False

        if update.get('PERIOD_MS', 0) == self.UPDATE_RATE:
            return True

        update['PERIOD_MS'] = self.UPDATE_RATE
        suc = self.client.sendNewNumber(deviceName=deviceName,
                                        propertyName='POLLING_PERIOD',
                                        elements=update,
                                        )

        return suc

    def updateData(self, deviceName, propertyName):
        """
        updateData is called whenever a new number is received in client. it runs
        through the device list and writes the number data to the according locations.
        for global weather data as there is no dew point value available, it calculates
        it and stores it as value as well.

        in addition it does a first setup and config for the device. basically the update
        rates are set to 10 seconds if they are not on this level.

        if no dew point is available in data, it will calculate this value from
        temperature and humidity.

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

            if element == 'DOME_ABSOLUTE_POSITION':
                self.signals.azimuth.emit()
            # print(element, value)
        return True
