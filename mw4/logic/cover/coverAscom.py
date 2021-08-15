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
from base.ascomClass import AscomClass


class CoverAscom(AscomClass):
    """
    the class Dome inherits all information and handling of the Dome device. there will be
    some parameters who will define the slewing position of the dome relating to the
    mount.dome = DomeAscom(app=None)
    """

    __all__ = ['CoverAscom',
               ]

    CYCLE_POLL_DATA = 1000
    coverStates = ['NotPresent', 'Closed', 'Moving', 'Open', 'Unknown', 'Error']

    def __init__(self, app=None, signals=None, data=None):
        super().__init__(app=app, data=data, threadPool=app.threadPool)

        self.signals = signals
        self.data = data

    def workerGetInitialConfig(self):
        """
        :return: true for test purpose
        """
        super().workerGetInitialConfig()
        return True

    def workerPollData(self):
        """
        :return: true for test purpose
        """
        state = self.getAscomProperty('CoverState')
        stateText = self.coverStates[state]
        self.storePropertyToData(stateText, 'Status.Cover')
        return True

    def closeCover(self):
        """
        :return: true for test purpose
        """
        if not self.deviceConnected:
            return False

        self.callMethodThreaded(self.client.CloseCover)
        return True

    def openCover(self):
        """
        :return: true for test purpose
        """
        if not self.deviceConnected:
            return False

        self.callMethodThreaded(self.client.OpenCover)
        return True

    def haltCover(self):
        """
        :return: true for test purpose
        """
        if not self.deviceConnected:
            return False

        self.callMethodThreaded(self.client.HaltCover)
        return True

    def lightOn(self):
        """
        :return:
        """
        if not self.deviceConnected:
            return False

        self.callMethodThreaded(self.client.CalibratorOn)
        return True

    def lightOff(self):
        """
        :return:
        """
        if not self.deviceConnected:
            return False

        self.callMethodThreaded(self.client.CalibratorOff)
        return True

    def lightIntensity(self, value):
        """
        :param value:
        :return:
        """
        if not self.deviceConnected:
            return False

        self.callMethodThreaded(self.client.Brightness, value)
        return True
