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
import numpy as np
from indibase import qtIndiBase
# local imports


class IndiClass(object):
    """
    the class indiClass inherits all information and handling of indi devices
    this class will be only referenced from other classes and not directly used

        >>> fw = IndiClass(
        >>>                  host=host
        >>>                  name='MBox'
        >>>                 )
    """

    __all__ = ['MBox',
               ]

    version = '0.1'
    logger = logging.getLogger(__name__)

    # update rate to 1 seconds for setting indi server
    UPDATE_RATE = 1

    def __init__(self,
                 host=None,
                 name='',
                 ):
        super().__init__()

        self.connected = False
        self.client = qtIndiBase.Client(host=host)
        self.name = name
        self.data = {}
        self.device = None

        # link signals
        self.client.signals.newDevice.connect(self.newDevice)
        self.client.signals.removeDevice.connect(self.removeDevice)
        self.client.signals.newProperty.connect(self.connectDevice)
        self.client.signals.newNumber.connect(self.updateData)
        self.client.signals.defNumber.connect(self.updateData)
        self.client.signals.deviceConnected.connect(self.setUpdateConfig)
        self.client.signals.serverConnected.connect(self.serverConnected)
        self.client.signals.serverDisconnected.connect(self.serverDisconnected)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    def serverConnected(self):
        if self.name:
            suc = self.client.watchDevice(self.name)
            self.logger.info(f'Indi server connected, starting watch: result:{suc}')
            return suc
        return False

    @staticmethod
    def serverDisconnected():
        return True

    def newDevice(self, deviceName):
        """
        newDevice is called whenever a new device entry is received in indi client. it
        adds the device if the name fits to the given name in configuration.

        :param deviceName:
        :return: true for test purpose
        """

        if deviceName == self.name:
            self.device = self.client.getDevice(deviceName)
        return True

    def removeDevice(self, deviceName):
        """
        removeDevice is called whenever a device is removed from indi client. it sets
        the device entry to None

        :param deviceName:
        :return: true for test purpose
        """

        if deviceName == self.name:
            self.device = None
            self.data = {}
            return True
        else:
            return False

    def startCommunication(self):
        """
        startCommunication adds a device on the watch list of the server.

        :return: success of reconnecting to server
        """

        self.client.startTimers()
        suc = self.client.connectServer()
        return suc

    def stopCommunication(self):
        """
        stopCommunication adds a device on the watch list of the server.

        :return: success of reconnecting to server
        """

        self.client.stopTimers()
        suc = self.client.disconnectServer()
        return suc

    def connectDevice(self, deviceName, propertyName):
        """
        connectDevice is called when a new property is received and checks it against
        property CONNECTION. if this is there, we could check the connection state of
        a given device

        :param deviceName:
        :param propertyName:
        :return: success if device could connect
        """
        if propertyName != 'CONNECTION':
            return False

        suc = False
        if deviceName == self.name:
            suc = self.client.connectDevice(deviceName=deviceName)
        return suc

    def setUpdateConfig(self, deviceName):
        """
        _setUpdateRate corrects the update rate of weather devices to get an defined
        setting regardless, what is setup in server side.

        :param deviceName:
        :return: success
        """
        pass

    def updateData(self, deviceName, propertyName):
        """
        updateData is called whenever a new number is received in client. it runs
        through the device list and writes the number data to the according locations.
        for global weather data as there is no dew point value available, it calculates
        it and stores it as value as well.

        in addition it does a first setup and config for the device. basically the update
        rates are set to 10 seconds if they are not on this level.

        :param deviceName:
        :param propertyName:
        :return:
        """
        pass
