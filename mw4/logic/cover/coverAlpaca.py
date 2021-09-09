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

        self.alpacaSignals = signals
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

        state = self.getAlpacaProperty('coverstate')
        stateText = states[state]
        self.storePropertyToData(stateText, 'Status.Cover')
        return True

    def closeCover(self):
        """
        :return: true for test purpose
        """
        if not self.deviceConnected:
            return False

        self.getAlpacaProperty('closecover')
        return True

    def openCover(self):
        """
        :return: true for test purpose
        """
        if not self.deviceConnected:
            return False

        self.getAlpacaProperty('opencover')
        return True

    def haltCover(self):
        """
        :return: true for test purpose
        """
        if not self.deviceConnected:
            return False

        self.getAlpacaProperty('haltcover')
        return True

    def lightOn(self):
        """
        :return:
        """
        if not self.deviceConnected:
            return False

        brightness = self.getAlpacaProperty('brightness')
        self.setAlpacaProperty('calibratoron', Brightness=brightness)
        return True

    def lightOff(self):
        """
        :return:
        """
        if not self.deviceConnected:
            return False

        self.getAlpacaProperty('calibratoroff')
        return True

    def lightIntensity(self, value):
        """
        :param value:
        :return:
        """
        if not self.deviceConnected:
            return False

        self.setAlpacaProperty('calibratoron', Brightness=value)
        return True
