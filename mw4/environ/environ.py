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
# Python  v3.6.5
#
# Michael Würtenberger
# (c) 2018
#
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
# external packages
import PyQt5
from indibase import indiBase
# local imports


class Environment(PyQt5.QtWidgets.QWidget):
    """
    the class Environ inherits all information and handling of environment devices

        >>> fw = Environment(
        >>>                  host=host
        >>>                  localWeatherName='MBox'
        >>>                  sqmName='SQM'
        >>>                  globalWeatherName='OpenWeather'
        >>>                 )
    """

    __all__ = ['Environment',
               ]

    version = '0.1'
    logger = logging.getLogger(__name__)

    def __init__(self,
                 host=None,
                 localWeatherName='',
                 sqmName='',
                 globalWeatherName='',
                 ):
        super().__init__()

        self.client = indiBase.Client(host=host)

        self.localWeatherName = localWeatherName
        self.sqmName = sqmName
        self.globalWeatherName = globalWeatherName

        self.localWeatherDevice = None
        self.sqmDevice = None
        self.globalWeatherDevice = None

        # link signals
        self.client.signals.newDevice.connect(self.newDevice)
        self.client.signals.removeDevice.connect(self.removeDevice)

    @property
    def localWeatherName(self):
        return self._localWeatherName

    @localWeatherName.setter
    def localWeatherName(self, value):
        self._localWeatherName = value

    @property
    def sqmName(self):
        return self._sqmName

    @sqmName.setter
    def sqmName(self, value):
        self._sqmName = value

    @property
    def globalWeatherName(self):
        return self._globalWeatherName

    @globalWeatherName.setter
    def globalWeatherName(self, value):
        self._globalWeatherName = value

    def newDevice(self, deviceName):
        """

        :param deviceName:
        :return:
        """

        if not self.client.isServerConnected():
            return False
        if deviceName == self.localWeatherName:
            self.localWeatherDevice = self.client.getDevice(deviceName)
        elif deviceName == self.sqmName:
            self.sqmDevice = self.client.getDevice(self.sqmName)
        elif deviceName == self.globalWeatherName:
            self.globalWeatherDevice = self.client.getDevice(deviceName)

    def removeDevice(self, deviceName):
        """

        :param deviceName:
        :return:
        """

        if not self.client.isServerConnected():
            return False
        if deviceName == self.localWeatherName:
            self.localWeatherDevice = None
        elif deviceName == self.sqmName:
            self.sqmDevice = None
        elif deviceName == self.globalWeatherName:
            self.globalWeatherDevice = None

    def startCommunication(self):
        self.client.connectServer()

        if self.localWeatherName:
            self.client.watchDevice(self.localWeatherName)
        if self.globalWeatherName:
            self.client.watchDevice(self.globalWeatherName)
        if self.sqmName:
            self.client.watchDevice(self.sqmName)

    def restart(self):
        if self.client.isServerConnected():
            self.client.disconnectServer()
        suc = self.client.connectServer()
        return suc
