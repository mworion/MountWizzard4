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
from base.alpacaClass import AlpacaClass


class CoverAlpaca(AlpacaClass):
    """
    """

    __all__ = ['CoverAlpaca']

    def __init__(self, app=None, signals=None, data=None):
        super().__init__(app=app, data=data)

        self.alpacaSignals = signals
        self.data = data

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

        brightness = self.getAlpacaProperty('Brightness')
        self.storePropertyToData(brightness,
                                 'FLAT_LIGHT_INTENSITY.FLAT_LIGHT_INTENSITY_VALUE')

        maxBrightness = self.getAlpacaProperty('MaxBrightness')
        self.storePropertyToData(maxBrightness,
                                 'FLAT_LIGHT_INTENSITY.FLAT_LIGHT_INTENSITY_MAX')
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

        maxBrightness = self.app.cover.data.get(
            'FLAT_LIGHT_INTENSITY.FLAT_LIGHT_INTENSITY_MAX', 255)
        brightness = int(maxBrightness / 2)
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
