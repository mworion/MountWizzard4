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


class Environ(PyQt5.QtWidgets.QWidget):
    """
    the class Environ inherits all information and handling of environment devices

        >>> fw = Environ(
        >>>                 host=host
        >>>                 environName=environName
        >>>                 sqmName=sqmName
        >>>                 weatherName=weatherName
        >>>              )
    """

    __all__ = ['Environ',
               ]

    version = '0.1'
    logger = logging.getLogger(__name__)

    def __init__(self,
                 host=None,
                 environName='',
                 sqmName='',
                 weatherName='',
                 ):
        super().__init__()

        self.client = indiBase.Client(host=host)

        self.environName = environName
        self.sqmName = sqmName
        self.weatherName = weatherName

        self.environDevice = None
        self.sqmDevice = None
        self.weatherDevice = None

        # link signals
        self.client.signals.newDevice.connect(self.newDevice)
        self.client.signals.removeDevice.connect(self.removeDevice)

    @property
    def environName(self):
        return self._environName

    @environName.setter
    def environName(self, value):
        self._environName = value

    @property
    def sqmName(self):
        return self._sqmName

    @sqmName.setter
    def sqmName(self, value):
        self._sqmName = value

    @property
    def weatherName(self):
        return self._weatherName

    @weatherName.setter
    def weatherName(self, value):
        self._weatherName = value

    def newDevice(self, deviceName):
        """

        :param deviceName:
        :return:
        """

        if not self.client.isServerConnected():
            return False
        if deviceName == self.environName:
            self.environDevice = self.client.getDevice(self.environName)
        elif deviceName == self.sqmName:
            self.sqmDevice = self.client.getDevice(self.sqmName)
        elif deviceName == self.weatherName:
            self.weatherDevice = self.client.getDevice(self.weatherName)

    def removeDevice(self, deviceName):
        """

        :param deviceName:
        :return:
        """

        if not self.client.isServerConnected():
            return False
        if deviceName == self.environName:
            self.environDevice = None
        elif deviceName == self.sqmName:
            self.sqmDevice = None
        elif deviceName == self.weatherName:
            self.weatherDevice = None
