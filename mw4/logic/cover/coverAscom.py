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
# written in python3, (c) 2019-2023 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages

# local imports
from base.ascomClass import AscomClass


class CoverAscom(AscomClass):
    """
    """

    __all__ = ['CoverAscom']
    coverStates = ['NotPresent', 'Closed', 'Moving', 'Open', 'Unknown', 'Error']

    def __init__(self, app=None, signals=None, data=None):
        super().__init__(app=app, data=data)

        self.signals = signals
        self.data = data

    def workerPollData(self):
        """
        :return: true for test purpose
        """
        state = self.getAscomProperty('CoverState')
        stateText = self.coverStates[state]
        self.storePropertyToData(stateText, 'Status.Cover')

        brightness = self.getAscomProperty('Brightness')
        self.storePropertyToData(brightness,
                                 'FLAT_LIGHT_INTENSITY.FLAT_LIGHT_INTENSITY_VALUE')

        maxBrightness = self.getAscomProperty('MaxBrightness')
        self.storePropertyToData(maxBrightness,
                                 'FLAT_LIGHT_INTENSITY.FLAT_LIGHT_INTENSITY_MAX')
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

        maxBrightness = self.app.cover.data.get(
            'FLAT_LIGHT_INTENSITY.FLAT_LIGHT_INTENSITY_MAX', 255)
        brightness = int(maxBrightness / 2)
        self.callMethodThreaded(self.client.CalibratorOn, brightness)
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

        self.callMethodThreaded(self.client.CalibratorOn, value)
        return True
