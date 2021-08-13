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
# written in python3, (c) 2019-2021 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages

# local imports
from base.alpacaClass import AlpacaClass
from base.alpacaBase import Covercalibrator


class CoverAlpaca(AlpacaClass):
    """
    the class Dome inherits all information and handling of the Dome device. there will be
    some parameters who will define the slewing position of the dome relating to the
    mount.dome = DomeAlpaca(app=None)
    """

    __all__ = ['CoverAlpaca',
               ]

    CYCLE_POLL_DATA = 1000

    def __init__(self, app=None, signals=None, data=None):
        super().__init__(app=app, data=data, threadPool=app.threadPool)

        # as we have in the base class only the base client there, we will get more
        # specialized with Dome (which is derived from the base class)
        self.client = Covercalibrator()
        self.signals = signals
        self.data = data

    def getInitialConfig(self):
        """
        :return: true for test purpose
        """
        super().getInitialConfig()
        return True

    def workerPollData(self):
        """
        :return: true for test purpose
        """
        states = ['NotPresent', 'Closed', 'Moving', 'Open', 'Unknown', 'Error']
        if not self.deviceConnected:
            return False

        state = self.client.coverstate()
        stateText = states[state]
        self.storePropertyToData(stateText, 'Status.Cover')
        return True

    def closeCover(self):
        """
        :return: true for test purpose
        """
        if not self.deviceConnected:
            return False

        self.client.closecover()
        return True

    def openCover(self):
        """
        :return: true for test purpose
        """
        if not self.deviceConnected:
            return False

        self.client.opencover()
        return True

    def haltCover(self):
        """
        :return: true for test purpose
        """
        if not self.deviceConnected:
            return False

        self.client.haltcover()
        return True

    def lightOn(self):
        """
        :return:
        """
        if not self.deviceConnected:
            return False

        brightness = self.client.brightness()
        self.client.calibratoron(Brightness=brightness)
        return True

    def lightOff(self):
        """
        :return:
        """
        if not self.deviceConnected:
            return False

        self.client.calibratoroff()
        return True

    def lightIntensity(self, value):
        """
        :param value:
        :return:
        """
        if not self.deviceConnected:
            return False

        self.client.calibratoron(Brightness=value)
        return True
