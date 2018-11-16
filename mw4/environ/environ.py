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
        >>>              )
    """

    __all__ = ['Environ',
               ]

    version = '0.1'
    logger = logging.getLogger(__name__)

    ENVIRON = ''
    SQM = ''
    WEATHER = ''

    def __init__(self,
                 host=None,
                 ):
        super().__init__()

        self.host = host
        self.client = indiBase.Client(host=self.host)
        self.environDevice = None
        self.sqmDevice = None
        self.weatherDevice = None

    def linkDevices(self, deviceName):
        if not self.client:
            return False
        if deviceName == self.ENVIRON:
            self.environDevice = self.client.getDevice(self.ENVIRON)
        elif deviceName == self.SQM:
            self.sqmDevice = self.client.getDevice(self.SQM)
        elif deviceName == self.WEATHER:
            self.weatherDevice = self.client.getDevice(self.WEATHER)
